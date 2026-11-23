"""Render: the text that a visitor sees. Hidden text must not pass."""

import io
import re

from bs4 import BeautifulSoup, Comment
from pypdf import PdfReader

_NOT_VISIBLE_TAGS = ["script", "style", "noscript", "template", "head", "title", "meta", "svg"]
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
    lines = (" ".join(line.split()) for line in soup.get_text("\n").splitlines())
    return "\n".join(line for line in lines if line)


def pdf_to_text(data: bytes) -> str:
    """Text of a PDF, page by page."""
    reader = PdfReader(io.BytesIO(data))
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        lines = (" ".join(line.split()) for line in (page.extract_text() or "").splitlines())
        pages.append(f"[page {number}]\n" + "\n".join(line for line in lines if line))
    return "\n".join(pages)
