#!/usr/bin/env python3
"""
批量处理外部存储设备中的视频文件
处理 /Volumes/VOLUME1/DCIM/Movie 目录下的所有 MP4 文件
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 配置
VIDEO_DIR = "/Volumes/VOLUME1/DCIM/Movie"
OUTPUT_CSV = "../../data/detections/batch_external_detections.csv"
OUTPUT_PATCHES = "../../data/roi_patches"
PYTHON_BIN = "/Users/boyangli/Repo/sentinel-map/.venv/bin/python"
SCRIPT_PATH = "detect_and_extract.py"

def main():
    # 检查视频目录
    if not os.path.exists(VIDEO_DIR):
        print(f"❌ 错误: 找不到视频目录 {VIDEO_DIR}")
        print("请确保外部存储设备已连接")
        sys.exit(1)
    
    # 获取所有 MP4 文件
    video_files = sorted(Path(VIDEO_DIR).glob("*.MP4"))
    total_videos = len(video_files)
    
    if total_videos == 0:
        print(f"❌ 错误: 在 {VIDEO_DIR} 中没有找到 MP4 文件")
        sys.exit(1)
    
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║         批量处理外部存储视频 - VOLUME1/DCIM/Movie            ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    print(f"📹 发现 {total_videos} 个视频文件")
    print(f"📂 输出CSV: {OUTPUT_CSV}")
    print(f"🎯 目标类别: 交通灯, 停止标志")
    print(f"⚙️  设备: MPS (M4 加速)\n")
    
    # 自动开始处理
    print(f"▶️  开始批量处理...")
    print(f"⏱️  预计时间: ~{total_videos * 0.5:.0f} 分钟 (假设每个视频30秒)\n")
    
    # 清空或创建输出CSV（保留表头）
    csv_path = Path(OUTPUT_CSV)
    if csv_path.exists():
        # 备份现有文件
        backup_path = csv_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        print(f"📦 备份现有CSV到: {backup_path}")
        csv_path.rename(backup_path)
    
    # 处理每个视频
    success_count = 0
    failed_videos = []
    start_time = datetime.now()
    
    for idx, video_path in enumerate(video_files, 1):
        print(f"\n{'='*60}")
        print(f"处理 [{idx}/{total_videos}]: {video_path.name}")
        print(f"{'='*60}")
        
        # 构建命令
        cmd = [
            PYTHON_BIN,
            SCRIPT_PATH,
            "--video", str(video_path),
            "--output-csv", OUTPUT_CSV,
            "--output-patches", OUTPUT_PATCHES,
            "--device", "mps",
            "--conf", "0.25",
            "--sample-fps", "1"
        ]
        
        try:
            # 运行检测脚本
            result = subprocess.run(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                success_count += 1
                print(f"✅ 成功处理")
            else:
                print(f"❌ 处理失败 (返回码: {result.returncode})")
                print(f"错误: {result.stderr}")
                failed_videos.append(video_path.name)
        
        except subprocess.TimeoutExpired:
            print(f"⏱️  超时 (>10分钟)")
            failed_videos.append(video_path.name)
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            failed_videos.append(video_path.name)
    
    # 最终报告
    elapsed_time = datetime.now() - start_time
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                      批处理完成                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print(f"✅ 成功: {success_count}/{total_videos} 视频")
    print(f"❌ 失败: {len(failed_videos)}/{total_videos} 视频")
    print(f"⏱️  总耗时: {elapsed_time}")
    print(f"📊 输出文件: {OUTPUT_CSV}")
    
    if failed_videos:
        print(f"\n失败的视频:")
        for video in failed_videos:
            print(f"  - {video}")
    
    print("\n下一步:")
    print("  1. 检查CSV文件")
    print("  2. 运行 Kafka producer 发送到 Kafka")
    print("  3. 运行 dbt 更新分析结果")

if __name__ == "__main__":
    main()
