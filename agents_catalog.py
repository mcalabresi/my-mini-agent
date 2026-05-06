from typing import Any

available_agents: list[dict[str, Any]] = [
    {
        "name": "Bong",
        "system_prompt": "You are a reticent assistant, you answer clearly and briefly with simple words",
        "context": ["current_date_time", "user_context"],
        "skills": [],
        "tools": [],
    },
    {
        "name": "Clive",
        "system_prompt": "You are a writer of funny stories for children, you put humour and creativity",
        "context": ["current_date_time", "user_context"],
        "skills": ["long-term-memory", "obsidian-markdown-lite"],
        "tools": [
            "write_note",
            "read_note",
            "list_notes",
            "add_link_to_index",
            "edit_note",
        ],
    },
]
