import time
from agents import TrumpAgent, BidenAgent
from speech import speak_input, speak_output
class DebateController():
    '''
    This class manages the debate process for ONE agent on ONE laptop.
    Each laptop runs its own DebateController instance.

    Speech-Based Design (Two Laptops):
    - Laptop 1 runs DebateController("trump") with TrumpAgent
    - Laptop 2 runs DebateController("biden") with BidenAgent
    - Each controller listens via STT for moderator cues (e.g., "Trump, your turn")
    - When the controller hears its agent's name, it triggers the agent to speak
    - When it hears "time is up" or opponent's name, it stops speaking
    - No network needed—all synchronization happens through speech
    
    Moderator Keywords:
    - "Trump" or "Trump, your turn" → Trump laptop starts speaking
    - "Biden" or "Biden, your turn" → Biden laptop starts speaking  
    - "time is up" or "next speaker" → current speaker stops
    
    Debate Format:
    1. Opening Statements (1 minute total)
        a. Trump (30 sec)
        b. Biden (30 sec)
    2. Policy Rounds (2 rounds, 3 minutes each = 6 min)
        a. Round 1: Economy
            - Moderator (30 sec)
            - Trump's Response (45 sec)
            - Biden's Response (45 sec)
            - Trump Rebuttal (30 sec)
            - Biden Rebuttal (30 sec)
        b. Round 2: Healthcare
        c. Round 3: Foreign Policy
    3. Closing Statements (1 minute)
        a. Biden
        b. Trump

    Total: 10 minutes
    '''
    
    # Keywords to detect in speech
    TURN_KEYWORDS = {
        "trump": ["trump", "mr. trump", "president trump", "trump's turn"],
        "biden": ["biden", "mr. biden", "president biden", "biden's turn"]
    }
    STOP_KEYWORDS = ["time is up", "time's up", "next speaker", "thank you"]
    
    def __init__(self, debater, topics=None):
        """
        Initialize controller for a single agent.
        
        Args:
            debater: "trump" or "biden" - which agent this laptop controls
            topics: list of debate topics
        """
        self.debater = debater.lower()  # "trump" or "biden"
        self.topics = topics
        self.debate_state = {
            "round": 0,
            "topic": None,
            "is_my_turn": False,
        }
        
        # Initialize the agent for this laptop
        if self.debater == "trump":
            self.agent = TrumpAgent()
            self.opponent = "biden"
        else:
            self.agent = BidenAgent()
            self.opponent = "trump"
    
    def _is_my_turn(self, text):
        """Check if heard speech indicates it's this agent's turn."""
        text_lower = text.lower()
        for keyword in self.TURN_KEYWORDS[self.debater]:
            if keyword in text_lower:
                return True
        return False
    
    def _is_stop_signal(self, text):
        """Check if heard speech indicates this agent should stop."""
        text_lower = text.lower()
        # Stop if moderator says time is up
        for keyword in self.STOP_KEYWORDS:
            if keyword in text_lower:
                return True
        # Stop if opponent's name is called (their turn now)
        for keyword in self.TURN_KEYWORDS[self.opponent]:
            if keyword in text_lower:
                return True
        return False
    
    def listen_for_turn(self):
        """
        Continuously listen via STT for moderator to call this agent's turn.
        Returns when it's this agent's turn to speak.
        """
        print(f"[{self.debater.upper()}] Listening for my turn...")
        while True:
            text = speak_input.get_input()
            if text:
                print(f"[{self.debater.upper()}] Heard: {text}")
                if self._is_my_turn(text):
                    print(f"[{self.debater.upper()}] It's my turn!")
                    self.debate_state["is_my_turn"] = True
                    return
    
    def speak_until_stopped(self, prompt, max_duration=60):
        """
        Agent speaks in response to prompt. Monitors for stop signals.
        Stops when: moderator interrupts, opponent's turn, or max_duration reached.
        
        Args:
            prompt: The prompt/context for the agent to respond to
            max_duration: Maximum speaking time in seconds
        """
        print(f"[{self.debater.upper()}] Speaking...")
        start_time = time.time()
        
        # Generate and speak the agent's response
        response = self.agent.respond(prompt)
        speak_output.say(response)
        
        elapsed = time.time() - start_time
        while elapsed <= max_duration:
            elapsed = time.time() - start_time
            time.sleep(0.5)  # Check every 0.5 seconds
        
        text = speak_input.get_input()
        if text and self._is_stop_signal(text):
            print(f"[{self.debater.upper()}] Stop signal heard: {text}")
        
        self.debate_state["is_my_turn"] = False
    
    def _timer(self, start_time,duration):
        elapsed = time.time() - start_time
        while elapsed <= duration: 
            elapsed = time.time() - start_time
            time.sleep(0.5)  # Check every 0.5 seconds
        return

    def run_debate(self):
        """
        Main loop: Listen for turn, speak when called, repeat.
        Each laptop runs this independently.
        """
        # OLD CODE - REFERENCE ONLY:
        # trump = TrumpAgent()
        # biden = BidenAgent()
        # print("Starting debate...")
        # print("Opening Statements:")
        # for debater in self.debaters:
        #     print(f"{debater['name']} is speaking...")
        #     if debater['name'] == "Trump":
        #         trump.speak()
        #     elif debater['name'] == "Biden":
        #         biden.speak()
        #     time.sleep(2)
        
        print(f"[{self.debater.upper()}] Debate controller started. Waiting for moderator...")

        # Start speech input/output threads
        speak_input.start()
        speak_output.start()

        # Get context from what was just heard (opponent's last statement)
        context = speak_input.get_input() 


        # 1. Opening Statement
        if self.debater == "trump":
            context = "Please give your opening statement, Trump. You go first."
            self.speak_until_stopped(prompt=context, max_duration=30)
            context = speak_input.get_input() 
        else: 
            #track trump's timer, then respond
            start_time = time.time()
            self._timer(start_time, 30)
            
            #prompt biden
            context = "That is time. Please give your opening statement, Biden."
            self.speak_until_stopped(prompt=context, max_duration=30)
        
        #2 policy rounds
        for topic in self.topics:
            #Moderator introduces topic
            context = f"The next topic is {topic}. Please respond to this question on {topic}. You will be given a chance to rebut after this."
            
            
            #let each debater respond to the topic for 45 seconds
            if self.debater == "trump":
                # Wait for moderator to call Trump's turn for this topic
                self.speak_until_stopped(prompt=context, max_duration=45)
                context = speak_input.get_input() # trump's agent will use this to respond
            else:
                speak_output.say(context)
                time.sleep(5) 
                #track trump's timer, then respond as biden
                start_time = time.time()
                context = speak_input.get_input() # biden's agent will use this to respond
                self._timer(start_time, 45)
                
                #prompt biden
                trump_context = "That is time. Please give your statement, Biden."
                speak_output.say(trump_context)
                self.speak_until_stopped(prompt=trump_context, max_duration=45)
            
            # Now give each debater a chance to rebut for 30 seconds
            if self.debater == "trump":
                self.speak_until_stopped(prompt=context, max_duration=30)
                context = speak_input.get_input()
            else:
                #track trump's timer, then respond as biden
                start_time = time.time()
                trump_rebut = speak_input.get_input() # biden's agent will use this to respond
                self._timer(start_time, 30)
                
                #prompt biden
                speak_output.say("That is time. Please give your rebuttal, Biden.")
                context = trump_rebut
                self.speak_until_stopped(prompt=context, max_duration=30)
            
            print(f"[{self.debater.upper()}] Finished speaking, listening for next turn...")
    
        # Closing statements could follow a similar pattern
        closing_prompt = "That concludes the policy rounds. Please give your closing statement."
        

        if self.debater == "biden":
            speak_output.say(closing_prompt)
            self.speak_until_stopped(prompt=closing_prompt, max_duration=60)
            speak_output.say("That is time. Trump, your closing statement, please.")
        else:
            #track biden's timer, then respond as trump
            start_time = time.time()
            self._timer(start_time, 30)
            self.speak_until_stopped(prompt=closing_prompt, max_duration=60)

