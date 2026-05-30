# E2E Tests

First smoke test target:
1. API starts.
2. `/health` returns ok.
3. `/agents` includes `openclaw-main`.
4. Web app renders Bureau HQ, Expedition Board, Field Reports, and Milestone Gallery.

## Future Playwright gate

Once the core Expedition HQ screens settle, convert repeated visual smoke checks into Playwright tests so they run reliably instead of depending on manual inspection.

Candidate checks:
1. Bureau HQ loads with real seed data and no API error state.
2. Expedition Board shows active expeditions, assigned specialists, latest report context, and clear state.
3. Field Reports render without layout overlap and keep audit/evidence signals readable.
4. Milestone Gallery and trophy/state views are visible across desktop and mobile widths.
5. Navigation between core screens works after resize and refresh.
6. No secret-looking values, unsafe controls, or fake live-control affordances are visible.

Use visual first-time-operator audits while the UI is changing quickly. Promote repeated findings into Playwright assertions after the layout and routes are stable.

Every time Expedition HQ adds a new dashboard screen, run a visual smoke pass before calling it done. This gives fast feedback on the human-facing layer without pretending it proves the whole system is correct.
