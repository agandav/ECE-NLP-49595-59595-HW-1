from __future__ import annotations
from typing import Any, Dict, List, Optional
from pathlib import Path

from agents.personas import PERSONAS


class BidenAgent:
    """
    Biden persona agent.
    - Keeps lightweight conversation memory
    - Builds LLM-ready message payload
    - LLM call is stubbed for now (plugs into Azure later)
    """

    def __init__(self):
        self.name = PERSONAS["biden"]["name"]
        prompt_path = PERSONAS["biden"]["prompt_path"]
        self.system_prompt = Path(prompt_path).read_text(encoding="utf-8")
        self.history: List[Dict[str, str]] = []  # [{"role": "...", "content": "..."}]

    def respond(self, opponent_message: str, debate_state: Optional[Dict[str, Any]] = None) -> str:
        debate_state = debate_state or {}
        topic = debate_state.get("topic", "general issues")
        round_num = debate_state.get("round", None)

        # Store opponent message
        self.history.append({"role": "user", "content": opponent_message})

        messages = self._build_messages(opponent_message=opponent_message, topic=topic, round_num=round_num)

        # For now: stub generation (replace later with Azure GPT call)
        response = self._generate(messages, topic=topic)

        # Store response
        self.history.append({"role": "assistant", "content": response})
        return response

    def _build_messages(self, opponent_message: str, topic: str, round_num: Optional[int]) -> List[Dict[str, str]]:
        # Keep last few turns so the agent stays consistent but doesn't grow forever
        recent_history = self.history[-6:]  # last 3 exchanges (user/assistant)

        user_instruction = (
            f"Debate topic: {topic}.\n"
            f"{'Round: ' + str(round_num) + '.' if round_num is not None else ''}\n\n"
            f"Opponent just said:\n{opponent_message}\n\n"
            "Respond in a debate style. Rebut one key point, then pivot to your best argument, "
            "and close with a short persuasive finish. Stay in character."
        )

        messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

        # Add recent conversation history (if any)
        for m in recent_history:
            messages.append(m)

        # Add current instruction
        messages.append({"role": "user", "content": user_instruction})
        return messages

    def _generate(self, messages, topic: str):
      opponent_statement = self.history[-1]["content"]

      topic_blocks = {
        "economy": "We've created jobs, strengthened supply chains, and lowered costs for working families.",
        "immigration": "We're securing the border while reforming a broken system responsibly.",
        "foreign policy": "We've restored alliances and strengthened America's leadership globally.",
        "healthcare": "We're expanding access and lowering prescription drug costs.",
    }

      topic_argument = topic_blocks.get(
        topic,
        "We're focused on practical solutions that strengthen working families and protect democracy."
    )

      response = (
        "Folks, let me be clear. My opponent just said that "
        f"\"{opponent_statement}\" — and that simply doesn't reflect the full picture.\n\n"
        f"Here's the deal: {topic_argument} "
        "Leadership grounded in facts and stability matters.\n\n"
        "This election is about protecting democracy and ensuring opportunity for the middle class. "
        "That's what I'll continue fighting for."
    )

      return response