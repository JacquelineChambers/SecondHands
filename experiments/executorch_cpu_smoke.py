# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["executorch==1.5.1", "torch==2.14.1"]
# ///
"""Check PyTorch -> XNNPACK export -> ExecuTorch CPU output agreement.

Uses an untrained network and synthetic inputs, not a gesture recognition model.
Run from the repository root with `just smoke-executorch`.
"""

import argparse
import json
import platform
from importlib.metadata import version
from pathlib import Path

import torch
from executorch.backends.xnnpack.partition.xnnpack_partitioner import XnnpackPartitioner
from executorch.exir import to_edge_transform_and_lower
from executorch.runtime import Runtime


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/executorch/synthetic_head_xnnpack.pte")
    )
    args = parser.parse_args()

    torch.manual_seed(0)
    torch.set_num_threads(1)
    model = torch.nn.Sequential(
        torch.nn.Linear(52, 16), torch.nn.ReLU(), torch.nn.Linear(16, 3)
    ).eval()
    samples = [torch.zeros(1, 52), torch.ones(1, 52)]
    samples.extend(torch.rand(1, 52) for _ in range(10))
    program = to_edge_transform_and_lower(
        torch.export.export(model, (samples[0],)), partitioner=[XnnpackPartitioner()]
    ).to_executorch()
    delegates = [d.id for d in program.executorch_program.execution_plan[0].delegates]
    if "XnnpackBackend" not in delegates:
        raise RuntimeError(f"No XNNPACK delegate in exported program: {delegates}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(program.buffer)
    loaded = Runtime.get().load_program(str(args.output))
    method = loaded.load_method("forward")
    max_error = 0.0
    with torch.inference_mode():
        for sample in samples:
            expected = model(sample)
            actual = method.execute([sample])[0]
            torch.testing.assert_close(actual, expected, rtol=1e-4, atol=1e-6)
            max_error = max(max_error, (actual - expected).abs().max().item())

    print(
        json.dumps(
            {
                "status": "passed",
                "platform": f"{platform.system()} {platform.machine()}",
                "executorch": version("executorch"),
                "torch": version("torch"),
                "model": "untrained 52-16-3 MLP; synthetic inputs only",
                "backend": delegates,
                "samples_checked": len(samples),
                "max_absolute_error": max_error,
                "artifact": args.output.as_posix(),
                "artifact_bytes": args.output.stat().st_size,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
