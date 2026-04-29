import os

# import getpass
from datetime import datetime
from pathlib import Path


def current_date_time() -> str:
    return f"Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"


# def user_context() -> str:
#     return f"Current user: {getpass.getuser()}\n"


def user_context() -> str:
    return "Current user: Marcello"


def my_files() -> str:
    cwd = os.getcwd()
    if cwd != "agent-space":
        # Change to agent-space directory
        try:
            os.chdir("agent-space")
        except FileNotFoundError:
            raise RuntimeError(
                "Directory 'agent-space' does not exist. Please create it first "
                "or run from the correct location."
            )

    # Construct full filename with .md extension
    file_path = Path.cwd() / "index.md"

    try:
        # Write the content to the file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {str(e)}")
    finally:
        # Always return to the original working directory
        os.chdir(cwd)


def obsidian_writer_skill() -> str:
    return """
    ---
    name: obsidian-markdown-lite
    description: Create and edit Obsidian Flavored Markdown with wikilinks. Use when working with .md files in Obsidian.
    ---

    # Obsidian Flavored Markdown Skill

    Create and edit valid Obsidian Flavored Markdown. Obsidian extends CommonMark and GFM with wikilinks, embeds, callouts, properties, comments, and other syntax. This skill covers only Obsidian-specific extensions -- standard Markdown (headings, bold, italic, lists, quotes, code blocks, tables) is assumed knowledge.

    ## Workflow: Creating an Obsidian Note

    1. **Write content** using standard Markdown for structure, plus Obsidian-specific syntax below.
    2. **Link related notes** using wikilinks (`[[Note]]`) for internal vault connections, or standard Markdown links for external URLs.

    ## Internal Links (Wikilinks)

    ```markdown
    [[Note Name]]                          Link to note
    [[Note Name|Display Text]]             Custom display text
    [[Note Name#Heading]]                  Link to heading
    [[Note Name#^block-id]]                Link to block
    [[#Heading in same note]]              Same-note heading link
    ```

    ## Diagrams
    If asked to create diagrams use mermaid format
    e.g a simple flowchart:

    ```mermaid
    flowchart TD
        A[Start] --> B{Condition}
        B -->|Yes| C[Execute]
        B -->|No| D[End]
        C --> D
    ```

    ## Workflow when writing a new note
    After writing a new note you need to modify note "index" and put a wikilink to the newly created note with a brief description

    """
