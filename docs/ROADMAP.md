# CarbonIQ MVP Roadmap

## 1. Delivery approach

The team will deliver the product through vertical milestones rather than building all subsystems to completion in isolation. Each milestone ends with an integrated, demonstrable user outcome.

Target duration: eight weeks for a six-person academic team. Dates can be assigned after the team confirms availability.

## 2. Team workstreams

| Workstream | Primary ownership | Main repository areas |
|---|---|---|
| Frontend and UX | Person 1 | `apps/web/` |
| API, database, and authentication | Person 2 | `services/api/app/api`, `core`, `database`, `models`, `schemas`, `services` |
| Data pipeline and market dataset | Person 3 | `data/`, `scripts/`, `services/api/app/data_pipeline/` |
| Scoring, recommendation, and optimization | Person 4 | `scoring/`, `recommendation/`, `portfolio/` |
| RAG, risk signals, and explainability | Person 5 | `rag/`, `risk/` |
| Testing, DevOps, security, and integration | Person 6 | `tests/`, `infrastructure/`, `.github/workflows/`, Docker and integration documentation |

Ownership identifies the primary reviewer and does not prevent collaboration. Changes to another workstream's public contract require that owner's review.

## 3. Milestone 0 - Contracts and project governance

### Goal

Create a shared definition of the product before parallel implementation begins.

### Outputs

- Approved project scope
- User journeys and navigation map
- Data entities and enumerations
- Versioned API contract
- Scoring and risk semantics
- Functional and non-functional requirements
- Branch and pull-request conventions

### Exit criteria

- All six members approve the MVP boundaries.
- Shared JSON examples use the same field names and score directions.
- GitHub issues reference stable requirement IDs.
- Unresolved design decisions have an owner and due date.

## 4. Milestone 1 - Runnable vertical foundation

### Target

Week 1-2

### User outcome

A user opens the web catalogue and views ten projects delivered by the real API and database.

### Work

- Scaffold Next.js frontend and FastAPI application
- Configure PostgreSQL, migrations, Docker Compose, and environment examples
- Implement health, project-list, and project-detail endpoints
- Create and import ten validated seed projects
- Build catalogue and project-detail screens
- Add temporary contract-compliant score and risk fields
- Establish formatting, linting, test, and CI commands

### Exit criteria

- A clean checkout starts using documented commands.
- `GET /api/v1/health` reports a working database.
- The frontend renders ten database-backed projects.
- Contract tests validate the first API responses.
- CI passes.

## 5. Milestone 2 - Discovery and comparison

### Target

Week 2-3

### User outcome

A user can efficiently narrow the catalogue and compare projects.

### Work

- Expand the dataset to at least 30 projects
- Implement search, filters, sorting, and pagination
- Implement project comparison
- Add provenance, freshness, partial-data, and synthetic-data labels
- Add map visualization for valid coordinates
- Complete catalogue and comparison accessibility states

### Exit criteria

- Required catalogue filters work through API and URL state.
- Two to four projects can be compared.
- Missing data is displayed as unavailable, not zero.
- Import validation tests cover invalid and duplicate records.

## 6. Milestone 3 - Scoring and risk intelligence

### Target

Week 3-4

### User outcome

A user can understand project strengths, evidence confidence, and warning signals.

### Work

- Implement scoring methodology version `1.0.0`
- Implement confidence calculation and minimum-evidence rule
- Implement initial deterministic risk-warning rules
- Add score recalculation and version storage
- Build score breakdown and warning interfaces
- Add explanations, evidence links, and disclaimers

### Exit criteria

- Scoring tests prove range, monotonicity, determinism, and weight totals.
- Unscorable projects show **Insufficient evidence**.
- Risk warnings contain stable codes, evidence, and rule versions.
- The UI clearly communicates that lower risk scores are better.

## 7. Milestone 4 - Preferences, recommendations, and portfolios

### Target

Week 4-5

### User outcome

A buyer receives personalized recommendations and a feasible diversified portfolio.

### Work

- Implement buyer authentication and authorization
- Implement preference-profile CRUD
- Apply hard constraints and match-score ranking
- Add reasons, trade-offs, and recommendation disclaimers
- Implement optimization constraints and infeasibility explanations
- Build preference, recommendation, and portfolio interfaces
- Store calculation and data-snapshot versions

### Exit criteria

- Recommendation rankings respond predictably to changed preferences.
- Portfolio totals are calculated server-side.
- Generated portfolios respect budget, quantity, and concentration constraints.
- Infeasible requests identify conflicting constraints.

## 8. Milestone 5 - Document intelligence

### Target

Week 5-6

### User outcome

A buyer asks a project question and receives an evidence-grounded answer.

### Work

- Secure PDF ingestion and status tracking
- Text extraction, chunking, metadata, and embeddings
- Project-scoped retrieval
- Answer generation with evidence references
- Supported, insufficient, conflicting, and unavailable answer states
- RAG evaluation fixture set
- AI-unavailable fallback interface

### Exit criteria

- At least five projects have processed documents.
- Supported answers cite a document and page where available.
- Unsupported questions return an explicit insufficient-evidence response.
- Prompt injection in document text does not override system behaviour in evaluation fixtures.

## 9. Milestone 6 - Simulation, reporting, and analytics

### Target

Week 6-7

### User outcome

A buyer simulates an order and downloads a transparent portfolio report.

### Work

- Simulated-order confirmation and immutable snapshot
- Report or certificate generation
- Mandatory non-transactional disclaimer
- Portfolio and market summary charts
- Safe product-event instrumentation
- End-to-end primary-journey test

### Exit criteria

- No payment, registry transfer, or retirement is initiated.
- The report contains allocations, sources, score versions, warnings, and timestamp.
- The primary end-to-end test completes from login through report download.

## 10. Milestone 7 - Hardening and final delivery

### Target

Week 7-8

### User outcome

Evaluators can reliably run and understand the complete MVP.

### Work

- Security and authorization review
- Accessibility and responsive-layout review
- Performance profiling against MVP targets
- Error, empty, partial-data, and recovery-state review
- Reproducible deployment and seed process
- User guide, API documentation, and architecture documentation
- Demo account, rehearsal script, and backup recording
- Update the presentation with actual product screenshots and measured results

### Exit criteria

- All Must requirements pass.
- CI and end-to-end tests pass from a clean checkout.
- No unresolved critical security or data-integrity issue remains.
- The deployed demo and documented local setup both work.
- Claims in the report and presentation match implemented behaviour.

## 11. Integration checkpoints

The whole team integrates at least twice per week.

At every checkpoint:

1. Pull the current `main` branch.
2. Run migrations and seed data.
3. Start the full stack.
4. Run contract, unit, integration, and available end-to-end tests.
5. Demonstrate the newest vertical outcome.
6. Record blockers as issues with an owner.

Do not postpone integration until all six workstreams are individually complete.

## 12. Git and review policy

- No direct development on `main`.
- Branches use `feature/`, `fix/`, `docs/`, or `chore/` prefixes.
- Pull requests reference requirement IDs and include test evidence.
- API or data-contract changes require review from affected workstream owners.
- Database migrations are committed and never rewritten after shared use.
- Scoring and risk changes increment their methodology or rule version.
- Merge small, integrated increments rather than long-lived feature branches.

## 13. Key risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Insufficient trustworthy project data | Weak scores and recommendations | Use provenance, synthetic labels, minimum-evidence rules, and a curated acceptance dataset |
| Six modules diverge | Late integration failure | Contract-first schemas, mock responses, contract tests, and twice-weekly integration |
| Overstated AI or fraud claims | Loss of credibility | Use deterministic warnings, explainability, disclaimers, and human-review language |
| RAG hallucination | Unsupported answers | Project-scoped retrieval, citations, answer states, and evaluation fixtures |
| Scope expansion | Incomplete MVP | Protect the out-of-scope list and require explicit change approval |
| External service failure | Broken demo | Graceful AI fallback, seeded local data, cached documents, and backup recording |
| Security defects | Exposure or unauthorized access | Server-side authorization, secret handling, safe uploads, tests, and final review |

## 14. Future phases after the MVP

### Phase 2 - Intelligent platform

- Registry and licensed market-data integrations
- Expert-reviewed project-type scoring rubrics
- Continuous news and evidence monitoring
- Evaluated machine-learning ranking models
- Stronger geospatial change-detection prototype

### Phase 3 - Marketplace readiness

- Verified buyer and seller onboarding
- Legal and regulatory assessment
- KYC, KYB, AML, and sanctions workflows
- Payment, settlement, registry transfer, and retirement integrations
- Production audit, dispute, and reconciliation processes

### Phase 4 - Advanced ecosystem

- Satellite-assisted digital MRV
- Forward-credit delivery-risk modelling
- Article 6 and CORSIA intelligence based on current authoritative rules
- Insurance or risk-protection integrations
- Multi-market and multi-currency support

Future capabilities require separate legal, scientific, data-licensing, security, and operational validation before production use.
