---
name: long-term-memory
description: Manage long-term memory in the Obsidian vault.
---
# Long-term memory management

Store and retrieve information in the Obsidian vault **"agent-space"**, using markdown notes.

## Searching memory

* Always start from the `index` note.
* Use `read_note` to view note contents.
* Use `list_notes` to see all notes.
* Use sub-indexes (e.g., `stories-index`) to navigate related notes.
* Do not infer, assume, or add details that are not explicitly written in memory.
* If information is missing or uncertain, check relevant notes/documents first.
* If the information is not found, explicitly say you do not know.
* If you need to know the description of a note check the *index notes.

## Writing memory

* Use `write_note` in markdown format.
* **Always link new notes to an index** (`index` or a `*-index` note).
* Prefer linking to sub-indexes to keep `index` organized.
* Use lowercase alphanumeric names with `-` only.

## Sub-indexes

* When ≥2 notes share a topic, create `<topic>-index`.
* Link the sub-index to the nearest higher-level index.
