from __future__ import annotations
from typing import Any, Dict, List, Optional
from pathlib import Path

from agents.personas import PERSONAS
from agents.llm_wrapper import AzureLLM


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
      self.history: List[Dict[str, str]] = []
      self.stance_summary = ""
      self.llm = AzureLLM()

    def respond(self, opponent_message: str, debate_state: Optional[Dict[str, Any]] = None) -> str:
        debate_state = debate_state or {}
        topic = debate_state.get("topic", "general issues")
        round_num = debate_state.get("round", None)

        # Store opponent message
        self.history.append({"role": "user", "content": opponent_message})


        messages = self._build_messages(opponent_message=opponent_message, topic=topic, round_num=round_num)

        response = self._generate(messages)

        self.history.append({"role": "assistant", "content": response})

        self._update_stance_summary(response)

        return response

    def _build_messages(self, opponent_message: str, topic: str, round_num: Optional[int]) -> List[Dict[str, str]]:
        # Keep last few turns so the agent stays consistent but doesn't grow forever
        recent_history = self.history[-6:]  # last 3 exchanges (user/assistant)

        user_instruction = (
          f"Debate topic: {topic}.\n"
          f"{'Round: ' + str(round_num) + '.' if round_num is not None else ''}\n\n"
          f"Opponent just said:\n{opponent_message}\n\n"
          "Respond as Joe Biden in a presidential debate.\n"
          "Constraints:\n"
          "- 3 short paragraphs, no bullet points\n"
          "- 120–180 words max\n"
          "- 1st paragraph: rebut 1 key claim\n"
          "- 2nd paragraph: pivot to your best argument on the topic\n"
          "- 3rd paragraph: values + closing line\n"
          "- Use at least one Biden-style phrase like 'folks' or 'here’s the deal'\n"
          "- Stay in character. No mentioning policies you cannot defend; keep it general and plausible.\n"
)

        messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

        if self.stance_summary:
          messages.append({
          "role": "system",
          "content": f"Context from earlier debate rounds:\n{self.stance_summary}"
        })

        # Add recent conversation history (if any)
        for m in recent_history:
            messages.append(m)

        # Add current instruction
        messages.append({"role": "user", "content": user_instruction})
        return messages

    def _generate(self, messages: List[Dict[str, str]]) -> str:
      response = self.llm.chat(messages, temperature=0.7)
      return response.replace("\\n", "\n")
    

    def _update_stance_summary(self, latest_response: str):
     """
     Keep a short rolling summary (2–3 lines max) of Biden's main claims
     so he stays consistent across rounds.
     """

     summary_prompt = [
        {
            "role": "system",
            "content": "Summarize Biden's main claim in 1 concise sentence."
        },
        {
            "role": "user",
            "content": latest_response
        }
     ]

     try:
        short_summary = self.llm.chat(summary_prompt, temperature=0.2)
        # Keep only last 3 summaries
        self.stance_summary += f"- {short_summary.strip()}\n"
        self.stance_summary = "\n".join(self.stance_summary.splitlines()[-3:])
     except:
        # Fail silently if summary fails
        pass