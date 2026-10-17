"""Experimental, deterministic trigger policy. No physical actions."""

from collections import deque
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Mapping:
    mode: str = "face"
    face_signal: str = "browInnerUp"
    hand_gesture: str = "Open_Palm"
    activate: float = 0.7
    release: float = 0.3
    hold_ms: int = 500
    release_ms: int = 300
    cooldown_ms: int = 800
    timeout_ms: int = 3000
    overlap_ms: int = 500
    max_gap_ms: int = 1000

    def __post_init__(self):
        if self.mode not in {"face", "hand", "either", "combined", "sequence"}:
            raise ValueError("Unknown mapping mode")
        if not 0 <= self.release < self.activate <= 1:
            raise ValueError("Require 0 <= release < activate <= 1")
        for name in (
            "hold_ms",
            "release_ms",
            "cooldown_ms",
            "timeout_ms",
            "overlap_ms",
            "max_gap_ms",
        ):
            value = getattr(self, name)
            if type(value) is not int or not 0 <= value <= 30000:
                raise ValueError(f"{name} must be an integer from 0 to 30000")
        if self.timeout_ms == 0 or self.max_gap_ms == 0:
            raise ValueError("Timeout and maximum frame gap must be positive")
        if not self.face_signal or len(self.face_signal) > 80:
            raise ValueError("Choose a face signal")
        if self.hand_gesture not in {
            "None",
            "Closed_Fist",
            "Open_Palm",
            "Pointing_Up",
            "Thumb_Down",
            "Thumb_Up",
            "Victory",
            "ILoveYou",
        }:
            raise ValueError("Choose a supported hand gesture")


class TriggerEngine:
    def __init__(self, mapping: Mapping):
        self.mapping = mapping
        self.state = "observing"
        self.events = deque(maxlen=100)
        self.active = [False, False]
        self.edges = [None, None]
        self.since = 0
        self.released_at = None
        self.last_time = None
        self.confirm_ready = False
        self.event_id = 0
        self.release_needed = None

    def transition(self, state, now, reason):
        self.state = state
        self.since = now
        self.event_id += 1
        self.events.append(
            {"id": self.event_id, "timestamp_ms": now, "state": state, "reason": reason}
        )

    def cancel(self, now):
        self.released_at = None
        self.transition("waiting_for_release", now, "Cancelled; release both selected cues")

    def update(self, now, face, hand):
        m = self.mapping
        if self.last_time is not None and now <= self.last_time:
            return False
        gap = self.last_time is not None and now - self.last_time > m.max_gap_ms
        self.last_time = now
        values = [face, hand]
        needed = [0] if m.mode == "face" else [1] if m.mode == "hand" else [0, 1]
        if m.mode == "either":
            needed = (
                self.release_needed
                if self.state == "waiting_for_release" and self.release_needed
                else [i for i, value in enumerate(values) if value is not None]
            )
        missing = not needed or any(values[i] is None or not isfinite(values[i]) for i in needed)
        if missing or gap:
            if self.release_needed is None:
                self.release_needed = [i for i, active in enumerate(self.active) if active]
            self.active = [False, False]
            self.edges = [None, None]
            self.released_at = None
            if self.state != "waiting_for_release":
                self.transition(
                    "waiting_for_release", now, "Missing input or frame gap; neutral input required"
                )
            return False
        for i, value in enumerate(values):
            value = value if value is not None else 0
            if not self.active[i] and value >= m.activate:
                self.active[i] = True
                self.edges[i] = now
            elif self.active[i] and value <= m.release:
                self.active[i] = False
                self.edges[i] = None
        f, h = self.active
        if self.state == "waiting_for_release":
            if all(values[i] <= m.release for i in needed):
                if self.released_at is None:
                    self.released_at = now
                if now - self.released_at >= m.release_ms and now - self.since >= m.cooldown_ms:
                    self.transition("observing", now, "Released; ready")
                    self.release_needed = None
            else:
                self.released_at = None
            return False
        if self.state == "awaiting_confirmation":
            if now - self.since > m.timeout_ms:
                self.transition("waiting_for_release", now, "Confirmation timed out")
                return False
            if not f:
                self.confirm_ready = True
            if f and self.confirm_ready:
                return self.activate(now)
            return False
        eligible = {"face": f, "hand": h, "either": f or h, "combined": f and h, "sequence": h}[
            m.mode
        ]
        if m.mode == "combined" and eligible:
            eligible = abs(self.edges[0] - self.edges[1]) <= m.overlap_ms
        if not eligible:
            if self.state == "candidate":
                self.transition("observing", now, "Cue released before hold completed")
            return False
        if self.state == "observing":
            self.transition("candidate", now, "Activation range entered")
        if now - self.since >= m.hold_ms:
            if m.mode == "sequence":
                self.confirm_ready = not f
                self.transition("awaiting_confirmation", now, "Waiting for a new face cue")
            else:
                return self.activate(now)
        return False

    def activate(self, now):
        self.release_needed = [i for i, active in enumerate(self.active) if active]
        self.transition("activated", now, "One simulated command accepted")
        self.released_at = None
        self.transition("waiting_for_release", now, "Held cues cannot repeat")
        return True
