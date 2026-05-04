"""Module containing helper functions"""

from typing import Any

import requests
from rich.console import Console


def message_debug(console: Console, messages: list[dict[str, Any]]) -> None:
    """ "Show nicely the list of messages so far
    :param console: Console - rich console
    :param messages: list[dict[str,Any]] - list of messages"""
    for message in messages:
        # print(f"{message=}")
        sender = message.get("role", "user")
        who_sent_text = ""
        if sender == "user":
            txt = "User".ljust(10, "-") + ">"
            who_sent_text = f"[green]{txt}[/green]"
        elif sender == "assistant":
            txt = "Agent".ljust(10, "-") + ">"
            who_sent_text = f"[blue]{txt}[/blue]"
        elif sender == "tool":
            txt = "Tool".ljust(10, "-") + ">"
            who_sent_text = f"[orange1]{txt}[/orange1]"

        console.print(f"| {who_sent_text} ", end="")
        content = message.get("content", "").strip()
        if len(content) > 0:
            console.print(content)
        if (tool_calls := message.get("tool_calls", [])) and len(tool_calls) > 0:
            for tc in tool_calls:
                fn = tc.get("function", {})
                console.print(
                    f"Calling tool function '{fn.get('name')}' with arguments {fn.get('arguments')}"
                )


def get_model_context_window() -> int:
    url = "http://localhost:1234/api/v1/models"
    # as usual you need to pass an API Key and you are going to send json data as post
    headers = {
        "Authorization": 'Bearer "NO_API_KEY"',
        "Content-Type": "application/json",
    }
    # here we make our post request, note that we send the whole list of messages, not just the last one
    r = requests.get(
        url,
        headers=headers,
        timeout=300,
    )
    r.raise_for_status()
    # get the data ( parse the json response )
    data = r.json()
    model_info = data.get("models")[0]
    loaded_instance = model_info.get("loaded_instances")[0]
    cfg = loaded_instance.get("config")
    context_length = cfg.get("context_length")
    return context_length
