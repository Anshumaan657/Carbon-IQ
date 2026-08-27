# CarbonIQ MVP API Specification

## 1. API conventions

- Base path: `/api/v1`
- Media type: `application/json`, except document upload and report download
- Authentication: bearer access token for protected routes
- Identifiers: UUID strings
- Timestamps: ISO 8601 UTC
- Pagination: `page` starts at 1; `page_size` defaults to 20 and is capped at 100
- Scores: decimals between 0 and 100
- `risk_score`: 0 is lowest risk and 100 is highest risk
- Currency: ISO 4217 code
- Country: ISO 3166-1 alpha-2 code
- Unknown values: JSON `null`, never fabricated placeholders

## 2. Standard error response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields are invalid.",
    "details": [
      {
        "field": "budget",
        "message": "Must be greater than zero."
      }
    ],
    "request_id": "req_01ABC"
  }
}
```

Common status codes:

- `200` successful read or calculation
- `201` resource created
- `202` asynchronous processing accepted
- `204` successful deletion with no response body
- `400` invalid business constraint
- `401` missing or invalid authentication
- `403` authenticated but unauthorized
- `404` resource not found
- `409` duplicate or stale-state conflict
- `422` request validation failure
- `429` rate limit exceeded
- `500` unexpected server error
- `503` dependent service unavailable

## 3. Health

### `GET /api/v1/health`

Authentication: none

Response `200`:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "database": "ok"
}
```

## 4. Authentication

### `POST /api/v1/auth/register`

Authentication: none

Request:

```json
{
  "email": "buyer@example.com",
  "password": "example-password",
  "organization_name": "Example University"
}
```

Response `201`:

```json
{
  "id": "8c2be159-9f20-4fbd-b1f9-fccf287eb673",
  "email": "buyer@example.com",
  "organization_name": "Example University",
  "role": "buyer"
}
```

### `POST /api/v1/auth/login`

Request:

```json
{
  "email": "buyer@example.com",
  "password": "example-password"
}
```

Response `200`:

```json
{
  "access_token": "token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### `GET /api/v1/auth/me`

Authentication: required

Returns the authenticated user's safe profile. Password hashes are never returned.

## 5. Projects

### `GET /api/v1/projects`

Authentication: optional for public catalogue; authenticated users may receive saved-state fields.

Query parameters:

- `q`: name, developer, or description search
- `project_type`: repeatable project-type filter
- `category`: avoidance, reduction, removal, or mixed
- `country`: repeatable country filter
- `registry`: repeatable registry filter
- `verification_status`
- `vintage_from`, `vintage_to`
- `price_min`, `price_max`
- `risk_max`
- `sdg`: repeatable integer 1-17
- `sort`: `name`, `price`, `carboniq_score`, `risk_score`, or `updated_at`
- `order`: `asc` or `desc`
- `page`, `page_size`

Response `200`:

```json
{
  "items": [
    {
      "id": "68edce1f-b722-41d8-95d6-d1254757dd38",
      "external_id": "project-001",
      "name": "Example Forest Restoration",
      "developer_name": "Example Developer",
      "country_code": "IN",
      "project_type": "reforestation",
      "category": "removal",
      "registry": "Example Registry",
      "vintage_start": 2025,
      "vintage_end": 2025,
      "price_per_credit": 850.0,
      "currency": "INR",
      "verification_status": "verified",
      "carboniq_score": 81.0,
      "risk_score": 25.0,
      "confidence": 0.78,
      "data_as_of": "2026-08-01",
      "is_synthetic": true
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1,
  "total_pages": 1
}
```

### `GET /api/v1/projects/{project_id}`

Returns complete project data, latest score, active risk signals, inventory summaries, documents, provenance, and data-freshness fields.

### `POST /api/v1/projects/compare`

Request:

```json
{
  "project_ids": [
    "68edce1f-b722-41d8-95d6-d1254757dd38",
    "a3e55473-c285-46d1-b556-0bc40da5996d"
  ]
}
```

Validation: between two and four unique IDs.

Response `200` contains aligned project attributes and does not fill missing values with inferred data.

## 6. Buyer preferences

### `POST /api/v1/preferences`

Authentication: required

Request:

```json
{
  "name": "India low-risk portfolio",
  "budget": 100000.0,
  "currency": "INR",
  "required_credits": 100.0,
  "risk_tolerance": "low",
  "preferred_project_types": ["reforestation", "biochar"],
  "preferred_countries": ["IN"],
  "preferred_category": "removal",
  "sdg_priorities": [8, 13, 15],
  "minimum_quality_score": 70.0,
  "delivery_start": null,
  "delivery_end": null
}
```

Response `201`: stored preference with ID and timestamps.

### `GET /api/v1/preferences`

Returns the authenticated user's preference profiles.

### `GET /api/v1/preferences/{preference_id}`

Returns one owned profile.

### `PATCH /api/v1/preferences/{preference_id}`

Updates supplied fields only.

### `DELETE /api/v1/preferences/{preference_id}`

Response `204`. Profiles referenced by runs may be archived instead of physically removed.

## 7. Scores and risk signals

### `GET /api/v1/projects/{project_id}/score`

Response `200`:

```json
{
  "project_id": "68edce1f-b722-41d8-95d6-d1254757dd38",
  "components": {
    "integrity": 85.0,
    "permanence": 78.0,
    "verification": 90.0,
    "co_benefits": 88.0,
    "value": 74.0,
    "delivery": 75.0,
    "compatibility": 80.0
  },
  "quality_score": 84.0,
  "impact_score": 86.0,
  "risk_score": 25.0,
  "carboniq_score": 81.0,
  "confidence": 0.78,
  "explanation": [
    {
      "component": "verification",
      "reason": "A current verification document is available.",
      "evidence_ids": ["doc-001"]
    }
  ],
  "missing_evidence": ["developer financial history"],
  "methodology_version": "1.0.0",
  "calculated_at": "2026-08-28T08:00:00Z"
}
```

If minimum evidence requirements are not met, score fields may be `null` and the response must explain why.

### `POST /api/v1/scores/calculate`

Authentication: curator or admin. Recalculates scores for specified projects or a validated import batch.

### `GET /api/v1/projects/{project_id}/risk-signals`

Returns active warnings with stable code, severity, message, evidence, rule version, and `requires_review`.

## 8. Recommendations

### `POST /api/v1/recommendations`

Authentication: required

Request:

```json
{
  "preference_id": "f0f9b647-e1c4-4298-944f-e9f4133af347",
  "limit": 10
}
```

Alternatively, the endpoint may accept an inline `preferences` object with the same fields used to create a preference profile, but exactly one of `preference_id` or `preferences` must be supplied.

Response `200`:

```json
{
  "run_id": "bbedce39-61d0-4ce1-8546-91c21a7b4ad6",
  "engine_version": "1.0.0",
  "project_data_as_of": "2026-08-28T08:00:00Z",
  "items": [
    {
      "project_id": "68edce1f-b722-41d8-95d6-d1254757dd38",
      "rank": 1,
      "match_score": 89.0,
      "reasons": ["Matches preferred country", "Quality exceeds minimum"],
      "trade_offs": ["Price is above the project-type median"],
      "risk_signal_ids": ["risk-001"]
    }
  ],
  "disclaimer": "Decision support only; not legal, investment, or climate-claim advice."
}
```

## 9. Portfolios

### `POST /api/v1/portfolios/optimize`

Authentication: required

Request:

```json
{
  "preference_id": "f0f9b647-e1c4-4298-944f-e9f4133af347",
  "recommendation_run_id": "bbedce39-61d0-4ce1-8546-91c21a7b4ad6",
  "minimum_projects": 2,
  "maximum_projects": 5,
  "maximum_single_project_percent": 50
}
```

Response `201`:

```json
{
  "id": "61323256-2519-4d4e-9492-b2632bb65c9d",
  "name": "Optimized portfolio",
  "currency": "INR",
  "total_cost": 98500.0,
  "total_credits": 100.0,
  "average_quality": 84.0,
  "portfolio_risk": 22.0,
  "items": [
    {
      "credit_id": "819f4a9e-b133-49f4-bfda-a82201e89632",
      "project_id": "68edce1f-b722-41d8-95d6-d1254757dd38",
      "quantity": 40.0,
      "unit_price": 850.0,
      "allocation_percent": 40.0,
      "is_locked": false
    }
  ],
  "constraint_summary": [],
  "optimizer_version": "1.0.0"
}
```

If no feasible solution exists, return `400` with code `NO_FEASIBLE_PORTFOLIO` and identify conflicting constraints.

### `GET /api/v1/portfolios`

Returns portfolios owned by the authenticated user.

### `GET /api/v1/portfolios/{portfolio_id}`

Returns one owned portfolio and its items.

### `PATCH /api/v1/portfolios/{portfolio_id}`

Allows name changes and valid manual allocation changes. Totals are always recalculated server-side.

## 10. Documents and AI assistant

### `POST /api/v1/projects/{project_id}/documents`

Authentication: curator or admin

Media type: `multipart/form-data`

Accepts PDF plus document type, title, source URL, and publication date. Returns `202` with document status `processing`.

### `GET /api/v1/projects/{project_id}/documents`

Returns document metadata and ingestion status. It does not return vector embeddings.

### `POST /api/v1/projects/{project_id}/assistant/ask`

Authentication: required

Request:

```json
{
  "question": "How is additionality justified?"
}
```

Response `200`:

```json
{
  "answer": "The available project document states ...",
  "answer_status": "supported",
  "citations": [
    {
      "document_id": "doc-001",
      "title": "Project Design Document",
      "page_start": 17,
      "page_end": 18,
      "excerpt": "Relevant short source passage"
    }
  ],
  "limitations": [],
  "retrieval_id": "ret-001"
}
```

`answer_status` is `supported`, `insufficient_evidence`, `conflicting_evidence`, or `unavailable`.

## 11. Simulated orders and reports

### `POST /api/v1/orders/simulate`

Authentication: required

Request:

```json
{
  "portfolio_id": "61323256-2519-4d4e-9492-b2632bb65c9d",
  "acknowledge_simulation": true
}
```

Response `201`:

```json
{
  "id": "438a48bb-af3b-44a8-828b-63a68981a6f4",
  "reference": "CIQ-DEMO-2026-00001",
  "status": "simulated",
  "total_cost": 98500.0,
  "total_credits": 100.0,
  "created_at": "2026-08-28T08:00:00Z",
  "disclaimer": "Simulation only - no credits purchased, transferred, or retired."
}
```

### `GET /api/v1/orders/{order_id}/report`

Authentication: required and resource owner

Returns a generated PDF or JSON report containing project allocations, score methodology versions, data timestamps, risk warnings, sources, and the mandatory simulation disclaimer.

## 12. Curator import

### `POST /api/v1/imports/projects`

Authentication: curator or admin

Accepts a supported CSV or JSON file and returns `202` with an import-batch ID.

### `GET /api/v1/imports/{batch_id}`

Returns processing state and inserted, updated, skipped, and rejected counts plus row-level validation messages.

## 13. Security requirements

- Enforce ownership checks for preferences, portfolios, orders, and reports.
- Rate-limit login and assistant endpoints.
- Validate file type, size, and content before document processing.
- Do not include stack traces, credentials, embeddings, or private storage keys in responses.
- Escape or sanitize imported display content.
- Generate request IDs and structured audit events for privileged operations.
- API documentation examples use synthetic data only.

## 14. Versioning policy

Breaking API changes require a new base version. Scoring, recommendation, risk-rule, optimizer, and disclaimer versions are independently recorded so historical results remain reproducible.
