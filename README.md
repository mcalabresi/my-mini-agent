# My Mini Agent

A small AI agent working on local LLM via LM Studio

# Acknowledgments

The starting point of this project comes from the tutorial by youtube channel indently => 

https://www.youtube.com/playlist?list=PL4KX3oEgJcfcPez5tpvsdC1ghaNFo1Bhc

github repo: https://github.com/indently/ai_agent_python

The code he used was written by 
Miss Cthulian Coder, Insanity by Design. Blog: https://AlyceOsbourne.github.io

Prerequisites:
having python 3 and uv installed

Having a local LLM server running ( in the tutorial we use ML Studio with model Qwen 3.5-9b ) or eventually an API Key for OpenAI / Anthropic etc

## what is new so far

* added logo (MyMiniAgent)
* added comments everywhere to explain better what is happening
* the responses of the agent are parsed as Markdown for better legibility
* added skills system
* added token counter for keeping an eye on the context window
* context catalog, tool catalog and agents catalog



## starting the agent
python main.py

## exiting 
put "quit" or "bye" or "exit" as prompt
