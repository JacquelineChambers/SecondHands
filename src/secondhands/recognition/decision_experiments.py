"""Reproducible visual model experiments, separate from live camera commands.

The entry scripts select isolated dependencies. Heavy libraries load only on demand.
"""

import argparse
import contextlib
import hashlib
import json
import math
import os
import platform
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

CACHE = Path("artifacts/huggingface/hub")
OPTIONS = ["thumbs up", "open palm", "closed fist", "other hand pose", "no visible hand"]
QUESTION = "Which visible hand gesture is present?"
CONTEXT = "Describe visible posture only. Do not infer a command or intent."


def download_samples(directory=Path("artifacts")):
    """Download two checksum-pinned public MediaPipe examples, never personal recordings."""
    from tempfile import NamedTemporaryFile
    from urllib.request import urlretrieve

    samples = {
        "portrait.jpg": "a6f11efaa834706db23f275b6115058fa87fc7f14362681e6abe14e82749de3e",
        "thumb_up.jpg": "5d673c081ab13b8a1812269ff57047066f9c33c07db5f4178089e8cb3fdc0291",
    }
    directory.mkdir(parents=True, exist_ok=True)
    for name, expected in samples.items():
        target = directory / name
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == expected:
            continue
        with NamedTemporaryFile(dir=directory, suffix=".part", delete=False) as f:
            partial = Path(f.name)
        try:
            urlretrieve(f"https://storage.googleapis.com/mediapipe-assets/{name}", partial)
            if hashlib.sha256(partial.read_bytes()).hexdigest() != expected:
                raise ValueError(f"Sample checksum mismatch: {name}")
            partial.replace(target)
        finally:
            partial.unlink(missing_ok=True)


@dataclass(frozen=True)
class ModelSpec:
    repository: str
    revision: str
    code_revision: str | None = None


MODELS = {
    "laya": ModelSpec(
        "thaitea/laya-vision-201m",
        "0b6228f7a0762566de1c4539e9aa4eb1c1aef5f4",
        "9e1e2419d855ad3e1a2af4d4bd1ef6be5418842c",
    ),
    "mapika": ModelSpec(
        "Mapika/decider-2b-vision",
        "863e290863655f1d6b69324d77d09ac972d21609",
        "d6fc522aed7fc392576a9b66a330409bc6c382bd",
    ),
    "smolvlm": ModelSpec(
        "HuggingFaceTB/SmolVLM-500M-Instruct",
        "a7da5b986cb59b408707209984f360a5f4ad7e47",
    ),
}


def check_choices(options):
    if not 2 <= len(options) <= 32:
        raise ValueError("Provide between 2 and 32 options")
    if any(not isinstance(x, str) or not x.strip() or len(x) > 160 for x in options):
        raise ValueError("Options must be nonempty strings of at most 160 characters")
    options = [x.strip() for x in options]
    if len({x.casefold() for x in options}) != len(options):
        raise ValueError("Options must be distinct")
    return options


def check_prediction(result, options):
    if result["kind"] == "text":
        text = result["text"].strip()
        if not text:
            raise ValueError("Model returned empty text")
        exact = next((x for x in options if x.casefold() == text.casefold().rstrip(".")), None)
        return {"kind": "text", "text": text, "exact_choice": exact}
    if result["kind"] != "choice":
        raise ValueError("Unknown prediction kind")
    scores = result["scores"]
    if len(scores) != len(options) or any(not math.isfinite(x) or not 0 <= x <= 1 for x in scores):
        raise ValueError("Invalid option probabilities")
    if not math.isclose(sum(scores), 1.0, abs_tol=0.002):
        raise ValueError("Option probabilities must sum to one")
    return {
        "kind": "choice",
        "choice": options[max(range(len(scores)), key=scores.__getitem__)],
        "scores": dict(zip(options, scores, strict=True)),
    }


def snapshot(key, *, download):
    from huggingface_hub import snapshot_download

    spec = MODELS[key]
    return snapshot_download(
        spec.repository,
        revision=spec.revision,
        cache_dir=str(CACHE),
        local_files_only=not download,
        ignore_patterns=["onnx/*", "*.md", ".gitattributes"],
    )


def load_runner(key, device):
    import torch

    torch.set_num_threads(8)
    if device == "auto":
        device = "mps" if torch.backends.mps.is_available() else "cpu"
    if device == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS is unavailable; choose --device cpu")
    path = snapshot(key, download=False)
    dtype = torch.float16 if key == "mapika" and device == "mps" else torch.float32
    details = {}

    if key == "laya":
        import laya

        model = laya.load_vlm(path, device=device, dtype="fp32")

        def predict(image, question, options):
            result = model.predict(
                {"image": image, "context": CONTEXT},
                {"gesture": {"type": "choice", "instructions": question, "criteria": options}},
                strict=True,
            )
            scores = result["answers"]["gesture"]["probabilities"]
            return {"kind": "choice", "scores": [scores[x] for x in options]}

    elif key == "mapika":
        from decider.infer import Example, Q
        from decider.vision import VisionDecisionModel

        model = VisionDecisionModel(path, dtype=dtype, grad_ckpt=False).to(device).eval()
        if device == "mps":
            from decider.mps_ops import patch_mps

            details["mapika_mps_patch"] = bool(patch_mps())

        def predict(image, question, options):
            prepared = model.prepare([(image, Example(CONTEXT, [Q(question, options, 0)]))])
            with torch.inference_mode():
                scores = model.slot_logits(prepared).softmax(-1)[0, : len(options)].cpu().tolist()
            return {"kind": "choice", "scores": scores}

    else:
        from transformers import AutoModelForImageTextToText, AutoProcessor

        processor = AutoProcessor.from_pretrained(
            path,
            do_image_splitting=False,
            size={"longest_edge": 512},
            local_files_only=True,
        )
        model = (
            AutoModelForImageTextToText.from_pretrained(
                path,
                dtype=dtype,
                attn_implementation="sdpa",
                local_files_only=True,
            )
            .to(device)
            .eval()
        )
        details["image_splitting"] = False
        details["image_longest_edge"] = 512
        details["max_new_tokens"] = 32

        def predict(image, question, options):
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {
                            "type": "text",
                            "text": (f"{CONTEXT} {question} Answer one: {', '.join(options)}."),
                        },
                    ],
                }
            ]
            prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
            inputs = processor(text=prompt, images=[image], return_tensors="pt").to(device)
            with torch.inference_mode():
                output = model.generate(**inputs, max_new_tokens=32, do_sample=False)
            text = processor.batch_decode(
                output[:, inputs["input_ids"].shape[1] :],
                skip_special_tokens=True,
            )[0]
            return {"kind": "text", "text": text}

    def synchronize():
        if device == "mps":
            torch.mps.synchronize()

    return (
        predict,
        synchronize,
        {
            "device": device,
            "dtype": str(dtype),
            "cpu_threads": 8,
            **details,
        },
    )


def main(key):
    parser = argparse.ArgumentParser(description=f"Pinned {key} image experiment")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("download", help="Explicitly fetch pinned model files")
    run = commands.add_parser("run", help="Run cached model; does not download weights")
    run.add_argument("images", nargs="+", type=Path)
    run.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    run.add_argument("--question", default=QUESTION)
    run.add_argument("--choice", action="append")
    run.add_argument("--repeats", type=int, default=3)
    run.add_argument("--output", type=Path)
    args = parser.parse_args()
    spec = MODELS[key]
    if args.command == "download":
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        snapshot(key, download=True)
        print(json.dumps({"model": spec.repository, "revision": spec.revision, "downloaded": True}))
        return
    options = check_choices(args.choice or OPTIONS)
    if not 1 <= args.repeats <= 30:
        parser.error("--repeats must be between 1 and 30")
    if any(not image.is_file() for image in args.images):
        parser.error("Every image must be an existing local file")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    from PIL import Image

    start = time.perf_counter()
    with contextlib.redirect_stdout(sys.stderr):
        predict, synchronize, runtime = load_runner(key, args.device)
    synchronize()
    load_ms = (time.perf_counter() - start) * 1000
    results = []
    for image_path in args.images:
        with Image.open(image_path) as opened:
            image = opened.convert("RGB")
        durations, outputs = [], []
        for _ in range(args.repeats + 1):
            synchronize()
            start = time.perf_counter()
            with contextlib.redirect_stdout(sys.stderr):
                result = predict(image, args.question, options)
            synchronize()
            durations.append((time.perf_counter() - start) * 1000)
            outputs.append(check_prediction(result, options))
        results.append(
            {
                "image": image_path.name,
                "sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
                "first_request_ms": durations[0],
                "warm_request_ms": durations[1:],
                "warm_median_ms": statistics.median(durations[1:]),
                "warm_max_ms": max(durations[1:]),
                "output": outputs[-1],
                "outputs_identical": all(x == outputs[0] for x in outputs),
            }
        )
    try:
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        peak_mib = rss / (1024**2 if platform.system() == "Darwin" else 1024)
    except ImportError:
        peak_mib = None
    report = {
        "schema_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "model": spec.repository,
        "revision": spec.revision,
        "code_revision": spec.code_revision,
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runtime": {
            **runtime,
            "python": platform.python_version(),
            "system": platform.system(),
            "machine": platform.machine(),
            "torch": version("torch"),
            "transformers": version("transformers"),
        },
        "load_ms": load_ms,
        "peak_process_rss_mib": peak_mib,
        "question": args.question,
        "context": CONTEXT,
        "choices": options,
        "results": results,
        "timing_scope": (
            "Request includes preprocessing, inference, decoding and device sync; "
            "excludes image file reading and model loading."
        ),
        "scope": (
            "Static image smoke experiment; "
            "not calibrated command intent or a statistical benchmark."
        ),
    }
    text = json.dumps(report, indent=2, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
    print(text)
