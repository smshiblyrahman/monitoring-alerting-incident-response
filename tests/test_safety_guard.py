import pytest
import time
from src.remediation.safety_guard import SafetyLoopGuard

def test_safety_guard_initial_allowance():
    guard = SafetyLoopGuard(cooldown_seconds=10, max_retries=2, window_seconds=60)
    allowed, reason = guard.can_remediate("test-app")
    assert allowed is True
    assert "No prior remediation history" in reason

def test_safety_guard_cooldown_enforcement():
    guard = SafetyLoopGuard(cooldown_seconds=5, max_retries=3, window_seconds=60)
    guard.record_action("test-app")
    
    # Immediate retry should be blocked by cooldown
    allowed, reason = guard.can_remediate("test-app")
    assert allowed is False
    assert "Cooldown in effect" in reason

    # After waiting beyond cooldown, should be allowed
    time.sleep(5.1)
    allowed, reason = guard.can_remediate("test-app")
    assert allowed is True

def test_safety_guard_max_retries_escalation():
    guard = SafetyLoopGuard(cooldown_seconds=0, max_retries=2, window_seconds=60)
    
    # 1st attempt
    allowed, _ = guard.can_remediate("test-app")
    assert allowed is True
    guard.record_action("test-app")
    
    # 2nd attempt
    allowed, _ = guard.can_remediate("test-app")
    assert allowed is True
    guard.record_action("test-app")

    # 3rd attempt exceeds max_retries (2)
    allowed, reason = guard.can_remediate("test-app")
    assert allowed is False
    assert "Max retries (2) exceeded" in reason

def test_safety_guard_reset():
    guard = SafetyLoopGuard(cooldown_seconds=10, max_retries=1, window_seconds=60)
    guard.record_action("test-app")
    allowed, _ = guard.can_remediate("test-app")
    assert allowed is False

    # Resetting clears history (e.g. after alert resolves)
    guard.reset_target("test-app")
    allowed, reason = guard.can_remediate("test-app")
    assert allowed is True
