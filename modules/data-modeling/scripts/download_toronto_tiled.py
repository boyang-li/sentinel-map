#!/usr/bin/env python3
"""
Download Toronto traffic signs in tiles to avoid Overpass API timeouts
"""

import requests
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple

def create_tiles(bbox: Tuple[float, float, float, float], tile_size: float = 0.02) -> List[Tuple]:
    """
    Split large bounding box into smaller tiles
    
    Args:
        bbox: (min_lat, min_lon, max_lat, max_lon)
        tile_size: Size of each tile in degrees (0.02 ≈ 2km)
    
    Returns:
        List of tile bounding boxes
    """
    min_lat, min_lon, max_lat, max_lon = bbox
    
    tiles = []
    lat = min_lat
    while lat < max_lat:
        lon = min_lon
        while lon < max_lon:
            tile_bbox = (
                lat,
                lon,
                min(lat + tile_size, max_lat),
                min(lon + tile_size, max_lon)
            )
            tiles.append(tile_bbox)
            lon += tile_size
        lat += tile_size
    
    return tiles

def download_tile(bbox: Tuple[float, float, float, float], retry: int = 3) -> str:
    """Download OSM data for a single tile"""
    min_lat, min_lon, max_lat, max_lon = bbox
    
    query = f"""
    [out:xml][timeout:60];
    (
      node["traffic_sign"]({min_lat},{min_lon},{max_lat},{max_lon});
      node["highway"="traffic_signals"]({min_lat},{min_lon},{max_lat},{max_lon});
      node["highway"="stop"]({min_lat},{min_lon},{max_lat},{max_lon});
      node["highway"="give_way"]({min_lat},{min_lon},{max_lat},{max_lon});
    );
    out body;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    
    for attempt in range(retry):
        try:
            response = requests.post(url, data={"data": query}, timeout=120)
            response.raise_for_status()
            return response.content
        except requests.exceptions.Timeout:
            if attempt < retry - 1:
                print(f"   ⏳ Timeout, retrying... ({attempt + 1}/{retry})")
                time.sleep(2)
            else:
                raise
        except requests.exceptions.RequestException as e:
            if attempt < retry - 1:
                print(f"   ⚠️  Error, retrying... ({attempt + 1}/{retry})")
                time.sleep(2)
            else:
                raise

def merge_osm_tiles(tiles_data: List[bytes]) -> ET.ElementTree:
    """Merge multiple OSM XML tiles into one"""
    # Create root element
    osm_root = ET.Element('osm', version='0.6')
    seen_ids = set()
    
    for tile_data in tiles_data:
        if not tile_data:
            continue
        
        try:
            tile_root = ET.fromstring(tile_data)
            for node in tile_root.findall('.//node'):
                node_id = node.get('id')
                if node_id not in seen_ids:
                    osm_root.append(node)
                    seen_ids.add(node_id)
        except ET.ParseError:
            continue
    
    return ET.ElementTree(osm_root)

def download_toronto_tiled():
    """Download Toronto in tiles and merge"""
    print("=" * 60)
    print("Tiled Toronto OSM Download")
    print("=" * 60)
    
    # Full Toronto bounds
    toronto_bbox = (
        43.58,   # min_lat (south)
        -79.64,  # min_lon (west)
        43.86,   # max_lat (north)
        -79.12   # max_lon (east)
    )
    
    # Create tiles (0.02 degrees ≈ 2km squares)
    tiles = create_tiles(toronto_bbox, tile_size=0.02)
    
    print(f"\n📦 Toronto split into {len(tiles)} tiles")
    print(f"   Downloading ~2km × 2km tiles to avoid timeouts...")
    
    tiles_data = []
    failed = 0
    
    for i, tile_bbox in enumerate(tiles, 1):
        print(f"\n🔄 Tile {i}/{len(tiles)}: {tile_bbox[0]:.4f},{tile_bbox[1]:.4f} → {tile_bbox[2]:.4f},{tile_bbox[3]:.4f}")
        
        try:
            data = download_tile(tile_bbox)
            tiles_data.append(data)
            
            # Count nodes in this tile
            tree = ET.fromstring(data)
            node_count = len(tree.findall('.//node'))
            print(f"   ✅ {node_count} nodes")
            
            # Rate limit: be nice to Overpass API
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            failed += 1
            if failed > len(tiles) * 0.1:  # More than 10% failed
                print("\n⚠️  Too many failures, stopping...")
                break
    
    print(f"\n🔀 Merging {len(tiles_data)} tiles...")
    merged_tree = merge_osm_tiles(tiles_data)
    
    # Save merged file
    output_file = Path(__file__).parent.parent.parent / 'local-mvp' / 'toronto_tiled.xml'
    ET.indent(merged_tree, space='  ')
    merged_tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    # Count total nodes
    total_nodes = len(merged_tree.getroot().findall('.//node'))
    
    print(f"\n✅ Merged successfully!")
    print(f"📊 Total nodes: {total_nodes:,}")
    print(f"💾 Saved to: {output_file}")
    print(f"\nNext: Run ingest_osm_to_snowflake.py with 'toronto_tiled.xml'")

if __name__ == "__main__":
    download_toronto_tiled()
