# SecondHands — repository governance

This file tells agents where to find project instructions, how to record decisions, and how to protect information in this public repository.

Start with [the Wiki index](Wiki/index.md). Then read only the documents needed for the task. Use [Project direction](Wiki/project.md) for the current project context, decisions, proposals, and facts that still need verification.

## Authority and ownership

Follow the human user's Personalization instructions for global operating rules. Use this file for SecondHands-specific rules. Use [Wiki/AGENTS.md](Wiki/AGENTS.md) for Wiki writing and maintenance; it applies the shared `docs-governance-dm` method.

Each type of information has one owner: the document where that information is maintained. Update that owner and link to it from other documents.

| Content | Owner |
| --- | --- |
| Repository governance | This file |
| Wiki authoring and maintenance conventions | [Wiki/AGENTS.md](Wiki/AGENTS.md) |
| Project knowledge, requirements, decisions, and unresolved Questions | The relevant topic linked from [Wiki/index.md](Wiki/index.md) |
| Where source material came from, what was available, and where it was used | [Source records](Wiki/index.md#source-records) |
| Historical conversation text | [Conversation archive](Wiki/SecondHands-conversation.md) |
| Documentation change history | [Wiki/log.md](Wiki/log.md) |
| Task sequence, work status, blockers, and verification links | [Wiki/plan.md](Wiki/plan.md) |
| Claude entry point | [CLAUDE.md](CLAUDE.md), which loads this file |

Use the maintained Wiki topics for current project knowledge. The conversation archive is historical source material. A claim in that archive is not a current project decision or a verified fact merely because the file is under `Wiki/`.

Label approved decisions, proposals, and unresolved Questions separately. Approved requirements describe intended behavior. Current code, configuration, and observed runtime or test results show implemented behavior. If they differ, record the difference in the relevant topic. Copying or summarizing a source does not approve its proposals or verify its claims.

## Project workflow

Keep the project's single task list in [Wiki/plan.md](Wiki/plan.md), as the user requested. Use it for task order, status, blockers, and links to verification. Keep requirements, decisions, explanations, and experiment methods and results in their relevant topic documents. Adding or completing a task does not authorize a change to product requirements.

When an authorized change affects a Wiki topic, update that topic. Follow the [Wiki maintenance conventions](Wiki/AGENTS.md#maintenance-and-checks): check the relevant sources and local links, and record the documentation change in the change log.

The project has not adopted OpenSpec, a formal documentation schema, or a documentation audit tool. A full docaudit is not required.

## Communication and documentation skills

Apply `wait-what-dm` to every response and repository document. Explain the subject, current state, and next step. Use established technical terms and explain unfamiliar terms. Give enough context for a reader who does not remember the conversation.

Apply `caveman` when communicating with the human user and subagents. Keep the required confidence prefix and technical meaning. If shorter wording would make the message unclear, preserve the explanation.

Use normal, clear prose for repository documents, code comments, and other saved writing. Read the installed skills through the active skill catalog. Their definitions remain the source of their detailed instructions.

## Questions and decisions

Put each unresolved question in the relevant document's Questions section. Follow the [Wiki question conventions](Wiki/AGENTS.md#questions) for placement and stable question identifiers.

Always use `wait-what-dm` for questions. Include:

- **Context:** Explain the current state, what needs deciding or finding out, and why it matters. State what is already approved and what remains uncertain.
- **Options and examples:** Give meaningful options and a concrete example for each. Explain the criteria and trade-offs needed to compare them.
- **File links:** Link every referenced repository file from the question so the reader can inspect it directly.

The question must make sense without the reader remembering the conversation. Add an unchecked task in [Wiki/plan.md](Wiki/plan.md) that links directly to the question. Keep its explanation and options in the relevant document; do not copy them into the plan. When the question is resolved, record the answer there and check the linked plan task.

## Public repository content

Before each SecondHands commit and push, apply the global publication check to the files being published. Include captured chats and generated files.

Keep credentials outside Git. Use role labels for team members and test participants. Keep the following outside Git unless the human user approves the exact content for publication:

- Personal contact details, local usernames, and home paths.
- Private conversation links and identifiers.
- Raw camera recordings, audio recordings, and calibration data.

Retain public project identifiers and source attribution needed to verify technical claims.

When removing private information from historical captures, mark the redactions, preserve the technical meaning, and update the source records.

Report sensitive findings by file location without repeating the sensitive values. Get separate explicit approval before rewriting Git history or force-pushing.

## Wiki rules

@Wiki/AGENTS.md
