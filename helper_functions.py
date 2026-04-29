"""Module containing helper functions"""

from typing import Any

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
