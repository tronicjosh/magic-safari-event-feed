# Expected answer against actual answer

The last stage of the project (2026-11-23). Joshua's two findings on the demo page: the agent's reply is too long, and the evidence has the same weight as the answer. We first agreed what a great answer is (`expected.md`, option B), then changed the feed until the actual answers matched.

## The lever

A designer's agent has no prompt from us. The feed has two levers: the **server instructions** that each agent receives one time, and the **text that a tool returns**. Both changed.

```text
BEFORE                                           AFTER
instructions: fact rules only                    instructions: fact rules + 8 rules for the answer
  "give each source link"                          answer first, 120 words or less, "3 of 13" first
  "say the counts", "name the holes"               one tag for each item: how sure, and what to do
  "call tell_me_more for what you recommend"       no quote unless the designer asks for proof
        v                                          tell_me_more only on request
agent: 300 to 970 words, 5 to 16 quotes                 v
       2 tool calls for each answer              agent: 108 to 129 words, 0 quotes (2 when asked for proof)
                                                        1 tool call for a list
```

## The tag

The tag says how sure the date is, and so how much work the designer has before a booking.

| Tag | Meaning | Work before a booking |
|---|---|---|
| Confirmed | A page states the date | None |
| Confirmed, programme not stated | A first and a last day only | Check the programme for the guest's days |
| From a weekly rule, confirm near the date | Code wrote the date from a rule on the page | Confirm near the date |
| Season | Months or a rule of the page, no year | None for the season; confirm an operator |
| Not confirmed, no dates yet | Held each year; no dates for this period | Check the organiser later; give no date |

## Rounds

Each round is the same 7 questions to `claude-opus-5-5` with only the four tools (`agent_test.py`).

| Round | Change | Words (Q1 to Q7) | Quotes (Q1 to Q7) | Checks by code | Cost (USD) |
|---|---|---|---|---|---|
| Before | none | 406, 368, 412, 447, 305, 970, 319 | 12, 5, 9, 10, 4, 16, 9 | not this shape | 0.593061 |
| 1 | Answer rules in the server instructions | 162, 157, 196, 193, 189, 186, 142 | 0, 0, 0, 0, 2, 0, 0 | 1 of 7 (length) | 0.351900 |
| 2 | Hard length; exact tag words; "if the feed cannot answer, say so" | 121, 107, 148, 122, 125, 150, 100 | 0, 0, 0, 0, 1, 0, 0 | 7 of 7 | 0.340222 |
| 3 | The feed itself says when a look was before its first collection | 126, 129, 125, 121, 123, 111, 108 | 0, 0, 0, 0, 2, 0, 0 | 7 of 7 | 0.227398 |

Transcripts: `agent_test_before.md`, `agent_test_round1.md`, `agent_test_round2.md`, `agent_test.md` (final).

## Why round 3 changed the feed, not the instructions

In rounds 1 and 2, the answer to "what changed since 1 November?" said that the feed could not tell, and then listed 7 or 8 items. The rule "do not fill the answer with a list" did not stop it. Two rounds with the same fault mean that the approach is wrong: the fault was in the feed. `what_changed` returned all 151 items as "new", because the feed first collected the place on 23 November. Now the feed says that the earlier look was before its first collection, counts those items, and does not list them as new. The answer became correct, and its cost fell from 0.13 to 0.02 US dollars.

## Final answers against expected (read by Claude; Joshua's judgment is the last check)

| # | Expected | Actual | Match |
|---|---|---|---|
| 1 | 5 of 13: FynArts, whales, three Saturday markets; left out; not covered; sources | 6 of 13: FynArts, two whale items, two markets, the Country Market; one line each with a tag; left out; not covered; sources | Yes |
| 2 | 3 of 13 for the couple: FynArts, the wine market, the whales | 3 of 13: FynArts, the wine market, a whale item; general markets and parkruns left out | Yes |
| 3 | 4 of 13 for the family: whales, markets, parkrun, FynArts | 4 of 13: two whale items, the parkrun, the Cricket Club market. FynArts is left out | Shape yes. The selection differs by one item; that is the agent's judgment |
| 4 | June to November; late June adds FynArts; September fairs; the Whale Festival not confirmed | The same four points, each with its tag | Yes |
| 5 | Confirmed; the organiser's quote; yearly since 2013; programme, venue, price not stated | The same, with 2 quotes because the designer asked how sure | Yes |
| 6 | The feed cannot answer yet; it first collected on 23 November; offer what is on | The same, with no list | Yes |
| 7 | Not confirmed, no dates yet; last held 2 to 4 October 2026; give no date; the season covers October | The same | Yes |

Facts: in each round, no link and no stated date came from outside the feed. The selections for the two guests differ in each round.

## Not checked

- One model (`claude-opus-5-5`). A different model or a different agent product can read the instructions differently.
- One run for each round. The answers of a model differ between runs.
- The same 7 questions were used to tune and to test. A new question is the honest test.
