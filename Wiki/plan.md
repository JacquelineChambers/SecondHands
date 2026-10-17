# SecondHands task plan

This is the task-tracking owner selected by the user on 2026-10-14. The sequence below is proposed from the [current proposal](proposal.md), [experiment plan](experiments-before-saturday.md), and [project evidence gaps](project.md#implementation-and-evidence-limits), with the 2026-10-16 camera decision recorded in [Project direction](project.md#established-user-direction). Completed tasks need the evidence specified below. Owners are not yet assigned.

Keep task status, blockers, and verification links here. Check a task only when its completion evidence is available. Product decisions remain in their owning topic; this checklist does not settle open design choices or authorize execution of every task.

## Project setup

- [x] **SH-T-018 — Configure the Python project and UI package.** Requested on 2026-10-16; the user selected Vue 3, TypeScript, and Vite. Added the Python package layout, uv dependency locking, optional PyTorch dependencies, development tools, and an independent Vue UI scaffold. [Setup verification](project.md#setup-verification) records package imports, a PyTorch CPU calculation, Python distribution builds, Ruff checks, and UI type checking and production build on the Mac. This completes configuration only; camera capture, model integration, the API connection, and Windows verification remain unimplemented or untested.

## Reference review

- [x] **SH-T-019 — Record model references and review captured model mentions.** Requested on 2026-10-16. Added the [model reference index](references/models/index.md), five detail pages for the supplied starting recommendation, and additional candidates from the full captured conversation. Recorded historical limits and the absence of explicit user exclusions in that capture. Updated navigation, source dispositions, and the model-selection Question's reference. Local links, heading targets, and Markdown whitespace were checked. No model was installed or evaluated by this documentation task.

## Before Saturday, October 17

- [ ] **SH-T-001 — Confirm the Compute environment and event requirements.** Published-source review completed on 2026-10-14 in [the Compute Track summary](hackathon-compute.md). Remaining work: confirm the allocated PC configuration, bundle location, mixed-runtime acceptance, and other [unresolved event details](hackathon-compute.md#unresolved-event-details). Done when those findings or explicit organizer deferrals are recorded in that owner. This source review alone does not complete the task.
- [ ] **SH-T-002 — Define the demonstration and acceptance criteria.** Select the physical object, the two volunteers' movements, and the expected confirmation and failure behavior for the [proposed demonstration](proposal.md#the-hackathon-demonstration). Agree how response time and false activations will be judged. Done when the intended behavior and examples are recorded and approved in the owning project topic; do not invent numerical thresholds from model benchmarks.
- [ ] **SH-T-003 — Establish local camera capture.** Use the Mac's built-in camera first, following the [2026-10-16 camera decision](project.md#established-user-direction). Record usable inputs and compatibility limits. Done when repeatable sample capture works; otherwise leave it unchecked and record the blocker. Astra 2 and a phone camera streaming over Wi-Fi are optional follow-up inputs.
- [ ] **SH-T-004 — Collect and label the comparison observations.** After capture works, prepare the shared observations specified by the [experiment plan](experiments-before-saturday.md#models-and-observations). Done when the two-volunteer set includes deliberate, neutral, and ambiguous movements with labels that can be reused across models.
- [ ] **SH-T-005 — Prepare a repeatable model comparison.** Establish local execution for the three experiment candidates and a common way to supply observations and record the [measurements](experiments-before-saturday.md#measurements). Done when each candidate has a reproducible invocation or a documented compatibility blocker, with model/runtime versions recorded.
- [ ] **SH-T-006 — Run the Mac experiments.** Use the same labeled set for each runnable candidate. Done when measured results and limitations are recorded on the [experiment page](experiments-before-saturday.md), separately from the proposed method. Record failed or unsupported runs explicitly.
- [ ] **SH-T-007 — Review the results and choose the initial integration candidate.** Use SH-T-001 and SH-T-006 to inform [SH-Q-001](project.md#sh-q-001--model-and-runtime-selection). Done when the choice, reasons, and remaining target-PC checks are recorded there. A provisional Mac choice must remain labeled provisional.
- [ ] **SH-T-008 — Establish physical control independently.** Using the object and behavior agreed in SH-T-002, test the microcontroller and actuator with an explicit manual command. Done when the intended action and agreed failure behavior can be demonstrated without a model in the loop. This can proceed alongside the model comparison.

## Saturday: verify the supplied PC

- [ ] **SH-T-009 — Run the supplied ExecuTorch demonstration.** Record the actual PC configuration and locate the supplied DeepLab model and matching runner. Done when the demonstration runs and its output is inspected. Distinguish a default-input smoke test from a real-image result; claim accelerator use only with supporting evidence.
- [ ] **SH-T-010 — Verify camera and candidate execution on the PC.** Test the capture path and initial candidate selected above on the actual device. Done when representative inputs produce inspected outputs and measured latency/memory results; otherwise leave it unchecked and record the blockers. Revisit [SH-Q-001](project.md#sh-q-001--model-and-runtime-selection) if the Mac choice cannot be deployed.

SH-T-009 establishes the supplied framework baseline. SH-T-010 establishes the application's target-device feasibility; neither task alone proves the integrated demonstration works.

## Build and verify the demonstration

- [ ] **SH-T-011 — Implement personalized calibration.** Build the calibration flow against the movements and behavior agreed in SH-T-002, using the verified capture/model path. Done when the two volunteers can establish different movement mappings for the same action and those mappings can be exercised independently.
- [ ] **SH-T-012 — Connect recognition, confirmation, and physical action.** Integrate SH-T-008 with SH-T-011 using the agreed confirmation and failure behavior. Done when deliberate, neutral, and ambiguous examples exercise the real path from camera input to actuator, with outcomes compared against the agreed examples.
- [ ] **SH-T-013 — Add the live demonstration interface.** Display the movement, action, confirmation status, and measured response latency specified in the [proposal](proposal.md#the-hackathon-demonstration). Done when these values come from the running application, with the latency measurement boundaries stated.
- [ ] **SH-T-014 — Rehearse the two-volunteer demonstration.** Run the same physical action using each volunteer's personalized movement. Done when the agreed acceptance criteria are evaluated on the target PC, results and failures are recorded, and local operation without cloud transmission of camera data is checked.
- [ ] **SH-T-015 — Prepare the presentation and evidence.** Use the observed demonstration to explain adaptive calibration, the actual ExecuTorch contribution, measured performance, and remaining limits. Done when the presentation separates demonstrated capabilities from experiments and future proposals, and externally sourced claims used in it have supporting references.

## Optional experiments

These tasks are separate from the initial demonstration sequence. Keep their results in the [experiment topic](experiments-before-saturday.md) and any selection decision in [SH-Q-001](project.md#sh-q-001--model-and-runtime-selection).

- [ ] **SH-T-016 — Evaluate Clef-Flash as the higher-level decision layer.** Test the role described in the [current proposal](proposal.md#how-it-works), subject to actual memory and runtime support. Done when a bounded comparison has recorded results or a deployment blocker. Its experimental status does not make it a prerequisite for the continuous recognition path.
- [ ] **SH-T-017 — Investigate the proposed SmolVLM-500M ExecuTorch path.** Verify the deployment claim from the earlier [model review](SecondHands-conversation.md#exchange-5--decision-model-ranking) against current primary documentation and the supplied environment before attempting a port. Done when feasibility and the effort required are recorded, with any execution result distinguished from documentation evidence.
