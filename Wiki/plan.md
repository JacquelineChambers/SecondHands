# SecondHands plan

Updated 2026-10-18 at the user's request. This is the single task tracker, organized by topic and phase. Checked tasks have implementation or verification evidence; their stated limits still apply. Unchecked tasks are remaining work or explicitly marked proposals, not blanket approval to implement every option.

Current position: all five starting candidates execute on the Mac. The two MediaPipe bundles feed the original exploration dashboard; Laya Vision, Mapika, and SmolVLM run as separate image experiments. Those image experiments expose false face classifications from Laya and SmolVLM. On the Snapdragon PC, the [Orbbec CLI](setup/orbbec-mediapipe.md) now executes CPU landmarks and NPU gesture classification, and the [scene application](setup/scene-understanding.md) combines CPU MediaPipe, YOLOv5s, and JEVision with verified live API operation and Stop/restart. Rendered-browser inspection of the new scene mode, comparative accuracy, and full deployment validation remain open. A separate [local depth bridge and person application](setup/ms-09-femto-bolt-bridge.md) passed initial Snapdragon tests, with a later capture timeout still unresolved. Detailed behavior stays in [the design](design/index.md) and the linked experiment/setup owners.

## Team coordination

The user requested these GitHub work items on 2026-10-17. Use the issues for named team coordination and this plan for the detailed project checklist. Issue descriptions contain the requested owners; only confirmed GitHub accounts receive formal assignments.

| Workstream | GitHub issue |
| --- | --- |
| Hackathon stack review | [Review the stack and Snapdragon deployment path](https://github.com/davidmoshal/SecondHands/issues/1) |
| Femto Bolt hardware | [Windows laptop first, then Dell Snapdragon](https://github.com/davidmoshal/SecondHands/issues/2) |
| Model evaluation | [Evaluate five local candidates](https://github.com/davidmoshal/SecondHands/issues/3) |
| UI | [Review and extend the dashboard](https://github.com/davidmoshal/SecondHands/issues/4) |
| Presentation | [Confirm the lead and prepare the presentation](https://github.com/davidmoshal/SecondHands/issues/5) |
| 3D room simulation | [Build the browser room with optional Quest 2 WebXR viewing](https://github.com/davidmoshal/SecondHands/issues/6) |
| Clinical application | [Define the clinical application — Kate](https://github.com/davidmoshal/SecondHands/issues/7) |
| Laptop remote access | [Set up Tailscale — Vishwa](https://github.com/davidmoshal/SecondHands/issues/9) |

- [ ] **SH-T-041 — Resolve the Dell camera path.** [SH-Q-002](hardware/femto-bolt.md#sh-q-002--which-capture-path-works-on-the-dell) is partially resolved by the local bridge. Record sustained capture, timeout diagnosis, reconnect/reboot recovery, measured distance accuracy, and application integration evidence before closing the remaining scope.
- [ ] **SH-T-042 — Confirm GitHub owner accounts.** Resolve [SH-Q-003](project.md#sh-q-003--github-accounts-for-the-named-owners) before assigning unverified accounts or changing repository access.
- [ ] **SH-T-043 — Confirm the presentation lead.** Resolve [SH-Q-004](project.md#sh-q-004--presentation-lead); Kate remains proposed.
- [ ] **SH-T-046 — Define the clinical application.** Kate owns [issue #7](https://github.com/davidmoshal/SecondHands/issues/7). Record the intended application and agreed requirements, then connect them to model evaluation, UI, and demonstration work. [Project direction](project.md#established-user-direction) records the confirmed role; presentation ownership remains separate.

## Project setup

**Phase 1: Mac foundation.**

- [x] **SH-T-018 — Configure Python and Vue packages.** Python 3.12, uv locking, optional PyTorch dependencies, and the original Vue 3/TypeScript/Vite scaffold were configured. SH-T-047 supersedes the frontend selection. [Setup checks](project.md#setup-verification) passed on the Mac.
- [x] **SH-T-021 — Add just commands.** Setup, model download, image/camera inference, dashboard services, tests, and the ExecuTorch smoke check are exposed through the [justfile](../justfile).
- [x] **SH-T-020 — Document shared Mac/PC development.** [The runbook](runbooks/mac-and-snapdragon-development.md) covers separate environments, Git synchronization, T3 execution context, and known Windows dependency limits. Remote connection and PC execution remain untested.

## Models

**Phase 2: establish about five runnable candidates on the Mac before porting.** The first completed baseline below contains two recognition bundles; the other three are separate integrations. A compatibility blocker must be recorded and does not count as a working model.

### Reference review

- [x] **SH-T-019 — Record model references.** [The model index](references/models/index.md) contains the top five, individual detail pages, and other retained candidates from the captured chats.

### Mac integrations

- [x] **SH-T-023 — Integrate MediaPipe Face Landmarker and Gesture Recognizer.** Both run on public sample images, with checked downloads, structured results, image/camera CLIs, and dashboard integration. [Observed results](experiments-before-saturday.md#mediapipe-baseline-observations); physical-camera use and participant accuracy remain untested.
- [x] **SH-T-026 — Integrate Laya Vision 201M.** The isolated CLI loads pinned weights, answers configurable image questions on Mac MPS and CPU, and records runtime, latency, memory, and failures. [Observed results](experiments-before-saturday.md#decision-model-image-observations) include an incorrect face classification. Dashboard integration and participant accuracy remain open.
- [x] **SH-T-027 — Integrate Mapika Decider 2B Vision.** The isolated CLI runs pinned weights on Mac MPS, with its MPS patch active. [The same image questions](experiments-before-saturday.md#decision-model-image-observations) establish output and cost differences from Laya; the participant benchmark, dashboard integration, and Windows path remain unverified.
- [x] **SH-T-028 — Integrate SmolVLM-500M-Instruct locally.** The isolated CLI executes pinned weights on Mac MPS and records image-conditioned text, runtime, latency, and memory. [Observed results](experiments-before-saturday.md#decision-model-image-observations) include an incorrect face classification. Generated text is not a typed decision score; dashboard integration and an ExecuTorch port remain separate work.

## Recognition features

**Phase 3: turn observations into configurable command experiments.** Implemented features below are deterministic logic over MediaPipe measurements, not validated intention recognition.

- [x] **SH-T-029 — Implement configurable trigger rules.** Face, hand, either, combined, and hand-then-face sequence modes include hold, hysteresis, confirmation timeout, cancellation, release, and cooldown. [Trigger behavior and limits](design/recognition-and-triggers.md#trigger-policy).
- [x] **SH-T-030 — Implement session calibration.** Collect neutral/deliberate measurements, show signal separation, and suggest an experimental threshold pair. Collection disables simulation; data stays in memory.
- [x] **SH-T-031 — Bound work and reject old results.** One camera owner, one frame job, session/frame/mapping identity, invalidation after control changes, and cleanup on Stop/disconnect are implemented and [tested](experiments-before-saturday.md#dashboard-implementation-observations).
- [ ] **SH-T-040 — Connect a decision model to candidate events.** Supply selected images, context, and configurable choices after a possible command is detected. Bound outstanding requests and reject expired decisions; do not require a large model on every frame.
- [ ] **SH-T-032 — Investigate independent face/hand thresholds.** Proposed improvement: current mappings share one activation/release pair, so applying one modality's calibration replaces that pair for both cues.
- [ ] **SH-T-033 — Add temporal movement experiments.** After selecting a movement such as nodding, test observations over time. MediaPipe video tracking alone does not implement movement-sequence recognition.
- [ ] **SH-T-011 — Validate personalized calibration with two participants.** The generic calibration flow exists; still demonstrate distinct usable movements mapped to the same action, against agreed criteria.

## UI

**Phase 4: let the team inspect capabilities and try command mappings.**

- [x] **SH-T-047 — Migrate the dashboard to React and Bun.** Completed the user-requested [issue #11](https://github.com/davidmoshal/SecondHands/issues/11) implementation with the same Python API, controls, and layout. Bun replaces pnpm; [verification](experiments-before-saturday.md#react-and-bun-migration-observations) covers locked installation, interaction tests, types, build, and stopped browser checks. Windows execution remains part of SH-T-010.
- [x] **SH-T-025 — Implement the live exploration dashboard.** The dashboard connects to the Python service and displays matched preview/landmarks, facial blendshapes, hand categories, timings, mapping controls, calibration, bounded history, and a simulated lamp. Comparison freezes existing MediaPipe results; three unintegrated candidates are labeled honestly. [Verification](experiments-before-saturday.md#dashboard-implementation-observations).
- [ ] **SH-T-003 — Verify the physical Mac camera and live dashboard.** Start capture, inspect real face/hand output, exercise mappings, and check Stop/restart. Public-image and mocked-camera checks do not complete this task.
- [ ] **SH-T-013 — Complete the demonstration interface.** Extend the working dashboard to show the actual selected action/device state and measured capture-to-action latency. Current task/frame timings exclude transport, display, and physical response.
- [ ] **SH-T-044 — Build and connect the 3D room simulation.** Under [issue #6](https://github.com/davidmoshal/SecondHands/issues/6), David and Vishwa will make an accepted gesture or facial command change a light in a browser-based room. Follow [the approved direction](project.md#established-user-direction); confirm the command/state connection and demonstrate the response. No implementation is complete yet.
- [ ] **SH-T-045 — Try optional Quest 2 viewing through WebXR.** Use the same room as a web experience, without an Android SDK. Record headset/browser compatibility, connection setup, and whether the selected movement remains observable when the participant wears the headset. Keep ordinary browser viewing available. Coordinate through [issue #6](https://github.com/davidmoshal/SecondHands/issues/6).

## Design and ExecuTorch

**Phase 5: document boundaries and establish useful framework execution.**

- [x] **SH-T-024 — Document the initial design and run ExecuTorch on the Mac.** [Design docs](design/index.md) exist. ExecuTorch 1.5.1 exported and executed an untrained XNNPACK CPU network with outputs matching PyTorch on 12 synthetic inputs. [Smoke result](experiments-before-saturday.md#executorch-cpu-smoke-observation); this is not a recognition model.
- [ ] **SH-T-034 — Expand the design documentation.** Proposed follow-ups: `architecture.md` for component/data boundaries, `model-integration.md` for adding candidates, and `dashboard.md` for exploration flows. Move existing owned explanations when splitting; do not duplicate them. These files are not yet created.
- [x] **SH-T-035 — Run a useful SecondHands component through ExecuTorch.** Connected pretrained gesture classification to the CLI using a native QNN worker. [Public-image numerical comparison, clean native execution, and a live Orbbec run](setup/orbbec-mediapipe.md#observed-checks) establish this component's NPU path. Face/hand landmarks remain on the CPU; dashboard integration and the full facial NPU scope remain separate.

## Comparison and selection

**Phase 6: measure the candidates on relevant observations.** [The experiment topic](experiments-before-saturday.md) owns methods and results. Its older Laya/Mapika/MobileCLIP2 benchmark remains a proposal; the five-candidate integration goal above is the newer direction.

- [ ] **SH-T-004 — Collect and label comparison observations.** Include deliberate, neutral, and ambiguous movements from two volunteers; retain personal recordings outside Git.
- [ ] **SH-T-005 — Build a repeatable comparison runner.** The shared image CLI now preserves distinct output types, versions, and timings for three candidates on the same inputs. Dataset-level aggregation and the labeled participant comparison remain to be implemented.
- [ ] **SH-T-006 — Run the Mac comparison.** Record accuracy, false activations, abstention, median/p95 latency, memory, calibration effort, and configurability. Smoke tests are not these measurements.
- [ ] **SH-T-007 — Select the initial integration candidate.** Record the choice and evidence under [SH-Q-001](project.md#sh-q-001--model-and-runtime-selection), including licensing and remaining PC checks.

## Snapdragon deployment

**Phase 7: verify the actual hackathon PC.** [The Compute summary](hackathon-compute.md) owns the supplied stack and unresolved event details. Mac success does not establish Windows ARM64 or NPU compatibility.

- [x] **SH-T-048 — Download all referenced models to the PC.** Completed the selected released checkpoints, including Clef-Flash and required adapter bases: 198 verified Hugging Face files (43.95 GB), 20 direct files, and the two existing verified MediaPipe bundles. [The device inventory](references/models/device-downloads.md) records versions, verification levels, and the unpublished organizer `.pte` and untrained custom classifier that cannot be downloaded.
- [x] **SH-T-049 — Run MediaPipe with the Orbbec color camera.** Added a dedicated-thread capture adapter and repeatable preview launcher. [Live CPU observations and checks](setup/orbbec-mediapipe.md#observed-checks) establish face/hand execution and camera restart; NPU use and participant accuracy are separate.
- [x] **SH-T-051 — Run JEVision with the Orbbec camera.** Connected the prepared local CPU service to a responsive camera preview with one sampled-image request at a time. [The runbook and live observations](setup/jevvision-orbbec.md) record the single-frame check, displayed results, latency, and execution limits. This does not select a model or establish accuracy, dashboard integration, or NPU execution.
- [x] **SH-T-052 — Develop and check the Orbbec scene application.** Added MediaPipe face/hand/pose tracking, YOLOv5s objects, and asynchronous JEVision scene hypotheses with their own source image. [Implementation and verification](setup/scene-understanding.md#implementation-and-verification) record a real 15-frame API session, Stop/restart, Python/UI tests, and build. All scene models run on the CPU; full browser inspection and accuracy remain open under SH-T-010 and the comparison tasks.
- [x] **SH-T-053 — Launch the requested depth viewer.** The server started on port 8767 and initially reported idle. After the blocked automatic capture/browser command, a later status check reported stopped with 2,097 captured frames. [The setup record](setup/ms-09-femto-bolt-bridge.md#depth-with-mediapipe) distinguishes this capture evidence from browser inspection and the subsequent combined viewer.
- [x] **SH-T-054 — Launch depth with MediaPipe.** Added a local window with measured depth alongside RGB face/hand tracking and pointer distance readings. [Verification](setup/ms-09-femto-bolt-bridge.md#depth-with-mediapipe) includes a 12-frame capture/shutdown check, a responsive interactive window with at least 150 frames, and focused lint/format checks. RGB/depth alignment, 3D landmarks, and accuracy remain unverified; SH-T-055 adds the later NPU gesture mode.
- [x] **SH-T-055 — Launch the depth viewer with NPU gestures.** Connected the existing native ExecuTorch/QNN classifier and disabled redundant CPU gesture classification. [Verification](setup/ms-09-femto-bolt-bridge.md#depth-viewer-with-npu-gestures) records 30 depth/RGB frames with 51 NPU hand calls and clean shutdown, a responsive interactive window with 177 calls, loaded HTP libraries, and 16 passing focused tests. Depth decoding and MediaPipe face/hand landmarks remain on the CPU.
- [ ] **SH-T-050 — Enable and verify face/gesture ExecuTorch NPU execution.** Gesture export, a matching native runtime, and live-camera QNN execution now pass. The final removal of redundant CPU gesture classification passed a [30-frame live rerun after Orbbec reconnection](setup/orbbec-mediapipe.md#observed-checks), and the interactive preview was launched. [SH-Q-005](setup/orbbec-mediapipe.md#sh-q-005--compatible-face-and-gesture-npu-export-bundle) remains open for the facial pipeline and output compatibility.

- [ ] **SH-T-001 — Confirm device configuration and event details.** The guide review is complete; the [deployment laptop's reported X1E80100 processor and observed Windows version](hardware/snapdragon-x-elite.md) are recorded. Actual RAM, exact laptop model, installed deployment runtimes, bundle location, mixed-runtime acceptance, and other organizer details remain open.
- [ ] **SH-T-036 — Verify Mac-to-PC development access.** Vishwa (@theja2289) owns [Tailscale setup on the Dell Snapdragon laptop](https://github.com/davidmoshal/SecondHands/issues/9). Verify Mac connectivity, ordinary SSH to Windows, and reconnection after restart; confirm commands use the PC checkout and environment. On 2026-10-17 the PC's OpenSSH Server was enabled and started automatically, Tailscale was observed connected, and the PC was shared with David and Jacqueline; the [Tailscale and SSH runbook](runbooks/tailscale-and-ssh.md) records the procedure, and the dashboard's Tailscale access panel tests reachability from the PC. [Model read permissions](runbooks/tailscale-and-ssh.md#read-model-files-from-a-separate-windows-account) were granted to a separate standard account and checked locally. A login from a teammate's Mac, reading the models through SSH, key login, and reconnection after restart remain unverified.
- [ ] **SH-T-009 — Run the supplied DeepLabV3 ExecuTorch demonstration.** Inspect real inputs and rendered outputs; retain profiling evidence before claiming Qualcomm NPU execution.
- [ ] **SH-T-010 — Run SecondHands on the PC.** The [scene application](setup/scene-understanding.md#implementation-and-verification) now verifies dependencies, live camera/model API execution, and Stop/restart. A separate 2026-10-18 [simultaneous-camera check](hardware/femto-bolt.md#simultaneous-capture-with-the-built-in-webcam) passed capture and reopening for the built-in webcam and Orbbec; two-camera dashboard integration is not implemented by that probe. Complete rendered-browser inspection, sustained capture, output quality, latency, and memory checks before closing the broader deployment task. Record blockers and revise the provisional model choice if necessary.

## Physical demonstration

**Phase 8: connect the validated interaction to an actual object.** This remains separate from the implemented virtual lamp.

- [ ] **SH-T-002 — Agree demonstration behavior and acceptance criteria.** Choose the object, participants' movements, confirmation/failure behavior, response targets, and acceptable false activations.
- [ ] **SH-T-008 — Test physical control manually.** Verify the selected microcontroller/actuator independently of recognition.
- [ ] **SH-T-012 — Connect recognition to the physical action.** Exercise deliberate, neutral, ambiguous, and failed-input cases against the agreed behavior.
- [ ] **SH-T-014 — Rehearse the two-participant demonstration.** Verify personalized mappings, physical response, target-PC operation, and local processing.
- [ ] **SH-T-015 — Prepare presentation and evidence.** Address the [five judging criteria](hackathon/judging-criteria.md#scoring). Separate demonstrated behavior, measured results, the actual ExecuTorch contribution, and future proposals.

## Optional experiments

These remain outside the initial completion requirement; record results in [experiments](experiments-before-saturday.md).

- [ ] **SH-T-017 — Investigate SmolVLM's Qualcomm ExecuTorch path.** Verify the recipe/version/Windows route before porting. The cited Android recipe is not a ready-made Compute PC package.
- [ ] **SH-T-016 — Evaluate Clef-Flash as a higher-level decision layer.** Subject to memory and runtime feasibility; it remains deferred, not excluded.
- [x] **SH-T-047 — Record the local Snapdragon depth bridge setup.** The [setup summary](setup/ms-09-femto-bolt-bridge.md) records the failed SDK route, successful depth/person verification, launch instructions, and later timeout from saved evidence. Applications remain outside this repository. The user later approved publication of the saved reports and raw captures in [the dated archive](../recordings/2026-10-17_18/README.md); that publication does not constitute a fresh camera test or additional SecondHands integration.
- [ ] **SH-T-037 — Connect Orbbec Femto Bolt.** The [hardware procedure](hardware/femto-bolt.md) links standalone Snapdragon bridge tests; [the CLI integration](setup/orbbec-mediapipe.md) and [scene API](setup/scene-understanding.md) now use live RGB for recognition. The originally requested x86 reference test, sustained reliability, measured accuracy, depth/trigger integration, and rendered-browser camera inspection remain open. Record driver, Viewer, Python, and application results separately. This replaces the Astra 2 hardware task.
- [ ] **SH-T-038 — Try a phone camera over Wi-Fi.** Verify input compatibility, latency, and disconnect behavior.
- [ ] **SH-T-039 — Explore audio recognition.** Select a useful audio interaction and candidate model if time permits; none is implemented yet.
