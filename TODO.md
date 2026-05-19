# TODO's

- [x] Fix skills
- [ ] Add toolbelt
- [ ] Add RAG
- [ ] Edit is not a real edit, it's a replaceAll
- [ ] Make a real edit , also read getting line numbers
- [ ] A2A study it, make it happen

## Fix skills
The logic should be the following: put into system prompt just the frontmatter of each available skill that we want to provide. Add a tool to get the full text of the skill if needed. It should work as a context function. If the skill is not relevant to the user prompt it should be removed (dynamic skillset). For the current scope we exclude links to other files than SKILL.md. Some clarification. We declare some skills for the agent. We should not dump the totality of those skills in the context as we do now, just put the frontmatters. We should add a tool to add the requested skills in the context. If we put all, we should get all the skills.

## Add toolbelt
As for skills, we should not give a fixed set of tools to our agent but just the ones that are necessary for the task
Let's consider the agent has a toolbelt that can handle a limited number of tools. Each time there is a prompt the agent should reflect on which tools may be needed. Only the relevant tools should be then added into context.

## Add RAG
We can do a lot of nice things if we leverage the api to get the embeddings such as confronting the prompt vector to the vectors of the skill descriptions and tool descriptions. Also for memory RAG would be a boost.
