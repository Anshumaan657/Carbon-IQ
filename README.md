# CarbonIQ

CarbonIQ is an AI-powered carbon-credit intelligence and comparison platform. It helps organizations discover, evaluate and compare carbon-credit projects using explainable quality, climate-impact, risk and value scores.

## Planned MVP

- Carbon-project catalogue
- Search and comparison
- CarbonIQ scoring engine
- Personalized recommendations
- Portfolio optimization
- Risk-warning indicators
- Document-based AI assistant
- Analytics dashboard
- Simulated purchase and retirement certificate

## Technology Stack

- Next.js and TypeScript
- Python FastAPI
- PostgreSQL and PostGIS
- pgvector
- scikit-learn
- Pandas
- Google OR-Tools
- Docker
- GitHub Actions

## Repository Structure

- `apps/web` — Next.js frontend
- `services/api` — FastAPI backend and AI services
- `data` — sample and locally processed data
- `docs` — architecture and project documentation
- `scripts` — development and data-import utilities
- `tests` — end-to-end tests
- `infrastructure` — deployment and container configuration

## Documentation

- [Complete project documentation](docs/PROJECT_DOCUMENTATION.md)
- [MVP project scope](docs/PROJECT_SCOPE.md)
- [API specification](docs/api/API_SPECIFICATION.md)
- [Data model](docs/DATA_MODEL.md)
- [Scoring methodology](docs/scoring/SCORING_METHODOLOGY.md)
- [Delivery roadmap](docs/ROADMAP.md)

## Project Status

Product contracts, typed backend configuration, PostgreSQL/Docker infrastructure,
and the core domain schema are implemented. Catalogue ingestion, frontend,
scoring, recommendations, optimization, RAG and reporting remain in development.
