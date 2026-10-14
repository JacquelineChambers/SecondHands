# SecondHands — repository governance

Start at [the Wiki index](Wiki/index.md), then read only the topic relevant to the task. [Project direction](Wiki/project.md) owns the current context, decisions, proposals, and evidence gaps.

## Authority and ownership

Global operating rules remain in the human user's Personalization instructions. This file owns SecondHands governance; [Wiki/AGENTS.md](Wiki/AGENTS.md) owns its documentation conventions and adopts the shared `docs-governance-dm` method.

| Content | Owner |
| --- | --- |
| Repository governance | This file |
| Wiki authoring and maintenance conventions | [Wiki/AGENTS.md](Wiki/AGENTS.md) |
| Maintained project knowledge, requirements, decisions, and unresolved Questions | The owning topic linked from [Wiki/index.md](Wiki/index.md) |
| Source identity, capture limits, and incorporation status | [Source records](Wiki/index.md#source-records) |
| Historical conversation text | [Conversation archive](Wiki/SecondHands-conversation.md) |
| Documentation change history | [Wiki/log.md](Wiki/log.md) |
| Task sequence, work status, blockers, and verification links | [Wiki/plan.md](Wiki/plan.md) |
| Claude entry point | [CLAUDE.md](CLAUDE.md), which loads this file |

The maintained Wiki is the project's knowledge corpus. The conversation archive is an explicit historical-source exception: its location under `Wiki/` does not make its claims authoritative. A maintained topic can contain approved decisions, proposals, and unresolved Questions; label their status separately.

Approved requirements establish intended behavior. Current source, configuration, and observed runtime or test results establish implemented behavior. When they differ, record the gap or conflict in the owning topic. Moving or summarizing a source does not approve its proposals or verify its claims.

## Project workflow

The user selected [Wiki/plan.md](Wiki/plan.md) as the task-tracking owner. Keep one task list there; topic pages own requirements, decisions, explanations, and experiment methods/results. The plan's location in Wiki is an explicit local convention, not authority to change product requirements. No OpenSpec workflow, formal documentation schema, or documentation audit tool is adopted.

For an authorized change, update the affected Wiki owner when its meaning changes. Review relevant source coverage, local links, and the change log under the [Wiki maintenance conventions](Wiki/AGENTS.md#maintenance-and-checks). A full docaudit is not required for this governance setup.

## Wiki rules

@Wiki/AGENTS.md
