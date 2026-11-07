# NBA Lab plan

Basketball Reference's functionality with a modern design, plus features bbref doesn't have (custom formula stats).

## Decisions so far
- V1 features: **formula builder** and **player pages**
- Data: **pre-fetch a fixed dataset** into SQLite, no live NBA calls while the app runs
- Stack: FastAPI backend + React/Tailwind frontend, served as one program
- Deploy to a **public link**; no deadline

## Done
- Shot data pipeline (nba_api -> SQLite -> pandas), 18 shot-based stats
- Safe formula evaluation with errors returned to the caller
- API: player search, stat list, shots, formula evaluate
- Formula builder page (player + season + formula + stat chips + breakdown)
- Frontend built and served by FastAPI on one port

## Phase 0: Data foundation (blocked until NBA stats is reachable again)
- [ ] Choose the dataset (which players, which seasons). Check size: shots are ~1,000 rows per player-season
- [ ] Resumable fetch script: skips what's already stored, sleeps between requests, retries on timeout
- [ ] Fetch season stats (per-game and totals) as well as shots, since player pages need them
- [ ] Clean schema: players, season_stats, shots. No duplicate rows, one season label format (fixes the "2025" row)
- [ ] API stops fetching live; unknown player/season returns a clear message

## Phase 1: Player pages
- [ ] Routing and a shared page layout (React Router)
- [ ] Search -> player page
- [ ] Season table: per game, totals, shooting splits, computed TS% and eFG%
- [ ] Career summary
- [ ] API: player profile and season stats endpoints
- [ ] Link from a player page into the formula builder, pre-filled

## Phase 2: Formula builder v2
- [ ] Build custom stats by picking zone and shot type, instead of only the fixed list
- [ ] Allow box-score stats in formulas (for example PTS, AST), not just shot percentages
- [ ] Warn on small samples (HookShot_PCT can be 7 attempts)
- [ ] Replace text substitution with a proper tokenizer, so stat names can't clobber each other
- [ ] Saved formulas (browser storage first)

## Phase 3: Design pass
- [ ] Design system: colors, type, spacing, components
- [ ] Navigation, page layouts, responsive behavior
- [ ] Empty, loading and error states
- [ ] Review the whole app against bbref's weak points (the reason this project exists)

## Phase 4: Deployment
- [ ] Pick a free host and check its current limits (Render and Fly.io are common options)
- [ ] Decide how the database ships (your .db is gitignored, so a fresh deploy starts empty)
- [ ] Production run command, pinned Python and package versions
- [ ] Public link in the README

## Phase 5: Quality and polish
- [ ] Real tests (pytest): calculate_stat, formula evaluation, API endpoints
- [ ] README with screenshots and a short "how it works"
- [ ] Remove old script-style files in tests/ or turn them into tests

## Later (not in V1)
- Shot chart visualization (court plot, data already exists)
- Leaderboards and player comparison, including custom stats
- Team pages
- Shareable formula links

## Open questions
- Dataset scope: all active players for the last few seasons, or a smaller curated set?
- Which box-score stats go in the player page and the formula builder?
- Database shipping approach for deployment
- Project name and branding ("NBA Lab"?)
