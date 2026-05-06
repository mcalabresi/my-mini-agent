"""Module containing helper functions"""

from pprint import pformat
from typing import Any, Dict, List

import requests


def message_debug(messages: list[dict[str, Any]]) -> str:
    """ "Show nicely the list of messages so far
    :param messages: list[dict[str,Any]] - list of messages
    :return: the messages in a way that can be parsed by rich console"""

    if len(messages) == 0:
        return "the list of messages is empty!"

    output = "This is the list of messages exchanged so far:\n\n"
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

        output += f"| {who_sent_text} "
        content = message.get("content", "").strip()
        if len(content) > 0:
            output += content + "\n"
        if (tool_calls := message.get("tool_calls", [])) and len(tool_calls) > 0:
            for tc in tool_calls:
                fn = tc.get("function", {})
                output += f"[orange1]Calling tool function '{fn.get('name')}' with arguments {truncate_long_args(**fn.get('arguments'))}[/orange1] \n"

    return output


def get_model_context_window(model_name: str) -> int:
    # this will work for LM Studio
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
    # print(f"{data=}")
    context_length = 0
    try:
        all_models = data.get("models", [])
        model_info = [m for m in all_models if m["key"] == model_name][0]
        loaded_instance = model_info.get("loaded_instances")[0]
        cfg = loaded_instance.get("config")
        context_length = cfg.get("context_length")
    except Exception as e:
        context_length = 0
        print("Cannot get total_context_tokens: ", str(e))

    return context_length


def list_format(input_list: List[Dict[str, Any]]) -> str:
    return pformat(input_list, depth=3)


def truncate_long_args(**kwargs: dict[str, str]) -> dict[str, str]:
    trunc_kwargs = {}
    for key, value in kwargs.items():
        t_value = value
        if len(value) > 20:
            t_value = str(value)[:20] + "..."
        trunc_kwargs[key] = t_value
    return trunc_kwargs


def prYellow(s):
    print("\033[93m {}\033[00m".format(s))
