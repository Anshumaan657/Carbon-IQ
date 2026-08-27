# CarbonIQ MVP User Flows

## 1. Actors

### Buyer

An authenticated organization representative who discovers projects, records preferences, receives recommendations, builds portfolios, asks document questions, and simulates an order.

### Visitor

An unauthenticated user who may view public educational content and a limited project catalogue but cannot save preferences, portfolios, or simulated orders.

### Data curator

An authorized project-team member who imports and validates project data. A curator is not a marketplace seller and cannot manually override calculated scores through the MVP interface.

## 2. Primary buyer journey

### Flow A: Register and sign in

1. The visitor opens CarbonIQ.
2. The visitor chooses **Create account**.
3. The visitor enters organization name, email, and password.
4. The system validates the input and creates the buyer account.
5. The buyer signs in and is redirected to the catalogue or onboarding questionnaire.

Alternative outcomes:

- An existing email returns a non-revealing validation error.
- An invalid or weak password returns field-level guidance.
- Failed authentication does not reveal whether a particular account exists.

### Flow B: Discover projects

1. The buyer opens the project catalogue.
2. The system displays paginated project summaries.
3. The buyer searches or filters by project type, category, country, registry, price, vintage, verification status, risk band, and SDG.
4. The buyer changes the sort order.
5. The system updates the result count and preserves the selected filters in the URL.
6. The buyer opens a project-detail page.

Project summaries must show data freshness and clearly distinguish unavailable values from zero values.

### Flow C: Examine a project

1. The buyer views the project description, developer, location, project type, registry, methodology, vintage, price, and availability.
2. The buyer views CarbonIQ component scores and confidence.
3. The buyer expands the explanation for each score.
4. The buyer reviews risk warnings and their evidence.
5. The buyer opens available source-document references.
6. The buyer adds the project to comparison or to a draft portfolio.

If a project lacks sufficient evidence, the interface shows **Insufficient evidence** rather than inventing a score.

### Flow D: Compare projects

1. The buyer selects between two and four projects.
2. The comparison page aligns common attributes and score components.
3. Missing values remain visible as **Not available**.
4. The system highlights meaningful differences without declaring one universal winner.
5. The buyer removes a project, opens its details, or continues to recommendations.

### Flow E: Record buyer preferences

1. The buyer enters a maximum budget and required number of credits.
2. The buyer selects a risk tolerance: low, medium, or high.
3. The buyer optionally selects project types, countries, avoidance/removal preference, SDGs, minimum quality, and delivery period.
4. The system validates that numeric constraints are positive and logically compatible.
5. The buyer saves the preference profile and requests recommendations.

If no optional preference is selected, the system uses documented neutral defaults.

### Flow F: Receive recommendations

1. The system filters projects that violate hard constraints.
2. It calculates the buyer-specific match score for eligible projects.
3. It returns a ranked list with reasons, trade-offs, confidence, and risk warnings.
4. The buyer adjusts preferences and observes how the ranking changes.
5. The buyer opens a recommended project or requests an optimized portfolio.

The interface must state that recommendations are decision support, not investment or legal advice.

### Flow G: Generate a portfolio

1. The buyer chooses **Build portfolio**.
2. The optimizer attempts to satisfy budget, quantity, risk, quality, and diversification constraints.
3. The system returns a feasible portfolio with allocations and summary metrics.
4. The buyer can lock, remove, or adjust an allocation and rerun optimization.
5. The buyer saves the resulting portfolio.

If no feasible portfolio exists, the system returns the conflicting constraints and suggested relaxations instead of an empty success response.

### Flow H: Ask about project documents

1. From a project page, the buyer opens the AI assistant.
2. The buyer asks a question about the selected project.
3. The system retrieves relevant document passages.
4. The assistant answers only from retrieved evidence.
5. The answer includes document name and page reference when available.
6. The buyer can open the cited source.

If evidence is missing or contradictory, the assistant says so and recommends human review.

### Flow I: Simulate an order

1. The buyer selects an eligible saved portfolio.
2. The system displays a final summary and explicit simulation notice.
3. The buyer confirms the simulated order.
4. The system records a non-financial order and generates a unique reference.
5. The buyer downloads a report or demonstration certificate.

The output must contain **Simulation only - no credits purchased, transferred, or retired**.

## 3. Data-curator journey

### Flow J: Import project data

1. The curator prepares a CSV or JSON file conforming to the data dictionary.
2. The curator runs the documented import command.
3. The pipeline validates required fields, enum values, identifiers, coordinates, prices, and provenance.
4. Invalid rows are rejected with actionable messages.
5. Valid rows are upserted by stable project identifier.
6. The pipeline reports inserted, updated, skipped, and rejected counts.
7. Changed project evidence triggers score recalculation.

## 4. Global error and recovery flows

- API failure: show a retry action without discarding completed form input.
- Session expiration: request sign-in and return the user to the previous safe location.
- Missing project: show a not-found page and link back to the catalogue.
- Stale recommendation: prompt recalculation when project data or methodology version has changed.
- AI unavailable: preserve the project page and explain that document Q&A is temporarily unavailable.
- Invalid optimization constraints: identify the exact incompatible fields.
- Partial data: render known facts and mark unknown fields explicitly.

## 5. Navigation map

```text
Home
|-- Project catalogue
|   |-- Project details
|   |   |-- Documents and AI assistant
|   |   `-- Add to comparison/portfolio
|   `-- Project comparison
|-- Buyer preferences
|   `-- Recommendations
|       `-- Portfolio builder
|           `-- Simulated order and report
|-- Saved portfolios
`-- Account
```

## 6. Analytics events

The MVP may record non-sensitive product events such as catalogue viewed, filter applied, comparison created, recommendations requested, portfolio generated, assistant question submitted, and simulated order completed. It must not record passwords, document contents, or full free-text questions in analytics by default.
