"""A Pygments lexer for BMMScript, registered under the name `bmms` (```bmms fences).

Loaded as an mkdocs hook (mkdocs.yml `hooks:`): importing it adds the lexer to Pygments' table,
so `pymdownx.highlight` colours the 20-odd BMMScript blocks of the docs the way it colours JSON or
shell, in the site and in the PDFs. Nothing here is executed from the docs themselves.

Tokens follow what the reader needs to tell apart: keywords (`task`, `do`, `if`…), the action
after `do` (`mods.scan`), parameter names (`message:`), strings (with `{item.id}` placeholders),
numbers and durations (`30s`, `03:00`), constants, and `#` comments.
"""
import re
import sys

from pygments.lexer import RegexLexer, bygroups, include
from pygments.lexers import LEXERS
from pygments.token import (Comment, Keyword, Name, Number, Operator, Punctuation,
                            String, Text, Whitespace)

__all__ = ["BmmsLexer"]  # Pygments reads this when it imports the module by name

KEYWORDS = (
    "task", "every", "on", "describe", "allow", "do", "if", "else", "for", "in", "list", "set", "shared",
    "clear", "wait", "waitfor", "timeout", "orcontinue", "stop", "run", "spawn", "call", "print", "ensure",
    "try", "catch", "finally", "retry", "times", "repeat", "parallel", "branch", "switch", "case",
    "default", "script", "import", "at", "lan", "while", "until", "return", "break", "continue",
)
OPERATORS_WORDS = ("and", "or", "not")
CONSTANTS = ("true", "false", "online", "always", "never", "info", "warn", "error", "day", "week", "month",
             "mon", "tue", "wed", "thu", "fri", "sat", "sun")


class BmmsLexer(RegexLexer):
    name = "BMMScript"
    aliases = ["bmms", "bmmscript"]
    filenames = ["*.bmms"]

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r"#.*$", Comment.Single),
            (r'"', String.Double, "string"),
            (r"\b(?:" + "|".join(OPERATORS_WORDS) + r")\b", Operator.Word),
            (r"\b(do)(\s+)([A-Za-z_][\w.]*)", bygroups(Keyword, Whitespace, Name.Function)),
            (r"\b(?:" + "|".join(KEYWORDS) + r")\b", Keyword),
            (r"\b(?:" + "|".join(CONSTANTS) + r")\b", Keyword.Constant),
            (r"\b\d{1,2}:\d{2}\b", Number),
            (r"\b\d+(?:\.\d+)?(?:ms|s|m|h|d)?\b", Number),
            (r"([A-Za-z_]\w*)(\s*)(:)(?!:)", bygroups(Name.Attribute, Whitespace, Punctuation)),
            (r"([A-Za-z_][\w.]*)(\()", bygroups(Name.Function, Punctuation)),
            (r"[A-Za-z_][\w.]*", Name.Variable),
            (r"[=<>!+\-*/%^]+", Operator),
            (r"[{}()\[\],]", Punctuation),
            (r".", Text),
        ],
        "string": [
            (r"\{[\w.]+\}", String.Interpol),
            (r'\\.', String.Escape),
            (r'[^"\\{]+', String.Double),
            (r"\{", String.Double),
            (r'"', String.Double, "#pop"),
        ],
    }


# Pygments finds lexers through its LEXERS table (module, name, aliases, filenames, mimetypes);
# the module has to be importable by name, so this file registers itself under `bmms_lexer`.
sys.modules.setdefault("bmms_lexer", sys.modules[__name__])
LEXERS["BmmsLexer"] = ("bmms_lexer", BmmsLexer.name, tuple(BmmsLexer.aliases), tuple(BmmsLexer.filenames), ())


# ── Shell blocks ────────────────────────────────────────────────────────────────────────────
# Pygments' `bash` lexer leaves a command, its flags and its paths all as plain text, which on
# paper reads as black. `bmsh` tells them apart (command / flag / path / string / variable /
# operator / comment). The docs keep writing ```bash (and sh, shell, console, zsh): the hook below
# renames those fences to `bmsh` in memory, just before the page is rendered.
class BmshLexer(RegexLexer):
    name = "BMM shell"
    aliases = ["bmsh"]
    filenames = []

    _common = [
        (r'"(?:\\.|[^"\\])*"', String.Double),
        (r"'[^']*'", String.Single),
        (r"\$\{?[A-Za-z_]\w*\}?|\$\(|\)", Name.Variable),
        (r"(?:^|(?<=\s))--?[A-Za-z][\w-]*(?:=[^\s]*)?", Name.Builtin),
        (r"(?:[A-Za-z]:[\\/]|~[\\/]|\.{1,2}[\\/]|/)[^\s\"'|&;<>]*", Number),
        (r"\b\d+(?:\.\d+)*\b", Number),
        (r"\|\||&&|[|&;<>]+|=", Operator),
        (r"[^\s\"'|&;<>$=]+", Text),
    ]
    tokens = {
        "root": [
            (r"\n", Whitespace),
            (r"[ \t]+", Whitespace),
            (r"#.*$", Comment.Single),
            (r"(?:\$|PS>|>)(?=\s)", Punctuation),
            (r"\b(?:sudo|if|then|else|elif|fi|for|while|do|done|in|case|esac|export|set|cd)\b", Keyword),
            (r"[A-Za-z_][\w.-]*(?=\s|$)", Name.Function, "args"),
            include("common"),
        ],
        "args": [
            (r"\\\n", Whitespace),
            (r"\n", Whitespace, "#pop"),
            (r"[ \t]+", Whitespace),
            (r"(?:(?<=\s)|^)#.*$", Comment.Single),
            (r"(?:&&|\|\||\||;)", Operator, "#pop"),
            include("common"),
        ],
        "common": _common,
    }


LEXERS["BmshLexer"] = ("bmms_lexer", BmshLexer.name, tuple(BmshLexer.aliases), (), ())
__all__.append("BmshLexer")

_SHELL_FENCE = re.compile(r"^([ \t]*)```(?:bash|sh|shell|console|zsh)[ \t]*$", re.MULTILINE)


def on_page_markdown(markdown, **kwargs):  # mkdocs hook
    return _SHELL_FENCE.sub(r"\1```bmsh", markdown)
