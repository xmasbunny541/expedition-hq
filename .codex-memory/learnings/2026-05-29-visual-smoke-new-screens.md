# Visual smoke new dashboard screens

observed_at: 2026-05-29
scope: Expedition HQ rollout quality

Every time Expedition HQ adds a new dashboard screen, run a visual smoke pass before calling it done. This gives fast feedback on the human-facing layer without pretending it proves the whole system is correct.

Use this before formal Playwright coverage exists. Once repeated visual checks stabilize, promote them into Playwright tests.

