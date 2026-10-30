# Steam Data Pipeline

A multi-version data engineering project built using Python, PostgreSQL, and SQL.

This project extracts video game data from the SteamSpy API, transforms it into structured datasets, and loads it into PostgreSQL for storage and analysis.

The project is organized into two versions, called *Marks*, demonstrating the progression from a foundational ETL pipeline to a historical data pipeline with automated validation and analytical SQL queries.

## Project Versions

### Mark II — Historical Data Pipeline (Current)

**Status: Completed**

Mark II expands the original pipeline with:

- Historical data collection using timestamped snapshots
- A relational PostgreSQL schema separating game metadata from collected metrics
- Idempotent loading and transaction-level validation
- Automated database integrity checks
- SQL analysis using window functions and CTEs
- Configurable PostgreSQL connections
- Reproducible setup and execution instructions

The pipeline collects data for 100 popular Steam games and preserves observations across multiple executions, allowing comparisons of reported player counts and prices over time.

**[Explore Mark II — Code, Architecture, and Setup](mark-2/README.md)**

### Mark I — Foundational ETL Pipeline

**Status: Completed**

Mark I established the initial extraction, transformation, and loading workflow.

Features include:

- SteamSpy API extraction using Python
- JSON staging and transformation
- PostgreSQL loading with UPSERT operations
- SQL views and data validation
- Single-command pipeline execution

**[Explore Mark I](mark-1/README.md)**

## Pipeline Architecture

```text
SteamSpy API
     |
     v
Python Extraction
     |
     v
JSON Staging
     |
     v
PostgreSQL
  |       |
  v       v
games   game_snapshots
     |
     v
Data Validation
     |
     v
Historical SQL Analysis
```

*Architecture shown for Mark II.*

## Technologies

- **Programming:** Python, SQL
- **Database:** PostgreSQL
- **Libraries:** Requests, Psycopg
- **Data source:** SteamSpy API
- **Version control:** Git and GitHub

## Future Improvements

Potential future enhancements include automated scheduling, improved logging and error handling, additional tests, and data visualizations.

## Getting Started

**Mark II is the recommended version for exploring this project.**

See the [Mark II README](mark-2/README.md) for installation instructions, database setup, pipeline execution, and SQL analysis.