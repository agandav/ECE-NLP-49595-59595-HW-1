import time
from agents import TrumpAgent, BidenAgent
from speech import speak_input, speak_output
from speech.text_to_speech_microsoft import TRUMP_VOICE, BIDEN_VOICE

SILENCE_WINDOW = 3.0  # seconds of silence after last chunk = opponent done


def wait_for_input(timeout=180):
    """Block until opponent finishes speaking (3s silence = done)."""
    speak_input.new_input_available = False
    print("[Listening for opponent...]")

    chunks = []
    last_heard_time = None
    start = time.time()

    while True:
        text = speak_input.get_input()

        if text and text.strip():
            chunks.append(text.strip())
            last_heard_time = time.time()
            print(f"[Heard]: {text.strip()}")

        if last_heard_time is not None:
            if time.time() - last_heard_time >= SILENCE_WINDOW:
                full_text = " ".join(chunks)
                print(f"[Opponent done]: {full_text}")
                return full_text

        if time.time() - start > timeout:
            print("[Timeout]")
            return " ".join(chunks) if chunks else ""

        time.sleep(0.1)


class DebateController():
    TOPICS = ["economics", "healthcare", "immigration"]

    def __init__(self, debater, topics=None):
        self.debater = debater.lower()
        self.topics = topics or self.TOPICS
        self.voice = TRUMP_VOICE if self.debater == "trump" else BIDEN_VOICE

        if self.debater == "trump":
            self.agent = TrumpAgent()
        else:
            self.agent = BidenAgent()

    def speak(self, prompt, duration=60):
        """Generate response, print it, speak it, wait until done."""
        response = self.agent.respond(prompt)
        print(f"\n[{self.debater.upper()}]: {response}\n")
        start_time = time.time()
        speak_output.say(response)
        self.timer(start_time, duration)  # enforce pacing; adjust duration as needed
        speak_output.stop()  # stop speaking if time's up

        # from speech import text_to_speech_microsoft as tts_mod
        # from speech import speech_to_text_microsoft as stt_mod
        # while (not stt_mod.listen) or len(tts_mod.things_to_say) > 0:
        #     time.sleep(0.1)
        # time.sleep(1.0)

    def timer(self, start_time, duration=60):
        """Simple timer to enforce pacing."""
        time_elapsed = time.time() - start_time
        while time_elapsed <= duration and time_elapsed > 0:
            time.sleep(0.5)
            time_elapsed = time.time() - start_time
        
    def run_debate(self):
        speak_input.start()
        speak_output.start(voice=self.voice)  # use persona-specific voice
        print(f"[{self.debater.upper()}] Ready. Voice: {self.voice}\n")

        # ── Opening statements ──────────────────────────────────────────────
        if self.debater == "trump":
            self.speak("Give your opening statement.")
        else:
            opponent_statement = wait_for_input()
            self.speak(f"Trump said: {opponent_statement}. Give your opening statement.")

        # ── Policy rounds ───────────────────────────────────────────────────
        for topic in self.topics:
            print(f"\n--- Topic: {topic} ---\n")

            if self.debater == "trump":
                self.speak(f"Give your statement on {topic}.")

                opponent_statement = wait_for_input()
                
                self.speak(f"Biden said: {opponent_statement}. Give your rebuttal on {topic}.")
            else:
                self.speak("Please give your opening statement. Trump will go first.")
                opponent_statement = wait_for_input()

                self.speak(f"Trump said: {opponent_statement}. Respond on {topic}.")

                opponent_statement = wait_for_input()
                self.speak(f"Trump said: {opponent_statement}. Give your rebuttal on {topic}.")

        # ── Closing statements ──────────────────────────────────────────────
        if self.debater == "biden":
            self.speak("Give your closing statement.")
        else:
            opponent_statement = wait_for_input()
            self.speak(f"Biden said: {opponent_statement}. Give your closing statement.")

        print(f"\n[{self.debater.upper()}] Debate complete.")
        speak_output.stop()
        speak_input.stop()