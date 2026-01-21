# Module C: Data Modeling & Cloud Ingestion

This module handles the bridge between Kafka streams and Snowflake analytics, including OSM ground truth ingestion.

## Directory Structure

```
modules/data-modeling/
├── snowflake/
│   ├── 01_initial_setup.sql          # Database, warehouse, and resource monitor setup
│   ├── 02_create_tables.sql          # STG_DETECTIONS and REF_OSM_NODES tables
│   ├── 03_configure_kafka_user.sql   # Kafka connector authentication
│   ├── 04_create_views.sql           # Flattened views for dbt
│   ├── 05_validation.sql             # Health checks and verification queries
│   ├── Initial_Configuration.sql     # (Legacy - use 01_initial_setup.sql)
│   └── Table_Definitions.sql         # (Legacy - use 02_create_tables.sql)
├── scripts/
│   └── ingest_osm_to_snowflake.py   # OSM XML to Snowflake uploader
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variable template
└── README.md                         # This file
```

## Quick Start

### 1. Snowflake Setup

Execute SQL scripts in order:

```sql
-- In Snowflake worksheet:
@01_initial_setup.sql       -- Creates database, warehouse, resource monitor
@02_create_tables.sql       -- Creates STG_DETECTIONS and REF_OSM_NODES
@04_create_views.sql        -- Creates flattened views
```

### 2. Kafka Connector

Follow these steps in Confluent Cloud:

1. Generate Snowflake key pair:
   ```bash
   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out snowflake_key.p8 -nocrypt
   openssl rsa -in snowflake_key.p8 -pubout -out snowflake_key.pub
   ```

2. Configure user in Snowflake:
   ```sql
   @03_configure_kafka_user.sql
   ```

3. Create connector in Confluent Cloud UI with Snowpipe Streaming

### 3. OSM Ground Truth Ingestion

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Snowflake credentials

# Run ingestion
python scripts/ingest_osm_to_snowflake.py
```

### 4. Validation

```sql
@05_validation.sql
```

## Key Features

- **GEOGRAPHY Type**: REF_OSM_NODES.LOCATION uses native GEOGRAPHY for accurate spherical distance calculations
- **VARIANT Type**: STG_DETECTIONS.RECORD_CONTENT stores raw JSON for schema flexibility
- **Resource Monitor**: Automatically suspends warehouse at 90% of $50 credit quota
- **Spatial Indexing**: Optimized for proximity queries between detections and OSM nodes
- **Auto-suspend**: Warehouse suspends after 60 seconds of inactivity

## Next Steps

- Set up dbt Cloud for transformation layer
- Create data quality tests
- Build audit dashboard in Streamlit

## Cost Management

Current configuration limits spend to $50 of $400 free trial credits:
- XSMALL warehouse (cheapest option)
- 60-second auto-suspend
- Resource monitor with hard stop at 90%

Monitor usage:
```sql
SHOW RESOURCE MONITORS;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE WAREHOUSE_NAME = 'SENTINEL_WH';
```
