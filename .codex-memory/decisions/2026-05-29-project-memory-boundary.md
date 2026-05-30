# Project memory boundary

observed_at: 2026-05-29
scope: Codex project-local memory

Decision: Expedition HQ may have a project-local `.codex-memory/` folder for Codex collaboration, but this does not mean the Expedition HQ product can mutate external memory systems.

Reasoning: the repo's MVP safety rules prohibit live control actions and memory mutation in the product. The local memory scaffold is a development aid for future agents, not an app feature.

Revisit this only if a future product design explicitly adds gated, auditable memory-write behavior after the read-only MVP is stable.

