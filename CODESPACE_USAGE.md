# Codespace Usage Strategy

Goal: finish the 5‑week roadmap without exceeding the free 60 hrs/month Codespaces quota.

## Hour Budgets

| Week | Focus            | Target Codespace Hours | Notes                              |
|------|------------------|------------------------|------------------------------------|
| 1    | M1 Content       | 30                     | Heavy coding → keep Codespace open |
| 2    | M2 Media         | 25                     | Voice/B-roll integration           |
| 3    | M3 Assembly      | 25                     | Split coding (cloud) + testing (local) |
| 4    | M4 Review UI     | 20                     | UI polish mostly local testing     |
| 5    | M5 Publishing    | 20                     | Integrations, can run locally      |

Total target: 120 hours (fits 2 months of free 60 hr quotas).

## Usage Rules

1. **Codespace only for coding/testing:** All implementation happens in `xseller-video-analysis`.
2. **Pause when idle:** After each session run `gh codespace stop --codespace xseller-video-analysis-…`.
3. **Local/Docs tasks:** Planning, documentation, and Notion updates happen locally/offline.
4. **Hour check:** Every Friday run `gh codespace list --repo gurharnimrat-xseller/xseller-ai-automation` and log hours.
5. **Overflow plan:** If hours exceed budget, either
   - Move more testing to the 2017 Mac locally, or
   - Purchase extra hours (~$0.18/hr, 92 hr ≈ $17) and update the budget tracker.

Stick to this schedule to stay within the approved $75/mo budget.
