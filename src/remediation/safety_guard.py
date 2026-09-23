import time
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger("safety_loop_guard")

class SafetyLoopGuard:
    """
    Prevents runaway remediation loops:
    1. Checks cooldown period between interventions for a target resource.
    2. Enforces maximum retry attempts per rolling window.
    3. Escalates when recovery fails repeatedly.
    """
    def __init__(self, cooldown_seconds: int = 300, max_retries: int = 3, window_seconds: int = 1800):
        self.cooldown_seconds = cooldown_seconds
        self.max_retries = max_retries
        self.window_seconds = window_seconds
        # Target identifier -> {"history": [timestamp1, timestamp2, ...], "last_action": timestamp}
        self._state: Dict[str, Dict] = {}

    def _cleanup_old_history(self, target: str, now: float):
        if target in self._state:
            window_start = now - self.window_seconds
            self._state[target]["history"] = [
                ts for ts in self._state[target]["history"] if ts >= window_start
            ]

    def can_remediate(self, target: str) -> Tuple[bool, Optional[str]]:
        """
        Returns (allowed: bool, reason: str).
        """
        now = time.time()
        self._cleanup_old_history(target, now)
        target_state = self._state.get(target)

        if not target_state:
            return True, "No prior remediation history."

        last_action = target_state.get("last_action", 0)
        time_since_last = now - last_action
        if time_since_last < self.cooldown_seconds:
            remaining = int(self.cooldown_seconds - time_since_last)
            return False, f"Cooldown in effect for {target}. Wait {remaining}s."

        history_count = len(target_state.get("history", []))
        if history_count >= self.max_retries:
            return False, f"Max retries ({self.max_retries}) exceeded within window for {target}. Escalating to on-call."

        return True, "Allowed within safe operational boundaries."

    def record_action(self, target: str):
        now = time.time()
        if target not in self._state:
            self._state[target] = {"history": [], "last_action": now}
        self._state[target]["history"].append(now)
        self._state[target]["last_action"] = now

    def reset_target(self, target: str):
        if target in self._state:
            del self._state[target]

    def get_status(self, target: str) -> Dict:
        now = time.time()
        self._cleanup_old_history(target, now)
        target_state = self._state.get(target, {"history": [], "last_action": 0})
        return {
            "target": target,
            "attempts_in_window": len(target_state.get("history", [])),
            "max_allowed": self.max_retries,
            "last_action_timestamp": target_state.get("last_action", 0),
            "cooldown_seconds": self.cooldown_seconds
        }
