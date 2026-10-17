# SecondHands — Wiki conventions

[Repository governance](../AGENTS.md#authority-and-ownership) owns authority and document placement. Apply the shared `docs-governance-dm` skill for consolidation, source handling, and Questions; apply `wait-what-dm` for clear explanations. This file records only the project's local conventions.

## Topic ownership

Start at [index.md](index.md). Each topic owns its detailed explanation, decisions, evidence gaps, and unresolved Questions. Indexes route to these owners; they do not repeat their requirements. Split a topic only when its scope requires a separate owner.

The user-selected [plan.md](plan.md) owns live tasks, status, blockers, and verification links. This is the local task-tracking exception within Wiki. Other pages link to it instead of maintaining duplicate checklists; task completion does not approve a requirement change.

Keep approved behavior, observed implementation, proposals, disputed claims, superseded claims, and unknowns distinct. Keep source links beside the claims they support. Record an approval's exact scope and provenance in the owning topic; an assistant recommendation is not an approval.

The [conversation archive](SecondHands-conversation.md) is retained under Wiki because the user requested that location. Its captured message bodies are historical evidence, outside the maintained knowledge corpus. Do not rewrite them to match later decisions. Apply [the public repository rules](../AGENTS.md#public-repository-content) to privacy redactions. Keep its capture and incorporation status in [Source records](index.md#source-records). New topic explanations must not present its unverified claims as established facts.

## Questions

Use stable project-wide identifiers `SH-Q-001`, `SH-Q-002`, and so on. Put unresolved Questions in the final Questions section of the owning topic and link to them elsewhere. Allocate the next unused identifier; do not renumber existing Questions.

Use the shared skill's Questions, Options, Examples, and Criteria method. Separate factual evidence gaps from decisions for the human user. When a comparison is needed, describe the experiment and decision criteria. After an answer, update the owning explanation and preserve the original alternatives, rationale, and approval evidence in a resolved decision section or recoverable history. Close only the answered scope.

## Format

Use ordinary Markdown with inline relative links. Use simple, distinct headings for stable section links. Keep each prose paragraph, list item, and table row on one natural line. Captured source text is exempt from reformatting.

This setup uses no formal schema or required frontmatter. Do not copy auction-specific feature sections, vocabularies, audit declarations, or tool configuration into this project as incidental metadata.

## Maintenance and checks

Use the shared governance method within the authorized scope. The local records are [Source records](index.md#source-records) and [the change log](log.md). Record each maintained Wiki change newest-first in the log, with the date, affected owner, and a short description. Keep task checklists out of the Wiki log.

For each change, review the affected explanation against its sources, update navigation and source dispositions where needed, and check changed local links, heading targets, and Markdown whitespace. Distinguish text preservation from incorporation of meaning. Report gaps without claiming a complete consolidation.

No docaudit, Drift, Open Knowledge, or MkDocs configuration is introduced here. Plain Markdown and focused checks are the selected starting point; adopt additional tooling only through a separate scoped change.
