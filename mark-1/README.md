# Steam Data Pipeline — Mark 1

## Project Overview

This project is a Python and PostgreSQL data pipeline that extracts game data from the SteamSpy API, processes the data into a structured JSON format, and loads it into a PostgreSQL database for querying and analysis.

The pipeline supports inserting new games, updating existing records, validating data quality, and rolling back database changes when validation fails.

The entire pipeline can be executed using a single Python command.

## Pipeline Architecture

```text
SteamSpy API
    |
    v
Python Extraction (src/extract.py)
    |
    v
JSON Staging (data/games.json)
    |
    v
PostgreSQL Loading (src/load.py)
    |
    v
SQL Transformation (sql/create_views.sql)
    |
    v
Data Validation (sql/validate_data.sql)
```

The loading stage includes transaction-level validation before committing records to PostgreSQL.

## Technologies Used

- **Python** — API extraction, JSON processing, and pipeline orchestration
- **PostgreSQL** — Relational database for storing game records
- **SQL** — Data transformation, querying, and validation
- **Requests** — HTTP requests to the SteamSpy API
- **Psycopg** — PostgreSQL connectivity from Python
- **SteamSpy API** — Source of game metadata and statistics

## Project Structure

```text
steam-data-pipeline/
├── src/
│   ├── extract.py
│   ├── load.py
│   └── run_pipeline.py
├── sql/
│   ├── analyze_games.sql   
│   ├── create_tables.sql
│   ├── create_views.sql
│   └── validate_data.sql
├── data/
├── requirements.txt
├── .gitignore
└── README.md
```

### Python Scripts

- **`src/extract.py`** — Retrieves game data from the SteamSpy API, selects relevant fields, converts pricing information into integers, and saves the processed records to a JSON file.

- **`src/load.py`** — Loads game records from JSON into PostgreSQL. Uses UPSERT operations to insert new games or update existing records. Performs data validation within a database transaction and rolls back changes if invalid data is detected.

- **`src/run_pipeline.py`** — Orchestrates the complete pipeline by executing extraction, loading, SQL transformations, and validation in sequence.

### SQL Scripts

- **`sql/create_tables.sql`** — Defines the PostgreSQL `games` table, including its columns, data types, and primary key.

- **`sql/create_views.sql`** — Creates a SQL view that transforms game prices from integer cents into dollar amounts, making the data easier to query and analyze.

- **`sql/validate_data.sql`** — Runs data quality checks for negative prices, invalid discount percentages, missing required values, and consistency between the source table and transformation view. Raises exceptions for invalid prices, discounts, and missing required values.

- **`sql/analyze_games.sql — Analyzes discounted games by calculating positive review percentages, filtering by minimum review counts, and ranking eligible games.

### Additional Files

- **`data/`** — Stores the intermediate JSON dataset generated during extraction. The JSON file is excluded from Git tracking.

- **`requirements.txt`** — Lists the Python dependencies needed to run the pipeline.

- **`.gitignore`** — Prevents virtual environments, temporary files, and local datasets from being committed to Git.

- **`README.md`** — Documents the project's purpose, architecture, setup instructions, and functionality.

## Data Validation

The pipeline uses two stages of data validation to check the quality of the stored game records.

### 1. Transaction-Level Validation

During loading, `src/load.py` checks for negative prices, invalid discount percentages, and missing required values before committing changes to PostgreSQL.

If invalid records are detected, the transaction is rolled back, preserving the previously committed data.

### 2. Post-Load Validation

After loading and transforming the data, `sql/validate_data.sql` performs additional checks against the database, including comparing record counts between the `games` table and the `game_prices` view.

The SQL script raises exceptions when it detects invalid prices, discounts, or missing required values, causing the pipeline to stop.

The row-count comparison currently serves as a reporting check rather than an enforced constraint. Post-load validation does not roll back changes already committed by the loader.

## Setup and Execution

### Prerequisites

- Python 3
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/gabe-di/steam-data-pipeline.git
cd steam-data-pipeline/mark-1
```

### 2. Install Python Dependencies

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Set Up PostgreSQL

Ensure PostgreSQL is installed and running.

Create the database:

```bash
createdb steam_data
```

Create the required table:

```bash
psql -d steam_data -v ON_ERROR_STOP=1 -f sql/create_tables.sql
```

These commands assume the local PostgreSQL user has the necessary permissions and can connect without additional credentials.

### 4. Run the Pipeline

From the project root directory, execute:

```bash
python src/run_pipeline.py
```

This runs extraction, loading, SQL transformations, and validation in sequence.

The pipeline retrieves up to 100 games from SteamSpy's top-games endpoint and inserts or updates their records in PostgreSQL.

## Analytical Findings

### Research Question

Which discounted games have the highest positive review percentages among games with at least 1,000 reviews?

### Methodology

Using PostgreSQL, the analysis calculates each game's positive review percentage by dividing positive reviews by the total number of positive and negative reviews.

Games must have at least 1,000 total reviews and a discount greater than 0% to qualify. Eligible games are ranked by positive review percentage, with total review count used as a secondary sorting criterion.

The analysis is implemented in `sql/analyze_games.sql`.

### Findings

Of the 100 games collected from SteamSpy, nine met the analysis criteria.

Portal ranked first with a 98.47% positive review percentage, an 80% discount, and a price of $1.99. Stardew Valley (98.44%) and Schedule I (98.41%) followed closely.

All nine qualifying games had positive review percentages above 96%, suggesting that the discounted games in this particular sample were generally well reviewed.

Portal and Counter-Strike shared the highest discount percentage at 80%.

### Limitations

The dataset comes from SteamSpy's top-games endpoint rather than the entire Steam catalog. Therefore, these results should not be generalized to all Steam games.

The analysis uses review counts supplied by SteamSpy, which may differ from the review scores displayed on Steam.

Prices and discounts reflect the API data at the time of extraction and may change.

The analysis ranks games by positive review percentage rather than combining review quality and discount size into a single value metric.



## Future Improvements

Potential improvements for future versions include:

- **Historical Data Tracking** — Store periodic snapshots to analyze changes in game prices, player counts, and review statistics over time.
- **Expanded SQL Transformations** — Create additional views for game popularity, review ratios, and publisher-level statistics.
- **Database Normalization** — Separate game, developer, and publisher information into related tables.
- **Automated Scheduling** — Run the pipeline at regular intervals instead of requiring manual execution.
- **Improved Error Handling** — Add API timeouts, retries, more comprehensive validation, and logging.

These improvements would expand the pipeline beyond its initial implementation while building on the existing extraction, loading, and validation functionality.
