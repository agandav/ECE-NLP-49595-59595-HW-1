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
    - Generates responses via Azure OpenAI wrapper

    Notes on realism & performance:
    - We DO NOT paste the last Biden response into the prompt; recent history already includes it.
      This keeps prompts smaller (faster) and reduces repetition loops.
    - We also keep a tiny stance summary, but by default we update it only occasionally
      to avoid an extra LLM call every turn (which can slow down later turns).
    """

    def __init__(self):
        self.name = PERSONAS["biden"]["name"]
        prompt_path = PERSONAS["biden"]["prompt_path"]
        self.system_prompt = Path(prompt_path).read_text(encoding="utf-8")

        self.history: List[Dict[str, str]] = []
        self.stance_summary: str = ""

        self.llm = AzureLLM()

        # Track turn count so we can throttle expensive extras (like stance summary refresh)
        self.turn_count: int = 0

    def respond(self, opponent_message: str, debate_state: Optional[Dict[str, Any]] = None) -> str:
        debate_state = debate_state or {}
        topic = debate_state.get("topic", "general issues")
        round_num = debate_state.get("round", None)

        self.turn_count += 1

        messages, user_instruction = self._build_messages(
            opponent_message=opponent_message,
            topic=topic,
            round_num=round_num,
        )

        response = self._generate(messages)

        # Store instruction + response in history
        self.history.append({"role": "user", "content": user_instruction})
        self.history.append({"role": "assistant", "content": response})

        # Update stance summary occasionally to avoid a second LLM call every single turn.
        # (If you want it every turn, set this to `if True:` but it will be slower.)
        if self.turn_count % 3 == 0:
            self._update_stance_summary(response)

        return response

    def _build_messages(
        self,
        opponent_message: str,
        topic: str,
        round_num: Optional[int],
    ):
        # Keep last few turns so the agent stays consistent but doesn't grow forever
        recent_history = self.history[-6:]  # last 3 exchanges (user/assistant)

        # Build a compact, turn-specific instruction.
        # Keep this short so latency stays stable across turns.
        user_instruction = (
            f"Debate topic: {topic}.\n"
            f"{'Round: ' + str(round_num) + '.' if round_num is not None else ''}\n\n"
            f"Opponent just said:\n{opponent_message}\n\n"
            "Respond as Joe Biden in a live presidential debate exchange.\n"
            "Constraints:\n"
            "- 90–180 words. About 1 in 4 turns can be 90–130 words (short and punchy).\n"
            "- Sound reactive and conversational, not like an essay, op-ed, or policy memo.\n"
            "- Use 1–3 short paragraphs OR one tight block of speech; vary structure naturally across turns.\n"
            "- Often start with a direct correction, quick contrast, or voter-centered line, but do not force the same opener.\n"
            "- Respond to ONE central claim; paraphrase rather than quote. Avoid quotation marks unless necessary.\n"
            "- You may choose ONE dominant mode this turn: mostly rebuttal, mostly contrast, or mostly moral framing.\n"
            "- A pivot to ordinary Americans is optional (costs, jobs, healthcare, dignity, fairness) — do not force a pivot every turn.\n"
            "- Include 0–2 concrete actions/outcomes; avoid lists and policy-mechanism explanations.\n"
            "- Biden-style phrase is optional; at most ONE (e.g., 'Here’s the deal', 'Come on', 'Folks') and not every turn.\n"
            "- Controlled bluntness is allowed when correcting false claims ('That’s simply wrong', 'He knows better').\n"
            "- Avoid repetition: do not reuse the same opener, pacing, framing, or emotional tone from your previous response.\n"
            "- Do not mention Ukraine/'Putin's war'/global supply chains/worldwide more than once every 3 Biden turns unless opponent raises it.\n"
            "- Stay plausible and defensible.\n"
        )

        messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

        # Optional compact context to keep continuity (keep it small!)
        if self.stance_summary.strip():
            messages.append(
                {
                    "role": "system",
                    "content": f"Continuity notes (keep consistent, don't repeat verbatim):\n{self.stance_summary}".strip(),
                }
            )

        # Add recent conversation history (if any)
        messages.extend(recent_history)

        # Add current instruction
        messages.append({"role": "user", "content": user_instruction})

        return messages, user_instruction

    def _generate(self, messages: List[Dict[str, str]]) -> str:
        response = self.llm.chat(
            messages,
            temperature=0.7,
            max_tokens=280,  # enough for ~180 words comfortably
            presence_penalty=0.25,
            frequency_penalty=0.35,
        )
        return response.replace("\\n", "\n")

    def _update_stance_summary(self, latest_response: str):
        """
        Keep a short rolling summary (2–3 bullets max) of Biden's recurring themes/claims
        to maintain coherence without bloating the prompt.

        Throttled by caller to avoid slowing down every turn.
        """

        summary_prompt = [
            {
                "role": "system",
                "content": (
                    "Summarize Biden's main point in ONE short bullet (max 18 words). "
                    "No quotes, no extra commentary."
                ),
            },
            {"role": "user", "content": latest_response},
        ]

        try:
            short_summary = self.llm.chat(summary_prompt, temperature=0.2, max_tokens=60)
            self.stance_summary += f"- {short_summary.strip()}\n"
            # Keep only last 3 bullets
            bullets = [ln for ln in self.stance_summary.splitlines() if ln.strip()]
            self.stance_summary = "\n".join(bullets[-3:]) + "\n"
        except Exception:
            # Fail silently if summary fails
            pass