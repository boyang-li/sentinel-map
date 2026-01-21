-- ============================================================================
-- SentinelMap: Table Definitions
-- ============================================================================

USE ROLE SENTINEL_ROLE;
USE WAREHOUSE SENTINEL_WH;
USE DATABASE SENTINEL_MAP;
USE SCHEMA RAW;

-- ============================================================================
-- Kafka Ingestion Table (Raw JSON)
-- Note: Snowpipe Streaming does not support DEFAULT values or GEOGRAPHY columns
-- ============================================================================

CREATE OR REPLACE TABLE STG_DETECTIONS (
    RECORD_METADATA VARIANT,        -- Kafka metadata (offset, partition, timestamp)
    RECORD_CONTENT VARIANT,         -- Raw JSON from Module B
    INGESTED_AT TIMESTAMP_NTZ,      -- Populated by Kafka connector
    KAFKA_TOPIC VARCHAR(255),
    KAFKA_PARTITION NUMBER(10,0),
    KAFKA_OFFSET NUMBER(38,0),
    KAFKA_TIMESTAMP TIMESTAMP_NTZ
)
COMMENT = 'Raw Kafka messages from traffic sign detections'
CLUSTER BY (KAFKA_TIMESTAMP);  -- Optimize for time-based queries

-- ============================================================================
-- OSM Ground Truth Table
-- Note: Store lat/lon as numbers, compute GEOGRAPHY in views for spatial queries
-- ============================================================================

CREATE OR REPLACE TABLE REF_OSM_NODES (
    OSM_ID VARCHAR(50) PRIMARY KEY,
    OSM_TYPE VARCHAR(50),           -- 'traffic_sign', 'traffic_light', etc.
    LATITUDE NUMBER(10, 7) NOT NULL,
    LONGITUDE NUMBER(10, 7) NOT NULL,
    TAGS VARIANT,                   -- JSON object with all OSM tags
    UPLOADED_AT TIMESTAMP_NTZ,
    SOURCE_FILE VARCHAR(255)
)
COMMENT = 'OpenStreetMap ground truth for traffic infrastructure';

-- Note: GEOGRAPHY will be computed in views using TO_GEOGRAPHY(POINT(LONGITUDE LATITUDE))

-- Note: Snowflake automatically optimizes GEOGRAPHY queries without explicit indexes
-- Clustering can be added if needed: CLUSTER BY (LOCATION)

-- ============================================================================
-- Verification: Sample queries
-- ============================================================================

SELECT 'STG_DETECTIONS created successfully' AS STATUS;
SELECT 'REF_OSM_NODES created successfully' AS STATUS;
