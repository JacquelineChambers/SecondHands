# SecondHands Wiki

**Our stream: Compute Track.** [Hackathon developer guide](https://github.com/aaishikasb/qc-executorch-guide) · [Compute rules and technical summary](hackathon-compute.md)

This Wiki holds maintained project knowledge. Read [the current proposal](proposal.md) for the vision, demonstration, and proposed architecture, then [Project direction](project.md) for its relation to earlier decisions and evidence gaps.

## Plan and experiments

- [Development setup](project.md#development-setup) — Python package, Vue UI package, installation, and checks.
- [Task plan](plan.md) — ordered preparation, target-PC verification, demonstration tasks, and optional experiments.
- [Experiments before Saturday](experiments-before-saturday.md) — the proposed Mac comparison, test observations, measurements, division of effort, and Compute PC follow-up.

## Governance and maintenance

- [Repository governance](../AGENTS.md) — authority and ownership.
- [Wiki conventions](AGENTS.md) — topic structure, Questions, and focused checks.
- [Change log](log.md) — documentation changes.

## References

- [Model references](references/models/index.md) — the five recommended starting candidates, detail pages, and additional model leads from the captured chats.

## Source records

| ID | Original and capture | Maintained destination | Disposition |
| --- | --- | --- | --- |
| SH-S-001 | [SecondHands conversation](https://chatgpt.com/c/6acfa731-2d64-8332-b752-7d7164a01ac7), captured 2026-10-14 in [the archive](SecondHands-conversation.md#import-scope); five exchanges, ten messages | [Project direction](project.md): user direction and open decisions; [Model references](references/models/index.md#other-candidates-from-captured-chats): model identities, suggested roles, and relevant source-stated limits from exchanges 4–5 | All returned message text is preserved. The full 826-line capture was reviewed for model candidates on 2026-10-16. Additional model leads, including HSEmotion from the quoted older ranking, are indexed without treating omissions or deferrals as exclusions. Detailed historical rankings, benchmark numbers, hardware claims, team correspondence, and deployment proposals are not fully consolidated or externally verified. Earlier messages, citation targets, some code blocks, and attachments remain unavailable. |
| SH-S-002 | Current proposal supplied directly by the user in this repository chat on 2026-10-14 | [Current proposal](proposal.md), with context reconciled in [Project direction](project.md) | Supplied proposal text preserved in full, without the enclosing code fence. Identified by the user as current; technical and market-size claims remain unverified. Its inclusion of Astra 2 is recorded alongside the earlier camera-only direction. |
| SH-S-003 | User attachment `Pasted text.txt`, “Decision models for SecondHands — revised Compute Track ranking,” supplied 2026-10-14 | [Experiments before Saturday](experiments-before-saturday.md) | The full attachment was read. Only “The experiment I'd run before Saturday,” including its division of effort and Saturday follow-up, was incorporated in this change. That source section exactly matches the text already preserved in the conversation archive. The remaining attachment content was not consolidated or copied into the repository; external claims were not reverified. |
| SH-S-004 | Hackathon repository at commit `9f3aae1f53053729ed28a242643e39feaf38fb9d`, plus Luma and Open Source AI Week event pages, reviewed 2026-10-14 | [Compute Track summary](hackathon-compute.md), with inline source links | Root README, full Compute README, artifact inventory, and public event descriptions reviewed. Summarized event requirements, deployment instructions, and unresolved details. Source bodies remain upstream; no hardware tests or organizer clarification performed. |
| SH-S-005 | Five-candidate recommendation quoted by the user in this repository chat on 2026-10-16, with a request to add it to the Wiki and review other model mentions | [Model references](references/models/index.md#recommended-starting-order) and its five linked detail pages | Incorporated the recommended order, model roles, initial combination, limits, and Clef-Flash deferral. Primary documentation for the five was checked earlier in the same conversation; HSEmotion's fixed-category capability was checked during this addition. Other historical model claims remain labeled unverified. Recording the recommendation does not select a final runtime or establish model execution. |

The archive records what the conversation reader returned. It is not a complete conversation export or evidence that its technical claims were tested. The source records above own incorporation status; [the archive](SecondHands-conversation.md#import-scope) owns the original import limits.
