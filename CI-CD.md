# CI/CD of this repository

The two GitHub Actions workflows of BMM Docs: what starts them, what they check, what makes them
fail, and how to run the same thing locally. (The workflows of the BMM app itself are documented in
the site: `docs/how-it-works/ci-cd.md`.) Français : [CI-CD_FR.md](CI-CD_FR.md).

| Workflow | File | Starts on | Blocks on |
|---|---|---|---|
| Docs | `.github/workflows/docs.yml` | push to `master`, every pull request, by hand | a replay that is an LFS pointer or missing, stale screenshot annotations, a broken link (`mkdocs build --strict`), a missing browser, a truncated PDF |
| Security | `.github/workflows/security.yml` | push to `master`, every pull request, Monday 04:23 UTC, by hand | a secret in the history, or a Semgrep / Trivy finding at or above the threshold |

Every action is pinned to a full commit SHA with its tag in a comment. Every Docker image is pinned
to a digest. Each workflow starts from `permissions: {}`, and each job asks only for what it uses.

## Docs (`docs.yml`)

The **build** job has `contents: read`. It:

1. checks out with `lfs: true` and checks the replays;
2. installs the toolchain with `pip install --require-hashes -r requirements.txt`;
3. checks the annotations (`python tools/annotate.py --check`);
4. builds the site with `mkdocs build --strict`;
5. builds the dark and light PDF editions and reads all four back with `tools/check_pdf.py`;
6. uploads the PDFs as the `bettermodsmanager-pdf` artifact.

On `master`, the **deploy** job publishes the site to GitHub Pages. It is the only job with
`pages: write` and `id-token: write`.

`requirements.txt` is a **full lock**: every transitive package, with the sha256 of every file PyPI
serves for it, generated from `requirements.in`. Edit `requirements.in`, then regenerate:

```bash
uv pip compile requirements.in --universal --python-version 3.12 --generate-hashes -o requirements.txt
```

`--universal` keeps the lock valid on Windows too: platform-only packages such as `colorama` are
listed with their markers.

- **Secrets:** none. **Variables:** none.
- **Run it locally:** `pip install -r requirements.txt`, then `mkdocs build --strict`. The PDF needs
  the pango and harfbuzz libraries listed in the workflow, or use `python tools/build_pdf_chrome.py`
  on Windows.

## Security (`security.yml`)

| Job | Tool | What it reads | Fails when |
|---|---|---|---|
| Gate self-test | `node --test` | `.github/scripts/security-gate.test.mjs` | the gate itself is wrong |
| Secrets | Gitleaks 8.30.1 | the whole git history | any finding not reviewed in `.gitleaks.toml` / `.gitleaksignore`, or zero commits read |
| SAST | Semgrep 1.178.0 | the whole checkout: `tools/`, `pdf_event_hook.py`, the replay player JS, the workflows | a finding at or above the Semgrep threshold |
| Dependencies | Trivy 0.74.0 | the `requirements.txt` lock, so every transitive package | a finding at or above the Trivy threshold |
| Upload SARIF to code scanning | `codeql-action/upload-sarif` | the three SARIF files | an upload that fails on a repository that supports code scanning |
| PR comment | `gh api` | the three verdicts | never fails a pull request by itself |

Each scanner writes its report and exits 0. **One script decides:**
`.github/scripts/security-gate.mjs`, the same file in BMM Docs, BMM, BetterInstaller and BCW.

- **Secrets:** none to create. The upload and comment jobs use `GITHUB_TOKEN`.
- **Artifacts** (kept 30 days): `security-gitleaks`, `security-semgrep` and `security-trivy`. Each
  holds the JSON report, the SARIF, a `*-summary.md` table and a `*.result.json` verdict.
- **No DAST (ZAP, Nuclei):** the site is static HTML. There is no staging server and no server-side
  code, and the only live host is the production site, which no scan here may target.

### Reading the results

- **Log and job summary:** one table per tool; each blocking finding is an `::error` annotation.
  Gitleaks runs with `--redact`, so a value never reaches a log.
- **PR comment:** one comment per pull request, edited on every run and found by its hidden first
  line `<!-- bmm-docs-security-gate -->`. It shows one row per tool, an overall `PASSED`, `FAILED`
  or `INCOMPLETE`, and a link to the run and its artifacts. `INCOMPLETE` means a scan produced no
  verdict; it is never a pass. A fork or Dependabot gets a read-only token: a notice, no comment.
- **Code scanning (Security tab):** one category per tool (`gitleaks`, `semgrep`, `trivy`). Alerts
  are tracked over time and annotated on pull-request lines. They are uploaded even when a gate
  failed. The job checks first that code scanning is available (this repository is public). If it
  is not, it prints a notice and keeps the SARIF in the artifacts.

Code scanning is a view. **The gate fails the build**, and a dismissed alert fails it again at the
next run as long as the tool reports it.

### Thresholds

Repository variables (**Settings > Secrets and variables > Actions > Variables**):

| Variable | Values | Default |
|---|---|---|
| `SECURITY_GATE_SEVERITY` | `critical`, `high`, `medium`, `low` | `high` |
| `SECURITY_GATE_SEVERITY_SEMGREP` | same | the global value |
| `SECURITY_GATE_SEVERITY_TRIVY` | same | the global value |

`high` and above block by default. `medium` blocks only when chosen. `low` blocks only at `low`, and
`info` never does. Gitleaks has no threshold. An unknown value fails the run: a typo must never mean
that nothing blocks.

### Running the scans by hand

```bash
GITLEAKS=zricethezav/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f
SEMGREP=semgrep/semgrep:1.178.0@sha256:32e459968daabe7ab86968184a29109b9564aa00392401156f9788452b42786b
TRIVY=aquasec/trivy:0.74.0@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969
mkdir -p reports

# Secrets (the log must say "N commits scanned", N > 0)
docker run --rm -v "$PWD:/repo" -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0='*' \
  "$GITLEAKS" git /repo --config /repo/.gitleaks.toml --redact --verbose \
  --report-format json --report-path /repo/reports/gitleaks.json --exit-code 0
node .github/scripts/security-gate.mjs --tool gitleaks --report reports/gitleaks.json

# SAST, with the rules at the pinned commit
REF=$(grep -oE 'SEMGREP_RULES_REF: [0-9a-f]{40}' .github/workflows/security.yml | cut -d' ' -f2)
git init -q ../semgrep-rules && git -C ../semgrep-rules fetch -q --depth 1 https://github.com/semgrep/semgrep-rules "$REF" \
  && git -C ../semgrep-rules checkout -q FETCH_HEAD
CFG=$(grep -v '^#' .github/security/semgrep-rules.txt | grep . | sed 's#^#--config=/rules/#')
docker run --rm -v "$PWD:/src" -v "$PWD/../semgrep-rules:/rules:ro" -w /src \
  -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0='*' \
  "$SEMGREP" semgrep scan --metrics=off $CFG --json-output=reports/semgrep.json .
node .github/scripts/security-gate.mjs --tool semgrep --report reports/semgrep.json

# Dependencies
docker run --rm -v "$PWD:/src" -w /src "$TRIVY" fs --scanners vuln,misconfig --show-suppressed \
  --format json --output reports/trivy.json --exit-code 0 .
node .github/scripts/security-gate.mjs --tool trivy --report reports/trivy.json

# The gate itself
node --test .github/scripts/security-gate.test.mjs
```

On Windows use Git Bash with `export MSYS_NO_PATHCONV=1`, and a fresh clone: a local `site/` makes
Trivy walk far more than CI does. To render the PR comment locally, add
`--json reports/<tool>.result.json` to each gate line, then run
`node .github/scripts/security-gate.mjs --markdown --results reports/gitleaks.result.json --results reports/semgrep.result.json --results reports/trivy.result.json`.

### Adding, excluding, dismissing

- **Semgrep rules:** `.github/security/semgrep-rules.txt` lists rule files from `semgrep/semgrep-rules`
  at `SEMGREP_RULES_REF`. It keeps only rules not tagged `subcategory: audit`, because audit rules flag
  every use of a sink for manual review. A pinned commit gives the same result next year; the price
  is bumping the ref by hand.
- **Paths:** a `.semgrepignore` for Semgrep, `--skip-dirs` in the `trivy fs` step for Trivy, each with
  a comment saying why.
- **False positives: prefer the tool's config over a Security-tab dismissal.** The config is
  versioned and reviewed, and it applies to the gate as well; a dismissal only hides the alert.
  - Gitleaks, one finding: its fingerprint in `.gitleaksignore`. A class of finding: an allowlist in
    `.gitleaks.toml` (see the PEM-header entry there).
  - Semgrep: `# nosemgrep: <rule-id>` on the line, with the reason above. See
    `tools/build_pdf_chrome.py`.
  - Trivy: `CVE-… exp:YYYY-MM-DD` in `.trivyignore`, under a comment with the reason.

  A real secret is never excluded; rotate it first. Use a Security-tab dismissal only to record a
  decision the config cannot express, and write the justification in its comment.

### Testing without touching anything live

The scans read only the checkout. No job contacts the published site or any other host, except to
fetch the pinned images, Trivy's advisory database and the pinned rules. Run them on a branch, a
pull request, with **Run workflow**, or locally with the commands above. The Pages deploy runs only
on `master`.
