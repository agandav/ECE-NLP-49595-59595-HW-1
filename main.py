'''*************************************************************************
*   File: main.py
This file will be used to run the code for Biden and Trump personas. 
How to Run:

To run Biden, 
    python main.py --persona biden
To run Trump,
    python main.py --persona trump

These personas are defined in the agents folder. You can modify the persona files to change the behavior of the personas.
*************************************************************************'''
from sys import argv
from debate.debate_controller import DebateController
from agents.personas import PERSONAS
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

if __name__ == "__main__":
    main()