#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻牌子工具 - 随机选择角色侍寝
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime
from pathlib import Path


def get_characters_dir(base_dir: str) -> Path:
    """获取角色目录"""
    return Path(base_dir) / "characters"


def load_all_characters(base_dir: str) -> list:
    """加载所有角色"""
    chars_dir = get_characters_dir(base_dir)

    if not chars_dir.exists():
        return []

    characters = []
    for char_dir in chars_dir.iterdir():
        if char_dir.is_dir():
            meta_file = char_dir / "meta.json"
            if meta_file.exists():
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    characters.append(meta)

    return characters


def fan_paizi_random(base_dir: str, exclude_list: list | None = None) -> dict | None:
    """完全随机翻牌子"""
    characters = load_all_characters(base_dir)

    if not characters:
        return None

    if exclude_list:
        characters = [c for c in characters if c.get("slug") not in exclude_list]

    if not characters:
        return None

    return random.choice(characters)


def fan_paizi_weighted(base_dir: str, exclude_list: list | None = None) -> dict | None:
    """按好感度加权翻牌子（好感度越高概率越大）"""
    characters = load_all_characters(base_dir)

    if not characters:
        return None

    if exclude_list:
        characters = [c for c in characters if c.get("slug") not in exclude_list]

    if not characters:
        return None

    weights = [max(c.get("affection", 0), 1) for c in characters]
    selected = random.choices(characters, weights=weights, k=1)[0]

    return selected


def fan_paizi_low_affection(
    base_dir: str, exclude_list: list | None = None
) -> dict | None:
    """翻牌子 - 选择好感度最低的角色（鼓励培养）"""
    characters = load_all_characters(base_dir)

    if not characters:
        return None

    if exclude_list:
        characters = [c for c in characters if c.get("slug") not in exclude_list]

    if not characters:
        return None

    characters.sort(key=lambda x: x.get("affection", 0))

    return characters[0]


def fan_paizi_unvisited(
    base_dir: str, days: int = 7, exclude_list: list | None = None
) -> dict | None:
    """翻牌子 - 选择超过 N 天未互动的角色"""
    characters = load_all_characters(base_dir)

    if not characters:
        return None

    if exclude_list:
        characters = [c for c in characters if c.get("slug") not in exclude_list]

    if not characters:
        return None

    now = datetime.now()
    unvisited = []

    for char in characters:
        last_interaction = char.get("last_interaction")
        if not last_interaction:
            unvisited.append(char)
            continue

        try:
            last_date = datetime.fromisoformat(last_interaction.replace("Z", "+00:00"))
            days_diff = (now - last_date).days
            if days_diff >= days:
                unvisited.append(char)
        except:
            unvisited.append(char)

    if unvisited:
        return random.choice(unvisited)

    return random.choice(characters)


def format_character_card(character: dict) -> str:
    """格式化角色卡片"""
    name = character.get("name", "未知")
    rank = character.get("rank", "无位分")
    affection = character.get("affection", 0)
    personality = character.get("personality", [])

    # 好感度等级
    if affection >= 80:
        level = "💕 倾心"
    elif affection >= 60:
        level = "💗 亲密"
    elif affection >= 40:
        level = "💓 友好"
    elif affection >= 20:
        level = "💕 相识"
    else:
        level = "🤍 陌生"

    # 生成开场白
    greetings = [
        f"皇上～臣妾等您好久了～",
        f"皇上吉祥！臣妾给您请安了～",
        f"皇上今夜...要臣妾伺候吗？",
        f"皇上～您终于来了～",
        f"臣妾参见皇上～",
    ]

    greeting = random.choice(greetings)

    card = f"""
╔════════════════════════════════════════╗
║         🎴 翻牌子结果 🎴              ║
╠════════════════════════════════════════╣
║                                        ║
║   今夜侍寝的是——                      ║
║                                        ║
║   【{rank}】{name}                      ║
║                                        ║
║   {greeting}                            ║
║                                        ║
║   好感度：{affection}/100 {level}              ║
║   性格：{", ".join(personality[:3])}                  ║
║                                        ║
╚════════════════════════════════════════╝
"""

    return card


def main():
    parser = argparse.ArgumentParser(description="翻牌子工具 - 随机选择角色")
    parser.add_argument(
        "--characters-dir", default="./后宫三千佳丽/characters", help="角色目录"
    )
    parser.add_argument(
        "--mode",
        choices=["random", "weighted", "low", "unvisited"],
        default="weighted",
        help="选择模式",
    )
    parser.add_argument("--exclude", nargs="+", default=[], help="排除的角色 slug 列表")
    parser.add_argument("--days", type=int, default=7, help="unvisited 模式的天数阈值")
    parser.add_argument("--output", help="输出到文件")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")

    args = parser.parse_args()

    # 选择模式
    if args.mode == "random":
        selected = fan_paizi_random(args.characters_dir, args.exclude)
    elif args.mode == "weighted":
        selected = fan_paizi_weighted(args.characters_dir, args.exclude)
    elif args.mode == "low":
        selected = fan_paizi_low_affection(args.characters_dir, args.exclude)
    elif args.mode == "unvisited":
        selected = fan_paizi_unvisited(args.characters_dir, args.days, args.exclude)
    else:
        selected = fan_paizi_weighted(args.characters_dir, args.exclude)

    if not selected:
        print("📭 后宫空无一人，快去创建角色吧！")
        sys.exit(1)

    # 输出
    if args.json:
        result = {
            "success": True,
            "character": selected,
            "card": format_character_card(selected),
        }
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        output = format_character_card(selected)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已输出到：{args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
