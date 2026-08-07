"""PDF render hook for mkdocs-with-pdf: draw the mermaid diagrams before WeasyPrint runs.

The plugin imports this by name — `pdf_event_hook`, from the working directory — so the file
has to sit at the repo root next to mkdocs.yml, and cannot move into tools/.

Why the browser pass lives here instead of in the plugin's own `render_js: true`
--------------------------------------------------------------------------------
The plugin has that feature and it is broken with current BeautifulSoup. Its `_render_js`
ends with `tag.text = self._mixed_script` (generator.py:381), and `Tag.text` is a read-only
property, so the build dies with `property 'text' of 'Tag' object has no setter` the moment
a page carries an inline <script> — which every Material page does. Reproduced in a Linux
container running the real pipeline.

So the hook does the same job at `pre_pdf_render`, which the plugin calls with the finished
document just before handing it to WeasyPrint. Same technique, none of that code path, and
the timeout and browser flags are ours.

Why it is needed at all
-----------------------
```mermaid fences are rendered by mermaid.js in the browser. WeasyPrint does not execute
JavaScript, so without this the 28 diagrams in the English book print as their own source
code. Material's own bundle would do the rendering, but its pipeline is tied to a page
structure the combined PDF document does not have — driving Chrome over the assembled file
with Material's scripts attached left all 28 fences untouched (`data-processed` count: 0).
Calling mermaid directly does not depend on that pipeline.
"""

import os
import shutil
import subprocess
import tempfile

from bs4 import BeautifulSoup

# The same version Material's bundle loads (grep `unpkg.com/mermaid` in
# assets/javascripts/bundle.*.js), so the PDF draws what the site draws. It does mean the
# PDF build needs the network — the site build already did, for the same file.
MERMAID_URL = "https://unpkg.com/mermaid@11/dist/mermaid.min.js"

# First name found wins. ubuntu-latest has google-chrome preinstalled; a plain Debian image
# has chromium. BMM_PDF_CHROME overrides both.
BROWSERS = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")

# Wall-clock, not the browser's virtual clock. A hung browser must fail the build, not hold
# the runner for six hours. 28 diagrams take a few seconds.
TIMEOUT_S = 180

# Two things here are not optional.
#
# `pre.mermaid > code`: pymdownx.superfences wraps the diagram source in a <code>. mermaid
# reads the element's own text, so the <code> is flattened away first.
#
# `htmlLabels: false`: by default mermaid puts node labels in <foreignObject> — HTML embedded
# in SVG, which WeasyPrint does not implement. Measured on this document: the first attempt
# produced 686 of them, and every diagram would have printed as empty boxes. With the flag
# off, mermaid emits real <text> elements and the count is 0.
INIT_JS = """
document.querySelectorAll('pre.mermaid > code').forEach(function (code) {
  code.parentNode.textContent = code.textContent;
});
mermaid.initialize({
  startOnLoad: false,
  theme: 'neutral',
  htmlLabels: false,
  flowchart: { htmlLabels: false, useMaxWidth: true },
  sequence: { useMaxWidth: true },
  class: { htmlLabels: false }
});
mermaid.run({ querySelector: 'pre.mermaid' });
"""


def _browser() -> str | None:
    override = os.environ.get("BMM_PDF_CHROME")
    if override:
        return shutil.which(override) or override
    for name in BROWSERS:
        found = shutil.which(name)
        if found:
            return found
    return None


def pre_pdf_render(soup: BeautifulSoup, logger) -> BeautifulSoup:
    blocks = soup.select("pre.mermaid")
    if not blocks:
        return soup

    browser = _browser()
    if not browser:
        # Deliberately not fatal. A contributor without a browser still gets a readable PDF,
        # just with the diagrams as source; CI has a preflight step that does fail.
        logger.warning(
            f"no browser found ({', '.join(BROWSERS)}) — "
            f"{len(blocks)} mermaid diagram(s) will print as source"
        )
        return soup

    body = soup.find("body")
    if body is None:  # pragma: no cover - the generator always builds one
        return soup
    body.append(soup.new_tag("script", src=MERMAID_URL))
    init = soup.new_tag("script")
    init.string = INIT_JS
    body.append(init)

    logger.info(f"mermaid: rendering {len(blocks)} diagram(s) via {browser}")

    # delete=False + explicit unlink: on Windows a NamedTemporaryFile cannot be reopened by
    # another process while it is still open here.
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
    try:
        tmp.write(str(soup))
        tmp.close()
        out = subprocess.run(
            [
                browser,
                "--headless",
                "--no-sandbox",          # CI and containers run as root
                "--disable-gpu",
                "--allow-file-access-from-files",   # the document links assets by file://
                "--run-all-compositor-stages-before-draw",
                "--virtual-time-budget=30000",
                "--dump-dom",
                tmp.name,
            ],
            capture_output=True,
            timeout=TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        logger.error(f"the browser did not finish in {TIMEOUT_S}s; diagrams left as source")
        return soup
    finally:
        os.unlink(tmp.name)

    rendered = out.stdout.decode("utf-8", errors="replace")
    if not rendered.strip():
        logger.error("the browser returned nothing; diagrams left as source")
        return soup

    new_soup = BeautifulSoup(rendered, "html.parser")
    drawn = len(new_soup.select("pre.mermaid[data-processed]"))
    if drawn < len(blocks):
        # Worth a loud line rather than a silent half-illustrated book: the usual cause is
        # unpkg being unreachable.
        logger.warning(
            f"mermaid: only {drawn}/{len(blocks)} diagram(s) drawn — "
            "the rest will print as source (is unpkg.com reachable?)"
        )
    else:
        logger.info(f"mermaid: {drawn} diagram(s) drawn")
    return new_soup
