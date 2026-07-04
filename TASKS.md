# Business Research AI — Project Task Status

Generated from a full read of the codebase (agents, tools, auth, database, api, services) to reflect what is actually implemented vs. stubbed/unused as of 2026-07-04.

Legend: `[x]` implemented and wired in · `[ ]` stub, dead code, or not wired in

## Core Setup
- [x] FastAPI app with lifespan startup, CORS, router registration (`main.py`)
- [x] PostgreSQL models & session handling (`database/models.py`, `database/postgres.py`, `database/crud.py`)
- [x] LangGraph pipeline wiring — 10 agent nodes, linear flow (`graphs/lead_research_graph.py`)
- [x] Excel input parsing — `Info` + `TAL` sheets with column-alias normalization (`services/excel_reader.py`)
- [ ] `app.py` — empty/unused file; `main.py` is the real entry point

## Agent Pipeline (`agents/`)
- [x] `RequirementAgent` — parses uploaded criteria + company list
- [x] `ApolloAgent` + `ApolloTool` — real Apollo.io API search
- [x] `LinkedInAgent` + `LinkedInTool` — Playwright Sales Navigator search, cookie session persistence, manual/auto login modes
- [x] `ValidationAgent` — dedupes/merges LinkedIn + Apollo leads
- [x] `EmailAgent` + `EmailTool` — generates email pattern guesses (not SMTP-verified)
- [x] `QualityAgent` + `LeadScorer` — scores leads 0–100 on field completeness
- [x] `HumanReviewAgent` — marks pipeline result `WAITING_FOR_REVIEW`
- [x] `ContactAgent` + `GoogleSearchTool.search_company_contact()` — looks up HQ phone/address/city/state/postal code via Gemini (Google Search grounding)
- [x] `CompanyAgent` — looks up industry/employee size via Gemini, merges result onto every lead in `contact_leads` as `company_data`
- [x] `RevenueAgent` + `ZoomInfoTool.get_company_revenue()` — looks up company revenue via Gemini
- [ ] `SupervisorAgent` — implemented but never added as a graph node (dead code; `human_review` goes straight to `END` instead)
- [ ] `agents/lead_agent.py` — empty file, not imported anywhere

## Auth / Sessions (`auth/`)
- [x] `LinkedInAuth` + `SessionManager` — cookie persistence to `auth/sessions/linkedin.json`
- [x] `login_linkedin.py` — standalone script, forces fresh manual login (email/password/passkey) and overwrites saved session
- [x] `ApolloAuth` + `CredentialManager` — reads `APOLLO_API_KEY` from env
- [x] `GeminiClient` (`tools/gemini_client.py`) — reads `GOOGLE_API_KEY` from env via `CredentialManager`, used by `CompanyAgent`, `GoogleSearchTool`, `ZoomInfoTool`
- (removed) `ZoomInfoAuth` — deleted; `ZoomInfoTool` no longer calls the paid ZoomInfo API, it uses Gemini instead

## API Endpoints (`api/`)
- [x] `GET /` — health check
- [x] `POST /research/start` — upload Excel, run graph per company (via `asyncio.to_thread`), persist leads to DB
- [x] `GET /leads/` — list leads, optional `status` filter (PENDING/APPROVED/REJECTED)
- [x] `PUT /review/{lead_id}` — approve/reject a lead

## Services (`services/`) — not wired into the live pipeline
- [ ] `ExcelWriter` — writes `Lead` objects to `.xlsx`; not called from anywhere in the app
- [ ] `GoogleSheetService` — gspread read/write wrapper; not called from anywhere in the app
- [ ] `Logger` — logging helper; defined but never imported/used

## Known Gaps / Next Steps
1. Decide whether `SupervisorAgent` should be wired into the graph, or removed along with `agents/lead_agent.py` if unneeded.
2. Decide whether `ExcelWriter` / `GoogleSheetService` / `Logger` should be connected to the pipeline (e.g. exporting reviewed leads) or removed as dead code.
3. `EmailAgent` only generates *guessed* email patterns — no verification (e.g. via an email-verification API) confirms deliverability.
4. Gemini free-tier calls (`CompanyAgent`, `GoogleSearchTool`, `ZoomInfoTool`) can hit transient `503`/rate-limit errors under load; each call already fails safe to `None`/`{}` rather than raising, but there's no retry/backoff yet.
5. `ContactAgent`/`RevenueAgent` now call Gemini once per company (not once per lead) — confirmed via a live 10-company/28-lead pipeline run that this was previously exhausting the free tier's `GenerateRequestsPerDayPerProjectPerModel` quota (20 requests/day for `gemini-2.5-flash`) after 1-2 companies. Even with the fix, a 10-company batch needs ~30 calls/day (10 company + 10 contact + 10 revenue), still above the 20/day free quota on a single key — expect some companies' enrichment to come back null once quota resets mid-batch. Options if this matters: request quota increase, spread runs across days, or add a second API key to round-robin.
