# Steam Data Pipeline — Mark II

## 1. Project Overview

Mark II builds on the original Steam Data Pipeline (Mark I) by introducing historical data collection, database validation, and SQL-based analysis.

The project uses Python to extract information about 100 popular Steam games from the SteamSpy API, transforms the API response into structured JSON, and loads the data into a PostgreSQL database.

Unlike Mark I, which maintained a single record per game, Mark II separates game metadata from time-dependent metrics. Each pipeline execution collects a new timestamped snapshot, allowing data to be compared across multiple collection runs.

The pipeline includes automated validation checks to verify data integrity and SQL queries that analyze changes in concurrent player counts (CCU) and game prices.

**Technologies:** Python, PostgreSQL, SQL, SteamSpy API, Requests, Psycopg.

## 2. Pipeline Architecture

```text
SteamSpy API
     |
     v
Python Extraction (extract.py)
     |
     v
JSON Data (games.json)
     |
     v
PostgreSQL Loading (load.py)
     |
     +--> games
     |
     +--> game_snapshots
     |
     v
Database Validation (validate.py)
     |
     v
SQL Historical Analysis
```

The `run_pipeline.py` script orchestrates extraction, loading, and validation in sequence. Historical analysis queries can then be executed against the stored snapshots.

## 3. Database Design

Mark II uses a relational PostgreSQL database consisting of two tables: `games` and `game_snapshots`.

### games

The `games` table stores identifying information about each Steam game.

| Column | Data Type | Description |
|---|---|---|
| `appid` | INTEGER | Primary key identifying each game |
| `name` | TEXT | Game title |
| `developer` | TEXT | Game developer |
| `publisher` | TEXT | Game publisher |

Each game appears only once in this table. If the pipeline encounters an existing game, its metadata is updated rather than creating a duplicate record.

### game_snapshots

The `game_snapshots` table stores metrics collected during each pipeline execution.

| Column | Data Type | Description |
|---|---|---|
| `appid` | INTEGER | Foreign key referencing `games.appid` |
| `collected_at` | TIMESTAMPTZ | Timestamp of data collection |
| `positive` | INTEGER | Reported positive reviews |
| `negative` | INTEGER | Reported negative reviews |
| `price` | INTEGER | Reported price in cents |
| `initialprice` | INTEGER | Reported original price in cents |
| `discount` | INTEGER | Reported discount percentage |
| `ccu` | INTEGER | Reported concurrent users |

The table uses a composite primary key consisting of `appid` and `collected_at`. This prevents duplicate snapshots for the same game and collection timestamp while allowing multiple historical observations.

### Relationship Between Tables

The database uses a one-to-many relationship:

- One game can have multiple historical snapshots.
- Each snapshot belongs to exactly one game.
- A foreign key ensures that snapshots reference existing games.

Separating game metadata from collected metrics reduces unnecessary duplication and makes historical comparisons easier.

### Historical Data Collection

Each extraction run assigns a shared UTC collection timestamp to its records. When loading data, the pipeline inserts new snapshots while preserving previously collected observations.

The loader uses PostgreSQL's `ON CONFLICT` functionality to avoid duplicate records when the same extracted dataset is loaded more than once.

As a result, Mark II supports repeated data collection without overwriting its historical snapshots.

## 4. Setup and Execution

### Prerequisites

Before running Mark II, make sure the following are installed:

- Python 3.13
- PostgreSQL
- Git

PostgreSQL must be running and configured to allow local database connections.

### Step 1: Clone the Repository

```bash
git clone https://github.com/gabe-di/steam-data-pipeline.git
cd steam-data-pipeline/mark-2
```

### Step 2: Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

The commands above use a macOS/Linux shell.

### Step 3: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

The project uses `requests` for API extraction and `psycopg` for PostgreSQL connectivity.

### Step 4: Create the PostgreSQL Database

Create a database named `steam_data_mk2`:

```bash
createdb steam_data_mk2
```

Initialize the database tables:

```bash
psql -d steam_data_mk2 -v ON_ERROR_STOP=1 -f sql/create_tables.sql
```

This creates the `games` and `game_snapshots` tables.

By default, the pipeline connects to a local PostgreSQL database named `steam_data_mk2`. Alternatively, the database connection can be configured using the `DATABASE_URL` environment variable.

For example, to connect to a different local PostgreSQL database:

```bash
export DATABASE_URL="postgresql:///steam_test"
python src/run_pipeline.py
```

The specified database must already exist and contain the required tables. PostgreSQL must also be running, and the configured user must have permission to access it.

If `DATABASE_URL` is not set, the pipeline connects to `steam_data_mk2` by default.

### Step 5: Run the Pipeline

```bash
python src/run_pipeline.py
```

The orchestration script automatically executes three stages:

1. **Extraction:** Retrieves game data from SteamSpy and saves it to `data/games.json`.
2. **Loading:** Inserts or updates game metadata and inserts timestamped snapshots into PostgreSQL.
3. **Validation:** Checks the database for orphaned snapshots, invalid metrics, and duplicate records.

A successful run ends with:

```text
All database validation checks passed!!
Steam Data Pipeline Mark II completed successfully!
```

### Step 6: Run Historical SQL Queries

To examine historical changes in concurrent player counts:

```bash
psql -d steam_data_mk2 -f sql/historical_ccu_analysis.sql
```

To examine the latest CCU changes:

```bash
psql -d steam_data_mk2 -f sql/latest_ccu_changes.sql
```

To identify price changes between snapshots:

```bash
psql -d steam_data_mk2 -f sql/price_changes.sql
```

These analyses become more useful as additional snapshots are collected over time.

### Repeated Execution

The pipeline can be run multiple times to collect additional observations.

Each new extraction generates a UTC collection timestamp. Previously stored snapshots are preserved, allowing historical comparisons.

Reloading the same JSON dataset does not create duplicate snapshots because the database enforces a composite primary key on `appid` and `collected_at`.

## 5. SQL Analysis

Mark II includes three SQL analysis scripts designed to compare game metrics across historical snapshots.

These queries use PostgreSQL window functions and common table expressions (CTEs) to identify changes between consecutive observations.

### Historical Concurrent Player Analysis

**File:** `sql/historical_ccu_analysis.sql`

This query examines changes in reported concurrent player counts (CCU) across all collected snapshots.

It uses the `LAG()` window function to retrieve the previous CCU observation for each game, ordered by collection timestamp.

By comparing the current and previous values, the query calculates the difference in reported concurrent players between consecutive snapshots.

This allows the database to support historical comparisons as additional observations are collected.

### Latest Concurrent Player Changes

**File:** `sql/latest_ccu_changes.sql`

This query focuses on the most recent CCU comparison for each game.

It combines `LAG()` with `ROW_NUMBER()` to identify each game's latest snapshot and compare its reported CCU against the preceding observation.

Results are ordered by the absolute size of the change, making it easier to identify games with the largest differences in reported concurrent players.

### Historical Price Changes

**File:** `sql/price_changes.sql`

This query identifies changes in reported game prices between consecutive snapshots.

It uses `LAG()` to compare each game's current price against its previous recorded price. Prices are converted from cents to dollars for readability.

During development, the pipeline detected a reported price change for *Dead by Daylight*, from $19.99 to $7.99, representing a 60% decrease between collected observations.

This example demonstrates how the historical snapshot model can capture changes that would be lost in a database storing only the latest values.

### Interpretation of Results

The SQL queries compare values returned by the SteamSpy API at different collection times.

Because SteamSpy may cache or periodically refresh its data, consecutive pipeline runs may return identical metrics even when time has passed.

Therefore, differences should be interpreted as changes between collected API observations rather than guaranteed real-time changes in Steam player activity.

The `collected_at` field records when the pipeline retrieved the data, not necessarily when SteamSpy originally updated its underlying metrics.

## 6. Data Quality and Limitations

### Data Validation

Mark II includes automated validation checks to help maintain data integrity throughout the ETL process.

The pipeline performs validation during database loading and after records have been committed.

**Validation during loading (`src/load.py`)**

Before committing a batch of records, the loader checks that:

- Positive and negative review counts are nonnegative.
- Concurrent player counts (`ccu`) are nonnegative.
- Prices (`price` and `initialprice`) are nonnegative.
- Discount percentages fall between 0 and 100.
- Required price and discount values are not null.

If validation fails, the transaction is rolled back rather than committing the invalid batch.

**Database validation (`src/validate.py`)**

After loading, a separate validation script checks for:

- **Orphaned snapshots:** Records referencing a game that does not exist in the `games` table.
- **Invalid snapshots:** Records containing invalid numerical values or missing required metrics.
- **Duplicate snapshots:** Multiple records with the same combination of `appid` and `collected_at`.

The database also enforces primary key and foreign key constraints to help prevent duplicate records and invalid relationships.

The SQL file `sql/validate_data.sql` provides additional queries for manually inspecting these conditions.

### Data Source Limitations

The pipeline retrieves information from the SteamSpy API, which introduces several limitations.

**1. API caching and update frequency**

SteamSpy may cache responses or update its underlying metrics periodically.

During development, multiple extractions returned identical concurrent player counts and review totals despite being collected at different times.

This means that repeated collection does not guarantee new underlying measurements.

**2. Collection time versus source update time**

The `collected_at` timestamp records when the pipeline retrieved the API response.

It does not establish when SteamSpy last refreshed the underlying game metrics.

Consequently, historical comparisons represent changes between collected API responses rather than a continuous record of real-time Steam activity.

**3. Limited dataset scope**

Each execution retrieves up to 100 games from SteamSpy's `top100in2weeks` endpoint.

This dataset represents a selected group of popular games rather than the entire Steam catalog. Its membership may also change between executions.

**4. API availability**

The pipeline depends on an external API. Network failures, service interruptions, or changes to the API response format may prevent successful extraction.

### Future Improvements

Potential extensions include:

- Automated scheduling for regular snapshot collection.
- Improved API error handling and retry logic.
- Logging to track pipeline executions and failures.
- Additional data quality checks, including checks for unexpectedly empty API responses.
- Visualizations or dashboards for exploring historical game metrics.

These improvements would make the pipeline more robust and easier to operate over longer periods.

## 7. Mark I vs. Mark II

Mark II builds on the original Steam Data Pipeline by improving how data is structured, stored, validated, and analyzed.

Mark I established the foundation of the project: extracting data from the SteamSpy API, transforming it into JSON, and loading it into PostgreSQL.

Mark II expands that foundation into a historical data pipeline capable of preserving observations across multiple executions.

### Comparison

| Feature | Mark I | Mark II |
|---|---|---|
| API extraction | SteamSpy API | SteamSpy API |
| Data processing | Python and JSON | Python and JSON |
| Database | PostgreSQL | PostgreSQL |
| Database structure | Single `games` table | Separate `games` and `game_snapshots` tables |
| Data storage | Latest values updated through UPSERT | Historical snapshots preserved across runs |
| Historical analysis | Not supported | SQL window functions and CTEs |
| Data validation | SQL validation queries | Transaction-level checks and automated post-load validation |
| Duplicate handling | UPSERT on game ID | UPSERT for metadata and composite primary key for snapshots |
| Pipeline execution | Python orchestration script | Python orchestration with automated validation |

### Key Engineering Improvements

**1. Historical data preservation**

Mark I stored the latest available values for each game, replacing previous measurements when the pipeline ran again.

Mark II preserves timestamped observations, making it possible to compare reported metrics across different collection runs.

**2. Improved relational database design**

Mark II separates relatively stable game metadata from frequently collected metrics.

This creates a one-to-many relationship between games and their historical snapshots, reducing unnecessary duplication and supporting time-based analysis.

**3. Automated data validation**

Mark II validates numerical values before committing database transactions and performs additional integrity checks after loading.

These checks help identify invalid metrics, duplicate snapshots, and broken relationships between tables.

**4. More advanced SQL analysis**

Mark II introduces SQL queries using window functions such as `LAG()` and `ROW_NUMBER()`, along with common table expressions.

These queries support historical comparisons of reported concurrent player counts and game prices.

**5. Improved reproducibility**

Mark II includes a dependency file, a database initialization script, and documentation explaining how to configure and execute the pipeline.

The Python scripts also resolve data paths relative to their own locations, reducing dependence on the terminal's working directory.

### Project Takeaways

Developing Mark II provided practical experience with several important data engineering concepts, including relational database design, historical data modeling, transaction management, idempotent loading, automated validation, and SQL-based analysis.

The transition from Mark I to Mark II demonstrates how a basic API-to-database workflow can be extended into a more maintainable analytical pipeline.