"""Export the pinned pretrained gesture network using the prepared native ARM64 environment."""

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import sys
import sysconfig
import urllib.request
from pathlib import Path

SOURCE_COMMIT = "70b5aeeec774d188465cac561d07cac0d022ce29"
SOURCE_URL = (
    f"https://raw.githubusercontent.com/qualcomm/ai-hub-models/{SOURCE_COMMIT}/"
    "src/qai_hub_models/models/mediapipe_hand_gesture/model.py"
)
SOURCE_SHA256 = "9b9855532bf33c74224b97a44cb87086fed9fe7d1761cc88aee52472a7b29d3c"


def load_model_class(work):
    source = work / "build-sources/gesture-model-70b5aeee.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    if not source.is_file():
        with urllib.request.urlopen(SOURCE_URL, timeout=30) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
            raise ValueError("Upstream gesture source checksum mismatch")
        source.write_bytes(data)
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("Cached gesture source checksum mismatch")
    classes = []
    for node in ast.parse(source.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.ClassDef) and node.name in (
            "_InnerGestureMLP",
            "CannedGestureClassifier",
        ):
            node.bases = [ast.parse("nn.Module", mode="eval").body]
            node.body = [
                item
                for item in node.body
                if isinstance(item, ast.Expr)
                or isinstance(item, ast.FunctionDef)
                and item.name in ("__init__", "_init_weights", "forward")
            ]
            classes.append(ast.unparse(node))
    generated = work / "gesture_model_pinned.py"
    generated.write_text(
        "# Copyright (c) 2025 Qualcomm Technologies, Inc. and/or its subsidiaries.\n"
        "# SPDX-License-Identifier: BSD-3-Clause\n"
        f"# Extracted neural methods from {SOURCE_URL}\n"
        "import torch\nfrom torch import nn\nimport torch.nn.functional as F\n\n"
        + "\n\n".join(classes),
        encoding="utf-8",
    )
    spec = importlib.util.spec_from_file_location("gesture_model_pinned", generated)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.CannedGestureClassifier


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "artifacts/qnn",
    )
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    work = args.work_dir.resolve()
    out = (args.output_dir or work / "gesture").resolve()
    if sysconfig.get_platform() != "win-arm64":
        parser.error("Use the prepared native ARM64 Python interpreter")
    sdk = work / "qairt/2.37.0.250724"
    libraries = sdk / "lib/aarch64-windows-msvc"
    os.environ["PATH"] = str(libraries) + os.pathsep + os.environ["PATH"]
    os.environ["ADSP_LIBRARY_PATH"] = str(sdk / "lib/hexagon-v73/unsigned")
    os.environ["QNN_SDK_ROOT"] = str(sdk)
    os.environ["FLATC_EXECUTABLE"] = str(work / "aot-python/executorch/data/bin/flatc.exe")
    handles = [os.add_dll_directory(str(p)) for p in (libraries, work / "build-stream")]
    sys.path.insert(0, str(work / "aot-python"))

    import executorch.backends.qualcomm.python.PyQnnManagerAdaptor as binding
    import executorch.backends.qualcomm.utils.check_qnn_version as version
    import torch
    from executorch.backends.qualcomm.serialization.qc_schema import QcomChipset
    from executorch.backends.qualcomm.utils.utils import (
        generate_htp_compiler_spec,
        generate_qnn_executorch_compiler_spec,
        to_edge_transform_and_lower_to_qnn,
    )

    # Upstream's version helper assumes an x64 host-library directory.
    version._get_sdk_build_id = lambda _: binding.GetQnnSdkBuildId(str(libraries / "QnnHtp.dll"))
    sdk_build = version.get_sdk_build_id()
    if not sdk_build.startswith("v2.37.0."):
        raise RuntimeError(f"Unexpected QNN SDK: {sdk_build}")
    model = load_model_class(work)().eval()
    weights, weight_hashes = {}, {}
    for name in ("gesture_embedder.pth", "gesture_classifier.pth"):
        path = work.parent / "models/mediapipe-hand-gesture" / name
        weights.update(torch.load(path, map_location="cpu", weights_only=True))
        weight_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if weights.pop("center_idx").tolist() != [0, 1, 5, 9, 13, 17]:
        raise ValueError("Unexpected landmark center indices")
    if weights.pop("x_mirror").tolist() != [[[-1.0, 1.0, 1.0]]]:
        raise ValueError("Unexpected mirror transform")
    model.load_state_dict(weights, strict=True)
    torch.manual_seed(123)
    inputs = (torch.rand(1, 64), torch.rand(1, 64))
    out.mkdir(parents=True, exist_ok=True)
    with torch.inference_mode():
        model(*inputs).numpy().tofile(out / "reference.raw")
    for index, tensor in enumerate(inputs):
        tensor.numpy().tofile(out / f"input_{index}.raw")
    specs = generate_qnn_executorch_compiler_spec(
        QcomChipset.SC8380XP,
        generate_htp_compiler_spec(use_fp16=True),
    )
    edge = to_edge_transform_and_lower_to_qnn(model, inputs, specs)
    calls = [n for n in edge.exported_program().graph.nodes if n.op == "call_function"]
    delegates = [n for n in calls if "executorch_call_delegate" in str(n.target)]
    if len(delegates) != 1 or any(
        n not in delegates and str(n.target) != "<built-in function getitem>" for n in calls
    ):
        raise RuntimeError("Gesture graph was not fully delegated to QNN")
    program = edge.to_executorch()
    path = out / "gesture_qnn.pte"
    path.write_bytes(program.buffer)
    manifest = {
        "model": "Qualcomm MediaPipe pretrained gesture embedder and classifier",
        "source": SOURCE_URL,
        "source_sha256": SOURCE_SHA256,
        "weights": weight_hashes,
        "executorch": "1.5.1",
        "torch": torch.__version__,
        "qnn_build": sdk_build,
        "platform": sysconfig.get_platform(),
        "chipset": "SC8380XP",
        "precision": "FP16",
        "qnn_delegates": 1,
        "cpu_compute_nodes": 0,
        "model_bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "inputs": [[1, 64], [1, 64]],
        "outputs": [[1, 8]],
        "reference_input": "synthetic; real-image validation is separate",
    }
    (out / "export.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    for handle in handles:
        handle.close()


if __name__ == "__main__":
    main()
