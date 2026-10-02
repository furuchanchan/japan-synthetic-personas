# Japan Launch Check — live demo

A small Cloudflare Workers app that turns a product idea into **hypothesis reactions
from 4 synthetic personas** and **5 neutral questions to ask real people in Japan**.

Public demo URL: [https://japan-launch-check.frosty-rice-fdbc.workers.dev](https://japan-launch-check.frosty-rice-fdbc.workers.dev)

## What it does

- You submit an idea (`idea`, 20–1200 chars, required), plus optional `price`
  (≤120 chars), `language` (`en` | `ja`, default `en`), and `audience`
  (`all` | `young-adults` | `working-age` | `older-adults`, default `all`).
- The Worker deterministically selects 4 personas from a **48-record illustrative
  subset** of the `furuchanchan/japan-synthetic-personas` dataset (CC BY 4.0;
  built on NVIDIA Nemotron-Personas-Japan conditioned on e-Stat income statistics,
  with TechWorker synthetic additions; modified by sampling).
- Your submitted idea is processed by **Cloudflare Workers AI**
  (`@cf/meta/llama-3.3-70b-instruct-fp8-fast`) to generate one concern and one
  question per persona, 3 cross-cutting themes, and 5 neutral survey questions.
- Output is strictly validated (exact counts, bounded strings, persona IDs must
  match the selected profiles). There is **no fallback** — invalid or failed
  inference returns an error.

## Honest limits

- These are **synthetic** profiles: hypotheses for what to ask real people,
  **not** a real survey, not real respondents, and not a representative or
  calibrated prediction of the Japanese market.
- Shared trial budget: **15 AI attempts per UTC day globally** — failed attempts
  count. Plus a best-effort **2 requests per IP per 60 seconds** rate limit.
- Idea text is processed for generation and not stored by this app; logs contain
  request counts and status only.

## Develop locally

```bash
npm ci
npm run types        # generate binding types before typecheck
npm run dev          # wrangler dev (local Worker + static UI)
npm test             # vitest (Workers pool; AI is stubbed, not live inference)
npm run typecheck    # tsc --noEmit
npm run deploy:dry   # wrangler deploy --dry-run
npm run deploy       # wrangler deploy
```

API surface: `POST /api/test`, `GET /api/health`, `GET /openapi.json`
(see `src/openapi.ts`).

For your own deployment, replace `account_id` in `wrangler.jsonc` with your
Cloudflare account and log in with Wrangler. Local `npm run dev` uses remote
Workers AI and can consume that account's AI allowance; automated tests stub AI.

## From synthetic to real

When a decision rides on the answer, the generated questions can be put to real
Japanese respondents: **$0.30 per person-question, minimum 3,000
person-questions** (e.g. 10 questions × 300 people = $900). Scope and price are
confirmed first — nothing is ordered or billed automatically.
Contact: **info@techworker.co.jp**.

## Status

Cloudflare demo and HTTP API are deployed. Hugging Face / Vercel mirror hosting and marketplace acceptance remain pending.
