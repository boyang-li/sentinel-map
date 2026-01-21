#!/usr/bin/env python3
"""
Automatically download OSM data based on detection coverage in Snowflake
"""

import snowflake.connector
import os
from dotenv import load_dotenv
from download_osm_data import download_osm_traffic_signs
from pathlib import Path

load_dotenv()

def get_detection_bbox():
    """Query Snowflake to get bounding box of all detections"""
    
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse='SENTINEL_WH',
        database='SENTINEL_MAP',
        schema='RAW'
    )
    
    cursor = conn.cursor()
    
    try:
        print("📊 Querying detection coverage from Snowflake...")
        
        cursor.execute("""
        SELECT 
            MIN(RECORD_CONTENT:vehicle_lat::NUMBER) AS min_lat,
            MAX(RECORD_CONTENT:vehicle_lat::NUMBER) AS max_lat,
            MIN(RECORD_CONTENT:vehicle_lon::NUMBER) AS min_lon,
            MAX(RECORD_CONTENT:vehicle_lon::NUMBER) AS max_lon,
            COUNT(*) AS total_detections
        FROM STG_DETECTIONS
        WHERE RECORD_CONTENT:vehicle_lat IS NOT NULL
        """)
        
        result = cursor.fetchone()
        min_lat, max_lat, min_lon, max_lon, count = result
        
        if min_lat is None:
            print("❌ No detections with GPS coordinates found")
            return None
        
        print(f"\n📍 Detection Coverage:")
        print(f"   Latitude:  {min_lat:.6f} to {max_lat:.6f}")
        print(f"   Longitude: {min_lon:.6f} to {max_lon:.6f}")
        print(f"   Total detections: {count}")
        
        # Add 10% buffer to catch nearby OSM nodes
        lat_buffer = (max_lat - min_lat) * 0.1
        lon_buffer = (max_lon - min_lon) * 0.1
        
        bbox = (
            min_lat - lat_buffer,
            min_lon - lon_buffer,
            max_lat + lat_buffer,
            max_lon + lon_buffer
        )
        
        print(f"\n📦 Bounding box (with 10% buffer): {bbox}")
        
        return bbox
        
    finally:
        cursor.close()
        conn.close()

def main():
    print("=" * 60)
    print("Auto-Download OSM Data for Detection Coverage")
    print("=" * 60)
    
    # Get bbox from Snowflake
    bbox = get_detection_bbox()
    
    if bbox is None:
        print("\n⚠️  No detections found. Upload detection data first.")
        return
    
    # Download OSM data
    output_file = Path(__file__).parent.parent.parent / 'local-mvp' / 'osm_auto.xml'
    
    print(f"\n🌍 Downloading OSM data for coverage area...")
    downloaded_file = download_osm_traffic_signs(bbox, str(output_file))
    
    print("\n✨ Complete!")
    print(f"\nNext: Update ingest_osm_to_snowflake.py to use: {output_file.name}")

if __name__ == "__main__":
    main()
