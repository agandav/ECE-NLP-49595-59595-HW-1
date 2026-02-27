from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.personas import PERSONAS
from agents.llm_wrapper import AzureLLM


class TrumpAgent:
    """
    Trump persona agent (debate mode).
    Goals:
    - Short, punchy, natural flow (not essays)
    - Per-turn format variety (1 para / 2 short paras / fragments)
    - Minimal prompt bloat (no long constraint lists)
    - Lightweight memory (recent turns + tiny stance summary)
    """

    # Weighted output formats (variety without randomness ruining style)
    _FORMATS = [
        ("one_para", 0.60),
        ("two_para", 0.25),
        ("fragments", 0.15),
    ]

    # Trump is punchier with a slightly higher temp, but cap length hard
    _GEN_CFG = {
        "temperature": 0.95,
        "presence_penalty": 0.7,
        "frequency_penalty": 0.4,
    }

    def __init__(self):
        self.name = PERSONAS["trump"]["name"]
        prompt_path = PERSONAS["trump"]["prompt_path"]
        self.system_prompt = Path(prompt_path).read_text(encoding="utf-8")

        self.llm = AzureLLM()
        self.history: List[Dict[str, str]] = []
        self.stance_summary: str = ""  # tiny rolling consistency memory

    # ---------------- Public API ----------------

    def respond(self, opponent_message: str, debate_state: Optional[Dict[str, Any]] = None) -> str:
        debate_state = debate_state or {}
        topic = debate_state.get("topic", "general")
        round_num = debate_state.get("round")

        # Store opponent message as a normal user turn (for continuity)
        self.history.append({"role": "user", "content": opponent_message})

        fmt = self._pick_format(round_num=round_num)

        messages = self._build_messages(
            opponent_message=opponent_message,
            topic=topic,
            round_num=round_num,
            fmt=fmt,
        )

        response = self._generate(messages, fmt=fmt)
        response = self._postprocess(response, fmt=fmt)

        self.history.append({"role": "assistant", "content": response})
        self._update_stance_summary(response)

        return response

    # ---------------- Prompting ----------------

    def _build_messages(
        self,
        opponent_message: str,
        topic: str,
        round_num: Optional[int],
        fmt: str,
    ) -> List[Dict[str, str]]:
        # Keep only last 2 exchanges (4 messages) to avoid ballooning
        recent_history = self._recent_history(max_msgs=4)

        # Minimal, non-bloated instruction (the system prompt does most of the work)
        user_instruction = (
            f"TOPIC: {topic}\n"
            f"ROUND: {round_num if round_num is not None else 'N/A'}\n"
            f"Opponent:\n{opponent_message}\n\n"
            "Write a Trump-like debate reply.\n"
            "Must respond to ONE specific point they made, but DO NOT quote/paraphrase it in the opener.\n"
            "Opener must be a blunt dismissal or punchy line (not 'You said...').\n"
            "Then pivot to your strongest argument and end with a punchline.\n"
        )
        messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

        if self.stance_summary:
            messages.append({"role": "system", "content": f"Debate consistency (keep it consistent):\n{self.stance_summary}"})

        messages.extend(recent_history)
        messages.append({"role": "user", "content": user_instruction})
        return messages

    # ---------------- Generation ----------------

    def _generate(self, messages: List[Dict[str, str]], fmt: str) -> str:
        response = self.llm.chat(
            messages,
            max_tokens=self._max_tokens_for(fmt),
            **self._GEN_CFG,
        )
        return response.replace("\\n", "\n")

    # ---------------- Style control ----------------

    def _pick_format(self, round_num: Optional[int]) -> str:
        """
        Weighted format choice with optional escalation:
        - Early rounds: more one_para
        - Later rounds: slightly more fragments/two_para for punch
        """
        # Base weights
        weights = dict(self._FORMATS)

        if round_num is not None:
            # Gentle escalation: later rounds get more "fragments"
            # (keeps it lively without turning into chaos)
            if round_num >= 3:
                weights["fragments"] = min(weights["fragments"] + 0.08, 0.30)
                weights["one_para"] = max(weights["one_para"] - 0.06, 0.35)
            if round_num >= 5:
                weights["two_para"] = min(weights["two_para"] + 0.05, 0.35)
                weights["one_para"] = max(weights["one_para"] - 0.05, 0.30)

        # Normalize + sample
        total = sum(weights.values())
        r = random.random() * total
        acc = 0.0
        for name in ("one_para", "two_para", "fragments"):
            acc += weights[name]
            if r <= acc:
                return name
        return "one_para"

    def _format_instruction(self, fmt: str) -> str:
        """
        Keep this SHORT. The system prompt should already encode the persona style.
        """
        if fmt == "one_para":
            return "One paragraph. 4–6 short sentences."
        if fmt == "two_para":
            return "Two short paragraphs. Para 1: 2–3 sentences. Para 2: 1–2 sentences."
        if fmt == "fragments":
            return "6–9 short sentences; allow 1–3 word fragments; include one rhetorical question."
        return "One paragraph. 4–6 short sentences."

    def _max_tokens_for(self, fmt: str) -> int:
        # Hard cap to prevent essays
        return {"one_para": 120, "two_para": 140, "fragments": 115}.get(fmt, 120)

    def _postprocess(self, text: str, fmt: str) -> str:
        """
        Clamp paragraph count to match chosen format so outputs stay consistent.
        """
        # Trim whitespace
        text = text.strip()

        # Split on blank lines
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]

        if fmt == "two_para":
            paras = paras[:2]
            return "\n\n".join(paras).strip()

        # one_para or fragments => collapse to single block
        collapsed = " ".join(paras).strip()
        # Remove accidental double spaces
        while "  " in collapsed:
            collapsed = collapsed.replace("  ", " ")
        return collapsed

    # ---------------- Memory ----------------

    def _recent_history(self, max_msgs: int = 4) -> List[Dict[str, str]]:
        """
        Return last N messages, but avoid duplicating the current opponent message
        because we also include it explicitly in the user instruction.
        """
        # history already includes opponent_message as last "user" entry
        # Keep prior context but exclude the last user message to prevent repetition
        hist = self.history[:-1]
        return hist[-max_msgs:] if hist else []

    def _update_stance_summary(self, latest_response: str) -> None:
        """
        Keep 2–3 short lines of "what Trump is claiming" so he stays consistent.
        """
        summary_prompt = [
            {"role": "system", "content": "Summarize Trump's core claim from this reply in ONE short line (no extra words)."},
            {"role": "user", "content": latest_response},
        ]

        try:
            short = self.llm.chat(summary_prompt, temperature=0.2, max_tokens=40)
            short = short.strip().lstrip("-•").strip()
            if short:
                # Keep last 3 lines
                lines = [ln.strip() for ln in self.stance_summary.splitlines() if ln.strip()]
                lines.append(f"- {short}")
                self.stance_summary = "\n".join(lines[-3:])
        except Exception:
            # Fail silently
            return