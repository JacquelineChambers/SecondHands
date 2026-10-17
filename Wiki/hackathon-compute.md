# Hackathon: Compute Track

SecondHands is in the **Compute Track**, as confirmed by the user. Reviewed on 2026-10-14: the [hackathon repository](https://github.com/aaishikasb/qc-executorch-guide), its root README, the full Compute guide and artifact inventory, and the two public event pages linked below. Repository references are pinned to [commit 9f3aae1](https://github.com/aaishikasb/qc-executorch-guide/commit/9f3aae1f53053729ed28a242643e39feaf38fb9d). This review verifies what those sources publish; it does not verify the supplied PC or execute their commands.

## Published event requirements

The [Luma event page](https://luma.com/executorch-hackathon) describes an ExecuTorch-powered application challenge, teams of 3–5, and one selected track per team. Compute projects target Snapdragon X Elite Copilot+ PCs. A team receives its track's device for event use; that wording does not promise ownership afterward.

Registration is an application requiring acceptance. The published proposal deadline was October 4, with selection announcements scheduled for October 7. These are past application dates, not final-demo deadlines. The page advertises prizes for each track's winning team and GitHub Copilot access; it does not provide a scoring rubric.

**Update, 2026-10-17:** The user supplied a photograph of the attendee guide's judging slide. [Judging criteria](hackathon/judging-criteria.md) now records the five criteria and their 100-point allocation. This resolves the earlier rubric gap; the photograph's partially hidden descriptions remain unavailable.

The [Open Source AI Week event page](https://opensourceaiweek.com/the-hackathon/) gives October 17–18, 2026 at Founder's Inc., 2 Marina Blvd B300, San Francisco, with the closing demo on Sunday. Its stated theme is open models and local, on-device inference.

**Interpretation for SecondHands:** ExecuTorch is a central event expectation. The reviewed pages do not say every model must run through it. They also do not explicitly approve an application combining ExecuTorch with a separate local decision-model runtime. Keep that acceptance question open; do not treat silence as approval.

## Track instructions versus competition rules

The [repository overview](https://github.com/aaishikasb/qc-executorch-guide/blob/9f3aae1f53053729ed28a242643e39feaf38fb9d/README.md) tells attendees to follow their selected track only. Mobile, XR, and IoT instructions are not Compute prerequisites. It says to start with the supplied model/runtime pair; custom compilation is optional. Do not replace missing Compute files with another track's bundle.

Qualcomm AI Hub is optional in this workflow. A model's catalog listing or performance through another runtime does not establish ExecuTorch compatibility. The PC having an NPU also does not make a CPU model use it automatically.

These are deployment instructions, not a published judging rubric or a requirement that SecondHands remain a segmentation application.

## Compute environment

The root guide identifies a Dell Latitude. [Compute target](https://github.com/aaishikasb/qc-executorch-guide/blob/9f3aae1f53053729ed28a242643e39feaf38fb9d/Compute/README.md):

| Item | Documented value |
| --- | --- |
| OS | Windows 11 ARM64 |
| Processor | Snapdragon X Elite |
| ExecuTorch | v1.5.1 |
| QAIRT/QNN | 2.37.0.250724 |
| Chipset target | SC8380XP |
| NPU architecture | Hexagon HTP v73 |

The guide reports a documentation/source check dated October 12, 2026, without executing the Windows/NPU workflow. The exact laptop model, RAM, storage, camera, and installed driver remain unconfirmed for our device.

## Compute deployment and verification

Follow the [attendee journey and testing instructions](https://github.com/aaishikasb/qc-executorch-guide/blob/9f3aae1f53053729ed28a242643e39feaf38fb9d/Compute/README.md):

1. Locate the installed bundle and compatible runtime.
2. Run real prepared inputs; default-input success proves only a smoke test.
3. Display image, segmentation mask, and end-to-end latency.
4. Check reference outputs, another image, and restart behavior.
5. Measure loading, warmed inference, preprocessing, CPU fallback, memory, and sustained thermal/power behavior against a CPU baseline.

Use profiling evidence for NPU delegation; Task Manager utilization alone is insufficient. Keep diagnostic profiling separate from benchmark timings.

## What the track team must supply

The [artifact inventory](https://github.com/aaishikasb/qc-executorch-guide/blob/9f3aae1f53053729ed28a242643e39feaf38fb9d/Compute/artifacts/README.md) says the repository does not contain the Compute bundle. The team must supply its installed location and model-specific instructions, including:

- `dlv3_qnn.pte`, the Windows ARM64 runner/backend, compatible QNN libraries, and v73 DSP files.
- Prepared input tensors and `input_list.txt`, preprocessing, reference results, and mask rendering instructions.
- Model identity/hash, tool versions, input/output specifications, delegation information, and a runner with profiling support.

An incomplete installation should be repaired by the track team. The promised preinstallation is not evidence that our assigned machine already has a usable bundle.

## Unresolved event details

The reviewed public pages do not establish:

- Whether a mixed-runtime design qualifies, or whether all inference must use ExecuTorch.
- Final submission format and cutoff, presentation length, or restrictions on work prepared before the event. The [scoring criteria and weights](hackathon/judging-criteria.md#scoring) are now recorded from the supplied photograph.
- Source-code publication, intellectual-property, or model-license conditions for submission.
- Permission and support for our external [Femto Bolt](hardware/femto-bolt.md), Arduino, and actuator hardware.
- The exact allocated PC configuration and bundle location.

These are evidence gaps, not additional rules. Resolve them through the organizers' published updates or a direct clarification when authorized. The [Luma page](https://luma.com/executorch-hackathon) provides the host contact and event Discord route. No organizer was contacted during this review.

## Effect on SecondHands

The [task plan](plan.md) owns follow-up work. SH-T-001 now has a source-backed guide review but remains open for the unresolved details above. SH-T-009 remains the actual-device baseline check. The [current proposal](proposal.md) and [model selection Question](project.md#sh-q-001--model-and-runtime-selection) retain their existing status; this review does not approve a different architecture or establish a working model deployment.
