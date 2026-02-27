from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import re

from agents.personas import PERSONAS
from agents.llm_wrapper import AzureLLM


class BidenAgent:
    """
    Biden persona agent.

    Design goals:
    - Realism: system prompt carries persona + style; user prompt stays short and reactive.
    - Speed: ONE LLM call per turn (no stance-summary LLM call).
    - Token control: do NOT store raw opponent walls-of-text in history.
    - Non-repetition: track last opener + recent anchor phrases locally (no LLM).
    - Stability: hard-bound history so latency doesn't grow over time.
    """

    def __init__(self):
        self.name = PERSONAS["biden"]["name"]
        prompt_path = PERSONAS["biden"]["prompt_path"]
        self.system_prompt = Path(prompt_path).read_text(encoding="utf-8")

        self.history: List[Dict[str, str]] = []
        self.llm = AzureLLM()

        # Lightweight local memory (no extra LLM calls)
        self.turn_count: int = 0
        self.last_opener: str = ""
        self.recent_anchors: List[str] = []  # small rolling list of phrases to discourage
        self.mode_last: str = ""             # track structure mode A/B/C/D

    def respond(self, opponent_message: str, debate_state: Optional[Dict[str, Any]] = None) -> str:
        debate_state = debate_state or {}
        topic = debate_state.get("topic", "general issues")
        round_num = debate_state.get("round", None)

        self.turn_count += 1

        messages, compact_user = self._build_messages(
            opponent_message=opponent_message,
            topic=topic,
            round_num=round_num,
        )

        response = self._generate(messages)

        # Store compact user + response
        self.history.append({"role": "user", "content": compact_user})
        self.history.append({"role": "assistant", "content": response})

        # Hard-bound history: keep last 3 exchanges (6 messages)
        if len(self.history) > 12:
            self.history = self.history[-12:]

        self._update_local_memory(response)
        return response

    # ---------------------------
    # Prompt construction
    # ---------------------------

    def _build_messages(
        self,
        opponent_message: str,
        topic: str,
        round_num: Optional[int],
    ) -> Tuple[List[Dict[str, str]], str]:
        recent_history = self.history[-6:]  # last 3 exchanges

        opponent_snip = self._compress_opponent(opponent_message, max_chars=650)

        # Choose a mode for this turn (rotate; don't repeat last)
        mode = self._choose_mode()

        compact_user = (
            f"Topic: {topic}. "
            f"{('Round ' + str(round_num) + '.') if round_num is not None else ''}\n"
            f"Opponent:\n{opponent_snip}\n\n"
            "Reply as Joe Biden in a live debate. Keep it reactive and natural.\n"
            "Target 120–180 words (occasionally 90–130 for punchy turns).\n"
            f"Use structure mode {mode} this turn.\n"
        )

        # Non-repetition hints (small, not a giant paste)
        if self.last_opener:
            compact_user += f"Avoid starting like last time (last opener: {self.last_opener}).\n"
        if self.recent_anchors:
            compact_user += "Avoid reusing these exact phrases: " + "; ".join(self.recent_anchors[-3:]) + "\n"

        messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]
        messages.extend(recent_history)
        messages.append({"role": "user", "content": compact_user})
        return messages, compact_user

    def _generate(self, messages: List[Dict[str, str]]) -> str:
        response = self.llm.chat(
            messages,
            temperature=0.65,     # helps human variation
            max_tokens=260,      # keeps it tighter; still enough for 180 words
            presence_penalty=0.15,
            frequency_penalty=0.35,
        )
        return response.replace("\\n", "\n").strip()

    # ---------------------------
    # Local helpers (NO LLM)
    # ---------------------------

    def _compress_opponent(self, text: str, max_chars: int = 650) -> str:
        t = re.sub(r"\s+", " ", text).strip()
        if len(t) <= max_chars:
            return t
        return t[: max_chars - 3].rstrip() + "..."

    def _choose_mode(self) -> str:
        """
        Rotate structure modes A/B/C/D without repeating the last mode.
        Simple deterministic rotation based on turn_count.
        """
        modes = ["A", "B", "C", "D"]
        # pick a mode based on turn_count but avoid repeating last
        idx = (self.turn_count - 1) % len(modes)
        mode = modes[idx]
        if mode == self.mode_last:
            mode = modes[(idx + 1) % len(modes)]
        self.mode_last = mode
        return mode

    def _update_local_memory(self, response: str) -> None:
        # last_opener = first ~8 words (lowercased)
        words = re.findall(r"[A-Za-z']+|[0-9]+", response)
        opener = " ".join(words[:8]).strip().lower()
        self.last_opener = opener

        # Track anchors we want to discourage repeating too often
        anchors = [
            "kitchen table",
            "working families",
            "middle class",
            "wall street",
            "fair shot",
            "dignity",
            "bottom up",
            "middle out",
            "here's the deal",
            "folks",
            "come on",
            "let’s be clear",
            "let me set the record straight",
        ]
        lower = response.lower()
        used = [a for a in anchors if a in lower]

        for u in used:
            if u not in self.recent_anchors:
                self.recent_anchors.append(u)

        # keep small rolling list
        if len(self.recent_anchors) > 8:
            self.recent_anchors = self.recent_anchors[-8:]