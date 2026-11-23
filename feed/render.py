"""Render: the text that a visitor sees. Hidden text must not pass."""

import io
import re

from bs4 import BeautifulSoup, Comment, Tag
from pypdf import PdfReader

_NOT_VISIBLE_TAGS = [
    *("script", "style", "noscript", "template", "head", "title", "meta", "svg"),
    *("textarea", "iframe"),
]
# Tags that do not start a new line. Text inside one continues the text around it, so a word
# or a price with a tag in it stays in one piece ("<b>R</b>75" is "R75").
_INLINE_TAGS = [
    *("a", "abbr", "b", "bdi", "bdo", "cite", "code", "data", "del", "dfn", "em", "font", "i"),
    *("ins", "kbd", "mark", "q", "s", "samp", "small", "span", "strong", "sub", "sup", "time"),
    *("u", "var"),
]
_KEEP_APART = ("sub", "sup")  # a footnote mark must not become a digit of a price: "R75 1"
_HIDDEN_STYLE = re.compile(
    r"display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0(px|pt|em|rem|%)?\s*(;|$)"
    r"|opacity\s*:\s*0(\.0+)?\s*(;|$)",
    re.IGNORECASE,
)


def html_to_text(html: str) -> str:
    """Visible text of an HTML document, one line for each block of text."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(_NOT_VISIBLE_TAGS):
        tag.decompose()
    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()
    for tag in soup.find_all(True):
        if tag.decomposed:
            continue
        hidden = (
            tag.has_attr("hidden")
            or tag.get("aria-hidden") == "true"
            or (tag.name == "input" and tag.get("type") == "hidden")
            or _HIDDEN_STYLE.search(tag.get("style") or "")
        )
        if hidden:
            tag.decompose()
    # Two inline tags with nothing between them get a space, not a join: a stylesheet often
    # shows them as separate cells, and "12" next to "5 June" must not read as "125 June".
    inline = soup.find_all(_INLINE_TAGS)
    for tag in inline:
        before = tag.previous_sibling
        if tag.name in _KEEP_APART:
            tag.insert_before(" ")
            tag.insert_after(" ")
        elif isinstance(before, Tag) and before.name in _INLINE_TAGS:
            tag.insert_before(" ")
    for tag in inline:
        tag.unwrap()
    soup.smooth()
    # One line for each run of text between block tags. A line break of the HTML source
    # inside a run is white space, not a new line.
    lines = (" ".join(string.split()) for string in soup.strings)
    return "\n".join(line for line in lines if line)


def pdf_to_text(data: bytes) -> str:
    """Text of a PDF, page by page."""
    reader = PdfReader(io.BytesIO(data))
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        lines = (" ".join(line.split()) for line in (page.extract_text() or "").splitlines())
        pages.append(f"[page {number}]\n" + "\n".join(line for line in lines if line))
    return "\n".join(pages)
