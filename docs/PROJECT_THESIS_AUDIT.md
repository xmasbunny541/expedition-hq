# Project Thesis Audit: Little AI Guys Running Around Doing Stuff

Audit date: 2026-05-28

Scope: audited all project-authored source, config, docs, archive, hook, skill, package, and test files visible from the repository root, including current untracked project files. Ignored generated/runtime/vendor areas were reviewed as categories, not line-by-line dependency content: `.venv/`, `node_modules/`, `data/*.db*`, `runtime/`, `apps/web/dist/`, `.pytest_cache/`, and `.git/`.

Verification:
- `.\.venv\Scripts\python.exe scripts\validate_seed.py` passed.
- `.\.venv\Scripts\python.exe -m pytest apps\api\tests --basetemp runtime\pytest-audit-temp` passed: 24 tests.
- `npm.cmd run build` passed.
- Plain `python` is currently the Microsoft Store alias and fails. Plain `npm` in PowerShell hits execution policy because `npm.ps1` is blocked. Use the repo venv Python and `npm.cmd`.
- First pytest attempt failed only because `%TEMP%\pytest-of-augus` is ACL-blocked. Project temp base fixed that.

## Executive Compatibility Read

First evaluation: the project is already strongly compatible with the thesis. It has the right mission, neutral operational nouns, read-only guardrails, seed-driven agent identity, event ledger, XP calibration, milestones, field reports, route risk records, and a themed HQ UI. Alignment: 7.7/10.

Devil's advocate evaluation: it still behaves more like a themed dashboard than a living ecosystem. The UI is largely tabs, cards, lists, scoreboards, and proposal review controls. Agents do not yet visibly move through work, inhabit locations deeply, show intentions over time, or leave rich environmental traces. Alignment under this stricter lens: 6.2/10.

Substantial difference: the project is compliant and directionally correct, but not yet experientially coherent. The next major work should prioritize a world/state model and ambient visualization before adding more analytics or desk workflows.

## File-by-File Audit

### Root And Governance

| File | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `.env.example` | Local configuration example. | Defines DB path, seed dir, write-event flag, and blank future integrations. | 8 | Local-first, redacted, integration restraint. | `EXPEDITION_HQ_ALLOW_WRITE_EVENTS` is not enforced by API, so config suggests a policy switch that does not exist. | Wire the flag into POST routes or remove it until implemented. Add refresh interval and redaction policy only if consumed. |
| `.gitignore` | Keeps runtime, secrets, dependencies, and local outputs out of git. | Protects local-first safety boundary. | 9 | Blocks DBs, runtime logs, env files, tokens, tunnel URLs, QR material. | Does not ignore `apps/web/dist/` via app-local path unless `dist/` root matching catches it, which it does for git but is implicit. | Add comments for generated UI build and pytest temp outputs. Keep runtime ignored. |
| `AGENTS.md` | Project rules and mission. | Best current statement of the thesis and safety boundaries. | 10 | Directly names little specialists, constructs, routes, archives, expeditions, field reports, artifacts, milestones, XP, badges. | None of substance. | Keep as the architectural constitution. Add a line saying UI should prefer environmental state over card grids when feasible. |
| `CODEX_PROJECT_PROMPT.md` | Initial implementation prompt. | Launch brief for MVP. | 9 | Strong read-only constraints and "what are my little AI guys doing?" target. | Mentions `POST /events`, which is safe locally but slightly weakens "read-only" language unless framed as local ledger ingest. | Clarify "read-only toward external systems, append-only/local toward ledger." |
| `README.md` | Project overview and runbook. | Practical entry point and current run commands. | 8 | Explains local startup, verification, XP claims, and safety. | Uses plain `python` and `npm`, which failed in current shell. Also centers setup more than ecosystem behavior. | Add Windows-tested commands using `.venv\Scripts\python.exe`, `npm.cmd`, and pytest `--basetemp runtime\pytest-temp`. Add a short "experience target" section. |
| `SECURITY.md` | Safety policy. | Guardrail reference. | 10 | Explicitly forbids secrets, live URLs, raw transcripts, and control posture. | None. | Add redaction-level taxonomy for artifacts: public-safe, local-private, secret-bearing excluded. |
| `START_HERE.md` | Starter bootstrap instructions. | Historical scaffold instructions. | 7 | Preserves origin workflow and non-negotiable read-only rule. | Still reads like a generic starter copy flow, not the current living project. | Mark as historical bootstrap or update to current local path and current verification commands. |
| `package.json` | Root npm scripts. | Convenience wrapper for seed, API, tests, and web. | 6 | Keeps common commands discoverable. | `python` and `npm` shims are brittle on this Windows setup. | Add PowerShell scripts or document direct venv/PATH-safe commands. Consider `api:test:local` with `--basetemp runtime/pytest-temp`. |

### Backend API

| File | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `apps/api/expedition_hq_api/__init__.py` | Package marker. | Minimal API package identity. | 5 | Fine and harmless. | No thesis function. | No change needed. |
| `apps/api/expedition_hq_api/main.py` | FastAPI routes and request models. | Serves read endpoints plus local event, XP claim, and proposal writes. | 8 | Strong external read-only posture, central endpoints, CORS local-only, server-side XP claim creation. | Proposal decision PATCH is a control-like UI action. It is local-only, but it pulls the product toward a review desk instead of pure observatory. | Add `GET /activity-signals`, `GET /agent-state-history`, and `GET /world-map`. Gate writes behind `EXPEDITION_HQ_ALLOW_WRITE_EVENTS`. Label proposal writes as local ledger append. |
| `apps/api/expedition_hq_api/db.py` | SQLite initialization, seeding, read rows, event/proposal persistence. | Core local archive and source of API data. | 8 | Simple SQLite, raw JSON preservation, seed imports, field report conversion, compatible schema migration. | `raw_json` can become the real schema while columns drift. Tables lack missions, agent-state snapshots, assignments, rooms, achievement unlock history, and relationships. | Add migrations for `missions`, `agent_state_snapshots`, `agent_locations`, `agent_expedition_assignments`, `achievement_unlocks`, `artifact_evidence`, and `redaction_level`. Add indexes on event timestamp/source/expedition. |
| `apps/api/expedition_hq_api/proposals.py` | Proposal normalization, decisions, dialogue messages, decision events. | Local Proposal Desk behavior. | 6 | Local-only, no implementation trigger, revision questions create visible dialogue. | This is the strongest drift toward management/control. Soft wager denial mechanics can feel punitive or corporate if foregrounded. | Reframe as "Agent Suggestions" or "Planning Bureau." Convert approved proposals into candidate missions, not work controls. Show suggestions as agent intent bubbles in the HQ map. |
| `apps/api/expedition_hq_api/xp.py` | XP formula, audit flags, agent XP aggregation, season summaries. | Main gamification engine. | 8 | Server owns XP, flags suspicious claims, preserves shadow multipliers, splits team credit. | Active minutes remain honor-ledger data, not hard telemetry. Scoreboard prominence can motivate spam unless the review state is equally visible. | Add "story value" signals separate from XP: discoveries, artifacts, blockers moved, mission continuity. Add per-agent journal summaries and gaming-pattern visibility. |
| `apps/api/pyproject.toml` | Python project metadata and pytest config. | Dependency declaration. | 7 | Small dependency footprint, FastAPI/Pydantic only. | `pythonpath = ["."]` works from `apps/api` root but root scripts insert paths manually. | Add a top-level test command that uses venv and local basetemp. Consider package install docs. |
| `apps/api/requirements.txt` | Runtime Python deps. | FastAPI stack. | 7 | Minimal and practical. | Version ranges are broad; future incompatibility risk. | Pin upper bounds or periodically lock for local stability. |
| `apps/api/requirements-dev.txt` | Test deps. | Adds pytest/httpx. | 7 | Minimal dev dependency list. | Same broad-version risk. | Add a tested version note from the current venv. |
| `apps/api/tests/test_seed_files.py` | Backend/seed/API tests. | Primary compliance harness. | 9 | Tests local-only behavior, no seed endpoint, XP audit, proposal soft wagers, no external dispatch terms. | Tests cover API behavior more than ecosystem experience. No visual/ambient assertions. | Add tests for world-state derivation: agent latest activity, room state, mission continuity, artifact redaction level, achievement unlock history. |

### Frontend App

| File | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `apps/web/index.html` | Vite entry HTML. | Hosts React root. | 5 | Simple and local. | No metadata beyond title. | Add app description and theme color. No product change required. |
| `apps/web/package.json` | Frontend scripts and deps. | React/Vite app manifest. | 6 | Small stack, no enterprise UI framework. | Very new major versions increase compatibility risk. | Consider pinning exact tested versions. Add `build:local` using `npm.cmd` in root docs rather than package script. |
| `apps/web/package-lock.json` | Dependency lock. | Reproducible frontend install. | 6 | Locks actual dependency graph. | Low product relevance; large generated file. | Keep. Audit with npm audit only when dependency/security work is requested. |
| `apps/web/tsconfig.json` | TypeScript config. | Strict frontend type checking. | 7 | `strict` supports schema reliability. | TS interfaces duplicate API/schema manually. | Generate or validate shared types from schemas once schema stabilizes. |
| `apps/web/src/api.ts` | Frontend API client. | Fetches all read data and patches proposal decisions. | 7 | Simple and readable. | No polling despite config `refresh_seconds`; no stale-state signal. Proposal PATCH is foregrounded. | Add timed refresh and "last updated" status. Add typed error surfaces. Keep mutation calls isolated in one local-ledger module. |
| `apps/web/src/App.tsx` | Main UI composition. | Tabs, HQ page, proposal desk, systems view, XP board, data loading. | 7 | Strong theme language, read-only banner, state summaries, room map, field reports, trophy shelf. | Still too much SaaS shape: sticky tabs, metric grid, cards, proposal analytics, decision buttons. The "little guys" mostly sit in cards instead of moving through a place. | Split into route-sized components. Make HQ map first-class: rooms, agents, routes, expeditions, active trails. Move scoreboards/analytics behind secondary drilldowns. |
| `apps/web/src/styles.css` | Visual system CSS. | Defines dark observatory look, cards, tokens, rooms, states, proposal UI. | 7 | Good non-corporate palette, restrained radius, state colors, room panels, pulse for awake specialists. | Token initials are abstract; environment is still card-grid. Heavy dark/brown palette risks one-note "dashboard skin." Animation is minimal and not yet movement. | Add map layout, paths/bridges, station glyphs, agent movement trails tied to latest event age. Add light/dark contrast variation and reduce card dominance. |
| `apps/web/src/types.ts` | Frontend data contracts. | Mirrors API objects. | 7 | Covers agents, events, XP, seasons, proposals, milestones, routes, stores. | Missing missions/tasks/state history/rooms/achievements. Duplicates schema definitions. | Add `Mission`, `AgentStateSnapshot`, `Room`, `RouteEdge`, `AchievementUnlock`, `Discovery`, `ArtifactEvidence`. |
| `apps/web/src/vite-env.d.ts` | Vite env typing. | Build support. | 5 | Necessary boilerplate. | No thesis relevance. | No change. |
| `apps/web/src/main.tsx` | React mount. | Starts app. | 5 | Standard and correct. | No thesis relevance. | No change. |
| `apps/web/src/components/AgentCard.tsx` | Agent roster card. | Shows avatar, state, assignment, latest event, XP status. | 7 | Makes state, assignment, latest activity, XP, review count visible. | It is still a profile card, not a living participant. Shows ID prominently, which pulls toward inventory. | Add "why now", "last seen", current room trail, and latest field-report link. In HQ, prefer small moving tokens over full cards. |
| `apps/web/src/components/CurrentActivity.tsx` | Latest signals panel. | Fixed list of important agents/systems and latest events. | 7 | Good glanceable summary. | Hard-coded IDs will age badly and hide new agents. | Derive from active/recent events and state priority. Show "doing / because / since" instead of title only. |
| `apps/web/src/components/EventRow.tsx` | Simple event list item. | Currently not imported in main app. | 4 | Useful fallback component. | Duplicates FieldReportCard and is not ecosystem-styled. | Remove if unused or repurpose as compact ledger row behind Field Reports. |
| `apps/web/src/components/ExpeditionCard.tsx` | Expedition card. | Shows progress and assigned specialists. | 6 | Clear progress and next objective. | Assignments are raw IDs and not visually connected to agents or map. | Render assigned agents as tokens, show latest report, blockers, route/room location, and mission phase. |
| `apps/web/src/components/FieldReportCard.tsx` | Rich event card. | Main event visualization with XP, multipliers, flags, evidence counts. | 8 | Strong ledger visibility, useful audit detail, surfaces review and evidence. | Still reads like accounting when XP details dominate. No artifact links/previews. | Add narrative mode: report headline, participants, artifact badges, discovered things. Put full XP breakdown behind expansion or secondary row. |
| `apps/web/src/components/HQRooms.tsx` | Room map. | Best current ecosystem metaphor. | 8 | Rooms, occupancy, latest activity, review desk, state from data. | Rooms are fixed in code, no coordinates, no movement, no routes between rooms. Review room mixes incidents/events but not agent intent. | Promote to data-driven world model. Add room config seed/schema, connections, agent positions, route status, and event trails. |
| `apps/web/src/components/ReviewDesk.tsx` | Review queue panel. | Shows risky events and open incidents. | 7 | Keeps suspicious activity visible, supports observability. | "Items Needing Eyes" is useful but management-flavored. | Reframe as "Signal Desk" or "Field Review." Add why flagged, age, source, and next safe observation step. |
| `apps/web/src/components/TrophyShelf.tsx` | Milestones/artifacts display. | Progress and artifact gallery. | 7 | Good motivation/history surface. | Milestones are static and artifact entries are not rich or inspectable. | Add unlock timeline, artifact thumbnails/safe previews, badge categories, and "earned by" agent/expedition links. |
| `apps/web/src/components/VisualToken.tsx` | Small visual identity token. | Shared token for agents/systems/rooms/reports. | 7 | Separates specialist/system/room/report visual classes. | Text initials are not enough for "little guys"; shape alone is weak character identity. | Add icon/glyph mapping and tiny pose/state variants. Keep generated visuals optional and data-driven. |
| `apps/web/src/data/.gitkeep` | Empty data folder marker. | Placeholder. | 4 | Leaves room for local frontend data fixtures. | No direct value now. | Either remove once unused or add readme explaining when frontend fixtures are allowed. |
| `apps/web/src/lib/.gitkeep` | Empty lib folder marker. | Placeholder. | 4 | Leaves room for helpers. | No current value. | Add utilities for formatting/world derivation when App is split. |

### Config And Seed Data

| File | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `config/agent-roster.seed.json` | Agent/system roster. | Primary identity and state source. | 9 | Rich roles, visual names, rooms, archetypes, review boundaries, little-guy eligibility. | Mixes agents, tools, hosts, routes, interfaces in one roster; useful but can blur "participant" vs "environment." | Keep neutral roster but add relationship tables: agent owns/uses route, host runs service, room contains construct. Add `last_observed_at`. |
| `config/blockers.seed.json` | Known blockers. | Incident seed data. | 8 | Makes risks visible and prevents fake readiness. | Blockers are not tied structurally to routes, rooms, expeditions, or agents. | Add `related_route_ids`, `related_expedition_ids`, `severity`, `blocked_until`, and `next_observation`. |
| `config/dashboard.config.example.json` | UI config example. | Documents intended mode/theme/refresh flags. | 7 | Theme and redaction-aware. | `refresh_seconds` and flags are not consumed. | Either consume it or mark as future config. Add map layout setting once world model exists. |
| `config/events.seed.json` | Initial event ledger. | Story/progression seed data. | 8 | Good field-report nouns, XP metadata, risks, party agents, shadow tags. | Events are point-in-time records only; no active task intervals, intent, location, or "why now" fields. | Add `location_id`, `mission_id`, `intent`, `started_at/ended_at`, `visible_effect`, and evidence refs for all nonzero XP events. |
| `config/expeditions.seed.json` | Project/expedition list. | Long-lived work efforts. | 8 | Strong persistent ecosystem objects and assigned specialists. | Missing missions/subtasks and latest report linkage; repeated next objectives are generic. | Add mission hierarchy, current phase, blockers, route dependencies, latest_event_id, and visual location. |
| `config/hook-manifest.example.json` | Future hook policy. | Read-only ingest contract. | 9 | Clear allowed/blocked list. | Not enforced by code. | Validate incoming hook payloads against this manifest when hook adapter is implemented. |
| `config/memory-stores.seed.json` | Archive/memory inventory. | Shows vault/archive sources. | 8 | Redaction-aware notes and persistent archives. | Paths are mostly raw and not visibly represented as vault contents or artifact sources. | Add `redaction_level`, `safe_to_display`, `last_indexed_at`, and related agents/expeditions. |
| `config/milestones.seed.json` | Milestone/badge definitions. | Trophy Shelf seed data. | 8 | Badge-only Season 0.x posture avoids arbitrary XP. | Unlock status is manually static and separate from event evidence. | Add unlock evidence refs, earned timestamp, agent/expedition attribution, and milestone categories. |
| `config/planned.seed.json` | Planned future items. | Blueprint list. | 7 | Supports ecosystem growth. | Too generic for visual evolution; not linked to proposals/missions. | Convert planned items into blueprint nodes on the map with dependencies and activation gates. |
| `config/proposals.seed.json` | Seed proposals. | Proposal Desk content and safety QA probe. | 6 | Good local-only calibration and a deliberate bad proposal to test denial. | Proposal mechanics can become the center of the product. "Wager" framing can overpower observatory wonder. | Treat proposals as agent intent/suggestions feeding missions. Keep safety QA but hide test probes from normal user-facing story. |
| `config/routes.seed.json` | Routes and bridges. | Systems view route list. | 8 | Strong bridge/gate metaphor and safety status. | Routes are text strings, not a visual graph. | Add source/target nodes, route type, privacy class, health, and related blockers for graph rendering. |
| `config/season-summaries.seed.json` | XP season aggregate seed. | Calibration display and summary. | 7 | Preserves history and audit aggregates. | Summary has static totals that can drift from events; UI currently foregrounds XP metrics. | Make generated summaries authoritative at runtime. Add narrative season recap and ecosystem growth deltas. |

### Archive Artifacts

| File | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `archive/artifacts/bootstrap/agent-census-2026-05-27.redacted.json` | Sanitized initial ecosystem census. | Source artifact behind seed data. | 9 | Excellent historical foundation, redaction statement, routes, blockers, memory stores, planned items. | Large raw artifact is not user-friendly in UI. | Index it into safe artifact metadata and show as a "founding census" artifact with redaction badge and derived nodes. |
| `archive/artifacts/bootstrap/deep-research-report.md` | Origin planning report. | Historical rationale for repo boot sequence. | 8 | Preserves decision history and guardrails. | Contains mojibake in current shell rendering, and references an external file citation artifact that is not meaningful locally. | Clean encoding if the actual file is corrupted, remove orphan citation marker, and link it as an origin field report. |
| `archive/field-reports/2026-05-27-bootstrap-field-report.json` | Bootstrap field report. | Seeded historical event. | 9 | Strong proof-of-progression artifact with sentiment, XP, party agents, artifact refs. | No schema-enforced `risk_level`/`needs_review` despite prompt asking for them. | Align field-report schema with event schema. Add evidence and redaction fields. |
| `archive/milestones/map-room-founded.json` | Archived milestone. | Historical badge record. | 8 | Good sentimental/progression marker. | Duplicates milestone seed without richer evidence. | Add earned timestamp, evidence refs, related field report, and display class. |

### Database And Shared Schemas

| File | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `db/migrations/001_initial.sql` | SQLite schema. | Core persistence schema. | 8 | Includes agents, expeditions, events, milestones, incidents, routes, memory stores, planned items, artifacts, seasons, proposals. | Missing world/ecosystem continuity tables; no foreign keys/indexes; raw_json dominates. | Add foreign keys where practical, indexes, and new tables for missions, agent state history, locations, relationships, achievement unlocks, evidence, discoveries. |
| `packages/schemas/expedition-hq.schema.json` | JSON schema. | Validates conceptual data shapes. | 7 | Covers agent/event/season/proposal. | Incomplete versus actual config: no expedition, milestone, incident, route, memory store, planned item, artifact schemas. Not used by validation script. | Expand schema and have `validate_seed.py` validate each seed file against it. |
| `packages/schemas/types.ts` | Shared seed TS types. | Type reference for schema package. | 7 | Enumerates visual classes, states, events, seasons, proposals. | Drifts from frontend `types.ts`; lacks many current seed classes and future ecosystem types. | Make this the source for frontend types or generate from JSON schema. Add world model types. |
| `packages/ui/.gitkeep` | Empty UI package marker. | Placeholder for future shared UI. | 4 | Allows monorepo growth. | Empty package adds structure without value. | Either remove until needed or add a tiny package readme with criteria for extracting shared UI. |

### Documentation

| File | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `docs/AGENT_MATURITY_STATES.md` | State vocabulary. | Defines visual behavior labels. | 9 | Useful bridge from operational truth to visual state. | State meanings are flat and not lifecycle-aware. | Add allowed transitions and visual behaviors per state. |
| `docs/AGENT_XP_STATUS_PLAN.md` | XP strategy. | Current plan for competitive calibration XP. | 8 | Strong scorekeeper doctrine and anti-gaming review flags. | XP as main competitive indicator can overshadow observation, identity, and history. | Balance with non-XP prestige: discoveries, artifacts, resolved blockers, expedition continuity, "trusted guide" status. |
| `docs/ASSET_INVENTORY.md` | Human-readable asset list. | Explains people-like vs environment assets. | 9 | Excellent anti-over-personification rule. | Static list will drift. | Generate from seed data or keep as historical snapshot with date. |
| `docs/design/VISUAL_SYSTEM.md` | Visual class design rules. | Maps neutral classes to themed renderings. | 9 | Exactly supports experiential coherence without over-theming data. | Too short for implementation details. | Add icon/glyph rules, motion rules, room/route examples, and forbidden fake-motion examples. |
| `docs/GAMIFICATION_RULES.md` | XP and milestone rules. | Governs Season 0.x scoring. | 8 | Clear formula, shadow multipliers, reward-real-progress rule. | Heavy XP focus risks shallow gamification if not paired with story/history. | Add "gamification as history" section: seasons, expeditions completed, discoveries cataloged, artifacts shelved, agent growth. |
| `docs/INITIAL_EXPEDITION_MAP.md` | Initial expedition list. | Starter campaign map. | 8 | Good campaign framing. | Not visual or connected to routes/agents yet. | Convert to graph/map seed data with expedition nodes, paths, dependencies, and current active front. |
| `docs/NON_GOALS.md` | MVP exclusions. | Safety and focus boundary. | 10 | Strongly prevents control creep and fake activity. | None. | Keep prominent. Add "no gamified fake chores" if needed. |
| `docs/PROJECT_CHARTER.md` | Product charter. | North-star reference. | 10 | Directly supports observatory, little guys, expeditions, artifacts, gamification. | None. | Add explicit "environment first, dashboard second" principle. |
| `docs/PROPOSAL_REPUTATION_METRICS.md` | Proposal analytics policy. | Keeps proposal metrics advisory. | 7 | Good guardrails against accidental reputation scoring. | More analytics can move the project toward KPI tooling. | Treat proposal metrics as back-office calibration, not primary HQ view. |
| `docs/PROPOSAL_WAGER_SYSTEM.md` | Proposal soft-wager rules. | Governs Proposal Desk MVP. | 6 | Clear no-implementation/no-real-XP policy. | Wagers and denial penalties are less "enjoyable observatory" and more management game. | Reframe as "scout suggestions" with confidence and learning, not penalties. Keep simulated data hidden behind calibration. |
| `docs/ROUTES_AND_RISKS.md` | Route posture summary. | Safety map for bridges/gates. | 8 | Clear observe-not-control stance. | Text list only. | Add route graph fields and visual risk cues. |
| `docs/runbooks/FIRST_CODEX_RUN.md` | First implementation checklist. | Historical runbook. | 7 | Good starter sequence. | Outdated now that MVP exists. | Mark as historical or replace with current "first local verification" runbook. |
| `docs/SEASON_0X_CALIBRATION.md` | Season XP policy. | Explains calibration, soft wagers, preservation, safety. | 8 | Good continuity and audit-history rule. | Still centered on XP mechanics. | Add season narrative recap expectations and ecosystem growth metrics. |
| `docs/SUCCESS_CRITERIA.md` | Success criteria. | MVP and little-guy success definitions. | 9 | Clear observability and state-glance targets. | Criteria are mostly presence-based, not experience-based. | Add criteria: "user can infer agent activity in 5 seconds," "map shows route/blocker relations," "field reports link to artifacts." |

### Hooks And Skills

| File | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `hooks/openclaw/README.md` | Future hook adapter policy. | Read-only integration placeholder. | 9 | Excellent allowed/blocked boundary. | Not implemented. | Add expected event envelope and redaction checks before any live hook. |
| `hooks/openclaw/event-ingest.example.json` | Example event payload. | Future ingest sample. | 8 | Shows safe metadata, XP inputs, API-computed XP. | Missing evidence refs for nonzero claim, so current XP audit would flag it. | Add `evidence_refs` or set `active_minutes` to 0 in example. |
| `skills/codex/README.md` | Project-local Codex skill intent. | Future agent reporting guide. | 8 | Aligns Codex work with field reports and no control mutation. | Placeholder only, not an actual Codex skill manifest. | Turn into usable local skill or rename as prompt guide. Include current event schema. |
| `skills/codex/write-field-report.prompt.md` | Field report prompt. | Template for reporting completed work. | 8 | Encourages factual reports and no invented success. | Mentions `suggested_xp`, while API owns XP calculation. | Replace `suggested_xp` with `active_minutes`, evidence refs, multiplier inputs, and "API computes XP." |

### Scripts

| File | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `scripts/validate_seed.py` | JSON validation. | Confirms seed JSON loads and key agents exist. | 7 | Useful local quality gate, excludes runtime/vendor. | Does not validate against JSON schema or required fields deeply. | Add schema validation per file and cross-reference checks for IDs. |
| `scripts/init_db.py` | DB seed initializer. | Rebuilds SQLite from seed. | 7 | Simple and clear. | `force=True` deletes local event/proposal records without warning if run casually. | Print warning or add `--force` flag. Consider backup before reset. |
| `scripts/new_field_report.py` | Creates placeholder field report JSON. | Manual field report helper. | 7 | Encourages archive-first behavior. | Uses file writes only, not API ingest; missing risk/review/evidence fields; can create placeholder reports that look real if not edited. | Add CLI arguments, required summary/evidence for nonzero minutes, and optional API POST. Mark draft status until completed. |
| `scripts/log_xp_claim.py` | CLI for local XP claim POST. | Cross-project event/XP submission helper. | 8 | Practical, evidence gate, dry-run, local API only. | It can make activity logging easier than thoughtful field reporting. | Add `--why`, `--outcome`, `--artifact-title`, and maybe write a field report artifact alongside the event. |
| `scripts/Start-ExpeditionHQ.ps1` | Starts API and web locally. | Durable local dev/startup launcher. | 8 | Resolves venv/bundled runtime, hidden windows, status file, logs under ignored runtime. | It launches services, which is fine locally but not part of observatory UX. It assumes Vite installed. | Add health HTTP checks beyond port listening, and surface `runtime/status.json` in UI read-only. |
| `scripts/Register-ExpeditionHQStartup.ps1` | Registers Windows startup. | Optional per-user persistence. | 7 | Useful for persistent observatory. Fallback shortcut is pragmatic. | Mutates Windows Task Scheduler/startup state, which is outside pure read-only app behavior. | Keep script manual-only. Add verification of actual status side effects and unregister docs. |
| `scripts/bootstrap-local.ps1` | Windows bootstrap helper. | Validates seed and initializes DB. | 6 | Simple. | Uses plain `python`, currently fails in this shell. | Use `.venv\Scripts\python.exe` fallback or same Resolve-Tool logic as start script. |
| `scripts/bootstrap-local.sh` | Unix bootstrap helper. | Cross-platform starter. | 6 | Simple. | Less relevant to current Windows machine; uses plain `python`. | Keep but mention `python3` fallback. |

### Tests

| File | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `tests/e2e/README.md` | E2E smoke target. | Manual target list. | 6 | Names API and core render expectations. | No executable browser test; criteria are now behind actual app maturity. | Add Playwright smoke test for HQ map, room occupancy, field reports, trophy shelf, proposal no-autostart. |

### Runtime, Generated, And Ignored Categories

| Path/Category | Purpose | Current Role | Score | Strengths | Conflicts With Thesis | Recommended Changes |
|---|---|---:|---:|---|---|---|
| `.venv/` | Python virtual environment. | Local dependency runtime. | N/A | Makes API testable with direct Python path. | Vendor/runtime content is not project architecture. | Keep ignored. Document direct venv commands. |
| `apps/web/dist/` | Vite production build output. | Generated web bundle from verification. | N/A | Confirms build works. | Generated artifact should not be audited as source. | Keep ignored and regenerate when needed. |
| `data/*.db*` | Local SQLite state. | Live local data store. | N/A | Supports local-first persistence. | Can contain local events and should not be source controlled. | Keep ignored. Add backup/export strategy before resets. |
| `runtime/` | Logs, smoke screenshots, temp DBs, pytest temp. | Local verification and startup output. | N/A | Useful proof and diagnostics. | Runtime artifacts can contain stale or private local state. | Keep ignored. Consider a safe redacted status endpoint/preview only. |
| `.git/` | Version control metadata. | Repo history. | N/A | Supports provenance. | Not product source. | No audit action. |

## Ecosystem Compatibility Summary

What already supports the thesis:
- The nouns are right: agents, expeditions, events, artifacts, routes, incidents, milestones, reviews, archives.
- The safety posture is right: local-first, no external sends, no tunnel/token/config/memory mutation.
- The seed data is rich enough to make a real ecosystem rather than a fake demo.
- The UI has a promising room map, trophy shelf, field reports, current activity, state colors, and read-only banner.
- XP calibration is implemented with server-side scoring and review flags, which keeps gamification auditable.

What only partially supports it:
- Agents are visible, but mostly as tokens/cards, not animated participants in a place.
- Expeditions exist, but they are not decomposed into missions/tasks or visually connected to agent motion.
- Routes exist, but they are text rows rather than bridges/gates in a graph.
- Field reports exist, but evidence/artifacts are counts or paths, not inspectable safe artifacts.
- Milestones exist, but unlock history is manual/static and not strongly tied to reports.

What conflicts with the thesis:
- The Proposal Desk and analytics are locally safe, but they feel closer to a management console than an observatory.
- The metric grid and calibration scoreboard are useful, but risk making the first impression "KPI dashboard."
- Data loading is snapshot-only; no refresh or "last observed" state means the ecosystem feels less alive.
- Static room definitions in code block the world from evolving through data.

## UX Alignment

The UI encourages observation more than control on the main HQ page. The read-only banner is strong, and the HQ rooms are the best experiential feature. The Proposal Desk introduces direct decision controls, but those controls are local-only and clearly labeled as non-implementation records.

Activity clarity is moderate. Users can see latest signals, field reports, review items, and state counts. They cannot yet understand at a glance why a specific agent is active, where it moved from, what it is trying to accomplish next, or how it relates to the surrounding routes and rooms.

Exploration is present through tabs, but not through the ecosystem itself. A user explores lists, not the HQ world. The next UX leap is to make the HQ map the main navigational surface.

Dashboard-oriented solution: add more charts, filters, sortable tables, and proposal analytics. This would improve management clarity, but it weakens the "little AI guys" feeling.

Ecosystem-oriented solution: add a data-driven HQ map with rooms, stations, routes, agents, current missions, recent trails, artifacts, and review signals. This better supports the project vision.

Recommendation: choose the ecosystem-oriented solution first. Put analytics behind drilldowns.

## Data Model Alignment

Currently supported:
- Agents and agent-like systems.
- Expeditions as long-lived efforts.
- Events and field reports.
- Artifacts.
- Routes.
- Incidents/blockers.
- Milestones.
- Proposal records and local decisions.
- XP seasons and per-agent XP status.

Missing or underdeveloped:
- Missions/tasks as smaller units within expeditions.
- Agent state history over time.
- Agent location/room snapshots.
- Relationships between agents, routes, rooms, hosts, artifacts, and expeditions.
- Achievement unlock records.
- Discovery records.
- Evidence/redaction model for artifacts.
- Current activity signals derived from events.
- "Why doing it" and "next intended movement" fields.

Recommended schema additions:
- `rooms(id, name, role, visual_class, x, y, width, height, raw_json)`
- `route_edges(id, from_node_id, to_node_id, route_type, status, privacy_class, risk_level, raw_json)`
- `missions(id, expedition_id, title, status, current_phase, summary, next_step, raw_json)`
- `agent_assignments(id, agent_id, expedition_id, mission_id, role, started_at, ended_at, raw_json)`
- `agent_state_snapshots(id, agent_id, timestamp, ui_state, room_id, activity, reason, source_event_id, raw_json)`
- `achievement_unlocks(id, milestone_id, unlocked_at, agent_id, expedition_id, event_id, artifact_id, raw_json)`
- `discoveries(id, event_id, title, summary, confidence, redaction_level, raw_json)`
- `artifact_evidence(id, artifact_id, event_id, redaction_level, safe_preview, path, raw_json)`

## Gamification Opportunities

High-value opportunities:
- Season journey view: show ecosystem growth over time, not just XP totals.
- Agent journals: per-agent timeline of field reports, artifacts, discoveries, blockers moved, review flags.
- Badge unlock history: each badge should show why it unlocked and which agent/expedition/report earned it.
- Artifact shelf: display safe artifact cards with redaction level and origin report.
- Discovery log: non-XP discoveries should accumulate as a visible research archive.
- Ecosystem growth map: new rooms, routes, agents, and missions visibly appear over seasons.

Guardrail: XP can motivate, but it must not become the only thing worth watching. The better motivational infrastructure is continuity: "look how this ecosystem has grown."

## Observability Gaps

Hidden or trapped:
- Runtime status and logs live under `runtime/` but are not surfaced except as ignored files.
- Startup status exists in `runtime/status.json`, but UI does not read it.
- Artifacts are paths/counts, not safe previews.
- Agent latest activity is derived from title only, not a structured current state.
- Why an agent is doing something is mostly buried in event summary or agent summary.
- Route blockers are not visually connected to affected routes.
- Proposal decisions create events, but the relationship is not visualized as agent learning or mission planning.

Should become visible:
- Last observed time per agent/system.
- Current mission and reason.
- Recent movement or activity trail.
- Route health as bridges/gates.
- Blockers attached to routes/rooms/expeditions.
- Artifact shelf with safe previews and redaction badges.
- Review flags as visible signal lights, not just text chips.

Should become visual:
- HQ floor/world map.
- Agent trails from latest events.
- Route graph.
- Expedition map/mission board.
- Archive vault shelves.
- Trophy shelf unlock timeline.
- Season growth rings or map expansion.

## Major Architectural Risks

1. The system can become a pretty dashboard instead of a living ecosystem if future work keeps adding panels before adding a world model.
2. Proposal Desk controls are locally safe, but they are the main control-like affordance and could dominate the product.
3. XP can cause incentive rot if score visibility outruns audit/story visibility.
4. Schema drift is already likely: SQLite schema, JSON schema, backend models, package TS types, and frontend TS types are separate.
5. Static seed state can become stale unless refreshed from safe event ingest or explicitly labeled as historical.
6. `raw_json` preservation is useful, but it can hide schema mistakes.
7. Reset scripts can wipe local DB records if run casually.
8. Windows command ergonomics are currently brittle around `python`, `npm`, and pytest temp permissions.

## Quick Wins

High-confidence, low-risk changes:
- Add `last_observed_at` and `latest_event_id` to agent API output.
- Add `evidence_refs` to `hooks/openclaw/event-ingest.example.json`.
- Update README/bootstrap commands to use `.venv\Scripts\python.exe`, `npm.cmd`, and pytest `--basetemp`.
- Move room definitions into `config/rooms.seed.json`.
- Show assigned agents as tokens in `ExpeditionCard`.
- Add "why active" and "last seen" to `AgentCard`.
- Link field reports to artifact refs and field report path.
- Rename or visually reframe Proposal Desk as a secondary Planning Bureau.
- Consume `dashboard.config.example.json` refresh seconds or remove the field.

## Highest-Leverage Improvements

1. Build a data-driven HQ world model.
   Files affected: `db/migrations/001_initial.sql`, `packages/schemas/expedition-hq.schema.json`, `packages/schemas/types.ts`, `apps/web/src/types.ts`, `apps/web/src/components/HQRooms.tsx`, `apps/web/src/App.tsx`, `config/rooms.seed.json` new, `config/route-edges.seed.json` new.

2. Add activity-state derivation.
   Files affected: `apps/api/expedition_hq_api/db.py`, `apps/api/expedition_hq_api/main.py`, `apps/api/tests/test_seed_files.py`, `config/events.seed.json`.

3. Turn artifacts and field reports into inspectable history.
   Files affected: `archive/field-reports/*.json`, `archive/artifacts/bootstrap/*`, `apps/web/src/components/FieldReportCard.tsx`, `apps/web/src/components/TrophyShelf.tsx`, schemas.

4. Rebalance gamification from scoreboard to ecosystem growth.
   Files affected: `docs/GAMIFICATION_RULES.md`, `docs/AGENT_XP_STATUS_PLAN.md`, `apps/web/src/App.tsx`, `apps/web/src/components/AgentCard.tsx`, `apps/api/expedition_hq_api/xp.py`.

5. Consolidate schemas and validation.
   Files affected: `packages/schemas/expedition-hq.schema.json`, `scripts/validate_seed.py`, `apps/web/src/types.ts`, `packages/schemas/types.ts`.

## Prioritized Recommendations

### High Impact

- Add world model tables and seed files: rooms, route edges, missions, assignments, state snapshots.
- Promote HQ map to primary navigation surface.
- Add activity signals: what, why, since when, where, evidence, next expected movement.
- Tie blockers/routes/agents/expeditions together visually.
- Reframe Proposal Desk as secondary planning, not the center of agent activity.
- Add safe artifact/evidence model and make artifacts visible.
- Expand schema validation and cross-reference tests.

### Medium Impact

- Add auto-refresh and last-updated indicators.
- Add per-agent journals.
- Add badge unlock records and milestone evidence refs.
- Add route graph and room occupancy from config instead of hard-coded arrays.
- Add redaction levels to memory stores and artifacts.
- Add executable e2e smoke tests.
- Add command fixes for Windows local verification.

### Low Impact

- Add HTML metadata/theme color.
- Remove or repurpose unused `EventRow`.
- Add readmes for empty package/folder placeholders.
- Clean mojibake if the deep research report file itself is corrupted, not just console rendering.
- Pin dependency versions when stability matters more than freshness.

## Implementation Follow-Up: 2026-05-29

This section records the first implementation pass made after the audit. The pass deliberately favored realistic, low-to-medium blast-radius product changes over a full rewrite of the architecture.

### Changed

| Recommendation | What changed | Why |
|---|---|---|
| Move room definitions out of frontend code. | Added `config/rooms.seed.json`, seeded it into SQLite, exposed `GET /rooms`, and updated `HQRooms` to render from API data. | This is the cleanest first step toward an actual world model. It makes the HQ environment durable data instead of a decorative React constant. |
| Add route graph data. | Added `config/route-edges.seed.json`, a `route_edges` table, `GET /route-edges`, and a route-edge strip below the HQ rooms. | Routes are now visible as bridges/gates between rooms instead of plain text inventory rows. This directly supports the observatory/expedition metaphor. |
| Add `last_observed_at` and latest activity context to agents. | `GET /agents` now enriches agents with `last_observed_at`, `latest_event_id`, `latest_event_title`, and `activity_reason`. `AgentCard` shows latest report, last seen time, and current reason. | This makes agents easier to understand at a glance without opening logs. It answers "what are they doing and why?" better than a static roster. |
| Add activity-signal API surface. | Added `GET /activity-signals` and `GET /world-map`. | These endpoints establish a backend-owned activity/world layer so future UI work does not have to re-derive everything locally. |
| Gate local writes with `EXPEDITION_HQ_ALLOW_WRITE_EVENTS`. | Added API enforcement for event, XP claim, proposal creation, and proposal decision writes. Added tests. | The environment config now means what it says. This tightens compliance with the local/read-only posture. |
| Consume dashboard refresh config. | Added `GET /dashboard-config`; the frontend polls using `refresh_seconds` and shows last observed time. | This makes the observatory feel more alive while still staying read-only toward external systems. |
| Reframe Proposal Desk as secondary planning. | UI and docs now use "Planning Bureau" language for the proposal surface. | The feature remains useful, but the wording moves it away from a control desk and toward agent suggestions/planning records. |
| Show assigned specialists visually. | `ExpeditionCard` now renders assigned agents as tokens and shows the latest expedition report. | Expeditions now connect visibly to participants, not just raw agent IDs. |
| Show field-report evidence/artifact refs. | `FieldReportCard` now displays report path, evidence refs, and artifact refs when present. | This starts turning the ledger into inspectable history instead of pure XP accounting. |
| Improve seed validation. | `scripts/validate_seed.py` now checks agent-room references, route-edge room references, and expedition assigned-agent references. | The new world model needs relationship checks or it will quietly drift. |
| Update local command ergonomics. | README, `package.json`, and bootstrap scripts now prefer venv Python, `npm.cmd`, and local pytest basetemp. | The audited verification found Windows command shims were brittle. The repo now documents and scripts the commands that actually worked. |
| Update hook/skill safety examples. | OpenClaw ingest example now includes evidence refs; field-report prompt now asks for evidence and XP inputs instead of `suggested_xp`. | The API owns XP calculation, and nonzero work should point to reviewable evidence. |
| Clarify product direction. | `AGENTS.md` now says to prefer environmental state, routes, artifacts, and activity trails over another card grid or scoreboard. | This keeps future work aligned with the thesis at the project instruction level. |

### Partially Changed

| Recommendation | What changed | What remains |
|---|---|---|
| Build a data-driven HQ world model. | Rooms and route edges are now real seed/API/UI data. | Missions, assignments, state snapshots, discoveries, and achievement unlock tables are still not implemented. |
| Add activity-state derivation. | Latest event, activity reason, last observed time, and route/room context are now derived. | There is no persisted `agent_state_snapshots` table yet, so historical movement over time is still reconstructed from events. |
| Turn artifacts and field reports into inspectable history. | Field report cards now surface report/evidence/artifact refs. | There are no artifact preview cards, redaction levels, or artifact evidence tables yet. |
| Consolidate schemas and validation. | Shared TS/schema files now include rooms and route edges, and seed validation checks relationships. | The JSON schema is still not used as the validation engine for every seed file. Frontend/backend/shared type drift is reduced, not eliminated. |
| Rebalance gamification away from pure scoreboard. | UI language and agent cards now emphasize current activity and evidence more. | XP is still prominent. A true season journey, discovery log, and ecosystem-growth view remain future work. |

### Not Changed Yet

| Recommendation | Reason deferred |
|---|---|
| Add full mission/task tables. | This needs product design, migration decisions, and UI treatment. Adding a shallow table now would create another disconnected record type. |
| Add persisted agent state snapshots and movement history. | The current event ledger can support derived activity. Persistent movement history should wait until the system has a clear event-to-state transition policy. |
| Add achievement unlock records. | Milestones are still manually seeded. Unlock records should be added with evidence refs and display rules together, not as empty schema first. |
| Add redaction levels to artifacts and memory stores. | Important, but it touches archive policy and UI display rules. It should be done as a focused safety pass. |
| Add executable browser/e2e tests. | Backend tests and a manual browser smoke were done. A real Playwright suite is useful, but setting it up cleanly is a separate testing task. |
| Remove or repurpose `EventRow`. | It is unused but harmless. Removing it was lower value than implementing the world-model path. |
| Add HTML metadata/theme color. | Low impact compared with the ecosystem-model changes. |
| Pin dependency versions. | Useful for stability, but not directly tied to the product thesis and could create dependency churn. |

### Verification After Changes

- `.\.venv\Scripts\python.exe scripts\validate_seed.py` passed.
- `.\.venv\Scripts\python.exe -m pytest apps\api\tests --basetemp runtime\pytest-implementation-temp` passed: 26 tests.
- `npm.cmd run build` passed.
- Browser smoke at `http://127.0.0.1:5173/` confirmed Planning Bureau, Staging Area, Signal Desk, route-edge text, and last-observed status rendered with no API error.

### Updated Judgment

The project moved meaningfully closer to the thesis, but it is still not finished. The biggest improvement is that HQ rooms and routes are now data-backed ecosystem objects rather than hard-coded presentation. The biggest remaining gap is time: agents still do not have a durable state history, mission trail, or achievement unlock history. Those are the next changes that would make the system feel less like a dashboard and more like a living observatory.

## Long-Term Evolution Path

Phase 1: Stabilize the observatory.
- Read-only external posture stays fixed.
- Add world model, activity signals, refresh, artifact previews, and cross-reference validation.

Phase 2: Make the ecosystem persistent.
- Agent journals, mission history, route graph, season recaps, badge unlocks, discoveries, and artifact shelves.
- Agents become recognizable through consistent roles, rooms, histories, and visible contributions.

Phase 3: Add safe live integrations.
- Only ingest redacted event/status/artifact metadata.
- No external sends or control actions until the read-only MVP has proven stable.
- Every live signal must become understandable in the HQ map without reading logs.

Phase 4: Add governed semi-autonomy.
- Agents may propose missions, report progress, and submit evidence.
- Expedition HQ remains the observatory and scorekeeper.
- Controls, if ever added, should be explicit, gated, auditable, and visually distinct from the ambient observatory.

Final judgment: this project is not off-track. It is a good foundation. The danger is building more conventional dashboard machinery because it is easy and measurable. The better next move is to make the HQ itself the product: rooms, trails, missions, artifacts, and little specialists whose work is visible without reading a log.

## Proposal Council Redesign: 2026-05-29

The old Planning Bureau was locally safe, but it was still shaped like one desk making one decision. The redesign changes the product direction to a council of specialists reviewing expedition plans.

First evaluation: this is a better fit for the thesis. It keeps the dashboard local-first and read-only toward external systems, but it lets agents behave like specialists with visible judgment. Support, oppose, and abstain are easy to understand. Abstain is especially important because it records honest uncertainty instead of fake confidence.

Devil's advocate evaluation: the feature can still become a corporate approval board if the UI over-focuses on counts, verdicts, and XP. The safe direction is to show the votes as field advice around a plan, not as a managerial gate.

Substantial difference: both evaluations support the council design, but the second one warns that the product should keep the council secondary to the expedition world. The next UI pass should make proposal participation appear as specialist activity trails and field notes, not just another analytics panel.

Implemented design anchors:
- Proposals carry local broadcast status and eligible specialist lists.
- Council votes support `support`, `oppose`, and `abstain`.
- Each vote stores confidence, simple reasoning, expected benefit, expected failure mode, and risk notes.
- Peer-review XP is separate from active-time, party-size, and work-contribution XP.
- Useful assessments can receive small peer-review XP after outcome is known.
- Wrong votes and abstains are not penalized.
- External systems such as Copilot, Claude, Perplexity, Gemini, DeepSeek, Kimi, and Manus are candidate visiting specialists until profiled.

## Homepage Concept Preferences: 2026-05-30

This section records user feedback from generated homepage concept exploration. Treat it as product direction for the next HQ/homepage design pass.

Confirmed direction:
- Cute elf-like and bean-like helpers are preferred. The product should feel like clever little helpers doing work inside the computer.
- The best homepage shape is a game-like hubworld with rooms, bridges, agents, and recent handoffs, not a spreadsheet, KPI board, or technical system map.
- The screen should be friendly, colorful, cute, and readable. Avoid grim-dark styling.
- Genre explorations worth keeping alive: magical computer workshop, shire-style helper village, space base with observation monitors, toy/train/mailroom dispatch systems, and bridge-focused hubworld maps.

Clarity requirements:
- The user must be able to tell who is doing what at a glance. Helpers need consistent portraits, roles, room placement, and short activity labels.
- Any `Needs a look` graphic should match the same helper visible in the hubworld, and clicking it should lead to the relevant review, decision, or input surface.
- `Saved stuff` is not precise enough. Use `Work archives` for records, reports, artifacts, and historical work.
- The central hub must be obvious. It should be named as a work-sorting place, such as `Work Board`, `Town Square`, `Dispatch Board`, or `Mission Board`.
- Rooms should feel like spaces that multiple agents can occupy together, not single-use cards.
- `Recent handoffs` is a strong pattern when shown as a compact chain of helper portraits passing work.
- Bridges are a strong metaphor when they visibly carry notes, questions, reports, ideas, or finished work. Avoid vague `Paths` language.

Learning surface:
- The dashboard should teach basic concepts through hover/tap tooltips, small nested explanations, and repeated symbols.
- A guide, legend, or manual tab is useful only if it explains symbols that visibly appear in the hubworld.
- The product may eventually need a simple car-manual-style primer, but the homepage itself should remain intuitive enough to use without reading homework first.

Naming and state preferences:
- Avoid `awake` as a primary state; its meaning is unclear.
- Prefer plain labels such as `Doing now`, `waiting for you`, `resting`, `building`, `saving`, `checking`, `carrying note`, `questions`, `reports`, and `finished work`.
- Do not show `All local` as a prominent normal-state badge. If the system is ever not local or could expose data, surface that as a warning with consequences and suggested remediation.

Devil's advocate:
- Cute theme alone is not enough. If symbols do not repeat, helper portraits do not match alerts, or labels remain vague, the UI becomes charming but confusing.
- The right target is playful observability: game-like enough to enjoy watching, but data-backed enough that every helper, room, handoff, archive item, and review alert reflects real project state.
