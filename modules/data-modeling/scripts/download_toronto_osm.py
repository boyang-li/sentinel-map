#!/usr/bin/env python3
"""
Download Toronto OSM data from Geofabrik (entire city extract)
This is faster and more reliable than Overpass API for large areas
"""

import requests
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

def download_geofabrik_extract():
    """
    Download Toronto region from Geofabrik (BBBike extracts)
    """
    print("=" * 60)
    print("Downloading Toronto OSM Extract")
    print("=" * 60)
    
    # BBBike Toronto extract (updated weekly)
    url = "https://download.bbbike.org/osm/bbbike/Toronto/Toronto.osm.gz"
    output_gz = Path(__file__).parent.parent.parent / 'local-mvp' / 'toronto_full.osm.gz'
    output_xml = output_gz.with_suffix('')
    
    print(f"\n📥 Downloading from BBBike.org...")
    print(f"   URL: {url}")
    print(f"   This may take 1-2 minutes...")
    
    try:
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        # Download with progress
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_gz, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    pct = (downloaded / total_size) * 100
                    print(f"\r   Progress: {pct:.1f}% ({downloaded:,} / {total_size:,} bytes)", end='')
        
        print(f"\n✅ Downloaded {downloaded:,} bytes")
        
        # Decompress
        print(f"\n📦 Decompressing...")
        subprocess.run(['gunzip', '-f', str(output_gz)], check=True)
        
        print(f"✅ Saved to: {output_xml}")
        
        # Count nodes
        print(f"\n📊 Analyzing OSM data...")
        tree = ET.parse(output_xml)
        root = tree.getroot()
        
        all_nodes = len(root.findall('.//node'))
        print(f"   Total nodes: {all_nodes:,}")
        
        return str(output_xml)
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        raise

def filter_traffic_signs(input_file: str, output_file: str):
    """
    Filter full OSM extract to only traffic infrastructure
    """
    print(f"\n🔍 Filtering traffic infrastructure nodes...")
    
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # Create new XML with only traffic nodes
    osm_filtered = ET.Element('osm', version='0.6')
    
    traffic_count = 0
    for node in root.findall('.//node'):
        tags = {tag.get('k'): tag.get('v') for tag in node.findall('tag')}
        
        # Keep nodes with traffic-related tags
        if any(key in tags for key in [
            'traffic_sign', 'highway', 'traffic_signals',
            'direction', 'maxspeed'
        ]):
            if tags.get('highway') in ['traffic_signals', 'stop', 'give_way', 'speed_camera']:
                osm_filtered.append(node)
                traffic_count += 1
            elif 'traffic_sign' in tags:
                osm_filtered.append(node)
                traffic_count += 1
    
    # Write filtered XML
    filtered_tree = ET.ElementTree(osm_filtered)
    ET.indent(filtered_tree, space='  ')
    filtered_tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    print(f"✅ Found {traffic_count:,} traffic infrastructure nodes")
    print(f"💾 Saved to: {output_file}")
    
    return traffic_count

def main():
    # Download full Toronto extract
    full_osm = download_geofabrik_extract()
    
    # Filter to traffic signs only
    output_file = Path(__file__).parent.parent.parent / 'local-mvp' / 'toronto_traffic.xml'
    traffic_count = filter_traffic_signs(full_osm, str(output_file))
    
    print("\n" + "=" * 60)
    print("✨ Download Complete!")
    print("=" * 60)
    print(f"\nNext step: Update ingest script to use 'toronto_traffic.xml'")
    print(f"Expected nodes to ingest: {traffic_count:,}")

if __name__ == "__main__":
    main()
