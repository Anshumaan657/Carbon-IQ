# CarbonIQ MVP Project Scope

## 1. Product summary

CarbonIQ is an AI-assisted carbon-credit intelligence and comparison platform. It helps organizations discover projects, compare price and quality, understand risk, receive evidence-backed recommendations, and construct a diversified credit portfolio.

The MVP is an academic decision-support product. It simulates procurement but does not execute real financial transactions, transfer registry assets, or guarantee that a credit is valid for a legal or environmental claim.

## 2. Problem statement

Carbon-credit information is fragmented across registries, project documents, marketplaces, rating providers, and news sources. Projects that claim the same climate benefit may differ substantially in additionality, permanence, verification quality, delivery risk, social impact, and price. Smaller buyers often lack the specialist resources needed to evaluate these trade-offs.

CarbonIQ addresses this problem by combining structured project data, transparent scoring, preference-based recommendations, portfolio optimization, risk warnings, and document-grounded AI explanations in one workflow.

## 3. Target users

### Primary users

- Small and medium-sized organizations exploring voluntary carbon credits
- Corporate sustainability and ESG teams
- Universities and public institutions supporting climate projects
- Consultants comparing projects for clients

### Secondary users

- Carbon-project developers who want their projects presented consistently
- Researchers and students studying carbon-market quality and pricing

### MVP administrative user

- A data curator who imports, validates, and updates the sample project dataset

## 4. MVP objective

The MVP must demonstrate that a buyer can move from an unclear requirement to an explainable, budget-constrained carbon-credit portfolio.

The complete demonstration journey is:

```text
Browse projects
-> Filter and compare projects
-> Enter budget, goals, and risk tolerance
-> Receive ranked, explainable recommendations
-> Review quality, impact, value, and risk indicators
-> Ask evidence-grounded questions about project documents
-> Generate an optimized portfolio
-> Simulate a purchase
-> Download a report or certificate
```

## 5. In-scope capabilities

### Project discovery

- Catalogue containing at least 30 curated sample projects
- Search, sorting, filtering, and pagination
- Project-detail pages with source and last-updated information
- Side-by-side comparison of up to four projects
- Map display when valid coordinates are available

### Decision intelligence

- Transparent CarbonIQ component scores and overall score
- Confidence indicator based on evidence completeness
- Buyer-specific match score and ranked recommendations
- Human-readable reasons, limitations, and trade-offs
- Rule-based risk-warning signals
- Portfolio optimization subject to budget and preference constraints

### Document intelligence

- Ingestion of selected project PDF documents
- Retrieval-augmented question answering
- Evidence references containing document name and page number when available
- Explicit refusal when the available evidence cannot support an answer

### Portfolio and simulation

- Save a recommended or manually selected portfolio
- Show total cost, total credits, diversification, average quality, and portfolio risk
- Simulate an order without collecting money
- Generate a clearly marked demonstration report or certificate

### Platform foundation

- Buyer authentication
- PostgreSQL persistence
- Versioned REST API
- Automated tests and continuous integration
- Docker-based local development
- Accessible, responsive interface

## 6. Out-of-scope capabilities

The following are future work and must not be represented as production-ready MVP features:

- Real payment processing or settlement
- Legal ownership transfer of carbon credits
- Registry retirement or registry account integration
- KYC, KYB, AML, sanctions, or financial-market compliance operations
- Production blockchain or tokenization
- Legal, investment, tax, or climate-claim advice
- Guaranteed fraud detection
- Guaranteed compliance eligibility
- Live exchange connectivity or real-time tradable prices
- Automated project ratings presented as independent certification
- Full satellite-based measurement, reporting, and verification
- Developer self-service listings and public project editing

## 7. Product principles

1. **Reduction first:** Carbon credits complement direct emissions reduction; they do not replace it.
2. **Evidence before assertion:** Important claims must point to a source or be marked as estimates.
3. **Explainability:** Every score and recommendation must expose its contributing factors.
4. **Uncertainty:** Missing evidence and model limitations must be visible.
5. **Risk indicator, not accusation:** Fraud-related outputs are warnings requiring human review.
6. **Separation of facts and predictions:** Verified data, derived scores, and AI-generated explanations must be distinguishable.
7. **Conflict transparency:** The academic MVP does not accept paid placement or allow sellers to alter scores.

## 8. Technical scope

- Web application: Next.js, TypeScript, and Tailwind CSS
- API and intelligence services: Python and FastAPI
- Data store: PostgreSQL with PostGIS and pgvector extensions
- Data processing: Pandas
- Initial scoring and ranking: deterministic rules and weighted formulas
- Portfolio optimization: Google OR-Tools or SciPy
- Document retrieval: embeddings stored with pgvector
- Local orchestration: Docker Compose
- Quality automation: Pytest, frontend tests, Playwright, and GitHub Actions

The MVP uses one FastAPI application rather than separate production microservices. Modules remain logically separated so they can be extracted later if required.

## 9. Assumptions and constraints

- Project and price data may be curated, licensed, public, or explicitly synthetic.
- Synthetic values must be labelled and must not be presented as live market facts.
- The dataset will contain enough variety to test filtering and recommendations.
- Advanced machine-learning claims require suitable training and evaluation data; otherwise deterministic methods will be used.
- LLM availability depends on configured credentials; a graceful unavailable state is required.
- Currency conversion is out of scope for the first milestone. Monetary values use the currency stored with each record.
- One carbon credit is represented as one tonne of CO2-equivalent for the educational workflow.

## 10. Success criteria

The MVP is accepted when:

- A user can register, sign in, and sign out.
- At least 30 projects can be imported with provenance and validation results.
- The catalogue, filters, project details, and comparison workflow operate correctly.
- Every scorable project shows component scores, an overall score, confidence, and methodology version.
- Recommendations change when buyer preferences change and include reasons and trade-offs.
- A generated portfolio respects its budget and required-credit constraints or explains why no feasible portfolio exists.
- Risk warnings show severity, evidence, and a human-review flag.
- The document assistant cites retrieved evidence and avoids unsupported answers.
- A simulated order creates a report clearly marked as non-transactional.
- Automated tests pass in continuous integration.
- A new developer can run the documented system locally.

## 11. Final demonstration scenario

The reference demo user is a small organization with a fixed INR budget, a preference for projects in India, low risk tolerance, and interest in community and biodiversity benefits. The presentation should show how CarbonIQ narrows the catalogue, explains its ranking, constructs a diversified portfolio, answers a document question, and generates a simulated procurement report.

## 12. Definition of done

A feature is done only when its implementation, validation, error handling, tests, API documentation, and user-facing state are complete. A screen backed only by hard-coded data is not considered integrated. A score without a methodology version and explanation is not considered complete.
