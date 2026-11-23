# Handover from the prototype

This file gives what the prototype made me think about. It gives thoughts and questions, not solutions. Use this file with the photos of my pen-and-paper notes to make `docs/design.md`.

## Thoughts

-A luxury holiday is the main selling point so ensuring what is upselled elevates the overall experience and meets a certain luxury threshold.
- This is a trust problem more than a ranking problem as if an agent sees a datapoint they don't trust all credibility is lost. The area has few events. The hard part is to know that a fact is true.
- A web page is not a reliable witness. Pages contradict themselves, change between years, and can hide text.
- A model alone cannot be the judge. Its answer needs evidence that code or a person can check.
- Time has a shape and a certainty. A date, a run of dates, a season and a projected date are different things.
- Access rules limit what the feed can know. The feed will have holes, and it must say where they are.
- A list that grows with each new case does not converge. That is the sign to change the approach.
- A false fact on a client's trip costs more than a missed event.

## Key open questions

These are the few questions that would change the design.

For Magic Safari:

- Is "zero false facts, some events held for a person" the correct trade for a travel agent?
- Do events that cannot be booked (a market, a whale season) help to sell a trip?

For the design:

- How does the system know what a visitor sees on a page?
- What does the feed do with a source that blocks robots, fully or in part?
- When two sites list the same event, which one can change its status, price or date?
- How is a model error found when code cannot see it?
- The model's output varies between runs. How does a run become live data?

## What the prototype tested

Each line is a question that the prototype tested. The design must have an answer for each one.

Sources and access

- Which sources exist for Hermanus, and how much can each one be trusted?
- What does each source's `robots.txt` permit?
- Do pages carry structured event data, or only free text?
- Do the sources publish PDFs, and can their text be read?

Reading a page

- Can fixed word lists interpret the wording of a page?
- Is a model's verdict alone enough?
- Do two models that must agree give a better result, and at what cost?
- Can a model's answer be verified against the page text?
- Can a page hide text from a person but show it to a parser?
- Is it safe to send only part of a page to the model to cut cost?
- Does the same page give the same extraction on each run?

Dates and time

- Which date formats do real pages use?
- Do last year's dates predict next year's dates?
- How are a single date, a run of dates, a recurring event and a season different?

Trust and safety

- Can text on a page give instructions to an AI?
- Which fields on a card can carry text that no rule can verify?
- What can an agent do if it has web content, private data and an action tool together?
- Which values need a shape check before they are shown: price, phone number, link, venue?
- Who is permitted to write facts, and through which path?

Relevance

- How many events are there, and how many are in the area?
- Is heavy ranking or a preference model necessary?
- Is location or drive-time data necessary for a first version?

Data and state

- Must judgments be stored, or can rules compute them on read?
- Can an unchanged page be skipped?
- Can a full run replace live data without a review?
- How is the history of a change kept?

Interfaces

- What does an agent need from the API to brief a trip?
- Does an agent need a route to submit facts?
- Is a demo UI, a cache, a rate limit or a webhook necessary for a first version?

Cost and scale

- What does one full run cost, measured?
- What grows when the number of sources or places grows?

Checking

- How is "correct" measured: which labelled pages, and who wrote the labels?
- How good are the tests: does a test fail when the code is broken on purpose?
- How is the effect of a later change measured?
- Does the luxury bar eliminate good trips?
