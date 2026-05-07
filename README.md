---
author: Marcello Calabresi
---

# My Mini Agent

A small AI agent to experiment with agents

# what is it?
It's an Agent ! It can run on local or remote models. It has:
* dynamic context definition
* tools
* skills
* slash-commands to debug your agent, run terminal commands, mess up with its memory, etc
* you can easily define an agent and load it
* also the code is fully commented so you can learn how an agent works!

# prerequisites
* Python 3 installed
* You need to have uv installed -> https://docs.astral.sh/uv/getting-started/installation/
* If you want to use local agents you need to download a launcher / server for your LLMs
* such as LM Studio or Ollama
* You also need to download a model to run. My preference so far goes to qwen/qwen3.5-9b
* You need to load a model and start the server so that the agent can reach it

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
API_KEY=NO_API_KEY
API_BASE_URL=http://127.0.0.1:1234/v1
```
Of course you can change these info to target other models /  local or remote
So far I tried with Mistral
* create a folder named "agent-space" which is a sandbox for the agents (at least with the actual tools)

# launching your chat with an agent
choose an example (files ending with _example.py)
> uv run simple_agent_example.py

Remember these files are meant mostly to be read than to be used
There are many more agents out there who are way more polished than this

once you are tired of speaking with the agent just send "bye" or "quit" or "ciao"

# Acknowledgments

The starting point of this project comes from the tutorial by youtube channel indently => 

https://www.youtube.com/playlist?list=PL4KX3oEgJcfcPez5tpvsdC1ghaNFo1Bhc

github repo: https://github.com/indently/ai_agent_python

The original code he used was written by 
Miss Cthulian Coder, Insanity by Design. Blog: https://AlyceOsbourne.github.io

part of it is still present here, so thanks Miss Cthulian Coder!

## what is new so far

* added logo (MyMiniAgent)
* added comments everywhere to explain better what is happening
* the responses of the agent are parsed as Markdown for better legibility
* added skills system
* added token counter for keeping an eye on the context window
* context catalog, tool catalog and agents catalog
* added .env to keep your secrets secret
