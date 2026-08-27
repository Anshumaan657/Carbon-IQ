# CarbonIQ MVP Data Model

## 1. Conventions

- Primary keys use UUIDs unless an imported record has an external stable identifier.
- Timestamps use UTC and ISO 8601 at API boundaries.
- Monetary values use `numeric(14, 2)` plus an ISO 4217 currency code.
- Quantities of credits use `numeric(14, 3)` to support fractional demo allocations.
- Scores use the range 0-100.
- `risk_score` is a risk index where 0 is lowest risk and 100 is highest risk.
- Other component scores use 0 as weakest and 100 as strongest.
- Unknown, not applicable, and zero are distinct states.
- Imported facts retain source, retrieval date, and update timestamp.
- Soft deletion is preferred for user-created records needed for auditability.

## 2. Enumerations

### UserRole

`buyer`, `curator`, `admin`

### ProjectCategory

`avoidance`, `reduction`, `removal`, `mixed`

### ProjectStatus

`draft`, `active`, `inactive`, `completed`, `unknown`

### VerificationStatus

`verified`, `validation_pending`, `verification_pending`, `unverified`, `unknown`

### RiskTolerance

`low`, `medium`, `high`

### RiskSeverity

`info`, `low`, `medium`, `high`, `critical`

### DocumentStatus

`pending`, `processing`, `ready`, `failed`

### OrderStatus

`simulated`

## 3. Entities

### User

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| email | string | Yes | Unique, normalized, never returned unnecessarily |
| password_hash | string | Yes | Never exposed through the API |
| organization_name | string | Yes | 2-160 characters |
| role | UserRole | Yes | Defaults to `buyer` |
| is_active | boolean | Yes | Defaults to true |
| created_at | timestamp | Yes | UTC |
| updated_at | timestamp | Yes | UTC |

### BuyerPreference

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| user_id | UUID | Yes | Foreign key to User |
| name | string | Yes | Named reusable preference profile |
| budget | decimal | Yes | Greater than zero |
| currency | char(3) | Yes | MVP requires comparable project currency |
| required_credits | decimal | Yes | Greater than zero |
| risk_tolerance | RiskTolerance | Yes | Buyer risk appetite |
| preferred_project_types | string array | No | Empty means no preference |
| preferred_countries | char(2) array | No | ISO 3166-1 alpha-2 |
| preferred_category | ProjectCategory | No | Optional |
| sdg_priorities | integer array | No | Values 1-17 |
| minimum_quality_score | decimal | No | 0-100 |
| delivery_start | date | No | Optional period constraint |
| delivery_end | date | No | Must not precede start |
| created_at | timestamp | Yes | UTC |
| updated_at | timestamp | Yes | UTC |

### Project

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Internal primary key |
| external_id | string | Yes | Stable unique imported identifier |
| name | string | Yes | 2-240 characters |
| slug | string | Yes | Unique URL identifier |
| developer_name | string | Yes | Project developer or organization |
| description | text | Yes | Source-backed description |
| country_code | char(2) | Yes | ISO 3166-1 alpha-2 |
| region | string | No | State, province, or broader region |
| latitude | decimal | No | -90 to 90 |
| longitude | decimal | No | -180 to 180 |
| project_type | string | Yes | Controlled vocabulary in data dictionary |
| category | ProjectCategory | Yes | Avoidance, reduction, removal, or mixed |
| registry | string | Yes | Registry or program name |
| registry_project_id | string | No | Unique with registry when available |
| methodology | string | No | Methodology identifier and version |
| vintage_start | integer | No | Four-digit year |
| vintage_end | integer | No | Cannot precede start |
| verification_status | VerificationStatus | Yes | Evidence state |
| status | ProjectStatus | Yes | Project lifecycle state |
| price_per_credit | decimal | No | Snapshot, not necessarily tradable |
| currency | char(3) | No | Required when price is present |
| available_quantity | decimal | No | Snapshot quantity |
| sdgs | integer array | No | Unique values 1-17 |
| source_url | URL | Yes | Primary provenance link |
| data_as_of | date | Yes | Date facts were current |
| is_synthetic | boolean | Yes | Identifies demonstration data |
| created_at | timestamp | Yes | UTC |
| updated_at | timestamp | Yes | UTC |

Recommended uniqueness constraints:

- `external_id`
- `slug`
- `(registry, registry_project_id)` when registry project ID is present

### CarbonCredit

Represents a project-level inventory or vintage lot for simulation; it does not represent a legally transferable token.

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| project_id | UUID | Yes | Foreign key to Project |
| vintage | integer | Yes | Four-digit year |
| quantity_available | decimal | Yes | Non-negative snapshot |
| price_per_credit | decimal | Yes | Non-negative |
| currency | char(3) | Yes | ISO 4217 |
| delivery_date | date | No | Optional estimate |
| data_as_of | date | Yes | Snapshot date |

### ProjectDocument

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| project_id | UUID | Yes | Foreign key to Project |
| document_type | string | Yes | PDD, validation, verification, monitoring, other |
| title | string | Yes | Display title |
| source_url | URL | Yes | Original source |
| storage_key | string | No | Internal object-store reference |
| checksum_sha256 | string | No | Duplicate and integrity detection |
| published_at | date | No | Source publication date |
| retrieved_at | timestamp | Yes | Retrieval timestamp |
| status | DocumentStatus | Yes | Ingestion state |
| page_count | integer | No | Positive when known |
| error_message | text | No | Populated on failed ingestion |

### DocumentChunk

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| document_id | UUID | Yes | Foreign key to ProjectDocument |
| chunk_index | integer | Yes | Unique within document |
| page_start | integer | No | First source page |
| page_end | integer | No | Last source page |
| content | text | Yes | Extracted passage |
| embedding | vector | Yes | Dimension set by chosen embedding model |
| metadata | JSONB | Yes | Extraction and heading metadata |

### ProjectScore

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| project_id | UUID | Yes | Foreign key to Project |
| integrity_score | decimal | No | 0-100 |
| permanence_score | decimal | No | 0-100 |
| verification_score | decimal | No | 0-100 |
| co_benefits_score | decimal | No | 0-100 |
| value_score | decimal | No | 0-100 |
| delivery_score | decimal | No | 0-100; higher means lower delivery risk |
| compatibility_score | decimal | No | 0-100 |
| quality_score | decimal | No | Derived quality summary |
| impact_score | decimal | No | Derived impact summary |
| risk_score | decimal | No | 0 low risk, 100 high risk |
| carboniq_score | decimal | No | Overall non-personalized score |
| confidence | decimal | Yes | 0-1 evidence confidence |
| explanation | JSONB | Yes | Component reasons and missing evidence |
| methodology_version | string | Yes | Reproducibility identifier |
| calculated_at | timestamp | Yes | UTC |

Only one current score per `(project_id, methodology_version)` is exposed by default; historical scores remain available for audit.

### RiskSignal

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| project_id | UUID | Yes | Foreign key to Project |
| code | string | Yes | Stable machine-readable code |
| severity | RiskSeverity | Yes | Warning level |
| title | string | Yes | Short user-facing label |
| message | text | Yes | Explanation, not accusation |
| evidence | JSONB | Yes | Source IDs and observed values |
| requires_review | boolean | Yes | Defaults according to rule |
| rule_version | string | Yes | Reproducibility identifier |
| detected_at | timestamp | Yes | UTC |
| resolved_at | timestamp | No | Null while active |

### RecommendationRun

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| user_id | UUID | Yes | Foreign key to User |
| preference_id | UUID | Yes | Foreign key to BuyerPreference |
| engine_version | string | Yes | Ranking version |
| project_data_as_of | timestamp | Yes | Data snapshot |
| created_at | timestamp | Yes | UTC |

### RecommendationItem

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| recommendation_run_id | UUID | Yes | Foreign key to RecommendationRun |
| project_id | UUID | Yes | Foreign key to Project |
| rank | integer | Yes | Starts at 1 |
| match_score | decimal | Yes | 0-100 buyer-specific score |
| reasons | JSONB | Yes | Positive match factors |
| trade_offs | JSONB | Yes | Limitations and compromises |
| excluded_constraints | JSONB | Yes | Empty for eligible items |

### Portfolio

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| user_id | UUID | Yes | Foreign key to User |
| preference_id | UUID | No | Input profile used |
| name | string | Yes | 2-160 characters |
| status | string | Yes | `draft`, `saved`, or `ordered` |
| currency | char(3) | Yes | One currency in MVP |
| total_cost | decimal | Yes | Derived |
| total_credits | decimal | Yes | Derived |
| average_quality | decimal | No | Quantity-weighted |
| portfolio_risk | decimal | No | Quantity-weighted plus concentration penalty |
| optimizer_version | string | No | Null for fully manual portfolios |
| created_at | timestamp | Yes | UTC |
| updated_at | timestamp | Yes | UTC |

### PortfolioItem

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| portfolio_id | UUID | Yes | Foreign key to Portfolio |
| credit_id | UUID | Yes | Foreign key to CarbonCredit |
| quantity | decimal | Yes | Greater than zero |
| unit_price_snapshot | decimal | Yes | Price used at creation |
| allocation_percent | decimal | Yes | 0-100, portfolio totals 100 within tolerance |
| is_locked | boolean | Yes | Used during re-optimization |

### SimulatedOrder

| Field | Type | Required | Notes |
|---|---|---:|---|
| id | UUID | Yes | Primary key |
| reference | string | Yes | Unique human-readable reference |
| user_id | UUID | Yes | Foreign key to User |
| portfolio_id | UUID | Yes | Foreign key to Portfolio |
| status | OrderStatus | Yes | Always `simulated` in MVP |
| total_cost_snapshot | decimal | Yes | Immutable snapshot |
| total_credits_snapshot | decimal | Yes | Immutable snapshot |
| disclaimer_version | string | Yes | Reported disclaimer version |
| created_at | timestamp | Yes | UTC |

## 4. Relationships

```text
User 1---N BuyerPreference
User 1---N RecommendationRun
User 1---N Portfolio
User 1---N SimulatedOrder

Project 1---N CarbonCredit
Project 1---N ProjectDocument
ProjectDocument 1---N DocumentChunk
Project 1---N ProjectScore
Project 1---N RiskSignal

RecommendationRun 1---N RecommendationItem
Project 1---N RecommendationItem

Portfolio 1---N PortfolioItem
CarbonCredit 1---N PortfolioItem
Portfolio 1---0..1 SimulatedOrder
```

## 5. Derived values

- `total_cost = sum(quantity * unit_price_snapshot)`
- `total_credits = sum(quantity)`
- `allocation_percent = item quantity / total credits * 100`
- `average_quality` is quantity-weighted across items with scores.
- `portfolio_risk` is quantity-weighted risk plus the documented concentration penalty.
- Project, score, and price snapshots used in a simulated order must not change retroactively.

## 6. Deletion and retention

- Deleting a buyer account anonymizes or removes personal data while preserving non-personal demo-order audit records where required by the project design.
- Source projects are deactivated rather than deleted when referenced by portfolios.
- Document chunks are deleted when their parent document is removed.
- Authentication secrets and raw passwords are never logged.
