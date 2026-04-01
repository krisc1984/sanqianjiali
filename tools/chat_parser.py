#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天记录解析工具 - 从聊天记录提取角色特征
"""

import os
import sys
import json
import re
import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path


def parse_txt_file(file_path: str) -> list:
    """解析 TXT 格式的聊天记录"""
    messages = []

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 尝试解析格式：时间 发送者：内容
        match = re.match(
            r"(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})\s+(\S+):\s*(.+)", line
        )
        if match:
            messages.append(
                {
                    "timestamp": match.group(1),
                    "sender": match.group(2),
                    "content": match.group(3),
                }
            )
        else:
            # 简单格式：发送者：内容
            simple_match = re.match(r"(\S+)：\s*(.+)", line)
            if simple_match:
                messages.append(
                    {
                        "timestamp": "",
                        "sender": simple_match.group(1),
                        "content": simple_match.group(2),
                    }
                )
            else:
                # 无法解析的行
                messages.append({"timestamp": "", "sender": "unknown", "content": line})

    return messages


def parse_json_file(file_path: str) -> list:
    """解析 JSON 格式的聊天记录"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    messages = []

    # 支持多种 JSON 格式
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                messages.append(
                    {
                        "timestamp": item.get("timestamp", item.get("time", "")),
                        "sender": item.get(
                            "sender", item.get("name", item.get("from", ""))
                        ),
                        "content": item.get(
                            "content", item.get("message", item.get("text", ""))
                        ),
                    }
                )
    elif isinstance(data, dict):
        if "messages" in data:
            for item in data["messages"]:
                messages.append(
                    {
                        "timestamp": item.get("timestamp", ""),
                        "sender": item.get("sender", item.get("name", "")),
                        "content": item.get("content", item.get("message", "")),
                    }
                )

    return messages


def analyze_messages(messages: list, target_name: str | None = None) -> dict | None:
    """分析聊天记录，提取角色特征"""

    if not messages:
        return None

    # 统计发送者
    sender_counts = Counter(m["sender"] for m in messages)

    # 如果没有指定目标，选择消息最多的发送者
    if not target_name:
        target_name = sender_counts.most_common(1)[0][0]

    # 过滤目标消息
    target_messages = [m for m in messages if m["sender"] == target_name]

    if not target_messages:
        return {"error": f"未找到 {target_name} 的消息"}

    # 提取特征
    analysis = {
        "target_name": target_name,
        "total_messages": len(target_messages),
        "catchphrases": [],
        "particles": [],
        "avg_length": 0,
        "sentence_patterns": [],
        "topics": [],
        "emotion_words": [],
        "sample_messages": [],
    }

    # 分析口头禅（高频词）
    all_content = " ".join(m["content"] for m in target_messages)

    # 常见语气词
    particles_list = ["呢", "呀", "嘛", "哦", "啦", "啊", "嗯", "哼", "哈", "嘛"]
    particle_counts = Counter()
    for p in particles_list:
        count = all_content.count(p)
        if count > 0:
            particle_counts[p] = count

    analysis["particles"] = particle_counts.most_common(5)

    # 平均消息长度
    lengths = [len(m["content"]) for m in target_messages]
    analysis["avg_length"] = sum(lengths) / len(lengths) if lengths else 0

    # 提取样例句
    analysis["sample_messages"] = [m["content"] for m in target_messages[:10]]

    # 常见句式
    question_count = sum(
        1 for m in target_messages if "?" in m["content"] or "？" in m["content"]
    )
    exclaim_count = sum(
        1 for m in target_messages if "!" in m["content"] or "！" in m["content"]
    )
    ellipsis_count = sum(
        1 for m in target_messages if "..." in m["content"] or "……" in m["content"]
    )

    analysis["sentence_patterns"] = {
        "questions": question_count,
        "exclamations": exclaim_count,
        "ellipses": ellipsis_count,
    }

    return analysis


def format_analysis(analysis: dict) -> str:
    """格式化分析结果"""

    output = []
    output.append("聊天记录分析报告\n")
    output.append("=" * 50)
    output.append(f"目标角色：{analysis.get('target_name', '未知')}")
    output.append(f"消息总数：{analysis.get('total_messages', 0)}")
    output.append(f"平均句长：{analysis.get('avg_length', 0):.1f} 字")
    output.append("")

    # 语气词
    output.append("【常用语气词】")
    particles = analysis.get("particles", [])
    for particle, count in particles:
        output.append(f"  - {particle}: {count} 次")
    output.append("")

    # 句式特征
    output.append("【句式特征】")
    patterns = analysis.get("sentence_patterns", {})
    output.append(f"  - 疑问句：{patterns.get('questions', 0)} 次")
    output.append(f"  - 感叹句：{patterns.get('exclamations', 0)} 次")
    output.append(f"  - 省略号：{patterns.get('ellipses', 0)} 次")
    output.append("")

    # 样例句
    output.append("【样例句】")
    samples = analysis.get("sample_messages", [])
    for i, sample in enumerate(samples[:5], 1):
        output.append(f"  {i}. {sample}")
    output.append("")

    output.append("=" * 50)

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="聊天记录解析工具")
    parser.add_argument("--file", required=True, help="聊天记录文件路径")
    parser.add_argument("--target", help="目标角色名称（可选）")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="输出格式"
    )

    args = parser.parse_args()

    # 检查文件
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 文件不存在：{file_path}")
        sys.exit(1)

    # 解析文件
    if file_path.suffix.lower() == ".json":
        messages = parse_json_file(str(file_path))
    else:
        messages = parse_txt_file(str(file_path))

    if not messages:
        print("❌ 未解析到任何消息")
        sys.exit(1)

    # 分析消息
    analysis = analyze_messages(messages, args.target)

    if not analysis:
        print("❌ 分析失败")
        sys.exit(1)

    # 输出
    if args.format == "json":
        output = json.dumps(analysis, ensure_ascii=False, indent=2)
    else:
        output = format_analysis(analysis)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已输出到：{args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
