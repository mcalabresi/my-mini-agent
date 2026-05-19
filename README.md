---
author: Marcello Calabresi
---

# My Mini Agent

A small AI agent to experiment with agents

# what is it?
It's an Agent ! It can run on local or remote models. It has:
*  **NEW!** MCP client! 
* dynamic context definition
* tools
* skills
* slash-commands to debug your agent, run terminal commands, mess up with its memory, etc
* you can easily define an agent and load it
* also the code is fully commented so you can learn how an agent works!

# prerequisites
* Python 3 installed
* You need to have uv installed -> https://docs.astral.sh/uv/getting-started/installation/
* If you want to use local agents you need to download a launcher / server for your LLMs such as LM Studio or Ollama
* You also need to download a model to run. My preference so far goes to qwen/qwen3.5-9b
* You need to load a model and start the server so that the agent can reach it

## Note about remote LLMs
If you want to go with a remote LLM you can do so by configuring correctly the .env file ( I test a lot with Mistral who has a free plan ) You can connect to any LLM using OpenAI api standard

# how to install
* Clone this repo
> cd my-mini-agent
* run the following command in your terminal 
>  uv sync
* create a .env file at the root of the project
and populate it with the following keys
```yaml
# QWEN - local
MODEL_NAME=qwen/qwen3.5-9b
MODEL_API_KEY=NO_API_KEY
MODEL_API_BASE_URL=http://127.0.0.1:1234/v1

# MCP API KEYS
IMAGEMCP_API_KEY=<your api key goes here>
PIXSERP_API_KEY=<your api key goes here>

```
Of course you can change these info to target other models / local or remote
So far I tried with Mistral with very good result ( and free ).
* create a folder at the root level named "agent-space" which is at the moment an obsidian vault where the agent writes what he wants (This agent is sandboxed by design. Its tools specifically target only this folder agent-space)

# launching your chat with an agent
choose an example (files ending with _example.py or main.py)
> uv run simple_agent_example.py

Remember these files are meant mostly to be read than to be used
There are many more agents out there who are way more polished than this

once you are tired of speaking with the agent just send "bye" or "quit" or "ciao"

# other examples
## load agent
file load_agent_example loads an agent from a catalog ( my_mini_agent/agents_catalog.py )  this is also what I keep on main.
In this specific example I load an agent who doesn't like to speak much, I called him "Bong" and he is some kind of caveman agent. I like agents when they are not very verbose. In this case he is "reticent" (a word that deserves a prize).

```json
 {
        "name": "Bong",
        "description": """
        Bong is no-nonsense assistant. He provides brief answers and is quick.
        He may not be the best choice to discuss directly to humans as his manners may be considered rude but he may be the best pick
        when you need a quick and concise answer.
        """,
        "system_prompt": "You are a reticent assistant, you answer clearly and briefly with simple words",
        "context": ["current_date_time", "user_context"],
        "skills": [],
        "tools": ["read_note"],
    },
```


## workflow
file story_writing_critique_example.py is a workflow involving two agents. One writes stories and a second one makes the critique. The response of the critic agent is passed to the writer agent to make a final draft of the story

## MCP
file mcp_client_example shows how to attach two different MCP servers and adding the tools to the agent.
The definition of the MCP servers is in my_mini_agent/mcp_catalog.py. You can add some more if you want.
!IMPORTANT : In the code you can see there is a convention: the API_KEY will be in the format
UPPERCASE_MCP_SERVER_NAME_API_KEY and normally you should put this in the .env file

```json
 "pixserp": {
        "command": "npx",
        "args": [
            "-y",
            "mcp-remote",
            "https://pixserp.com/api/v1/mcp",
            "--header",
            "Authorization: Bearer ${PIXSERP_API_KEY}",
        ],
        "env": {"PIXSERP_API_KEY": "PUT_YOUR_API_KEY_IN_DOT_ENV_FILE"},
```
In practice we will get the api key from .env file and recreate the env property with the real api key.

# How to personalize this agent:
* You can create different agent profiles in agents_catalog.py and load them. Each agent will have a name and a description and a list of context functions, skills, (local) tools
* You can add skills in the standard format ( folder skills, each skill has a subdirectory and inside a file named SKILL.md)
* You can add context functions in context_catalog.py ( you can change your name for example )
* You can add local tools in tool_catalog.py. The important thing is that you write the annotations and the docfile as in the examples. This information will be necessary to create the tool schema to pass to the LLM.
* You can add mcp servers in mcp_catalog. Remember you need also to add mcp tools to your agent ( see mcp_client_example.py)

# How much help did I get from other agents to do this agent? 
Not a lot really. I asked chatGPT some help for doing some tools and skills but the rest comes from 'old-school' coding, following tutorials, reading articles, etc. The important is not the destination but the journey and clearly this is a project to learn the capabilities of Agentic AI.

# Acknowledgments

The starting point of this project comes from the tutorial by youtube channel indently => 

https://www.youtube.com/playlist?list=PL4KX3oEgJcfcPez5tpvsdC1ghaNFo1Bhc

github repo: https://github.com/indently/ai_agent_python

The original code he used was written by 
Miss Cthulian Coder, Insanity by Design. Blog: https://AlyceOsbourne.github.io

part of it is still present here, so thanks Miss Cthulian Coder e grazie Federico!

## what is new so far

* added logo (MyMiniAgent)
* added comments everywhere to explain better what is happening
* the responses of the agent are parsed as Markdown for better legibility
* added skills system
* added token counter for keeping an eye on the context window
* context catalog, tool catalog and agents catalog
* added .env to keep your secrets secret
* added MCP client (multiple mcp clients supported)
