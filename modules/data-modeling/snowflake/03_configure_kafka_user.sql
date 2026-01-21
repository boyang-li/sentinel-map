-- ============================================================================
-- Configure User for Kafka Connector
-- ============================================================================

USE ROLE ACCOUNTADMIN;

-- Set public key for your user (paste output from snowflake_key.pub)
ALTER USER <YOUR_USERNAME> SET RSA_PUBLIC_KEY='<PASTE_PUBLIC_KEY_HERE>';

-- Grant permissions
GRANT USAGE ON DATABASE SENTINEL_MAP TO ROLE SENTINEL_ROLE;
GRANT USAGE ON SCHEMA SENTINEL_MAP.RAW TO ROLE SENTINEL_ROLE;
GRANT INSERT ON TABLE SENTINEL_MAP.RAW.STG_DETECTIONS TO ROLE SENTINEL_ROLE;
GRANT SELECT ON TABLE SENTINEL_MAP.RAW.STG_DETECTIONS TO ROLE SENTINEL_ROLE;

-- Verify key is set
DESC USER <YOUR_USERNAME>;
