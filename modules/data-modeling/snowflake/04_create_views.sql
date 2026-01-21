-- ============================================================================
-- SentinelMap: Verification Views
-- ============================================================================

USE ROLE SENTINEL_ROLE;
USE WAREHOUSE SENTINEL_WH;
USE DATABASE SENTINEL_MAP;
USE SCHEMA RAW;

-- ============================================================================
-- Flatten Kafka JSON for dbt Consumption
-- ============================================================================

CREATE OR REPLACE VIEW VW_DETECTIONS_FLAT AS
SELECT
    -- Metadata
    RECORD_CONTENT:detection_id::VARCHAR AS detection_id,
    RECORD_CONTENT:vehicle_id::VARCHAR AS vehicle_id,
    RECORD_CONTENT:session_id::VARCHAR AS session_id,
    TO_TIMESTAMP_NTZ(RECORD_CONTENT:ingested_at::VARCHAR) AS detection_timestamp,
    
    -- Frame data
    RECORD_CONTENT:frame_number::NUMBER AS frame_number,
    RECORD_CONTENT:timestamp_sec::NUMBER AS timestamp_sec,
    
    -- Pixel coordinates
    RECORD_CONTENT:pixel_u::NUMBER AS pixel_u,
    RECORD_CONTENT:pixel_v::NUMBER AS pixel_v,
    
    -- Detection metadata
    RECORD_CONTENT:confidence::NUMBER AS confidence,
    RECORD_CONTENT:class_name::VARCHAR AS class_name,
    
    -- GPS data (GEOGRAPHY conversion)
    CASE 
        WHEN RECORD_CONTENT:vehicle_lat IS NOT NULL 
         AND RECORD_CONTENT:vehicle_lon IS NOT NULL
        THEN ST_POINT(
            RECORD_CONTENT:vehicle_lon::NUMBER,
            RECORD_CONTENT:vehicle_lat::NUMBER
        )
        ELSE NULL
    END AS vehicle_location,
    
    RECORD_CONTENT:vehicle_lat::NUMBER AS vehicle_lat,
    RECORD_CONTENT:vehicle_lon::NUMBER AS vehicle_lon,
    RECORD_CONTENT:heading::NUMBER AS heading,
    
    -- Kafka metadata
    KAFKA_TOPIC,
    KAFKA_PARTITION,
    KAFKA_OFFSET,
    KAFKA_TIMESTAMP,
    INGESTED_AT AS snowflake_ingested_at
    
FROM STG_DETECTIONS
WHERE RECORD_CONTENT IS NOT NULL;

-- ============================================================================
-- Test Spatial Join (Detection within 50m of OSM node)
-- ============================================================================

CREATE OR REPLACE VIEW VW_DETECTION_OSM_PROXIMITY AS
SELECT
    d.detection_id,
    d.class_name,
    d.vehicle_lat,
    d.vehicle_lon,
    o.OSM_ID,
    o.OSM_TYPE,
    o.LATITUDE AS osm_lat,
    o.LONGITUDE AS osm_lon,
    ST_DISTANCE(
        d.vehicle_location,
        TO_GEOGRAPHY('POINT(' || o.LONGITUDE || ' ' || o.LATITUDE || ')')
    ) AS distance_meters
FROM VW_DETECTIONS_FLAT d
CROSS JOIN REF_OSM_NODES o
WHERE d.vehicle_location IS NOT NULL
  AND ST_DISTANCE(
      d.vehicle_location,
      TO_GEOGRAPHY('POINT(' || o.LONGITUDE || ' ' || o.LATITUDE || ')')
  ) < 50  -- Within 50 meters
ORDER BY d.detection_id, distance_meters;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check ingestion status
SELECT 
    'Kafka Detections' AS source,
    COUNT(*) AS record_count,
    MIN(KAFKA_TIMESTAMP) AS earliest,
    MAX(KAFKA_TIMESTAMP) AS latest
FROM STG_DETECTIONS

UNION ALL

SELECT 
    'OSM Ground Truth' AS source,
    COUNT(*) AS record_count,
    MIN(UPLOADED_AT) AS earliest,
    MAX(UPLOADED_AT) AS latest
FROM REF_OSM_NODES;

-- Sample flattened records
SELECT * FROM VW_DETECTIONS_FLAT LIMIT 5;

-- Test spatial query
SELECT * FROM VW_DETECTION_OSM_PROXIMITY LIMIT 10;
