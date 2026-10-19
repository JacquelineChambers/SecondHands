"""JSON-compatible observations; scores do not establish user intent."""


def _landmarks(points):
    return [{"x": p.x, "y": p.y, "z": p.z} for p in points]


def _categories(categories):
    return [{"label": c.category_name, "score": c.score} for c in categories]


def frame_result(face, hand, *, timestamp_ms, width, height, face_ms, hand_ms, hand_gestures=None):
    """Convert task outputs. Timings cover synchronous task calls only."""
    return {
        "schema_version": 1,
        "model": "mediapipe-face-and-gesture",
        "timestamp_ms": timestamp_ms,
        "image": {"width": width, "height": height},
        "timing_ms": {"face": face_ms, "hand": hand_ms, "total": face_ms + hand_ms},
        "faces": [
            {
                "landmarks": _landmarks(points),
                "blendshapes": {c.category_name: c.score for c in shapes},
            }
            for points, shapes in zip(face.face_landmarks, face.face_blendshapes, strict=True)
        ],
        "hands": [
            {
                "landmarks": _landmarks(points),
                "handedness": _categories(side),
                "gestures": _categories(gestures),
            }
            for points, side, gestures in zip(
                hand.hand_landmarks,
                hand.handedness,
                hand.gestures if hand_gestures is None else hand_gestures,
                strict=True,
            )
        ],
    }
