'''*************************************************************************
These personas are defined in the agents folder. You can modify the persona files to change the behavior of the personas.
*************************************************************************'''
import time
import openai
from speech import speech_to_text_microsoft as stt
from speech import text_to_speech_microsoft as tts
from agents.personas import PERSONAS
from sys import argv
from debate.debate_controller import DebateController

import keys

# Set to False to type instead of speak (fallback for demo)
USE_SPEECH = True

openai.api_type    = "azure"
openai.api_key     = keys.azure_openai_key
openai.api_base    = keys.azure_openai_endpoint
openai.api_version = keys.azure_openai_api_version

def main():
    persona = argv[2] if len(argv) == 3 else None
    debate_topics = ["economics", "healthcare", "immigration"]
    if persona == "biden":
        print("Running Biden persona...")
        # Code to run Biden persona goes here
        DebateController("biden", topics = debate_topics).run_debate()
        #note: the debate controller will only control timing from biden's laptop
    elif persona == "trump":
        print("Running Trump persona...")
        # Code to run Trump persona goes here
        DebateController("trump", topics = debate_topics).run_debate()
    else:
        print("Please specify a valid persona (biden or trump).")


def get_response(persona_key, conversation_history):
    persona = PERSONAS[persona_key]
    messages = [{"role": "system", "content": persona["system_prompt"]}] + conversation_history
    response = openai.ChatCompletion.create(
        engine=keys.azure_openai_deployment,
        messages=messages)
    return response.choices[0].message.content

def say(text):
    print(text)
    tts.say(text)
    while (not stt.listen) or len(tts.things_to_say) > 0:
        time.sleep(0.1)

if __name__ == "__main__":
    main()
    
    if USE_SPEECH:
        stt.start()
    tts.start()

    conversation_history = []
    opening = "The topic is the economy. Biden, you go first."
    say("Moderator: " + opening)
    conversation_history.append({"role": "user", "content": opening})

    for round_number in range(5):
        biden_response = get_response("biden", conversation_history)
        say("Biden: " + biden_response)
        conversation_history.append({"role": "assistant", "content": biden_response})
        conversation_history.append({"role": "user", "content": biden_response})

        trump_response = get_response("trump", conversation_history)
        say("Trump: " + trump_response)
        conversation_history.append({"role": "assistant", "content": trump_response})
        conversation_history.append({"role": "user", "content": trump_response})

    tts.stop()
    if USE_SPEECH:
        stt.stop()
