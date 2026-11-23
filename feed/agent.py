"""A demo agent: a normal Claude with only the tools and the server instructions of the feed.

It stands in for a travel designer's agent, so that the feed can be tested from a web page.
It has the same tools, the same tool descriptions and the same instructions as the MCP server,
and nothing else. Each answer costs money: the usage and the cost are measured and returned.
"""

import json
import os
from datetime import date
from pathlib import Path

from feed import mcp_server

# US dollars for each 1 million tokens (input, output). Source: the claude-api skill table,
# cached 2026-11-03. Haiku: prompts up to 100K tokens.
PRICE = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}
MAX_ROUNDS = 8  # tool rounds in one answer


def _tool(function, properties: dict, required: list[str]) -> dict:
    return {
        "name": function.__name__,
        "description": " ".join(function.__doc__.split()),  # the description of the MCP tool
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
    }


_TEXT, _MONTH = {"type": "string"}, {"type": "integer", "minimum": 1, "maximum": 12}
TOOLS = [
    _tool(
        mcp_server.what_is_on,
        {"place": _TEXT, "from_date": _TEXT, "to_date": _TEXT},
        ["place", "from_date", "to_date"],
    ),
    _tool(
        mcp_server.when_to_go, {"place": _TEXT, "from_month": _MONTH, "to_month": _MONTH}, ["place"]
    ),
    _tool(mcp_server.what_changed, {"place": _TEXT, "since": _TEXT}, ["place", "since"]),
    _tool(mcp_server.find, {"place": _TEXT, "text": _TEXT}, ["place", "text"]),
    _tool(
        mcp_server.tell_me_more,
        {"ids": {"type": "array", "items": {"type": "integer"}}},
        ["ids"],
    ),
]


def run_tool(name: str, arguments: dict) -> str:
    """The text of one tool call.

    It calls the function of the MCP server itself. So the demo agent and a Claude that is
    connected to the server get the same text for the same call.
    """
    if name not in {tool["name"] for tool in TOOLS}:
        return f"error: unknown tool {name}"
    try:
        return getattr(mcp_server, name)(**arguments)
    except TypeError as error:  # a missing or an unknown input
        return f"error: bad input for {name}: {error}"


def system_prompt() -> str:
    path = Path(os.environ.get("FEED_REGISTRY", "registry.json"))
    places = json.loads(path.read_text(encoding="utf-8"))["places"]
    known = ", ".join(place["name"] for place in places.values())
    return (
        mcp_server.INSTRUCTIONS
        + f"\nThe feed has these places: {known}.\nThe date of today is {date.today().isoformat()}.\n"
    )


def _cost(model: str, usage) -> float:
    price_in, price_out = PRICE[model]
    read_tokens = getattr(usage, "cache_read_input_tokens", 0) or 0
    write_tokens = getattr(usage, "cache_creation_input_tokens", 0) or 0
    tokens_in = usage.input_tokens + 0.1 * read_tokens + 1.25 * write_tokens
    return (tokens_in * price_in + usage.output_tokens * price_out) / 1_000_000


def answer(client, model: str, messages: list) -> dict:
    """One answer of the agent. `messages` is the history; the new turns are appended to it.

    Returns the text, the tool calls that the agent made, and the measured tokens and cost.
    """
    calls, cost, tokens_in, tokens_out = [], 0.0, 0, 0
    request = {
        "model": model,
        "max_tokens": 16000,
        "system": system_prompt(),
        "tools": TOOLS,
        "cache_control": {"type": "ephemeral"},  # the history repeats in each round of the loop
    }
    for _ in range(MAX_ROUNDS):
        if model == "claude-haiku-5-5":  # no server-side fallback on this model
            response = client.messages.create(messages=messages, **request)
        else:  # if a safety classifier declines, the API runs the request on a fallback model
            response = client.beta.messages.create(
                messages=messages,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                **request,
            )
        cost += _cost(model, response.usage)
        cached = (getattr(response.usage, "cache_read_input_tokens", 0) or 0) + (
            getattr(response.usage, "cache_creation_input_tokens", 0) or 0
        )
        tokens_in += response.usage.input_tokens + cached
        tokens_out += response.usage.output_tokens
        # The whole content goes back: thinking blocks and tool calls must stay as they are.
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason == "pause_turn":
            continue
        if response.stop_reason != "tool_use":
            break
        results = []
        for block in response.content:
            if block.type == "tool_use":
                calls.append({"name": block.name, "input": block.input})
                text = run_tool(block.name, block.input)
                result = {"type": "tool_result", "tool_use_id": block.id, "content": text}
                if text.startswith("error:"):
                    result["is_error"] = True
                results.append(result)
        messages.append({"role": "user", "content": results})  # all results in one message

    text = "\n".join(block.text for block in response.content if block.type == "text").strip()
    if response.stop_reason == "refusal":
        text = text or "The model declined to answer this question."
    elif response.stop_reason == "tool_use":
        text = text or f"The agent stopped after {MAX_ROUNDS} rounds of tool calls."
    elif response.stop_reason == "max_tokens":
        text += "\n\n(The answer was cut: it reached the token limit.)"
    return {
        "text": text,
        "calls": calls,
        "model": response.model,
        "input_tokens": tokens_in,
        "output_tokens": tokens_out,
        "cost_usd": round(cost, 6),
    }
