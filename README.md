# Steam Data Pipeline

A multi-version data engineering project built using Python, PostgreSQL, and SQL.

The project explores the development of a data pipeline that extracts video game data from the SteamSpy API, processes and stores it in PostgreSQL, and makes it available for querying and analysis.

Each version, referred to as a **Mark**, builds on the previous implementation by introducing new functionality and data engineering concepts.

## Project Versions

### Mark 1 — Foundational ETL Pipeline

**Status:** Completed

The first implementation establishes the foundation of the pipeline, including:

- API extraction using Python and Requests
- JSON staging and data processing
- PostgreSQL loading with UPSERT operations
- SQL transformations using database views
- Transaction-level validation and rollback
- Post-load SQL data quality checks
- Single-command pipeline execution

**[View Mark 1](mark-1/README.md)**

## Planned Improvements

Future versions may explore:

- Historical data collection and tracking
- More advanced SQL transformations and analytics
- Database normalization
- Automated pipeline scheduling
- Improved logging and error handling

Each Mark will have its own implementation and documentation to demonstrate how the project evolves over time.

## Technologies

- Python
- PostgreSQL
- SQL
- Requests
- Psycopg
- SteamSpy API