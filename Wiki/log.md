# Wiki change log

## 2026-10-18 — Recorded experiments prepared for GitHub

Added the user-requested [dated experiment archive](../recordings/2026-10-17_18/README.md), including explicitly approved raw sensor frames and RGB/depth captures. Its manifest accounts for 252 files and 40,813,252 bytes, with SHA-256 checksums and marked redactions in 39 text files. Calibration packets, credentials, dependency/model installations, browser profiles, and unrelated personal recordings remain outside the archive. Linked the archive from navigation and the relevant evidence owners, recorded source SH-S-042, and clarified the earlier local-only source dispositions. Publication checks passed 69 Python tests with one optional skip, 11 UI tests, Ruff, TypeScript, production build, archive checksums/JSON, and targeted privacy scans. No fresh camera or accuracy test was performed.

## 2026-10-18 — Simultaneous webcam and Orbbec capture

Recorded the user-requested [two-camera test](hardware/femto-bolt.md#simultaneous-capture-with-the-built-in-webcam): native Windows shared-read capture produced changing 1080p built-in and 720p Orbbec frames at about 30 FPS each over a common 30-second interval, followed by a successful 10-second reopen check. Preserved the earlier access errors and static DirectShow output as failed usable-video evidence. Added source SH-S-041 and linked the result from SH-T-010 while retaining application and sustained-reliability limits. Reports and the local probe remain ignored; no camera images were saved.

## 2026-10-17 — NPU gestures in the depth viewer

Extended [the combined depth viewer](setup/ms-09-femto-bolt-bridge.md#depth-viewer-with-npu-gestures) at the user's request to use the native ExecuTorch/QNN gesture classifier. Recorded the CPU landmark/depth boundary, removed redundant CPU gesture classification in that mode, and added visible runtime/timing labels. Documented the live 30-frame/51-call check, clean shutdown, responsive preview, HTP libraries, and focused tests. Updated runtime roles, source SH-S-027, and SH-T-055 without publishing imagery, calibration, or local logs.

## 2026-10-17 — Combined depth and MediaPipe viewer

Added [the combined viewer procedure and evidence](setup/ms-09-femto-bolt-bridge.md#depth-with-mediapipe) after the user's explicit launch request. Recorded simultaneous measured depth and CPU face/hand tracking, pointer distance readings, a 12-frame check with clean shutdown, and a responsive live window. Added source SH-S-026 and completed SH-T-054. Updated SH-S-025 and SH-T-053 with the earlier browser viewer's later 2,097-frame stopped status. Image alignment and measurement accuracy remain unverified; private calibration and images stay in memory.

## 2026-10-17 — Depth viewer server started

Updated [the depth setup record](setup/ms-09-femto-bolt-bridge.md#depth-viewer-alongside-secondhands), SH-S-025, and SH-T-053 after the user repeated the launch request. The server started on port 8767, returned HTTP 200, and reported idle with zero frames. Automatic approval review blocked the follow-up capture/browser command; no fresh depth-stream verification is claimed.

## 2026-10-17 — Scene application and requested depth viewer

Added [the scene application runbook](setup/scene-understanding.md) for the user's requested MediaPipe/Orbbec scene understanding. Recorded the implemented CPU model pipeline, delayed JEVision source images, shared camera ownership, real API Stop/restart verification, automated checks, and browser inspection blocked by automatic approval review. Updated design/runtime boundaries, project evidence, navigation, source SH-S-024, and SH-T-052. Also recorded the subsequent [depth viewer launch request](setup/ms-09-femto-bolt-bridge.md#depth-viewer-alongside-secondhands), connected sensor status, blocked server launch, and manual port-8767 procedure under SH-S-025 and SH-T-053. Reports and private camera artifacts remain outside Git.

## 2026-10-17 — JEVision camera experiment

Added [the JEVision Orbbec runbook](setup/jevvision-orbbec.md) and camera client after the user's request to run a JEV vision model with the camera. Recorded the prepared CPU service, a successful live-image request, a responsive preview with sampled-frame results, observed latency, and focused code checks. Updated model execution evidence, navigation, source SH-S-023, and completed SH-T-051. Camera images remain in memory; model files, logs, and result reports stay outside Git.

## 2026-10-17 — Reconnected Orbbec NPU gesture preview

Recorded the user's requested [live application run](setup/orbbec-mediapipe.md#observed-checks): the final CPU-landmark/NPU-gesture pipeline completed 30 camera frames with clean shutdown, then opened a responsive preview with the QNN HTP runtime loaded. Updated SH-T-050 to close the pending live rerun while retaining the unresolved facial NPU scope. Extended source SH-S-021. The aggregate report and process logs remain outside Git.

## 2026-10-17 — Requested profile read access

Updated [the SSH access record](runbooks/tailscale-and-ssh.md#read-model-files-from-a-separate-windows-account) after the user explicitly broadened the request to the PC owner's entire profile folder. Applied inheritable read and execute permission for the existing standard SSH account and checked the profile root and ordinary top-level directories. Protected permissions remain unchanged; remote SSH access remains unverified. Updated source SH-S-022 without publishing the account name or absolute profile path.

## 2026-10-17 — SSH access to model folders

Updated [the SSH runbook](runbooks/tailscale-and-ssh.md#read-model-files-from-a-separate-windows-account) after granting a separate standard account read access to the located model stores. Recorded permission checks on 606 files and directories, a local path catalog, and the pending remote access check. Added [the additional local model locations](references/models/device-downloads.md#additional-local-model-locations), updated SH-T-036, and recorded source SH-S-022. Account names, absolute personal paths, and permission reports remain outside Git.

## 2026-10-17 — Device model files and live Orbbec recognition

Added [the device model inventory](references/models/device-downloads.md) for the completed all-candidate downloads, with unpublished/untrained artifacts identified separately. Added [the Orbbec recognition setup](setup/orbbec-mediapipe.md) for the CPU baseline and native ExecuTorch/QNN gesture classifier, reproducible build/export scripts, numerical comparison, and successful live run. Recorded the resolved native shutdown failure, final public-image VIDEO-mode check, missing camera at the final rerun, remaining CPU facial/landmark stages, and upstream sample search. Updated model navigation, MediaPipe status pages, [runtime roles](design/runtime-stack.md), hardware/project evidence limits, source records SH-S-020/021, and tasks. Downloaded weights and local reports remain outside Git; full facial NPU execution remains unverified.

## 2026-10-17 — Tailscale and SSH runbook and access check

Created [the Tailscale and SSH runbook](runbooks/tailscale-and-ssh.md) after enabling the Windows OpenSSH Server on the deployment PC. It records the observed service, firewall, network-profile, and sharing state, the Mac connection and SSH-key steps, dashboard port forwarding, and troubleshooting. The dashboard gained a Tailscale access panel with a connection test. Updated navigation, source SH-S-019, the [development runbook](runbooks/mac-and-snapdragon-development.md#run-pc-commands-through-t3), and [SH-T-036](plan.md#snapdragon-deployment). Logins from teammates' machines remain untested.

## 2026-10-17 — Local depth bridge setup documented

Created [the MS-09 / Femto Bolt setup summary](setup/ms-09-femto-bolt-bridge.md) in the user-requested `setup` folder. Reviewed the earlier local session and saved installation/test evidence to explain the SDK failure, direct capture bridge, depth decoding, person-position application, and launch procedure. Preserved the initial successful checks and a later capture timeout as separate observations. Updated navigation, source SH-S-018, [hardware findings](hardware/femto-bolt.md), [deployment hardware](hardware/snapdragon-x-elite.md), [project evidence limits](project.md#implementation-and-evidence-limits), and [task status](plan.md). No camera tests were rerun, no application integration was performed, and no private recordings or calibration files were copied into Git.

## 2026-10-17 — React and Bun dashboard migration

Recorded the user-approved replacement of Vue with React and pnpm with Bun in [Project direction](project.md#development-setup), [runtime stack](design/runtime-stack.md), and [recognition design](design/recognition-and-triggers.md). Updated [runbook commands](runbooks/mac-and-snapdragon-development.md), SH-T-047 in [the plan](plan.md#ui), source SH-S-017, and [migration evidence](experiments-before-saturday.md#react-and-bun-migration-observations). Historical Vue checks remain labeled as earlier results. Issue #11 tracks the requested migration; Windows and physical-camera checks remain open.

## 2026-10-17 — Event backers recorded

Added GitHub, Meta, and Qualcomm to [the judging page](hackathon/judging-criteria.md#event-backers), following the user's identification and the logos visible in the supplied photograph. No specific sponsorship roles or commitments are inferred.

## 2026-10-17 — Judging criteria recorded

Added [judging criteria](hackathon/judging-criteria.md) from the user-supplied attendee-guide photograph: five criteria totaling 100 points. Preserved the visible wording and weights without reconstructing hidden descriptions. Linked the page from the index and presentation task, recorded source SH-S-016, and resolved the earlier rubric gap in [the Compute summary](hackathon-compute.md). The source page could not be retrieved through the web tool; the photograph was not added to Git.

## 2026-10-17 — Tailscale setup assigned

Created [issue #9](https://github.com/davidmoshal/SecondHands/issues/9) for Tailscale and Mac-to-Windows command access on the Dell Snapdragon laptop, assigned to Vishwa's collaborator account `theja2289`. Updated existing SH-T-036 in [the plan](plan.md#snapdragon-deployment), [project direction and account mappings](project.md), and source SH-S-015. Installation and connection testing remain open.

## 2026-10-17 — Clinical application ownership confirmed

Recorded Kate's clinical application role in [Project direction](project.md#established-user-direction), created [issue #7](https://github.com/davidmoshal/SecondHands/issues/7), and linked the work from [the plan](plan.md#team-coordination). Updated source record SH-S-014 and the owner-account context. Presentation ownership remains unconfirmed; no clinical requirements or findings were established by this assignment.

## 2026-10-17 — Browser-based 3D room demonstration added

Recorded the user's [3D room direction](project.md#established-user-direction) and created [issue #6](https://github.com/davidmoshal/SecondHands/issues/6) for David and Vishwa. Added linked work in [the plan](plan.md#ui) for a gesture/facial-command light response and optional Quest 2 viewing through WebXR, without an Android SDK. Recorded source SH-S-013. Existing physical-control work remains separate; no 3D implementation or headset compatibility is claimed.

## 2026-10-17 — Deployment laptop processor recorded

Added the [Dell Snapdragon hardware page](hardware/snapdragon-x-elite.md) with the user's exact X1E80100/Oryon processor description and reported 3.42 GHz speed. Separated those supplied details from unknown RAM, OS build, runtime versions, and untested deployment behavior. Linked the page from the index, device-configuration task, and Femto Bolt procedure. No hardware inspection or performance test was performed.

## 2026-10-17 — Femto Bolt selection and team work items

Replaced the current Astra 2 hardware choice with [Orbbec Femto Bolt](hardware/femto-bolt.md), following the user's revised direction. Added the Windows laptop-first, Dell Snapdragon-second procedure with current SDK evidence and explicit architecture limits. Updated the proposal, README, project direction, Compute hardware reference, navigation, source records, and [plan](plan.md#team-coordination). Created five GitHub coordination issues for stack, hardware, models, UI, and presentation. Recorded unconfirmed account mappings and Kate's proposed presentation ownership as linked Questions. No Astra-specific capture code existed to move, and no hardware connection was tested.

## 2026-10-17 — Additional local model experiments

Added isolated, locked image experiments and root just commands for Laya Vision, Mapika Decider Vision, and SmolVLM. Updated [model references](references/models/index.md), [observed results](experiments-before-saturday.md#decision-model-image-observations), [runbook commands](runbooks/mac-and-snapdragon-development.md#run-the-other-three-image-models), [runtime boundaries](design/runtime-stack.md), Project direction, source record SH-S-010, and [the task plan](plan.md#models). The records distinguish successful execution, model mistakes, dependency failures, and unresolved work. Added the user-requested `wait-what-dm` and `caveman` pointers to [repository governance](../AGENTS.md#communication-and-documentation-skills). Personal recordings remain outside Git; the new model runners do not yet supply the dashboard or execute through ExecuTorch.

## 2026-10-17 — Task plan reorganized by topic and phase

Reworked [the existing plan](plan.md) at the user's request into Mac foundation, models, recognition features, UI, design/ExecuTorch, comparison, Snapdragon deployment, and physical demonstration phases. Preserved earlier task identifiers and evidence limits, added explicit remaining model integrations and feature follow-ups, and removed governance/personal-name cleanup from the task list. Checked tasks distinguish implemented exploration from untested real-camera, participant, and target-device behavior. Updated navigation and source record SH-S-009; no application behavior changed.

## 2026-10-17 — Approved exploration dashboard implemented

Implemented the user-approved dashboard through a subagent and reconciled the [design](design/recognition-and-triggers.md), [runtime stack](design/runtime-stack.md), [Project direction](project.md#live-exploration-dashboard), source record SH-S-008, and SH-T-025 in [the task plan](plan.md#project-setup). Added [startup and interaction steps](runbooks/mac-and-snapdragon-development.md#run-the-live-exploration-dashboard). [Observed checks](experiments-before-saturday.md#dashboard-implementation-observations) record 33 Python tests, two transport tests, Vue type checking/build, native MediaPipe execution on public images, and parent source/browser review. The docs distinguish implemented deterministic triggers and frozen comparison from future decision-model inference. Real-camera, participant accuracy, remote operation, and Windows remain untested. Current personal-name checks remain clear; no Git history was rewritten.

## 2026-10-17 — Design approved and personal-name check repeated

Recorded the user's approval of the reviewed wording and explicit subagent implementation request in [the design](design/index.md), [Project direction](project.md#established-user-direction), source record SH-S-008, and SH-T-025 in [the task plan](plan.md#project-setup). Rechecked current repository content for the requested personal names and reviewed prose candidates for other names. The requested names were already absent from prose after the earlier redactions; working repository and technical source links remain. No further captured text was changed and no Git history was rewritten. Implementation evidence will be recorded separately after verification.

## 2026-10-17 — Recognition design and local ExecuTorch check

Added [system design](design/index.md) at the user's request: continuous recognition versus command triggers, proposed calibration/state transitions, dashboard exploration modes, package boundaries, and the reviewed [runtime stack](design/runtime-stack.md). Recorded the user's five-candidate Mac exploration and mixed-runtime preference separately from proposed product behavior and unresolved organizer acceptance. Added `just smoke-executorch` with a standalone script lock; the [observed Mac check](experiments-before-saturday.md#executorch-cpu-smoke-observation) verifies export, XNNPACK delegation, `.pte` loading, and agreement with PyTorch on 12 synthetic inputs. Updated the [runbook](runbooks/mac-and-snapdragon-development.md#run-the-executorch-cpu-smoke-check), project direction, model-index navigation, source records, and SH-T-024/SH-T-005 in [the task plan](plan.md). This is not a trained gesture model, implemented trigger policy, or target-PC result.

## 2026-10-16 — First MediaPipe Python baseline implemented

Implemented the user-requested Face Landmarker and Gesture Recognizer baseline through a subagent, with explicit checked model downloads, image and bounded camera CLIs, structured outputs, and focused tests. Updated [Project direction](project.md#mediapipe-baseline), the [model references](references/models/index.md), the [runbook](runbooks/mac-and-snapdragon-development.md#run-mediapipe-face-and-hand-recognition), and SH-T-023 in [the task plan](plan.md#project-setup). [Dated observations](experiments-before-saturday.md#mediapipe-baseline-observations) record the real image smoke checks, 10 passing tests with local models, and the limits of the evidence. Camera use, Windows, comparative accuracy, and Vue integration remain untested or unimplemented.

## 2026-10-16 — Public-repository privacy policy applied

Applied the user-approved [public repository rule](../AGENTS.md#public-repository-content) and linked the Wiki convention to that owner. Replaced team names with role labels and removed private conversation links and identifiers from the public archive and source record. Marked the redactions and retained the technical exchange content. Updated the model reference's source description and SH-T-022 in [the task plan](plan.md#project-setup). Targeted current-file scans passed; this was not a full secret or history audit. Earlier Git commits retain the original archive and have not been rewritten.

## 2026-10-16 — Local development tasks added

Added the root [justfile](../justfile) for the four commands the user confirmed working, plus combined setup and task listing. Updated [the development runbook](runbooks/mac-and-snapdragon-development.md#try-the-existing-scaffold-on-the-mac) to use the shortcuts and retain the Windows ARM64 dependency limit. Recorded verification under SH-T-021 in [the task plan](plan.md#project-setup). Recipe execution is verified on the Mac except for UI startup, whose command was checked by dry run; Windows execution remains untested.

## 2026-10-16 — Mac and Snapdragon development runbook added

Created [the development runbook](runbooks/mac-and-snapdragon-development.md) from the user-approved workflow explanation. Consolidated installation and check commands from [Project direction](project.md#development-procedure), while retaining package responsibilities and observed verification there. Recorded the separate checkouts and environments, Git workflow, T3 execution context, and current lockfile's Windows ARM64 PyTorch limitation. Updated [navigation and source records](index.md) and SH-T-020 in [the task plan](plan.md#project-setup). The Windows and remote-connection procedures remain untested.

## 2026-10-16 — Model references added

Added [the model reference index](references/models/index.md) and detail pages for the five recommended starting candidates supplied by the user. Reviewed the full captured conversation for other model mentions, including HSEmotion in the older quoted ranking; retained additional leads and distinguished deferrals from exclusions. Updated the [source records](index.md#source-records), [model-selection Question](project.md#sh-q-001--model-and-runtime-selection), experiment context, and SH-T-019 in [the task plan](plan.md#reference-review). The archive is unchanged. Historical technical claims remain unverified except where a primary-source check is explicitly stated; no models were installed or evaluated.

## 2026-10-16 — Python and UI project configured

Updated [Project direction](project.md#development-setup) with Python and Vue package responsibilities, setup commands, implementation limits, and observed Mac verification. Recorded the user's built-in-camera-first decision, with Astra 2 and a phone camera as optional inputs. Updated SH-T-003 and recorded completed setup as SH-T-018 in [the task plan](plan.md). Linked development instructions from the repository README and [Wiki index](index.md). No camera, recognition model, browser interaction, or Windows execution was tested.

## 2026-10-14 — Compute Track guide reviewed

Added [the Compute Track summary](hackathon-compute.md) from the current hackathon repository and public event pages, with pinned repository references and explicit evidence limits. Placed the hackathon link at the top of [the Wiki index](index.md). Updated [Project direction](project.md) and SH-T-001 in [the task plan](plan.md) to distinguish verified source statements from unresolved organizer and hardware questions. No runtime tests, organizer contact, or full docaudit were performed.

## 2026-10-14 — Task plan established

Created the user-requested [task plan](plan.md) with ordered preparation, Compute PC verification, demonstration integration, and optional experiment tasks. Each task states its expected completion evidence; no task is marked complete. Updated [repository governance](../AGENTS.md), [Wiki conventions](AGENTS.md), and [navigation](index.md) to make this the single task-tracking owner and linked it from the [experiment page](experiments-before-saturday.md).

## 2026-10-14 — Pre-Saturday experiments extracted

Created [Experiments before Saturday](experiments-before-saturday.md) from the user-supplied review: three-model Mac comparison, 30–50 observations from two volunteers, seven measurements, proposed responsibilities, and Saturday follow-up. Confirmed that the selected source section matches the existing archive. Replaced the duplicated comparison summary in [Project direction](project.md) with a link and updated [navigation and source records](index.md). This records a proposed plan, not experiment results or confirmed assignments.

## 2026-10-14 — Current proposal recorded

Preserved the user-supplied [current proposal](proposal.md) in full. Updated [Project direction](project.md) to identify it as current, record the Astra 2 difference from the earlier camera-only direction, and clarify the remaining model/deployment Question. Added the proposal to [navigation and source records](index.md). Technical and market-size claims were not independently verified; the historical conversation archive is unchanged.

## 2026-10-14 — Governance adoption

Adapted the ownership and maintenance structure reviewed in `au2604-auction-legacy` (`AGENTS.md`, `Wiki/AGENTS.md`, `Wiki/index.md`, and the update and consolidation sections of its maintenance runbook). The shared `docs-governance-dm` skill remains the method owner; auction-specific rules and tooling were not adopted.

Established [repository governance](../AGENTS.md), [Wiki conventions](AGENTS.md), and [the index with source records](index.md). Moved the existing project context from root guidance into [Project direction](project.md), with explicit evidence limits and an unresolved model/runtime Question. [CLAUDE.md](../CLAUDE.md) now contains only `@AGENTS.md`.

The [conversation archive](SecondHands-conversation.md) remains unchanged. This change does not claim complete incorporation of that source or verification of its technical claims. No full docaudit was run.
