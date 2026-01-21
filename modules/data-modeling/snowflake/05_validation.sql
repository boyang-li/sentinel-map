-- ============================================================================
-- SentinelMap: Validation Queries
-- ============================================================================

USE ROLE SENTINEL_ROLE;
USE WAREHOUSE SENTINEL_WH;
USE DATABASE SENTINEL_MAP;
USE SCHEMA RAW;

-- 1. Check table row counts
SELECT 'STG_DETECTIONS' AS table_name, COUNT(*) AS row_count FROM STG_DETECTIONS
UNION ALL
SELECT 'REF_OSM_NODES', COUNT(*) FROM REF_OSM_NODES;

-- 2. Verify table structure
SHOW COLUMNS IN TABLE REF_OSM_NODES;

-- 3. Test spatial distance calculation
SELECT
    OSM_ID,
    OSM_TYPE,
    LATITUDE,
    LONGITUDE,
    ST_DISTANCE(
        TO_GEOGRAPHY('POINT(' || LONGITUDE || ' ' || LATITUDE || ')'),
        TO_GEOGRAPHY('POINT(-79.3140 43.7900)')  -- Example detection location
    ) AS distance_from_detection_meters
FROM REF_OSM_NODES
ORDER BY distance_from_detection_meters
LIMIT 5;

-- 4. Check resource monitor status
SHOW RESOURCE MONITORS;

-- 5. View warehouse credit usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE WAREHOUSE_NAME = 'SENTINEL_WH'
ORDER BY START_TIME DESC
LIMIT 10;
