from agents.trump_agent import TrumpAgent

a = TrumpAgent()
print(a.respond("You failed to help working families and you divided the country.", {"topic": "the economy", "round": 1}))