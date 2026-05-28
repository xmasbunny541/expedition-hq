# OpenClaw Hook Adapter Placeholder

MVP posture: read-only/event-ingest only.

Allowed future use:
- forward safe event metadata into `POST /events`
- forward redacted status summaries
- forward artifact metadata, not raw secret-bearing artifacts

Blocked:
- live control actions
- tunnel control
- token rotation
- memory mutation
- production MCP setup
