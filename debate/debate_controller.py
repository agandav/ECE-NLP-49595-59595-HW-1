import time
from agents import TrumpAgent, BidenAgent
class DebateController():
    '''
    This class manages the debate process and manages logistics and topics.

    1. Turn management: Keeps track of which debater is speaking and when to switch turns.
    2. Topic management: Introduces new topics or questions for each round of the debate.
    3. Time management: Enforces time limits for each debater's response.
    4. Debate flow control: Orchestrates the overall flow of the debate, ensuring that it proceeds in an organized manner.
    5. Moderation: Optionally, the controller could also include a moderation function to ensure that debaters adhere to debate rules and guidelines.
    
    Debate Format:
    1. Opening Statements (2 minutes)
        a. Trump
        b. Biden
    2. Policy Rounds (3 rounds, 4 minutes each = 12 min)
        a. Round 1: Economy
            - Moderator (30 sec)
            - Trump's Response (1 min)
            - Biden's Response (1 min)
            - Trump Rebuttal (45sec)
            - Biden Rebuttal (45 sec)
        b. Round 2: Healthcare
        c. Round 3: Foreign Policy
    3. Crossfire (4 min)
        - Both debaters can speak freely, but must respond to each other's points. No new topics allowed.
        - Question (30 sec)
        - Answer (1 min each)
    4. Closing Statements (2 minutes)
        a. Biden
        b. Trump

    Total: 20 minutes
    '''
    def __init__(self, debater, topics=None):
        self.debater = debater #trump or biden
        self.topics = topics
        self.turn_flag = 0  # 0 for Trump, 1 for Biden
        self.debate_state = {
            "round": 0,
            "topic": None,
        }
    
    def switch_turn(self):
        self.turn_flag = 1 - self.turn_flag
    
    def get_current_debater(self):
        return self.debaters[self.turn_flag]
    
    def run_debate(self):
        # Implement the debate flow based on the defined format
        trump = TrumpAgent()
        biden = BidenAgent()
        #start debate
        print("Starting debate...")

        #Opening statements
        print("Opening Statements:")
        for debater in self.debaters:
            print(f"{debater['name']} is speaking...")
            if debater['name'] == "Trump":
                trump.speak()
            elif debater['name'] == "Biden":
                biden.speak()
            time.sleep(2)  # Simulate time taken for opening statement
        
    

