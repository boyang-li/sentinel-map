#!/usr/bin/env python3
"""
Download OSM traffic infrastructure data using Overpass API
"""

import requests
import time
from pathlib import Path

def download_osm_traffic_signs(bbox: tuple, output_file: str):
    """
    Download traffic signs from OSM using Overpass API
    
    Args:
        bbox: (min_lat, min_lon, max_lat, max_lon)
        output_file: Path to save XML file
    """
    min_lat, min_lon, max_lat, max_lon = bbox
    
    # Overpass query for traffic infrastructure
    query = f"""
    [out:xml][timeout:180];
    (
      node["traffic_sign"]({min_lat},{min_lon},{max_lat},{max_lon});
      node["highway"="traffic_signals"]({min_lat},{min_lon},{max_lat},{max_lon});
      node["highway"="stop"]({min_lat},{min_lon},{max_lat},{max_lon});
      node["highway"="give_way"]({min_lat},{min_lon},{max_lat},{max_lon});
      node["highway"="speed_camera"]({min_lat},{min_lon},{max_lat},{max_lon});
      node["traffic_sign:forward"]({min_lat},{min_lon},{max_lat},{max_lon});
      node["traffic_sign:backward"]({min_lat},{min_lon},{max_lat},{max_lon});
      node["direction"]["highway"="street_lamp"]({min_lat},{min_lon},{max_lat},{max_lon});
    );
    out body;
    >;
    out skel qt;
    """
    
    print(f"🌍 Downloading OSM data for bbox: {bbox}")
    print(f"   Area: {abs(max_lat-min_lat):.4f}° lat × {abs(max_lon-min_lon):.4f}° lon")
    
    # Overpass API endpoint
    url = "https://overpass-api.de/api/interpreter"
    
    try:
        response = requests.post(url, data={"data": query}, timeout=300)
        response.raise_for_status()
        
        # Save to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded {len(response.content):,} bytes")
        print(f"💾 Saved to: {output_path}")
        
        # Parse and count nodes
        import xml.etree.ElementTree as ET
        tree = ET.fromstring(response.content)
        node_count = len(tree.findall('.//node'))
        print(f"📊 Found {node_count} traffic infrastructure nodes")
        
        return str(output_path)
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Try a smaller area or increase timeout.")
        raise
    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        raise

def main():
    # Example: Downtown Toronto area
    # Adjust these coordinates based on your detection coverage
    bbox = (
        43.62,  # min_lat (south)
        -79.45, # min_lon (west)
        43.75,  # max_lat (north)
        -79.30  # max_lon (east)
    )
    
    output_file = Path(__file__).parent.parent.parent / 'local-mvp' / 'osm_full.xml'
    
    print("=" * 60)
    print("OSM Traffic Infrastructure Downloader")
    print("=" * 60)
    
    # Download data
    downloaded_file = download_osm_traffic_signs(bbox, str(output_file))
    
    print("\n✨ Download complete!")
    print(f"\nNext step: Run ingest script to upload to Snowflake:")
    print(f"   python scripts/ingest_osm_to_snowflake.py")

if __name__ == "__main__":
    main()
