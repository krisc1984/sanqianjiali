#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后宫三千佳丽 - 养成系统工具

功能：
- 更新角色好感度和属性
- 保存聊天记录到角色目录
- 更新角色记忆库
- 解锁剧情进度

使用示例：
    # 更新好感度
    python growth_system.py --action update-affection --slug zhenhuan --delta +5 --reason "沐浴侍寝"

    # 保存聊天记录
    python growth_system.py --action save-chat --slug zhenhuan --input chat.txt

    # 添加记忆
    python growth_system.py --action add-memory --slug zhenhuan --event "汤泉宫沐浴" --date "2026-04-01"

    # 查看养成进度
    python growth_system.py --action status --slug zhenhuan --output json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class GrowthSystem:
    """养成系统管理器"""

    # 好感度阈值定义
    AFFECTION_LEVELS = {
        0: ("陌生", "疏远", "恭敬但冷淡"),
        20: ("相识", "友好", "初步了解"),
        40: ("友好", "正常", "正常互动"),
        60: ("亲密", "亲密", "主动关心"),
        80: ("倾心", "倾心", "专属互动、特殊剧情"),
    }

    # 剧情解锁条件
    STORY_UNLOCKS = {
        "story_30": {"affection": 30, "name": "初入宫廷·倚梅园相遇"},
        "story_60": {"affection": 60, "name": "莞尔一笑·汤泉宫沐浴"},
        "story_80": {"affection": 80, "name": "熹贵妃册封·回宫复仇"},
        "story_100": {"affection": 100, "name": "凤仪天下·圣母皇太后"},
        "story_strategy_80": {"strategy": 80, "name": "黑化复仇·斗垮华妃"},
        "story_talent_90": {"talent": 90, "name": "诗词对决·以诗会友"},
    }

    def __init__(self, characters_dir: str):
        """初始化养成系统

        Args:
            characters_dir: 角色目录路径
        """
        self.characters_dir = Path(characters_dir)
        if not self.characters_dir.exists():
            raise FileNotFoundError(f"角色目录不存在：{characters_dir}")

    def get_character_dir(self, slug: str) -> Path:
        """获取角色目录"""
        return self.characters_dir / slug

    def get_meta_path(self, slug: str) -> Path:
        """获取 meta.json 路径"""
        return self.get_character_dir(slug) / "meta.json"

    def get_chat_history_dir(self, slug: str) -> Path:
        """获取聊天记录目录"""
        return self.get_character_dir(slug) / "chat_history"

    def get_memories_dir(self, slug: str) -> Path:
        """获取记忆库目录"""
        return self.get_character_dir(slug) / "memories"

    def load_meta(self, slug: str) -> Dict[str, Any]:
        """加载角色元数据"""
        meta_path = self.get_meta_path(slug)
        if not meta_path.exists():
            raise FileNotFoundError(f"角色元数据不存在：{meta_path}")

        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_meta(self, slug: str, meta: Dict[str, Any]) -> None:
        """保存角色元数据"""
        meta_path = self.get_meta_path(slug)
        meta["updated_at"] = datetime.now().isoformat()

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def get_affection_level(self, affection: int) -> tuple:
        """获取好感度等级"""
        level = 0
        for threshold in sorted(self.AFFECTION_LEVELS.keys(), reverse=True):
            if affection >= threshold:
                level = threshold
                break

        info = self.AFFECTION_LEVELS.get(level, self.AFFECTION_LEVELS[0])
        return info

    def update_affection(
        self, slug: str, delta: int, reason: str = ""
    ) -> Dict[str, Any]:
        """更新好感度

        Args:
            slug: 角色标识
            delta: 好感度变化值（正数增加，负数减少）
            reason: 变化原因

        Returns:
            更新后的状态信息
        """
        meta = self.load_meta(slug)

        old_affection = meta["attributes"]["affection"]
        new_affection = max(0, min(100, old_affection + delta))
        meta["attributes"]["affection"] = new_affection

        # 记录好感度变化历史
        if "affection_history" not in meta:
            meta["affection_history"] = []

        meta["affection_history"].append(
            {
                "date": datetime.now().isoformat(),
                "old": old_affection,
                "new": new_affection,
                "delta": delta,
                "reason": reason,
            }
        )

        # 检查剧情解锁
        unlocked_stories = self.check_story_unlocks(meta)

        self.save_meta(slug, meta)

        # 获取等级信息
        level_info = self.get_affection_level(new_affection)

        return {
            "success": True,
            "slug": slug,
            "old_affection": old_affection,
            "new_affection": new_affection,
            "delta": delta,
            "reason": reason,
            "level_name": level_info[0],
            "level_status": level_info[1],
            "level_desc": level_info[2],
            "unlocked_stories": unlocked_stories,
        }

    def check_story_unlocks(self, meta: Dict[str, Any]) -> List[str]:
        """检查剧情解锁"""
        unlocked = []

        if "unlock_status" not in meta:
            meta["unlock_status"] = {}

        for story_key, condition in self.STORY_UNLOCKS.items():
            should_unlock = False

            if "affection" in condition:
                if meta["attributes"]["affection"] >= condition["affection"]:
                    should_unlock = True

            if "strategy" in condition:
                if meta["attributes"].get("strategy", 0) >= condition["strategy"]:
                    should_unlock = True

            if "talent" in condition:
                if meta["attributes"].get("talent", 0) >= condition["talent"]:
                    should_unlock = True

            if should_unlock and not meta["unlock_status"].get(story_key, False):
                meta["unlock_status"][story_key] = True
                unlocked.append(condition["name"])

        return unlocked

    def save_chat(
        self, slug: str, chat_content: str, chat_date: Optional[str] = None
    ) -> str:
        """保存聊天记录

        Args:
            slug: 角色标识
            chat_content: 聊天内容
            chat_date: 聊天日期（YYYY-MM-DD 格式，默认今天）

        Returns:
            保存的文件路径
        """
        if chat_date is None:
            chat_date = datetime.now().strftime("%Y-%m-%d")

        chat_dir = self.get_chat_history_dir(slug)
        chat_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%H%M%S")
        chat_file = chat_dir / f"{chat_date}_{timestamp}.txt"

        with open(chat_file, "w", encoding="utf-8") as f:
            f.write(f"# 聊天记录 - {chat_date}\n\n")
            f.write(chat_content)

        # 更新 meta.json 中的聊天记录列表
        meta = self.load_meta(slug)
        if "chat_records" not in meta:
            meta["chat_records"] = []

        meta["chat_records"].append(
            {
                "date": chat_date,
                "file": str(chat_file),
                "timestamp": datetime.now().isoformat(),
            }
        )
        meta["chat_count"] = len(meta["chat_records"])

        self.save_meta(slug, meta)

        return str(chat_file)

    def add_memory(
        self,
        slug: str,
        event: str,
        date: Optional[str] = None,
        details: Optional[str] = None,
    ) -> Dict[str, Any]:
        """添加角色记忆

        Args:
            slug: 角色标识
            event: 事件名称
            date: 事件日期
            details: 事件详情

        Returns:
            添加结果
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        memories_dir = self.get_memories_dir(slug)
        memories_dir.mkdir(parents=True, exist_ok=True)

        memories_file = memories_dir / "memories.json"

        # 加载现有记忆
        if memories_file.exists():
            with open(memories_file, "r", encoding="utf-8") as f:
                memories = json.load(f)
        else:
            memories = {"important_events": [], "anniversaries": [], "promises": []}

        # 添加新记忆
        new_memory = {
            "date": date,
            "event": event,
            "details": details or "",
            "created_at": datetime.now().isoformat(),
        }

        memories["important_events"].append(new_memory)

        # 保存记忆
        with open(memories_file, "w", encoding="utf-8") as f:
            json.dump(memories, f, ensure_ascii=False, indent=2)

        # 同时更新 meta.json 中的 memories
        meta = self.load_meta(slug)
        if "memories" not in meta:
            meta["memories"] = []

        meta["memories"].append({"date": date, "event": event})

        self.save_meta(slug, meta)

        return {
            "success": True,
            "slug": slug,
            "event": event,
            "date": date,
            "memory_file": str(memories_file),
        }

    def update_attribute(self, slug: str, attribute: str, delta: int) -> Dict[str, Any]:
        """更新角色属性

        Args:
            slug: 角色标识
            attribute: 属性名称（talent/beauty/temperament/cooking/strategy/health）
            delta: 变化值

        Returns:
            更新结果
        """
        meta = self.load_meta(slug)

        if attribute not in meta["attributes"]:
            raise ValueError(f"未知属性：{attribute}")

        old_value = meta["attributes"][attribute]
        new_value = max(0, min(100, old_value + delta))
        meta["attributes"][attribute] = new_value

        self.save_meta(slug, meta)

        return {
            "success": True,
            "slug": slug,
            "attribute": attribute,
            "old_value": old_value,
            "new_value": new_value,
            "delta": delta,
        }

    def get_status(self, slug: str) -> Dict[str, Any]:
        """获取角色养成状态

        Args:
            slug: 角色标识

        Returns:
            完整状态信息
        """
        meta = self.load_meta(slug)

        affection = meta["attributes"]["affection"]
        level_info = self.get_affection_level(affection)

        # 计算已解锁剧情
        unlocked_count = sum(1 for v in meta.get("unlock_status", {}).values() if v)
        total_stories = len(self.STORY_UNLOCKS)

        return {
            "slug": slug,
            "name": meta.get("name", "Unknown"),
            "rank": meta.get("rank", "Unknown"),
            "attributes": meta["attributes"],
            "affection_level": {
                "value": affection,
                "level_name": level_info[0],
                "level_status": level_info[1],
                "level_desc": level_info[2],
            },
            "unlocked_stories": {
                "count": unlocked_count,
                "total": total_stories,
                "details": meta.get("unlock_status", {}),
            },
            "chat_count": meta.get("chat_count", 0),
            "memory_count": len(meta.get("memories", [])),
            "created_at": meta.get("created_at", "Unknown"),
            "updated_at": meta.get("updated_at", "Unknown"),
        }


def format_status_output(status: Dict[str, Any], output_format: str = "text") -> str:
    """格式化状态输出"""
    if output_format == "json":
        return json.dumps(status, ensure_ascii=False, indent=2)

    # 文本格式
    lines = [
        f"╔{'═' * 50}╗",
        f"║  📊 {status['name']} · 养成进度 {' ' * 26}║",
        f"╠{'═' * 50}╣",
        f"║  位分：{status['rank']:<40}║",
        f"╠{'═' * 50}╣",
        f"║  💕 好感度：{status['affection_level']['value']}/100 【{status['affection_level']['level_status']}】{' ' * 10}║",
        f"║  {' ' * 50}║",
    ]

    # 属性条
    attrs = status["attributes"]
    attr_names = {
        "talent": "才情",
        "beauty": "容貌",
        "temperament": "气质",
        "cooking": "厨艺",
        "strategy": "谋略",
        "health": "健康",
    }

    for attr_key, attr_name in attr_names.items():
        value = attrs.get(attr_key, 0)
        bar_length = int(value / 5)
        bar = "█" * bar_length + " " * (20 - bar_length)
        lines.append(
            f"║  {attr_name}: {bar} {value}/100{' ' * (15 - len(str(value)))}║"
        )

    lines.extend(
        [
            f"╠{'═' * 50}╣",
            f"║  🎁 已解锁剧情：{status['unlocked_stories']['count']}/{status['unlocked_stories']['total']}{(' ' * 25)}║",
            f"║  💬 聊天记录：{status['chat_count']} 条{' ' * 35}║",
            f"║  📜 记忆库：{status['memory_count']} 条{' ' * 36}║",
            f"╚{'═' * 50}╝",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="后宫三千佳丽 - 养成系统工具")
    parser.add_argument(
        "--action",
        required=True,
        choices=[
            "update-affection",
            "save-chat",
            "add-memory",
            "update-attribute",
            "status",
        ],
        help="操作类型",
    )
    parser.add_argument("--slug", required=True, help="角色标识")
    parser.add_argument("--characters-dir", default="./characters", help="角色目录路径")
    parser.add_argument("--delta", type=int, help="变化值（用于好感度/属性更新）")
    parser.add_argument("--reason", default="", help="变化原因")
    parser.add_argument("--input", help="输入文件路径（用于保存聊天记录）")
    parser.add_argument("--event", help="事件名称（用于添加记忆）")
    parser.add_argument("--date", help="日期（YYYY-MM-DD 格式）")
    parser.add_argument("--details", help="事件详情")
    parser.add_argument("--attribute", help="属性名称")
    parser.add_argument(
        "--output", choices=["text", "json"], default="text", help="输出格式"
    )

    args = parser.parse_args()

    try:
        gs = GrowthSystem(args.characters_dir)

        if args.action == "update-affection":
            if args.delta is None:
                print("错误：--delta 参数必填")
                sys.exit(1)
            result = gs.update_affection(args.slug, args.delta, args.reason)
            print(
                format_status_output(result, "json")
                if args.output == "json"
                else json.dumps(result, ensure_ascii=False, indent=2)
            )

        elif args.action == "save-chat":
            if args.input is None:
                print("错误：--input 参数必填")
                sys.exit(1)
            with open(args.input, "r", encoding="utf-8") as f:
                chat_content = f.read()
            file_path = gs.save_chat(args.slug, chat_content, args.date)
            print(
                json.dumps(
                    {"success": True, "file": file_path}, ensure_ascii=False, indent=2
                )
            )

        elif args.action == "add-memory":
            if args.event is None:
                print("错误：--event 参数必填")
                sys.exit(1)
            result = gs.add_memory(args.slug, args.event, args.date, args.details)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.action == "update-attribute":
            if args.delta is None or args.attribute is None:
                print("错误：--delta 和 --attribute 参数必填")
                sys.exit(1)
            result = gs.update_attribute(args.slug, args.attribute, args.delta)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.action == "status":
            status = gs.get_status(args.slug)
            print(format_status_output(status, args.output))

    except Exception as e:
        print(
            json.dumps(
                {"success": False, "error": str(e)}, ensure_ascii=False, indent=2
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
