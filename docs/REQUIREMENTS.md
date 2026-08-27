# CarbonIQ MVP Requirements

## 1. Requirement notation

- `Must`: required for MVP acceptance
- `Should`: important but may be deferred if the core journey is at risk
- `Could`: optional enhancement

Each functional requirement has a stable ID for issues, tests, and pull requests.

## 2. Functional requirements

### Authentication and authorization

| ID | Priority | Requirement |
|---|---|---|
| FR-AUTH-001 | Must | A visitor can create a buyer account using organization name, email, and password. |
| FR-AUTH-002 | Must | A registered buyer can sign in and sign out securely. |
| FR-AUTH-003 | Must | Protected resources are accessible only to their owner or an authorized role. |
| FR-AUTH-004 | Must | Curator and administrator operations require role authorization. |

### Project catalogue

| ID | Priority | Requirement |
|---|---|---|
| FR-PROJ-001 | Must | The platform imports and displays at least 30 curated projects. |
| FR-PROJ-002 | Must | Users can search projects by name, developer, and description. |
| FR-PROJ-003 | Must | Users can filter by project type, category, country, registry, vintage, price, verification status, risk, and SDG. |
| FR-PROJ-004 | Must | Users can sort and paginate catalogue results. |
| FR-PROJ-005 | Must | A project-detail page shows project facts, provenance, freshness, scores, confidence, risks, inventory, and documents. |
| FR-PROJ-006 | Must | Users can compare between two and four projects. |
| FR-PROJ-007 | Should | Projects with coordinates can be explored on a map. |

### Data ingestion and governance

| ID | Priority | Requirement |
|---|---|---|
| FR-DATA-001 | Must | A curator can import supported CSV or JSON project data using a documented process. |
| FR-DATA-002 | Must | The importer validates required fields, types, enums, ranges, identifiers, and provenance. |
| FR-DATA-003 | Must | Invalid rows produce actionable validation messages without corrupting valid data. |
| FR-DATA-004 | Must | Each important imported fact records its source and data-as-of date. |
| FR-DATA-005 | Must | Synthetic data is visibly identified. |
| FR-DATA-006 | Should | Changes affecting a project trigger score and risk recalculation. |

### Scoring and risk

| ID | Priority | Requirement |
|---|---|---|
| FR-SCORE-001 | Must | The system calculates scores using the documented, versioned methodology. |
| FR-SCORE-002 | Must | Score responses include components, overall score, confidence, explanations, missing evidence, and methodology version. |
| FR-SCORE-003 | Must | Projects missing minimum evidence are marked unscored rather than assigned invented values. |
| FR-RISK-001 | Must | The system generates deterministic risk-warning signals from documented rules. |
| FR-RISK-002 | Must | Each warning includes code, severity, evidence, rule version, and human-review status. |
| FR-RISK-003 | Must | User-facing language describes warning signals as risk indicators, not proven fraud. |

### Preferences and recommendations

| ID | Priority | Requirement |
|---|---|---|
| FR-PREF-001 | Must | A buyer can save budget, credit quantity, risk tolerance, and optional project preferences. |
| FR-REC-001 | Must | The engine applies hard constraints before ranking projects. |
| FR-REC-002 | Must | The engine returns a buyer-specific match score, rank, reasons, trade-offs, and relevant warnings. |
| FR-REC-003 | Must | Recommendations change deterministically when material preferences change. |
| FR-REC-004 | Must | Recommendations display a decision-support disclaimer. |

### Portfolio optimization

| ID | Priority | Requirement |
|---|---|---|
| FR-PORT-001 | Must | A buyer can generate a portfolio constrained by budget and required credits. |
| FR-PORT-002 | Must | The optimizer supports minimum and maximum project counts and a concentration limit. |
| FR-PORT-003 | Must | Portfolio totals are calculated server-side. |
| FR-PORT-004 | Must | The platform explains when no feasible portfolio exists. |
| FR-PORT-005 | Should | A buyer can lock or manually adjust items and rerun optimization. |

### Documents and AI assistant

| ID | Priority | Requirement |
|---|---|---|
| FR-DOC-001 | Must | A curator can ingest selected PDF project documents. |
| FR-DOC-002 | Must | The pipeline records document provenance, checksum, status, and page metadata. |
| FR-AI-001 | Must | A buyer can ask a question scoped to one project. |
| FR-AI-002 | Must | Answers are grounded in retrieved project-document passages. |
| FR-AI-003 | Must | Supported answers include document and page references when available. |
| FR-AI-004 | Must | The assistant reports insufficient or conflicting evidence instead of inventing an answer. |
| FR-AI-005 | Should | Retrieved source passages can be opened from the answer. |

### Simulation and reporting

| ID | Priority | Requirement |
|---|---|---|
| FR-ORD-001 | Must | An authenticated buyer can create a simulated order from an owned portfolio. |
| FR-ORD-002 | Must | The user explicitly acknowledges that the order is a simulation. |
| FR-ORD-003 | Must | The generated report states that no credits were purchased, transferred, or retired. |
| FR-ORD-004 | Must | The report includes allocation, price snapshot, score versions, warnings, sources, and timestamp. |

### Administration and observability

| ID | Priority | Requirement |
|---|---|---|
| FR-OPS-001 | Must | The API exposes a health endpoint. |
| FR-OPS-002 | Must | Privileged imports and recalculations produce structured audit events. |
| FR-OPS-003 | Should | Application errors include a request ID for troubleshooting. |

## 3. Non-functional requirements

### Security

| ID | Requirement |
|---|---|
| NFR-SEC-001 | Passwords must be hashed using an established password-hashing algorithm. |
| NFR-SEC-002 | Secrets must be supplied through environment variables and never committed. |
| NFR-SEC-003 | Inputs, uploaded files, and imported content must be validated. |
| NFR-SEC-004 | Authorization must be enforced server-side. |
| NFR-SEC-005 | Logs must exclude passwords, access tokens, document contents, and unnecessary personal data. |
| NFR-SEC-006 | Login, upload, and assistant endpoints must support rate limiting. |

### Performance

| ID | Requirement |
|---|---|
| NFR-PERF-001 | Catalogue and project-detail APIs should respond within 500 ms at the 95th percentile for the demo dataset in the local reference environment. |
| NFR-PERF-002 | A recommendation request should complete within 2 seconds for 1,000 project records, excluding external AI calls. |
| NFR-PERF-003 | Portfolio optimization should complete within 5 seconds for the MVP dataset and constraints. |
| NFR-PERF-004 | Long document-ingestion tasks must run asynchronously and expose status. |

### Reliability

| ID | Requirement |
|---|---|
| NFR-REL-001 | Database migrations and seed operations must be repeatable. |
| NFR-REL-002 | Failed imports must not partially corrupt committed records. |
| NFR-REL-003 | External AI failure must not prevent catalogue, scoring, recommendation, or portfolio use. |
| NFR-REL-004 | Calculations must be deterministic for identical inputs and versions. |

### Accessibility and usability

| ID | Requirement |
|---|---|
| NFR-UX-001 | Core flows must be keyboard accessible. |
| NFR-UX-002 | Form controls, warnings, charts, and score indicators must have textual labels. |
| NFR-UX-003 | Colour must not be the only method used to communicate risk or score state. |
| NFR-UX-004 | The interface must support current desktop and mobile viewport sizes. |
| NFR-UX-005 | Loading, empty, partial-data, and failure states must be designed explicitly. |

### Maintainability

| ID | Requirement |
|---|---|
| NFR-MNT-001 | Frontend, API, scoring, risk, recommendation, RAG, and data-pipeline modules must remain logically separated. |
| NFR-MNT-002 | Public functions and endpoints must use typed schemas. |
| NFR-MNT-003 | New behaviour requires automated tests. |
| NFR-MNT-004 | Formatting, linting, and tests must run in continuous integration. |
| NFR-MNT-005 | A clean checkout must be runnable using documented commands. |

### Data and AI governance

| ID | Requirement |
|---|---|
| NFR-GOV-001 | Verified facts, calculated values, synthetic data, and AI-generated text must be distinguishable. |
| NFR-GOV-002 | Scores, rules, recommendations, and optimization results must store their version. |
| NFR-GOV-003 | AI answers must expose supporting evidence or an unsupported-answer state. |
| NFR-GOV-004 | Project developers or commercial interests must not influence calculated rankings in the MVP. |

## 4. Data requirements

The acceptance dataset must include:

- At least 30 projects
- At least five project types
- At least five countries, including India
- Avoidance/reduction and removal categories
- Multiple registries or programs
- Multiple vintages and price points
- Projects with complete and intentionally incomplete evidence
- At least five projects with ingestible documents
- At least five deterministic risk-warning cases
- Explicit `is_synthetic` and provenance fields

## 5. Testing requirements

- Backend unit tests for validation, scoring, ranking, risks, and optimization
- API integration tests for authentication, ownership, projects, recommendations, portfolios, assistant, and simulated orders
- Frontend component tests for important forms and score displays
- End-to-end tests for the primary buyer journey
- Data-import fixture tests for valid, invalid, duplicate, and partial rows
- RAG evaluation cases covering supported, insufficient, and conflicting evidence
- Security tests for unauthorized resource access and unsafe uploads

## 6. MVP acceptance scenario

Using a seeded buyer and curated dataset, an evaluator must be able to:

1. Sign in.
2. Browse and filter projects.
3. Compare three projects.
4. Save an INR budget and low-risk India-focused preference profile.
5. Receive ranked recommendations with reasons and trade-offs.
6. Inspect score evidence and a warning signal.
7. Generate a feasible diversified portfolio.
8. Ask a document question and open its cited evidence.
9. Simulate an order.
10. Download a report bearing the mandatory simulation disclaimer.

## 7. Traceability rule

Every pull request implementing an MVP feature must reference at least one requirement ID. Tests should include the relevant ID in the test name, marker, or description where practical.
