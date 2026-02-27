from agents.trump_agent import TrumpAgent

a = TrumpAgent()

test_inputs = [
    "You failed to help working families and you divided the country.",
    "Inflation is worse under your leadership.",
    "You were impeached twice.",
    "You mishandled COVID.",
    "You are a threat to democracy."
]

for i, attack in enumerate(test_inputs):
    print("\n" + "="*60)
    print(f"ROUND {i+1}")
    print("="*60)
    print(a.respond(attack, {"topic": "general issues", "round": i+1}))