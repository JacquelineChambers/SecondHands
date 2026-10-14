# Project direction

The [current proposal](proposal.md) owns the SecondHands vision, demonstration, proposed architecture, and longer-term opportunity. The user supplied it on 2026-10-14 and identified it as the current proposal. This page records its relation to earlier direction and remaining evidence gaps.

## Established user direction

- The current proposal includes Orbbec Astra 2 RGB and depth sensing. This differs from the earlier instruction to use the device's camera and defer the Astra in [exchange 4](SecondHands-conversation.md#exchange-4--camera-hardware-and-model-options). Preserve that earlier instruction as historical context; the latest supplied proposal is recorded in [proposal.md](proposal.md).
- Explore decision models and review their suitability for the Compute PC. The user requests an updated ranking and evidence about ExecuTorch requirements in [exchange 5](SecondHands-conversation.md#exchange-5--decision-model-ranking).
- Use [qc-executorch-guide](https://github.com/aaishikasb/qc-executorch-guide) as the supplied hackathon reference. The user supplies this repository in [exchange 3](SecondHands-conversation.md#exchange-3--hackathon-repository).

The supplied text is the user's current proposal. The assistant's earlier model ranking remains research input; it does not override that proposal or establish a tested implementation.

## Implementation and evidence limits

At the 2026-10-14 import, this repository contained no application, build process, or test suite. The archive preserves five exchanges and is incomplete; see [its import scope](SecondHands-conversation.md#import-scope).

The [Compute Track review](hackathon-compute.md) verifies the published event direction and documented deployment target as of 2026-10-14. It distinguishes those source statements from actual-device evidence and records unresolved event details. The exact allocated PC configuration, Astra 2 compatibility, model compatibility and performance, and acceptance of mixed runtimes remain unverified. Other assistant claims and the proposal's market-size claims remain unchecked research leads. No model was run during this documentation work.

## Questions

### SH-Q-001 — Model and runtime selection

**Open.** Which specific models and deployment paths should implement the decision component? The [current proposal](proposal.md) specifies lightweight PyTorch models through ExecuTorch for continuous recognition and identifies Clef-Flash as a potential, experimental higher-level layer. It does not select the lightweight models or establish a working Clef-Flash deployment.

The [assistant's ranking](SecondHands-conversation.md#exchange-5--decision-model-ranking) proposes Laya Vision 201M first, Mapika Decider 2B Vision second, and Clef-Flash 9B as a stretch experiment. It also proposes SmolVLM-500M as an ExecuTorch investigation. These are prior proposals, not verified deployment options or a new recommendation.

The [pre-Saturday experiment plan](experiments-before-saturday.md) owns the proposed comparison, observations, measurements, and division of effort. Its results would inform this decision. Target-PC execution, licensing, and the [unresolved event details](hackathon-compute.md#unresolved-event-details) remain evidence needed for selection.
