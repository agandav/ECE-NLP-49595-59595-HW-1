"""
test.py

This script runs a single-topic debate simulation between the TrumpAgent
and BidenAgent.

What it does:
- Uses one debate topic (TOPICS[0])
- Runs a single round
- Generates 10 total responses (5 Trump, 5 Biden)
- Alternates turns automatically
- Maintains conversational flow (each response reacts to the previous one)

How to run:
    python test.py

Make sure you have:
    pip install -r requirements.txt
    .env file configured for Azure OpenAI
"""

from agents.biden_agent import BidenAgent
from agents.trump_agent import TrumpAgent

TOPICS = [
    ("economy", "Inflation is out of control."),
]

def run_debate(total_turns=10):
    biden = BidenAgent()
    trump = TrumpAgent()

    topic, seed = TOPICS[0]

    print("\n" + "=" * 80)
    print(f"ROUND 1 | TOPIC: {topic}")
    print("=" * 80)

    # First message starts from the seed claim
    last_message = seed

    for t in range(1, total_turns + 1):
        if t % 2 == 1:
            # Odd turns → Trump speaks
            output = trump.respond(
                last_message,
                {"topic": topic, "round": 1, "turn": t}
            )
            print("\nTRUMP:\n", output)
        else:
            # Even turns → Biden speaks
            output = biden.respond(
                last_message,
                {"topic": topic, "round": 1, "turn": t}
            )
            print("\nBIDEN:\n", output)

        # Next speaker responds to this output
        last_message = output


if __name__ == "__main__":
    run_debate(total_turns=10)