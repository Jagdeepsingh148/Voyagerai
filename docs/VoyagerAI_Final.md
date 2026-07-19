# VoyagerAI — Final Plan (Zero-Budget, Final-Year 10/10 Target)
### Multi-Agent Travel Planning Platform powered by LangGraph

---

## 0. What This Revision Changes

Two problems were fixed from the prior plan:

1. **Cost risk.** Amadeus is being decommissioned (self-service portal shuts down July 17, 2026 — new signups already paused). Google Maps requires a billing card. Render's free Postgres expires after 30 days. All three are swapped for genuinely free, no-card alternatives below — same architecture, different vendor behind each box.
2. **"10/10" as a CSE-AIML final-year project, not just as an engineering build.** The original plan is a strong *application engineering* project but is light on demonstrable ML/AI contribution — almost everything AI-related was "call Gemini via LangGraph." A 10/10 rating from AIML examiners needs a visible evaluation component, not just a working agent pipeline. This revision adds that as a first-class deliverable (Section 4, Week 13) rather than an afterthought.

---

## 1. Zero-Budget Tech Stack (Final)

| Layer | Technology | Why / Note |
|---|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS, ShadCN UI, React Query, Zustand | Unchanged — free, standard |
| Frontend hosting | **Vercel (free tier)** | Built for Next.js, no card, no cold-start issues |
| Backend | FastAPI, LangGraph, LangChain, Pydantic v2, SQLAlchemy 2.0, Alembic | Unchanged |
| Backend hosting | **Render (free web service)** | No card; wake it up before demos to avoid cold-start |
| AI Models | Gemini 2.5 Pro (reasoning agents), Gemini 2.5 Flash (cheap/fast agents) | Free tier at AI Studio, no card needed for dev-scale use |
| Database | **PostgreSQL + pgvector on Neon (free tier)** | Scale-to-zero, no forced deletion (unlike Render's 30-day expiry), no card |
| Cache | **Redis via Render Key Value (free tier)** | 25MB/50 connections — enough for this project's caching/rate-limiting |
| Flights | **Synthetic Flight Data Service (self-built mock)** | Replaces Amadeus (shutting down); same interface, same ranking logic |
| Maps/Directions | **Leaflet.js + OpenStreetMap tiles + OpenRouteService** | Free, no card, replaces Google Maps SDK/Directions |
| Places/Geocoding | **Nominatim / LocationIQ (free tier)** | Replaces Google Places |
| Weather | OpenWeather (free tier) | Unchanged |
| Search | Tavily (free tier) | Unchanged |
| Reliability | `tenacity`, Redis-based rate limiting | Unchanged |
| Observability | LangSmith (free tier), `structlog` | Unchanged; Prometheus/Grafana dropped (not worth it on free hosting) |
| CI/CD | GitHub Actions, `ruff`, `black`, `mypy`, `pytest`, Docker | Unchanged |

**Total monthly cost: $0.** No step in this plan requires a credit card.

---

## 2. What "10/10" Actually Requires (beyond a working app)

Examiners grading a working prototype vs. a 10/10 project are usually looking for five things most student projects skip:

1. **A measurable AI/ML contribution**, not just "I called an LLM API." → Section 4, Week 13: an evaluation harness (LLM-as-judge + rule-based checks) scoring itinerary quality, plus an ablation comparing your multi-agent design against a single-prompt baseline.
2. **Evidence the system actually works under stress**, not just the happy path. → Failure-injection tests: killed API mid-call, invalid destination, budget that can't be met, conflicting constraints.
3. **Professional documentation**: architecture diagrams, ER diagram, a short demo video, and a README a stranger could deploy from.
4. **A clear, rehearsed narrative for the viva** — why multi-agent instead of single-agent, why LangGraph instead of a custom state machine, what the RAG component actually retrieves and why it matters, what the evaluation numbers show.
5. **Something uniquely yours** — one feature or finding that isn't in every other "AI travel planner" GitHub repo. Pick one (see Week 13 options) and go deep on it rather than adding more surface features.

These are woven into the week plan below rather than bolted on at the end.

---

## 3. Architecture (unchanged, still correct)

```
                              User
                               │
                               ▼
                      Next.js Frontend (Vercel)
                               │
                               ▼
                       FastAPI API Layer (Render)
                               │
                               ▼
                   LangGraph Orchestrator
                               │
                               ▼
                  Destination Resolution
                   (fast, runs first)
                               │
              ┌────────────────┴────────────────┐
              │                                  │
              ▼                                  ▼
       Research Team                       Booking Team
   (Weather + Attraction)           (Flight ‖ Hotel ‖ Transport)
              │                                  │
              └────────────────┬─────────────────┘
                                ▼
                         Planning Team
                    (Budget Agent → Itinerary Agent)
                                │
                                ▼
                          Review Agent
                       (conflict detector)
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
         Budget conflict  Weather conflict  Route conflict
              │                 │                 │
              ▼                 ▼                 ▼
         Booking Team     Research Team      Planning Team
```

Research and Booking only need destination + dates, never each other's output, so they run in true parallel. Planning waits for both to join.

---

## 4. Pre-Day-1 Checklist (do this before writing any code)

- [ ] GitHub repo created, monorepo structure (`/backend`, `/frontend`) scaffolded
- [ ] Neon account + Postgres project created, `pgvector` extension confirmed available
- [ ] Render account created (web service + Key Value, no card entered)
- [ ] Vercel account created
- [ ] Google AI Studio account + Gemini API key generated
- [ ] OpenWeather, Tavily, OpenRouteService, LocationIQ free-tier keys generated
- [ ] LangSmith account created (free tier)
- [ ] Docker + Docker Compose installed and tested locally
- [ ] Python 3.11+, Node.js 20+ installed
- [ ] `.env.example` written listing every key name you'll need across all 13 weeks, even ones you won't touch until Week 5
- [ ] One day spent on the official LangGraph quickstart if you haven't built a `StateGraph` before — Week 3 assumes this, not teaches it

---

## 5. Week-by-Week Plan (13 weeks, ~4–5 hrs/day)

### Week 1 — Foundation & Environment Setup
**Goal:** A running skeleton, not features.
- Monorepo (`/backend`, `/frontend`); FastAPI skeleton with health-check endpoint
- Docker Compose for **local dev only** (Postgres+pgvector, Redis) — production uses Neon + Render Key Value
- Alembic baseline migration; `pydantic-settings` for config/secrets
- Next.js 14 + TypeScript + Tailwind + ShadCN scaffold
- GitHub Actions: lint job (`ruff`, `black`, `mypy`) from day one
- **Deliverable:** `docker compose up` brings up API + DB + Redis locally; frontend renders a placeholder; CI passes.

### Week 2 — Auth & Core Data Models
- SQLAlchemy models: `User`, `Trip`, `Preference`, `Flight`, `Hotel`, `Itinerary`
- Alembic migrations; JWT auth (register/login/refresh); password hashing + reset flow
- Pydantic schemas for auth + trip endpoints; profile GET/PATCH
- **Deliverable:** Full auth flow testable via Swagger; protected routes 401 without a token.

### Week 3 — LangGraph Core & State Design
- `GlobalState` (TypedDict): trip_id, user_id, destination, budget, dates, research_results, booking_results, planning_results, approval_status, final_plan
- Team-level sub-states; `StateGraph` skeleton with stub pass-through nodes
- **Postgres-backed LangGraph checkpointer** on Neon
- **Tool Registry** pattern: base `Tool` interface so agents never call external services directly (this abstraction is what lets you swap in mock flight data cleanly in Week 5)
- Stub Global Supervisor node + routing function
- **Also this week:** build the four documentation diagrams (architecture, LangGraph execution graph, ER diagram, agent state-flow) while the design is fresh — don't leave this to Week 13
- **Deliverable:** Empty-but-correct graph runs end-to-end with stub nodes, persists/resumes state via Neon.

### Week 4 — Destination Resolution + Research Team
- Destination Agent (resolves vague input like "somewhere warm in December")
- Weather Agent (OpenWeather)
- Attraction Agent (Tavily + Nominatim/LocationIQ, pgvector similarity search over a seeded attractions table)
- Embedding pipeline for attraction/destination data
- **Deliverable:** Given a vague destination request, the graph returns resolved destination + weather + ranked attractions.

### Week 5 — Booking Team: Flights (Mock Service)
- Build the **Synthetic Flight Data Service**: realistic routes/prices/times/airlines, seeded in Postgres, served behind the same Tool Registry interface a real API would use
- Flight Agent: ranking logic (cheapest/fastest/balanced/premium) against the mock service
- Redis cache layer (`flight:{origin}:{dest}:{date}:{cabin}`, 6h TTL); durable fallback table in Postgres
- Retry/backoff via `tenacity`; rate limiting via Redis counters (yes, even against your own mock — it's the pattern that matters for the evaluation, not the vendor)
- **Deliverable:** Flight search returns ranked mock results, hits cache on repeat queries, degrades gracefully on simulated failure.

### Week 6 — Booking Team: Hotels & Transport + Parallel Wiring
- Hotel Agent (price/rating/distance/review-quality ranking), same cache pattern
- Transport Agent using OpenRouteService for route optimization
- Wire Research and Booking as sibling branches (LangGraph fan-out/fan-in) fed only by resolved destination
- **Measure actual end-to-end latency** via LangSmith trace timestamps — don't estimate, measure
- **Deliverable:** Research and Booking demonstrably run concurrently; Booking Team fully functional.

### Week 7 — Planning Team: Budget & Itinerary
- Budget Agent: allocates budget, flags overages, applies constraint logic
- Itinerary Agent: daily scheduling, attraction ordering by location/time-window
- Fan-in join: Planning only fires once both branches complete
- Define `final_plan` structured JSON format
- **Deliverable:** A complete structured trip plan from a single request, no approval yet.

### Week 8 — Review Agent, Conditional Routing & Human-in-the-Loop
- Review Agent: conflict detection (budget, weather, route/distance)
- Conditional routing to the right team per conflict type
- HITL via `interrupt()` at flight/hotel/final-itinerary approval
- FastAPI resume endpoint; guard against infinite review loops
- **Deliverable:** A run pauses for approval and resumes correctly — verified by killing and restarting the API process mid-run.

### Week 9 — Memory & RAG
- Long-term memory (past trips, preferences, budget habits) in Postgres
- Short-term memory in Redis (24h TTL)
- RAG knowledge base: travel guides, visa info, safety info, local transport info — ingested and embedded, queried via pgvector during Research
- **Deliverable:** Returning users' preferences influence new plans; Research answers cite retrieved knowledge-base content, not just live API data.

### Week 10 — Frontend Build
- Trip creation form; live agent progress view (SSE/polling against graph state)
- Approval UI for the three HITL checkpoints
- Results dashboard: itinerary, flight/hotel cards, budget breakdown
- Leaflet + OpenStreetMap route/itinerary visualization
- **Deliverable:** A user can create a trip, watch it progress, approve checkpoints, and see the final plan through the UI.

### Week 11 — PDF Export, Sharing & Polish
- Server-side PDF export of the final itinerary (WeasyPrint)
- Shareable read-only trip links (public token-based URL)
- Profile management UI; error/loading states across all flows — this is what makes a demo look production-grade, don't skip it
- **Deliverable:** A finished trip exports as a PDF and shares via a public link.

### Week 12 — Observability, CI/CD & Deployment
- LangSmith tracing on every agent/tool call
- `structlog` structured logging across the backend
- Full CI pipeline: lint → test → Docker build → deploy
- Per-trip cost dashboard using LangSmith token counts
- Deploy: frontend → Vercel, backend → Render, DB → Neon; wake Render before any live demo
- **Deliverable:** Live, deployed app with CI/CD, full tracing, and a documented cost-per-trip figure.

### Week 13 — Evaluation, Differentiator & Viva Prep *(new — this is what pushes it to 10/10)*
This week has no new features. It exists to produce the evidence and narrative an AIML examiner is actually scoring.

**Evaluation harness (do this first — it's the core AIML deliverable):**
- Build a small labeled test set: 15–20 diverse trip requests (varied budgets, destinations, constraints, including deliberately hard/edge cases)
- Score generated itineraries two ways:
  - **Rule-based checks:** budget adherence, date/weather consistency, no route conflicts
  - **LLM-as-judge:** a separate Gemini call scoring coherence/relevance/feasibility on a fixed rubric, run against the same test set
- **Baseline comparison:** run the same 15–20 requests through a single-prompt "just ask Gemini for a full itinerary" baseline (no agents, no RAG, no tools) and compare scores side-by-side. This is your strongest piece of evidence that the multi-agent architecture is doing real work, not just adding complexity — put this table front and center in your report.

**Pick one differentiator and go deep (choose one, don't spread thin):**
- A short ablation study: how much does RAG grounding actually change itinerary quality vs. without it?
- A cost/quality tradeoff analysis: Gemini Flash vs. Pro across different agents — where does the cheaper model hold up, where does it degrade?
- A failure-injection report: deliberately break the mock flight service, feed contradictory constraints, and document how the Review Agent's conflict routing recovers (or doesn't).

**Stress/failure tests (quick, high value):**
- Invalid/nonsense destination input
- Budget that's mathematically impossible to meet
- Simulated API timeout mid-graph-run
- Concurrent requests from the same user

**Documentation & presentation:**
- README: setup instructions a stranger could follow, architecture diagrams (from Week 3), the evaluation table, cost-per-trip figure
- 3–5 minute demo video (screen recording, not live-only — protects you if the live demo has network issues on viva day)
- One-page "Results & Evaluation" section written specifically to answer "where's the ML?" before an examiner asks it

**Deliverable:** A report section and README that stand on their own as evidence of a measured AI system, not just a working app — and a rehearsed answer for why this counts as an AIML project.

---

## 6. Suggested Diagrams (build in Week 3, keep updated)
1. System Architecture Diagram (Section 3 above)
2. LangGraph Execution Diagram (exported from LangGraph's built-in visualization)
3. Database ER Diagram
4. Agent State Flow Diagram (GlobalState → team states → final_plan)

## 7. Final Submission Checklist
- [ ] Live deployed link (Vercel + Render) working, Render pre-warmed before any live demo
- [ ] GitHub repo: clean README, setup instructions, architecture diagrams, evaluation table
- [ ] Demo video recorded (backup for live demo)
- [ ] Evaluation harness results + baseline comparison table in report
- [ ] One differentiator write-up (ablation / cost-quality / failure-injection)
- [ ] Cost-per-trip figure documented
- [ ] Viva narrative rehearsed: why multi-agent, why LangGraph, what RAG retrieves and why, what the evaluation shows
