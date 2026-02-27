from sys import argv
from debate.debate_controller import DebateController

def main():
    persona = argv[1] if len(argv) == 2 else None
    debate_topics = ["economics", "healthcare", "immigration"]
    if persona == "biden":
        print("Running Biden persona...")
        DebateController("biden", topics=debate_topics).run_debate()
    elif persona == "trump":
        print("Running Trump persona...")
        DebateController("trump", topics=debate_topics).run_debate()
    else:
        print("Usage: python main.py biden   OR   python main.py trump")

if __name__ == "__main__":
    main()