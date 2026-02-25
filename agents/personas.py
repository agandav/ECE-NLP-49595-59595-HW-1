'''*************************************************************************
personas.py
This file defines the personas for the presidential debate. Each persona has a name and a system prompt that guides the behavior of the persona during the debate.
*************************************************************************'''

PERSONAS = {
    "biden": {
        "name": "Biden",
        "prompt_path": "agents/prompts/biden_system.txt",
    },

    "trump": {
        "name": "Trump",
        "prompt_path": "agents/prompts/trump_system.txt",
    }
}