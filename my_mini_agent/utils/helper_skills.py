import asyncio
from pathlib import Path

import aiofiles


async def read_frontmatter(file_path):
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()
            start = content.find("---")
            end = content.find("---", start + 3)
            if start != -1 and end != -1:
                return content[start + 3 : end].strip()
            return None
    except Exception:
        return None


async def gather_skill_frontmatter(skills_dir, allowed_skills: list[str]):
    """Gather the skill frontmatters in the allowed skills list.
    If allowed_skills contains an unique element named "all", gather all available skills

    :param skills_dir: StrPath - path to skills directory
    :param allowed_skills: list[str] - list of allowed skills
    """
    skills_dir = Path(skills_dir)
    tasks = []
    searchable_dirs = []
    if len(allowed_skills) == 0:
        return []
    elif len(allowed_skills) == 1 and allowed_skills[0].lower() == "all":
        searchable_dirs = [
            skill_folder
            for skill_folder in skills_dir.iterdir()
            if skill_folder.is_dir()
        ]
    else:
        searchable_dirs = [
            skill_folder
            for skill_folder in skills_dir.iterdir()
            if (skill_folder.is_dir() and skill_folder.name in allowed_skills)
        ]

    for dir in searchable_dirs:
        skill_file = dir / "SKILL.md"
        if skill_file.exists():
            tasks.append(read_frontmatter(skill_file))

    results = await asyncio.gather(*tasks)
    return [result for result in results if result is not None]


# Usage
async def extract_skills_frontmatters(
    skills_dir: str, allowed_skills: list[str]
) -> str:
    """extract all skills frontmatters

    :param skills_dir: str - The name of the folder containing the skills
    :param allowed_skills: list[str] - The list of skills the agent is allowed to load in context

    """
    frontmatters = await gather_skill_frontmatter(skills_dir, allowed_skills)
    output = ""
    if len(frontmatters) > 0:
        for fm in frontmatters:
            output += fm + "\n"
    if __name__ == "__main__":
        print(output)
    return output


if __name__ == "__main__":
    asyncio.run(
        extract_skills_frontmatters(
            r"C:\Users\marce\CODE\my-mini-agent\skills",
            ["obsidian-markdown-lite"],
        )
    )
