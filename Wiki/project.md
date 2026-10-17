# Project direction

The [current proposal](proposal.md) owns the SecondHands vision, demonstration, proposed architecture, and longer-term opportunity. The user supplied it on 2026-10-14 and identified it as the current proposal. This page records its relation to earlier direction and remaining evidence gaps.

## Established user direction

- On 2026-10-16, the user chose the computer's built-in camera first: develop on the Mac, then test on the supplied Snapdragon PC at the hackathon. Orbbec Astra 2 or a phone camera streaming over Wi-Fi are optional follow-up inputs. This supersedes the Astra-first capture sequence in the preserved [2026-10-14 proposal](proposal.md#how-it-works). The earlier camera-only instruction remains in [exchange 4](SecondHands-conversation.md#exchange-4--camera-hardware-and-model-options).
- Explore decision models and review their suitability for the Compute PC. The user requests an updated ranking and evidence about ExecuTorch requirements in [exchange 5](SecondHands-conversation.md#exchange-5--decision-model-ranking).
- Use [qc-executorch-guide](https://github.com/aaishikasb/qc-executorch-guide) as the supplied hackathon reference. The user supplies this repository in [exchange 3](SecondHands-conversation.md#exchange-3--hackathon-repository).

The supplied text is the user's current proposal. The assistant's earlier model ranking remains research input; it does not override that proposal or establish a tested implementation.

## Implementation and evidence limits

At the 2026-10-14 import, this repository contained no application, build process, or test suite. The archive preserves five exchanges and is incomplete; see [its import scope](SecondHands-conversation.md#import-scope).

The 2026-10-16 setup adds an installable Python package and a Vue UI scaffold, described below. Camera capture, recognition, decision processing, and the UI-to-Python connection are not implemented. The Snapdragon PC will first be available at the hackathon, as confirmed by the user in the same session.

The [Compute Track review](hackathon-compute.md) verifies the published event direction and documented deployment target as of 2026-10-14. It distinguishes those source statements from actual-device evidence and records unresolved event details. The exact allocated PC configuration, Astra 2 compatibility, model compatibility and performance, and acceptance of mixed runtimes remain unverified. Other assistant claims and the proposal's market-size claims remain unchecked research leads. No model was run during this documentation work.

## Development setup

The user requested Python configuration on 2026-10-16 and selected Vue 3, TypeScript, and Vite for the UI. The repository uses one Python package under `src/secondhands/` and one independent frontend package under `ui/`. Python 3.12 is the selected starting version; [the Compute guide](https://github.com/aaishikasb/qc-executorch-guide/blob/9f3aae1f53053729ed28a242643e39feaf38fb9d/Compute/README.md) also specifies Python 3.12 for its optional export workflow. The package layout is scaffolding, not a working recognition application.

### Package responsibilities

- [`src/secondhands/capture/`](../src/secondhands/capture/__init__.py): camera input and recorded observations.
- [`src/secondhands/recognition/`](../src/secondhands/recognition/__init__.py): gesture and facial movement recognition, including model loading for that task.
- [`src/secondhands/decisions/`](../src/secondhands/decisions/__init__.py): decision models and interpretation of observations over time.
- [`src/secondhands/training/`](../src/secondhands/training/__init__.py): PyTorch training, evaluation, and model export. Keep these offline operations separate from live recognition.
- [`src/secondhands/api/`](../src/secondhands/api/__init__.py): the future application interface for the UI. No server framework or protocol is selected or implemented yet.
- [`ui/`](../ui/package.json): Vue components, browser interaction, and presentation. It has its own dependencies and build; it is not included in the Python wheel.

Each Python subpackage currently contains only its package description. Add behavior tests under `tests/` when behavior is implemented; pytest is configured, but there is no test suite yet. Keep experimental scripts outside the live application package when they are added. Local recordings and datasets belong under `data/`, and model weights and exported models under `artifacts/`; both paths are ignored by Git and are not created by setup.

The recommended runtime boundary is for the UI to send commands and display results while Python owns camera capture and inference on the selected machine. This would let the Mac display the Snapdragon PC's results without changing the capture source. That connection remains a proposal for the next implementation step.

### Python commands

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these commands from the repository root. [`pyproject.toml`](../pyproject.toml) defines the package, Ruff, and pytest configuration; [`uv.lock`](../uv.lock) records resolved dependencies. `.python-version` selects Python 3.12.

```sh
uv sync --locked
uv run --locked ruff check src
uv run --locked ruff format --check src
uv build
```

PyTorch and torchvision are an optional `pytorch` extra. Enable it for PyTorch work:

```sh
uv sync --locked --extra pytorch
uv run --locked --extra pytorch python -c "import torch, torchvision; print(torch.__version__, torchvision.__version__)"
```

The default setup installs the Python package and development tools without requiring PyTorch. MediaPipe, decision-model runtimes, and ExecuTorch are not installed by this scaffold. Select their dependencies when integrating each verified execution path. The Mac's PyTorch installation does not establish Windows ARM64 or Qualcomm NPU compatibility.

### UI commands

Use Node.js 22.12 or later and pnpm 10.33.0, as recorded in [`ui/package.json`](../ui/package.json). From the repository root:

```sh
pnpm --dir ui install --frozen-lockfile
pnpm --dir ui dev
```

The Vite command prints the local development URL. The initial page contains the SecondHands title and a description; it has no camera access or Python connection. To type-check and build it:

```sh
pnpm --dir ui build
```

`ui/pnpm-lock.yaml` records frontend dependencies. Python and UI dependencies are managed separately; no JavaScript workspace or additional Python packages are needed for this initial layout.

### Setup verification

Observed on the Apple Silicon Mac on 2026-10-16: Python 3.12.9 imported all six package modules; PyTorch 2.14.1 and torchvision 0.29.1 imported and a CPU tensor calculation returned the expected values. Ruff lint and formatting checks passed. `uv build` produced a source distribution and wheel; the wheel imported successfully in an isolated environment outside the repository. The Vue UI passed `vue-tsc` and its Vite production build.

These checks verify packaging and tooling. No recognition models, cameras, browser interaction, or Windows execution were tested. No behavior tests were added for the scaffold. See [SH-T-018](plan.md#project-setup) for setup completion; recognition and demonstration tasks remain open.

## Questions

### SH-Q-001 — Model and runtime selection

**Open.** Which specific models and deployment paths should implement the decision component? The [current proposal](proposal.md) specifies lightweight PyTorch models through ExecuTorch for continuous recognition and identifies Clef-Flash as a potential, experimental higher-level layer. It does not select the lightweight models or establish a working Clef-Flash deployment.

The [model reference index](references/models/index.md) owns the current five-candidate recommendation and the additional candidates retained from the captured chats. The user requested that reference on 2026-10-16; it records an experiment starting order, not a final runtime selection. The [earlier rankings](SecondHands-conversation.md#exchange-5--decision-model-ranking) remain historical source material. No recognition or decision model has been evaluated in this repository.

The [pre-Saturday experiment plan](experiments-before-saturday.md) owns the proposed comparison, observations, measurements, and division of effort. Its results would inform this decision. Target-PC execution, licensing, and the [unresolved event details](hackathon-compute.md#unresolved-event-details) remain evidence needed for selection.
