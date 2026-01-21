-- ============================================================================
-- SentinelMap: Initial Snowflake Setup
-- Purpose: Create database, schema, and resource monitoring
-- ============================================================================

-- Use ACCOUNTADMIN role for initial setup
USE ROLE ACCOUNTADMIN;

-- Create dedicated role for SentinelMap
CREATE ROLE IF NOT EXISTS SENTINEL_ROLE;
GRANT ROLE SENTINEL_ROLE TO USER <YOUR_USERNAME>;

-- Create warehouse with cost controls
CREATE WAREHOUSE IF NOT EXISTS SENTINEL_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60              -- Suspend after 1 minute of inactivity
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Warehouse for SentinelMap ingestion and analytics';

GRANT USAGE ON WAREHOUSE SENTINEL_WH TO ROLE SENTINEL_ROLE;

-- Create database and schema
CREATE DATABASE IF NOT EXISTS SENTINEL_MAP
  COMMENT = 'Traffic sign detection and map audit data';

CREATE SCHEMA IF NOT EXISTS SENTINEL_MAP.RAW
  COMMENT = 'Raw ingestion layer for Kafka data and OSM truth';

GRANT USAGE ON DATABASE SENTINEL_MAP TO ROLE SENTINEL_ROLE;
GRANT USAGE ON SCHEMA SENTINEL_MAP.RAW TO ROLE SENTINEL_ROLE;
GRANT CREATE TABLE ON SCHEMA SENTINEL_MAP.RAW TO ROLE SENTINEL_ROLE;
GRANT CREATE VIEW ON SCHEMA SENTINEL_MAP.RAW TO ROLE SENTINEL_ROLE;

-- ============================================================================
-- COST GUARDRAILS: Resource Monitor
-- ============================================================================

CREATE RESOURCE MONITOR IF NOT EXISTS SENTINEL_MONITOR
  WITH CREDIT_QUOTA = 50          -- Limit to $50 of $400 credits
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS
    ON 75 PERCENT DO NOTIFY        -- Alert at 75% usage
    ON 90 PERCENT DO SUSPEND       -- Suspend warehouse at 90%
    ON 100 PERCENT DO SUSPEND_IMMEDIATE;  -- Hard stop at 100%

ALTER WAREHOUSE SENTINEL_WH SET RESOURCE_MONITOR = SENTINEL_MONITOR;

-- Verify setup
SHOW RESOURCE MONITORS;
SHOW WAREHOUSES LIKE 'SENTINEL_WH';
SHOW DATABASES LIKE 'SENTINEL_MAP';
