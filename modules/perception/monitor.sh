#!/bin/bash
# 监控批处理进度

LOG_FILE="batch_nohup.log"
CSV_FILE="../../data/detections/batch_external_detections.csv"

clear
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              批处理进度监控 - 按 Ctrl+C 退出                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

while true; do
    # 检查进程
    if ps aux | grep -q "[b]atch_process.sh"; then
        STATUS="🟢 运行中"
    else
        STATUS="🔴 已停止"
    fi
    
    # 统计检测数
    if [ -f "$CSV_FILE" ]; then
        DETECTIONS=$(wc -l < "$CSV_FILE" | tr -d ' ')
        DETECTIONS=$((DETECTIONS - 1))  # 减去表头
    else
        DETECTIONS=0
    fi
    
    # 获取当前处理的视频
    if [ -f "$LOG_FILE" ]; then
        CURRENT_VIDEO=$(grep -E "\[[0-9]+/346\]" "$LOG_FILE" | tail -1)
        LAST_SUCCESS=$(grep -c "✅ 成功" "$LOG_FILE")
        LAST_FAILED=$(grep -c "❌ 失败" "$LOG_FILE")
    else
        CURRENT_VIDEO="等待中..."
        LAST_SUCCESS=0
        LAST_FAILED=0
    fi
    
    # 清屏并显示
    tput cup 3 0
    echo "状态: $STATUS"
    echo "已完成: $LAST_SUCCESS 成功, $LAST_FAILED 失败"
    echo "检测数: $DETECTIONS 条记录"
    echo ""
    echo "当前处理:"
    echo "  $CURRENT_VIDEO"
    echo ""
    echo "最近日志 (最后20行):"
    echo "────────────────────────────────────────────────────────────────"
    if [ -f "$LOG_FILE" ]; then
        tail -20 "$LOG_FILE"
    else
        echo "等待日志生成..."
    fi
    
    sleep 5
done
