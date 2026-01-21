#!/usr/bin/env python3
"""
Quick OCR GPS test on first 10 frames of video
"""
import cv2
import sys
sys.path.insert(0, '/Users/boyangli/Repo/sentinel-map/modules/perception')
from detect_and_extract import PerceptionPipeline

# Test video
video_path = "/Users/boyangli/Repo/sentinel-map/data/videos/20260118191513_035087.MP4"

print("="*80)
print("Quick OCR GPS Test - First 10 Frames")
print("="*80)

# Open video
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"❌ Failed to open video: {video_path}")
    sys.exit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"📹 Video: {fps:.1f} FPS, {total_frames} frames")

# Initialize pipeline
pipeline = PerceptionPipeline()

print(f"\n📍 Testing GPS extraction on first 3 frames (OCR is slow ~1-2 sec/frame):")
print("-"*80)

for i in range(3):
    ret, frame = cap.read()
    if not ret:
        break
    
    import time
    start = time.time()
    lat, lon, heading = pipeline.extract_gps_from_frame(frame, i)
    elapsed = time.time() - start
    print(f"Frame {i:3d}: lat={lat:.6f}, lon={lon:.6f}, heading={heading:.1f} ({elapsed:.2f}s)")

cap.release()
print("\n" + "="*80)
print("✅ Test complete!")
print("="*80)
