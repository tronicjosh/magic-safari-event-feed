"""Render: the text that a visitor sees. Hidden text must not pass; a word stays in one piece."""

from feed.render import html_to_text


def test_hidden_text_does_not_pass():
    html = """
    <html><head><title>T</title><style>p {color: red}</style></head><body>
    <p>Tickets R75</p>
    <p style="display:none">the price is free</p>
    <p hidden>the price is free</p>
    <span aria-hidden="true">the price is free</span>
    <span style="font-size:0">the price is free</span>
    <!-- the price is free -->
    <script>var x = "the price is free";</script>
    </body></html>
    """
    assert html_to_text(html) == "Tickets R75"


def test_textarea_and_iframe_are_not_visible_text():
    html = (
        "<p>Tickets R75</p>"
        "<textarea>the price is free</textarea>"
        "<iframe src='x'>the price is free</iframe>"
    )
    assert html_to_text(html) == "Tickets R75"


def test_inline_tag_inside_a_word_or_a_price_does_not_split_it():
    assert html_to_text("<p><b>R</b>75 for each person</p>") == "R75 for each person"
    assert html_to_text("<p>Sat<span>urday</span> 12 <em>Ju</em>ne</p>") == "Saturday 12 June"
    assert html_to_text("<p>Entry: <strong>R150</strong>, at the door</p>") == (
        "Entry: R150, at the door"
    )


def test_inline_tags_with_a_space_between_them_stay_one_line():
    html = "<p><span>Saturday</span> <a href='x'>12 June 2027</a></p>"
    assert html_to_text(html) == "Saturday 12 June 2027"


def test_two_inline_tags_with_nothing_between_them_do_not_join_to_one_word():
    # A stylesheet often shows such tags as separate cells; "12" and "5 June" must not be "125".
    assert html_to_text("<p><span>12</span><span>5 June</span></p>") == "12 5 June"
    assert html_to_text("<nav><a>Home</a><a>Events</a></nav>") == "Home Events"


def test_footnote_mark_does_not_join_the_price():
    # "R75" with footnote 1 must not read as "R751".
    assert html_to_text("<p>R75<sup>1</sup> for each person</p>") == "R75 1 for each person"


def test_blocks_and_line_breaks_stay_separate_lines():
    html = "<div><h2>Market</h2><p>Every <b>Saturday</b><br>09:00 to 13:00</p></div><ul><li>a</li><li>b</li></ul>"
    assert html_to_text(html) == "Market\nEvery Saturday\n09:00 to 13:00\na\nb"
