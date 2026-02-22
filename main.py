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

def main():
    persona = argv[1] if len(argv) > 1 else None
    if persona == "biden":
        print("Running Biden persona...")
        # Code to run Biden persona goes here
    elif persona == "trump":
        print("Running Trump persona...")
        # Code to run Trump persona goes here
    else:
        print("Please specify a valid persona (biden or trump).")
    

if __name__ == "__main__":
    main()