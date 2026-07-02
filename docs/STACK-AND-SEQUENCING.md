# The Woodshed — Stack & Sequencing (ADR-001)

**Status:** Accepted (direction) · Jul 2 2026
**Owner:** Chris
**Related:** `docs/woodshed-validation-gameplan.md` (milestone ladder), `docs/woodshed-M0-M2-execution-plan.md`, `woodshed-lite/VOTING-AND-DEPLOY-BRIEF.md`

---

## Context

The end-state vision is large: a paywalled, OAuth, per-user practice platform (custom content, progress, the 5,000 × $10/mo target). The validation gameplan is deliberately staged and warns against building that platform before willingness-to-pay is proven ("volume never fixes a broken rate"; "resist the engineer's urge to keep building"). The tension to resolve: **pick a stack that scales to the vision, but sequence its adoption to the milestone ladder so we never build the authed platform ahead of validation.**

## Decision — target stack

- **Astro** — app + marketing shell, static now, SSR on Cloudflare later. Consistent with Chris's other projects.
- **Supabase** — Postgres + **Auth (OAuth)** + storage. One project spans the whole journey: it backs the vote board today and `auth.users` + per-user practice content tomorrow.
- **Stripe** — billing. Hosted payment link at M3; metered/subscription billing post-M3.
- **Cloudflare Pages** — hosting for `woodshed-music.com`. Wrangler direct upload now; Git-connected build later.

**The through-line is Supabase.** The votes backend built at M0 is the first brick of the real backend — same project, same conventions — not a throwaway widget. Design it Auth-ready.

## Sequencing (bound to the milestone ladder)

| Phase | Milestone | Stack move | Explicitly NOT yet |
|---|---|---|---|
| Phase 0 (now) | M0 — demo live | Static shell + **Supabase votes** + hosted email + hosted Stripe link | No Astro, no login, no billing code |
| Phase 1 (wks 3–6) | M1 / M2 — list + activation | Migrate the **shell to Astro** *iff* the build-in-public devlog/marketing grows past one page. Engine stays canonical, loaded as a client script. | No auth, no paywall |
| Post-M3 (Q4+) | M3 proven → bigger build | **Supabase Auth (OAuth)** + per-user content + **Stripe billing** in Astro | — |

## The no-fork invariant (carries across the whole plan)

The audio/notation **engine has exactly one home** (canonical `index.html`, extracted to `engine.js`). Every shell — `shell.html` today, Astro tomorrow — *mounts* it, never copies it. Astro adoption must preserve this: Astro owns chrome/routing/auth; the engine is a vanilla client island. See `project-woodshed-lite` no-fork contract.

## Consequences

- **Do now, cleanly:** Supabase voting with an Auth-ready schema (nullable `user_id → auth.users`, anon `voter_hash` for pre-login); RLS via security-definer RPCs that work for both anon and authed callers.
- **Don't pull forward:** OAuth, per-user content, and billing are post-M3. Building them earlier is the "leaky-bucket-scaling" mistake the gameplan names.
- **Astro is a Phase-1 shell decision, not a Phase-0 dependency.** It must not block the M0 launch.
- Revisit this ADR at the end-of-Q3 go/no-go (Phase 3 of the gameplan).
