import pytest

from secondhands.recognition.decision_experiments import (
    check_choices,
    check_prediction,
    download_samples,
)


def test_options_must_be_distinct_nonempty_and_bounded():
    assert check_choices(["open palm", "no visible hand"]) == ["open palm", "no visible hand"]
    for options in (["one"], ["one", "one"], ["one", " "], [str(i) for i in range(33)]):
        with pytest.raises(ValueError):
            check_choices(options)


def test_invalid_or_incomplete_model_probabilities_are_rejected():
    options = ["open palm", "no visible hand"]
    for scores in ([float("nan"), 0.2], [0.5], [-0.1, 1.1], [0.2, 0.3]):
        with pytest.raises(ValueError):
            check_prediction({"kind": "choice", "scores": scores}, options)


def test_choice_is_derived_from_scores_not_a_separate_model_claim():
    result = check_prediction({"kind": "choice", "scores": [0.2, 0.8]}, ["palm", "none"])
    assert result["choice"] == "none"
    assert result["scores"] == {"palm": 0.2, "none": 0.8}


def test_generated_text_is_not_converted_to_confidence():
    result = check_prediction({"kind": "text", "text": "Maybe an open palm."}, ["palm", "none"])
    assert result == {"kind": "text", "text": "Maybe an open palm.", "exact_choice": None}


def test_empty_generated_answer_is_not_a_successful_model_result():
    with pytest.raises(ValueError, match="empty"):
        check_prediction({"kind": "text", "text": "  "}, ["palm", "none"])


def test_sample_download_rejects_changed_bytes_and_removes_partial(tmp_path, monkeypatch):
    def altered_download(url, destination):
        destination.write_bytes(b"not the official sample")

    monkeypatch.setattr("urllib.request.urlretrieve", altered_download)
    with pytest.raises(ValueError, match="checksum"):
        download_samples(tmp_path)
    assert list(tmp_path.iterdir()) == []
