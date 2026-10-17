"""Session state stays on the event loop; camera work returns immutable observations."""

from collections import deque
from dataclasses import asdict
from statistics import mean
from uuid import uuid4

from secondhands.decisions.triggers import Mapping, TriggerEngine

MODELS = [
    {"name": "MediaPipe Face Landmarker", "available": True, "runtime": "MediaPipe CPU"},
    {"name": "MediaPipe Gesture Recognizer", "available": True, "runtime": "MediaPipe CPU"},
    {"name": "Laya Vision 201M", "available": False, "runtime": "Not integrated"},
    {"name": "Mapika Decider 2B Vision", "available": False, "runtime": "Not integrated"},
    {"name": "SmolVLM-500M-Instruct", "available": False, "runtime": "Not integrated"},
]


class DashboardSession:
    def __init__(self):
        self.id = uuid4().hex
        self.version = 1
        self.running = True
        self.simulate = False
        self.lamp = False
        self.frame_id = 0
        self.latest = None
        self.mapping = Mapping()
        self.engine = TriggerEngine(self.mapping)
        self.history = deque(maxlen=100)
        self.calibration = {"neutral": deque(maxlen=120), "deliberate": deque(maxlen=120)}
        self.collecting = None
        self.remaining = 0

    @property
    def token(self):
        return self.id, self.version

    def configure(self, settings, simulate):
        mapping = Mapping(**settings)
        if type(simulate) is not bool:
            raise ValueError("Simulation must be true or false")
        self.mapping = mapping
        self.simulate = simulate
        self.version += 1
        self.engine = TriggerEngine(mapping)
        self.latest = None
        self.collecting = None
        self.remaining = 0
        for samples in self.calibration.values():
            samples.clear()
        self.note("configured", "Mapping changed; pending evidence and calibration cleared")

    def note(self, state, reason):
        self.history.append(
            {
                "id": uuid4().hex,
                "state": state,
                "reason": reason,
                "frame_id": self.frame_id,
                "mapping_version": self.version,
            }
        )

    def stop(self):
        self.running = False
        self.version += 1
        self.simulate = False
        self.latest = None
        self.collecting = None
        self.remaining = 0
        for samples in self.calibration.values():
            samples.clear()
        self.engine = TriggerEngine(self.mapping)
        self.note("stopped", "Camera stopped; pending commands and calibration cleared")

    def cancel(self):
        self.version += 1
        self.latest = None
        self.engine.cancel(self.engine.last_time or 0)
        self.note("cancelled", "Pending command cancelled; release required")

    def calibrate(self, label):
        if label not in self.calibration:
            raise ValueError("Calibration label must be neutral or deliberate")
        self.version += 1
        self.simulate = False
        self.engine = TriggerEngine(self.mapping)
        self.latest = None
        self.collecting = label
        self.remaining = 30
        self.calibration[label].clear()
        self.note("calibrating", f"Collecting 30 {label} samples; simulation disabled")

    def signals(self, observation):
        faces, hands = observation["faces"], observation["hands"]
        face = faces[0]["blendshapes"].get(self.mapping.face_signal) if faces else None
        # Two hands can belong to different people; fail closed for command experiments.
        hand = (
            max(
                (
                    g["score"]
                    for g in hands[0]["gestures"]
                    if g["label"] == self.mapping.hand_gesture
                ),
                default=0.0,
            )
            if len(hands) == 1
            else None
        )
        return face, hand

    def accept(self, token, observation, jpeg, captured_ms, processing_ms, capture_ms):
        if not self.running or token != self.token:
            return None
        self.frame_id += 1
        face, hand = self.signals(observation)
        available = {
            "face": face is not None,
            "hand": hand is not None,
            "either": face is not None or hand is not None,
            "combined": face is not None and hand is not None,
            "sequence": face is not None and hand is not None,
        }[self.mapping.mode]
        if self.collecting and available:
            self.calibration[self.collecting].append((face, hand))
            self.remaining -= 1
            if not self.remaining:
                self.note("calibrated", f"Collected {self.collecting} samples")
                self.collecting = None
        last_event = self.engine.event_id
        if self.simulate and self.engine.update(captured_ms, face, hand):
            self.lamp = not self.lamp
        for event in self.engine.events:
            if event["id"] > last_event:
                self.note(event["state"], event["reason"])
        self.latest = {
            "type": "frame",
            "session_id": self.id,
            "frame_id": self.frame_id,
            "mapping_version": self.version,
            "captured_ms": captured_ms,
            "processing_ms": processing_ms,
            "capture_ms": capture_ms,
            "preview": "data:image/jpeg;base64," + jpeg,
            "recognition": observation,
            "signals": {"face": face, "hand": hand},
            **self.status(),
        }
        return self.latest

    def calibration_summary(self):
        result = {"collecting": self.collecting, "remaining": self.remaining}
        for label, samples in self.calibration.items():
            result[label] = {"count": len(samples), "face_mean": None, "hand_mean": None}
            for i, signal in enumerate(("face", "hand")):
                values = [s[i] for s in samples if s[i] is not None]
                result[label][signal + "_mean"] = mean(values) if values else None
        for i, signal in enumerate(("face", "hand")):
            neutral = [s[i] for s in self.calibration["neutral"] if s[i] is not None]
            deliberate = [s[i] for s in self.calibration["deliberate"] if s[i] is not None]
            suggestion = None
            if neutral and deliberate:
                low, high = max(neutral), min(deliberate)
                if high - low >= 0.1:
                    suggestion = {
                        "release": low + (high - low) * 0.25,
                        "activate": low + (high - low) * 0.75,
                    }
            result[signal + "_suggestion"] = suggestion
        return result

    def status(self):
        return {
            "session_id": self.id,
            "mapping_version": self.version,
            "running": self.running,
            "simulate": self.simulate,
            "lamp": self.lamp,
            "state": self.engine.state if self.simulate else "observing",
            "mapping": asdict(self.mapping),
            "events": list(self.history),
            "calibration": self.calibration_summary(),
            "models": MODELS,
        }

    def compare(self):
        if self.latest is None:
            raise ValueError("Capture a current frame before comparison")
        return {
            **self.latest,
            "type": "comparison",
            "note": "Frozen results from the same frame; no extra inference run. "
            "Task times exclude model loading and camera/transport/display time.",
        }
