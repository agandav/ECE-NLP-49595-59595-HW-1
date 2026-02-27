from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.personas import PERSONAS
from agents.llm_wrapper import AzureLLM


class TrumpAgent:
    """
    Debate-mode Trump persona agent.
    Mechanical goals:
    - No opponent-text duplication
    - Short, reactive replies
    - Optional burst-mode with preserved line breaks
    - Round-based escalation via sampling params (not prompt bloat)
    """

    _BASE_CFG = {"presence_penalty": 0.6, "frequency_penalty": 0.3}

    def __init__(self):
        self.name = PERSONAS["trump"]["name"]
        self.system_prompt = Path(PERSONAS["trump"]["prompt_path"]).read_text(encoding="utf-8")
        self.llm = AzureLLM()

        self.history: List[Dict[str, str]] = []
        self.stance_summary: str = ""  # keep very short

    def respond(self, opponent_message: str, debate_state: Optional[Dict[str, Any]] = None) -> str:
        debate_state = debate_state or {}
        topic = debate_state.get("topic", "general")
        round_num = debate_state.get("round")

        fmt = self._pick_format(opponent_message, round_num)

        messages = self._build_messages(opponent_message, topic, round_num, fmt)
        response = self._generate(messages, fmt, round_num)
        response = self._postprocess(response, fmt)

        self._append_turn(opponent_message, response)
        self._update_stance_summary(response)

        return response

    # ---------------- Prompt construction ----------------

    def _build_messages(self, opponent_message: str, topic: str, round_num: Optional[int], fmt: str):
        msgs: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

        if self.stance_summary:
            msgs.append({"role": "system", "content": f"Consistency (short):\n{self.stance_summary}"})

        msgs.extend(self._recent_history(4))

        # Opponent message ONCE
        msgs.append({"role": "user", "content": opponent_message})

        # Tiny director note (no opponent text here)
        msgs.append({"role": "system", "content": self._director_note(topic, round_num, fmt)})

        return msgs

    def _director_note(self, topic: str, round_num: Optional[int], fmt: str) -> str:
        r = round_num if round_num is not None else "N/A"
        return (
            f"TOPIC: {topic} | ROUND: {r}\n"
            f"FORMAT: {fmt}\n"
            "React live. No 'you said' opener. No quoting.\n"
            "Include one concrete detail.\n"
        )

    # ---------------- Sampling control ----------------

    def _cfg_for_round(self, round_num: Optional[int]) -> Dict[str, float]:
        if round_num is None:
            temp = 0.85
        elif round_num < 3:
            temp = 0.80
        elif round_num < 6:
            temp = 0.88
        else:
            temp = 0.92
        return {**self._BASE_CFG, "temperature": temp}

    # ---------------- Format control ----------------

    def _pick_format(self, opponent_message: str, round_num: Optional[int]) -> str:
        # Start with base weights
        weights = {"one_para": 0.55, "two_para": 0.25, "burst": 0.20}

        # If opponent is short, burst becomes more likely (this is *huge* for realism)
        if len(opponent_message.strip()) < 140:
            weights["burst"] += 0.20
            weights["one_para"] -= 0.10
            weights["two_para"] -= 0.10

        # Late rounds: slightly more burst chance
        if round_num is not None and round_num >= 4:
            weights["burst"] = min(weights["burst"] + 0.10, 0.45)
            weights["one_para"] = max(weights["one_para"] - 0.07, 0.25)

        # Normalize + sample
        total = sum(max(v, 0.01) for v in weights.values())
        r = random.random() * total
        acc = 0.0
        for k in ("one_para", "two_para", "burst"):
            acc += max(weights[k], 0.01)
            if r <= acc:
                return k
        return "one_para"

    def _max_tokens_for(self, fmt: str) -> int:
        # Strongest lever for short outputs
        return {"one_para": 105, "two_para": 135, "burst": 95}.get(fmt, 105)

    # ---------------- Generation ----------------

    def _generate(self, messages, fmt: str, round_num: Optional[int]) -> str:
        cfg = self._cfg_for_round(round_num)
        out = self.llm.chat(messages, max_tokens=self._max_tokens_for(fmt), **cfg)
        return out.replace("\\n", "\n").strip()

    # ---------------- Postprocess ----------------

    def _postprocess(self, text: str, fmt: str) -> str:
        text = text.strip()

        if fmt == "burst":
            # Preserve line breaks; trim empty lines
            lines = [ln.rstrip() for ln in text.splitlines()]
            lines = [ln for ln in lines if ln.strip()]
            return "\n".join(lines[:6]).strip()  # cap lines

        # For paragraphs: keep at most 2 paragraphs, but do NOT over-flatten
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        if fmt == "two_para":
            return "\n\n".join(paras[:2]).strip()

        # one_para
        return paras[0] if paras else text

    # ---------------- Memory ----------------

    def _recent_history(self, max_msgs: int) -> List[Dict[str, str]]:
        return self.history[-max_msgs:] if self.history else []

    def _append_turn(self, opponent: str, response: str) -> None:
        self.history.append({"role": "user", "content": opponent})
        self.history.append({"role": "assistant", "content": response})
        self.history = self.history[-4:]  # last 2 exchanges

    def _update_stance_summary(self, latest_response: str) -> None:
        summary_prompt = [
            {"role": "system", "content": "6–10 word stance snippet. No full sentence."},
            {"role": "user", "content": latest_response},
        ]
        try:
            short = self.llm.chat(summary_prompt, temperature=0.6, max_tokens=25).strip()
            short = short.lstrip("-•").strip()
            if short:
                lines = [ln.strip() for ln in self.stance_summary.splitlines() if ln.strip()]
                lines.append(f"- {short}")
                self.stance_summary = "\n".join(lines[-3:])
        except Exception:
            pass