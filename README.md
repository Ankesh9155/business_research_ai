# Business Research AI

A multi-agent AI system for automated B2B lead research and enrichment. It takes a list of target companies and search criteria as input, orchestrates a LangGraph pipeline of specialized agents to discover, validate, and enrich leads across multiple data sources, then presents results for human review.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Agent Pipeline](#agent-pipeline)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Input Format](#input-format)
- [API Reference](#api-reference)
- [Data Flow](#data-flow)
- [Lead Scoring](#lead-scoring)
- [Database Schema](#database-schema)

---

## Overview

Business Research AI automates the prospecting workflow for B2B sales teams:

1. **Input**: An Excel file with target companies (TAL sheet) and search criteria (Info sheet)
2. **Research**: Agents query Apollo.io, LinkedIn, and Gemini (with Google Search grounding) to find and enrich matching leads
3. **Quality**: Each lead is scored 0–100 based on data completeness
4. **Review**: A human-in-the-loop gate lets your team approve or reject leads before export

---

## Architecture

```
FastAPI (app.py)
│
├── POST /research/start ──► ExcelReader ──► LangGraph Pipeline
│                                                    │
│           ┌────────────────────────────────────────┘
│           ▼
│   [RequirementAgent]  ← parse criteria + companies
│           │
│   [ApolloAgent]       ← search leads by job title per company
│           │
│   [LinkedInAgent]     ← verify + enrich via LinkedIn
│           │
│   [ValidationAgent]   ← data quality checks
│           │
│     ┌─────┼─────┐
│     ▼     ▼     ▼
│  [Email][Company][Contact]   ← parallel enrichment
│     └─────┼─────┘
│           │
│   [RevenueAgent]      ← Gemini-sourced revenue data
│           │
│   [QualityAgent]      ← score leads 0–100
│           │
│   [HumanReviewAgent]  ← set status = WAITING_FOR_REVIEW
│           │
│        PostgreSQL     ← persist all leads
│
├── GET  /leads/        ──► return all leads from DB
└── PUT  /review/{id}   ──► approve or reject a lead
```

---

## Agent Pipeline

| Order | Agent | Responsibility | Output Key |
|-------|-------|---------------|------------|
| 1 | `RequirementAgent` | Parse Excel input into structured criteria and company list | `criteria`, `companies` |
| 2 | `ApolloAgent` | Search Apollo.io for people matching job titles at each company | `apollo_leads` |
| 3 | `LinkedInAgent` | Verify current role and enrich with LinkedIn profile data | `linkedin_leads` |
| 4 | `ValidationAgent` | Apply data quality validation rules | `validated_leads` |
| 5a | `EmailAgent` | Generate and verify email address patterns | `email_leads` |
| 5b | `CompanyAgent` | Look up industry and employee count | `company_data` |
| 5c | `ContactAgent` | Google-search HQ phone, address, city, state, postal code | `contact_leads` |
| 6 | `RevenueAgent` | Look up company revenue via Gemini | `revenue_leads` |
| 7 | `QualityAgent` | Score each lead 0–100 | `final_leads` |
| 8 | `HumanReviewAgent` | Halt pipeline, await human approval | `approved_leads` |

Agents 5a, 5b, and 5c run in parallel within the LangGraph state machine.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API server | FastAPI + Uvicorn |
| Agent orchestration | LangGraph + LangChain |
| LLM | Google Gemini (free tier, `gemini-2.5-flash` with Google Search grounding) |
| Database | PostgreSQL + SQLAlchemy |
| Data processing | Pandas + OpenPyXL |
| Browser automation | Playwright |
| Google Sheets | gSpread |
| Web scraping | BeautifulSoup4 |
| Logging | Loguru |
| Retries | Tenacity |

---

## Project Structure

```
business_research_ai/
├── app.py                  # FastAPI application factory
├── main.py                 # Entry point (uvicorn)
├── config.py               # Settings and constants
├── create_tables.py        # One-time DB schema creation
├── requirements.txt
│
├── agents/                 # One file per pipeline agent
│   ├── supervisor.py
│   ├── requirement_agent.py
│   ├── apollo_agent.py
│   ├── linkedin_agent.py
│   ├── validation_agent.py
│   ├── email_agent.py
│   ├── company_agent.py
│   ├── contact_agent.py
│   ├── revenue_agent.py
│   ├── quality_agent.py
│   └── human_review_agent.py
│
├── graphs/
│   ├── lead_research_graph.py  # LangGraph state machine definition
│   └── state.py                # Shared TypedDict state schema
│
├── api/
│   ├── research.py         # POST /research/start
│   ├── leads.py            # GET /leads/
│   └── review.py           # PUT /review/{lead_id}
│
├── models/                 # Pydantic models
│   ├── lead.py
│   ├── company.py
│   ├── contact.py
│   ├── sheet.py            # InfoCriteria, TALCompany, ResearchInput
│   └── response.py
│
├── database/
│   ├── models.py           # SQLAlchemy ORM models
│   ├── postgres.py         # Engine and session setup
│   └── crud.py             # DatabaseService (create, read, update)
│
├── tools/                  # External service wrappers
│   ├── apollo_tool.py
│   ├── linkedin_tool.py
│   ├── email_tool.py
│   ├── zoominfo_tool.py
│   ├── google_search_tool.py
│   ├── browser_tool.py
│   └── excel_tool.py
│
├── services/
│   ├── excel_reader.py     # Parse input Excel → ResearchInput
│   ├── excel_writer.py     # Export leads → Excel
│   ├── google_sheet.py     # Google Sheets read/write
│   ├── scorer.py           # Lead confidence scoring
│   └── logger.py
│
└── auth/
    ├── credential_manager.py
    ├── apollo_auth.py
    ├── linkedin_auth.py
    └── zoominfo_auth.py
```

---

## Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL database
- Apollo.io API key
- LinkedIn account credentials
- Google API key (free tier, for Gemini — get one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey))

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
# LLM (free tier)
GOOGLE_API_KEY=your_key_here

# Data sources
APOLLO_API_KEY=your_key_here
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/business_research_ai
```

### 4. Create the database schema

```bash
python create_tables.py
```

### 5. Run the server

```bash
python main.py
```

The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## Input Format

The system accepts an Excel file with two sheets:

### Sheet 1 — `Info` (search criteria)

| Column | Description | Example |
|--------|-------------|---------|
| Countries | Target countries | `United States, Canada` |
| Industries | Target industries | `SaaS, FinTech` |
| Job Titles | Roles to search for | `CTO, VP Engineering` |
| Employee Size | Company size range | `50-500` |
| Max Contacts Per Domain | Lead cap per company | `3` |

### Sheet 2 — `TAL` (Target Account List)

| Column | Description | Example |
|--------|-------------|---------|
| Company Name | Company to research | `Acme Corp` |
| Domain | Company website domain | `acme.com` |

---

## API Reference

### `POST /research/start`

Upload an Excel file to start a research pipeline run.

**Request:** `multipart/form-data` with field `file` (`.xlsx`)

**Response:**
```json
{
  "job_id": "uuid",
  "status": "WAITING_FOR_REVIEW",
  "leads": [
    {
      "id": 1,
      "first_name": "Jane",
      "last_name": "Doe",
      "job_title": "VP Engineering",
      "company_name": "Acme Corp",
      "email": "jane.doe@acme.com",
      "linkedin_url": "https://linkedin.com/in/janedoe",
      "confidence_score": 80,
      "review_status": "PENDING"
    }
  ]
}
```

---

### `GET /leads/`

Return all leads stored in the database.

**Response:** Array of `LeadRecord` objects.

---

### `PUT /review/{lead_id}`

Approve or reject a specific lead.

**Request body:**
```json
{
  "status": "APPROVED"
}
```

Accepted values: `APPROVED`, `REJECTED`

---

## Data Flow

```
Excel upload
  → ExcelReader.read()          → ResearchInput (criteria + TAL companies)
  → LangGraph.invoke(input)
      → RequirementAgent         → structured search params
      → ApolloAgent              → raw leads list
      → LinkedInAgent            → verified leads with profile URLs
      → ValidationAgent          → cleaned + validated leads
      → [Email|Company|Contact]  → enriched leads (parallel)
      → RevenueAgent             → leads with revenue data
      → QualityAgent             → leads with confidence scores
      → HumanReviewAgent         → persisted to DB, status = WAITING_FOR_REVIEW
  → API response with final_leads
  → Human calls PUT /review/{id} → APPROVED or REJECTED
```

---

## Lead Scoring

The `LeadScorer` service computes a confidence score from 0 to 100:

| Signal | Points |
|--------|--------|
| Company data found | 20 |
| Job title confirmed | 20 |
| LinkedIn URL present | 20 |
| Email verified | 20 |
| Revenue data available | 20 |

---

## Database Schema

### `research_jobs`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Job identifier |
| `status` | String | `RUNNING`, `WAITING_FOR_REVIEW`, `COMPLETE` |
| `created_at` | Timestamp | Creation time |

### `lead_records`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Lead identifier |
| `job_id` | UUID FK | Parent research job |
| `first_name` | String | |
| `last_name` | String | |
| `job_title` | String | Verified current title |
| `company_name` | String | |
| `company_domain` | String | |
| `email` | String | Best candidate email |
| `linkedin_url` | String | |
| `phone` | String | HQ phone |
| `address` | String | HQ address |
| `industry` | String | |
| `employee_size` | String | |
| `revenue` | String | From Gemini lookup |
| `confidence_score` | Integer | 0–100 |
| `review_status` | String | `PENDING`, `APPROVED`, `REJECTED` |

### `agent_logs`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Log entry ID |
| `job_id` | UUID FK | Parent job |
| `agent_name` | String | Name of the agent |
| `message` | String | Log message |
| `timestamp` | Timestamp | |
