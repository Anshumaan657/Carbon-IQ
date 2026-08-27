# CarbonIQ MVP Scoring Methodology

## 1. Purpose

The CarbonIQ score is a transparent academic decision-support measure for comparing projects in the curated MVP dataset. It is not a certification, credit rating, guarantee of one tonne of climate benefit, legal opinion, or investment recommendation.

Version `1.0.0` uses deterministic rules and documented inputs. Machine-learning models must not silently replace this methodology.

## 2. Score direction

- Component, quality, impact, value, compatibility, match, and CarbonIQ scores: `0` weakest to `100` strongest.
- Risk score: `0` lowest observed risk to `100` highest observed risk.
- Confidence: `0.00` least supported to `1.00` most supported.

The interface must always label the direction of the risk score.

## 3. Overall components and weights

| Component | Weight | Main question |
|---|---:|---|
| Climate integrity and additionality | 25% | Is the claimed mitigation likely to be real and additional? |
| Permanence and reversal protection | 15% | How durable is the climate benefit and how is reversal managed? |
| Verification and methodology quality | 15% | Is the project supported by an appropriate methodology and current independent evidence? |
| Social and biodiversity co-benefits | 15% | Are wider benefits evidenced and safeguards described? |
| Price and buyer value | 10% | Is the price reasonable relative to comparable projects and buyer constraints? |
| Delivery and developer reliability | 10% | How strong are delivery evidence, monitoring, governance, and track record? |
| Regulatory and claims compatibility | 10% | Does documented eligibility align with the stated buyer use case? |
| **Total** | **100%** | |

All component scores are normalized to 0-100 before weighting.

```text
CarbonIQ score =
    0.25 * integrity
  + 0.15 * permanence
  + 0.15 * verification
  + 0.15 * co_benefits
  + 0.10 * value
  + 0.10 * delivery
  + 0.10 * compatibility
```

Round displayed scores to one decimal place. Store intermediate precision for reproducibility.

## 4. Component rubrics

Each component is built from documented subcriteria. The implementation must store which input caused each awarded or deducted point.

### 4.1 Climate integrity and additionality

Suggested subweights:

| Subcriterion | Share |
|---|---:|
| Additionality evidence | 35% |
| Baseline credibility | 25% |
| Quantification conservativeness | 20% |
| Leakage assessment | 10% |
| Double-counting controls | 10% |

### 4.2 Permanence and reversal protection

| Subcriterion | Share |
|---|---:|
| Expected storage duration | 35% |
| Reversal-risk assessment | 25% |
| Buffer, insurance, or replacement mechanism | 20% |
| Monitoring duration | 10% |
| Climate and disturbance exposure | 10% |

For non-storage project types, permanence scoring uses the applicable methodology rubric and records that a project-type-specific interpretation was used.

### 4.3 Verification and methodology quality

| Subcriterion | Share |
|---|---:|
| Methodology identified and applicable | 25% |
| Validation evidence | 20% |
| Verification evidence | 25% |
| Monitoring recency | 15% |
| Registry traceability | 15% |

### 4.4 Social and biodiversity co-benefits

| Subcriterion | Share |
|---|---:|
| Safeguards and stakeholder consultation | 25% |
| Community benefit evidence | 25% |
| Biodiversity benefit evidence | 20% |
| SDG evidence quality | 15% |
| Benefit-sharing transparency | 15% |

Self-reported SDG labels alone do not receive full evidence credit.

### 4.5 Price and buyer value

| Subcriterion | Share |
|---|---:|
| Price relative to comparable project-type and vintage median | 45% |
| Quality-adjusted price | 35% |
| Availability and delivery fit | 20% |

Synthetic or stale price data lowers confidence. A low price is not automatically a high value score.

### 4.6 Delivery and developer reliability

| Subcriterion | Share |
|---|---:|
| Monitoring and issuance history | 30% |
| Delivery evidence | 25% |
| Developer transparency | 20% |
| Governance and operational controls | 15% |
| Material controversy handling | 10% |

Absence of negative news is not treated as proof of strong governance.

### 4.7 Regulatory and claims compatibility

| Subcriterion | Share |
|---|---:|
| Documented program eligibility | 35% |
| Methodology/category eligibility | 30% |
| Vintage and geography compatibility | 20% |
| Claims-use documentation | 15% |

Compatibility is conditional on the buyer's declared use case. The MVP must use **Not assessed** where it lacks current authoritative evidence.

## 5. Summary scores

The UI may display the following derived summaries:

```text
quality_score =
    0.45 * integrity
  + 0.25 * permanence
  + 0.30 * verification

impact_score =
    0.60 * integrity
  + 0.40 * co_benefits
```

These are presentation summaries and do not add extra weight to the overall CarbonIQ score.

## 6. Risk score

The risk score combines the inverse of selected strength components with active risk-signal penalties:

```text
base_risk =
    0.35 * (100 - integrity)
  + 0.25 * (100 - permanence)
  + 0.20 * (100 - verification)
  + 0.20 * (100 - delivery)
```

Risk-signal penalties are capped so that the final score remains between 0 and 100:

- Info: 0 points
- Low: 2 points
- Medium: 6 points
- High: 12 points
- Critical: 20 points

```text
risk_score = clamp(base_risk + active_signal_penalties, 0, 100)
```

Duplicate signals arising from the same underlying evidence must be deduplicated. A critical signal requires human review and may make the project ineligible for low-risk recommendations.

Suggested display bands:

| Risk score | Label |
|---:|---|
| 0-24.9 | Low |
| 25-49.9 | Moderate |
| 50-74.9 | High |
| 75-100 | Very high |

## 7. Evidence confidence

Confidence reflects evidence coverage, recency, provenance, and consistency. It does not measure the probability that the project will succeed.

```text
confidence =
    0.35 * required_field_completeness
  + 0.30 * document_coverage
  + 0.20 * evidence_recency
  + 0.15 * cross_source_consistency
```

Each term is normalized between 0 and 1.

Suggested display bands:

| Confidence | Label |
|---:|---|
| 0.00-0.39 | Limited evidence |
| 0.40-0.69 | Moderate evidence |
| 0.70-1.00 | Stronger evidence |

### Minimum evidence rule

The overall score is `null` and marked **Insufficient evidence** when any of the following is missing:

- Stable project identity
- Project type and category
- Registry or issuing-program information
- Primary source URL
- At least one methodology, validation, verification, or monitoring evidence record appropriate to the project status

Missing optional evidence lowers the relevant component and confidence but is not automatically scored as fraud.

## 8. Buyer-specific match score

The match score is separate from the CarbonIQ score. It measures suitability for one preference profile.

Hard constraints are applied first:

- Currency comparability in the MVP
- Positive available quantity
- Maximum budget and required credits
- Explicit project-type, geography, category, delivery, or minimum-quality requirements
- Low-risk profile exclusions for unresolved critical warnings

Eligible projects are ranked using:

| Match factor | Default weight |
|---|---:|
| CarbonIQ score | 30% |
| Risk-tolerance fit | 20% |
| Budget/value fit | 20% |
| Project-type/category fit | 10% |
| Geography fit | 10% |
| SDG fit | 10% |

Weights are redistributed proportionally when the user leaves an optional preference unspecified. Every recommendation response includes matched factors and trade-offs.

## 9. Portfolio risk and optimization objective

The initial optimizer maximizes total buyer match and project quality while minimizing cost, risk, and concentration.

```text
portfolio_risk =
    quantity_weighted_project_risk
  + concentration_penalty
```

The concentration penalty begins when one project exceeds the configured maximum allocation. The optimizer must respect hard budget and quantity constraints and return `NO_FEASIBLE_PORTFOLIO` when they cannot be satisfied.

## 10. Risk-warning rules

Initial rules include:

- Missing verification evidence
- Unidentified methodology
- Duplicate registry project identifier
- Duplicate or highly similar description
- Implausible or inconsistent coordinates
- Vintage inconsistent with project dates
- Price far below comparable records
- Stale price or quantity snapshot
- Missing provenance
- Unresolved high-severity document inconsistency

Each signal includes a stable code, severity, message, evidence, rule version, and human-review requirement. The phrase **fraud detected** must not be used by deterministic warning rules.

## 11. Governance and versioning

- Store `methodology_version`, calculation time, and evidence snapshot with every score.
- Publish weight or rubric changes before recalculating scores.
- Preserve historical results for comparison.
- Test boundary values and representative project types.
- Review project-type fairness and systematic missing-data effects.
- Never allow transaction revenue, paid placement, or seller identity to alter a score.
- Human reviewers may resolve evidence errors but must not silently overwrite calculated results.

## 12. Validation tests

The scoring module must include tests proving that:

- All scores remain within their stated ranges.
- Component weights total 100%.
- Increasing a positive component cannot reduce the overall score when other inputs are unchanged.
- Increasing a risk penalty cannot reduce the risk score.
- Missing required evidence returns an unscored result.
- Identical inputs and methodology versions produce identical outputs.
- Explanations identify the inputs responsible for the result.
