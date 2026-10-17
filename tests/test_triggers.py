from secondhands.decisions.triggers import Mapping, TriggerEngine


def make(**kwargs):
    return TriggerEngine(Mapping(hold_ms=100, release_ms=50, cooldown_ms=100, **kwargs))


def feed(engine, time, face=0.0, hand=0.0):
    return engine.update(time, face, hand)


def test_hold_hysteresis_and_release_prevent_repeat():
    e = make(mode="face")
    assert not feed(e, 0, 0.9)
    assert feed(e, 100, 0.7)
    assert not feed(e, 300, 0.9)
    assert not feed(e, 400, 0.4)
    assert not feed(e, 450, 0.2)
    assert not feed(e, 500, 0.2)
    assert not feed(e, 510, 0.9)
    assert feed(e, 610, 0.9)


def test_missing_input_cancels_hold_and_requires_release():
    e = make(mode="face")
    feed(e, 0, 0.9)
    feed(e, 90, None)
    assert not feed(e, 200, 0.9)
    feed(e, 250, 0)
    feed(e, 300, 0)
    feed(e, 310, 0.9)
    assert feed(e, 410, 0.9)


def test_either_fires_once_for_simultaneous_cues():
    e = make(mode="either")
    feed(e, 0, 0.9, 0.9)
    assert feed(e, 100, 0.9, 0.9)
    assert not feed(e, 200, 0.9, 0.9)


def test_combined_requires_overlap_window():
    e = make(mode="combined", overlap_ms=100)
    feed(e, 0, 0.9, 0)
    feed(e, 200, 0.9, 0.9)
    assert not feed(e, 400, 0.9, 0.9)
    feed(e, 500, 0, 0)
    feed(e, 600, 0.9, 0.9)
    assert feed(e, 700, 0.9, 0.9)


def test_sequence_needs_new_confirmation_edge_not_held_face():
    e = make(mode="sequence", timeout_ms=500)
    feed(e, 0, 0.9, 0.9)
    assert not feed(e, 100, 0.9, 0.9)
    assert e.state == "awaiting_confirmation"
    assert not feed(e, 200, 0.9, 0.9)
    feed(e, 210, 0, 0.9)
    assert feed(e, 220, 0.9, 0.9)


def test_sequence_timeout_and_cancel_cannot_activate():
    e = make(mode="sequence", timeout_ms=200)
    feed(e, 0, 0, 0.9)
    feed(e, 100, 0, 0.9)
    assert not feed(e, 301, 0.9, 0.9)
    assert e.state == "waiting_for_release"
    e = make(mode="sequence")
    feed(e, 0, 0, 0.9)
    feed(e, 100, 0, 0.9)
    e.cancel(110)
    assert not feed(e, 120, 0.9, 0.9)


def test_time_gap_resets_candidate_and_events_are_bounded():
    e = make(mode="face", max_gap_ms=200)
    feed(e, 0, 0.9)
    assert not feed(e, 1000, 0.9)
    for i in range(1, 300):
        e.cancel(1000 + i)
    assert len(e.events) <= 100


def test_invalid_threshold_order_is_rejected():
    import pytest

    with pytest.raises(ValueError):
        Mapping(activate=0.2, release=0.8)


def test_either_accepts_one_visible_modality_but_loss_is_not_release():
    for face, hand in ((0.9, None), (None, 0.9)):
        e = make(mode="either")
        feed(e, 0, face, hand)
        assert feed(e, 100, face, hand)
        assert not feed(e, 200, None, None)
        assert not feed(e, 300, face, hand)
        assert not feed(e, 400, face, hand)
        feed(e, 500, 0 if face else None, 0 if hand else None)
        feed(e, 550, 0 if face else None, 0 if hand else None)
        feed(e, 600, face, hand)
        assert feed(e, 700, face, hand)
