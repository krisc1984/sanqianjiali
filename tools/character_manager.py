#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后宫三千佳丽 - 角色管理工具

功能：
- 列出所有角色
- 删除角色
- 导出角色
- 导入角色
"""

import os
import sys
import json
import argparse
import shutil
from datetime import datetime
from pathlib import Path


def get_characters_dir(base_dir: str) -> Path:
    """获取角色目录"""
    return Path(base_dir) / "characters"


def list_characters(base_dir: str, verbose: bool = False) -> None:
    """列出所有角色"""
    chars_dir = get_characters_dir(base_dir)

    if not chars_dir.exists():
        print("📭 后宫空无一人，快去创建角色吧！")
        return

    characters = []
    for char_dir in chars_dir.iterdir():
        if char_dir.is_dir():
            meta_file = char_dir / "meta.json"
            if meta_file.exists():
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    characters.append(meta)

    if not characters:
        print("📭 后宫空无一人，快去创建角色吧！")
        return

    print("\n📜 后宫名录\n")
    print("=" * 50)

    # 按好感度排序
    characters.sort(key=lambda x: x.get("affection", 0), reverse=True)

    for i, char in enumerate(characters, 1):
        name = char.get("name", "未知")
        rank = char.get("rank", "无位分")
        affection = char.get("affection", 0)
        updated = char.get("updated_at", "未知")

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

        print(f"{i}. 【{rank}】{name} - 好感度 {affection}/100 {level}")

        if verbose:
            print(f"   创建：{char.get('created_at', '未知')}")
            print(f"   更新：{updated}")
            print(f"   性格：{', '.join(char.get('personality', []))}")
            print()

    print("=" * 50)
    print(f"\n共 {len(characters)} 位佳丽\n")


def delete_character(base_dir: str, slug: str, confirm: bool = True) -> bool:
    """删除角色"""
    chars_dir = get_characters_dir(base_dir)
    char_dir = chars_dir / slug

    if not char_dir.exists():
        print(f"❌ 未找到角色：{slug}")
        return False

    # 读取角色名
    meta_file = char_dir / "meta.json"
    if meta_file.exists():
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
            name = meta.get("name", slug)
    else:
        name = slug

    # 确认删除
    if confirm:
        print(f"\n⚠️  确认删除：{name}？")
        print("此操作不可恢复！\n")
        response = input("输入 'y' 确认删除：")
        if response.lower() != "y":
            print("已取消删除")
            return False

    # 删除目录
    shutil.rmtree(char_dir)
    print(f"✅ 已删除：{name}")
    return True


def export_character(base_dir: str, slug: str, output_path: str) -> bool:
    """导出角色"""
    chars_dir = get_characters_dir(base_dir)
    char_dir = chars_dir / slug

    if not char_dir.exists():
        print(f"❌ 未找到角色：{slug}")
        return False

    # 创建输出目录
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 复制角色目录
    dest_dir = output_dir / slug
    if dest_dir.exists():
        print(f"⚠️  目标已存在：{dest_dir}")
        response = input("是否覆盖？(y/N): ")
        if response.lower() != "y":
            return False
        shutil.rmtree(dest_dir)

    shutil.copytree(char_dir, dest_dir)
    print(f"✅ 已导出到：{dest_dir}")
    return True


def import_character(base_dir: str, source_path: str) -> bool:
    """导入角色"""
    source_dir = Path(source_path)

    if not source_dir.exists():
        print(f"❌ 源路径不存在：{source_path}")
        return False

    # 读取 slug
    meta_file = source_dir / "meta.json"
    if not meta_file.exists():
        print(f"❌ 未找到 meta.json：{source_path}")
        return False

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)
        slug = meta.get("slug", source_dir.name)

    # 检查是否已存在
    chars_dir = get_characters_dir(base_dir)
    dest_dir = chars_dir / slug

    if dest_dir.exists():
        print(f"⚠️  角色已存在：{slug}")
        response = input("是否覆盖？(y/N): ")
        if response.lower() != "y":
            return False
        shutil.rmtree(dest_dir)

    # 复制角色目录
    shutil.copytree(source_dir, dest_dir)
    print(f"✅ 已导入：{meta.get('name', slug)}")
    return True


def show_character_info(base_dir: str, slug: str) -> bool:
    """显示角色详情"""
    chars_dir = get_characters_dir(base_dir)
    char_dir = chars_dir / slug

    if not char_dir.exists():
        print(f"❌ 未找到角色：{slug}")
        return False

    meta_file = char_dir / "meta.json"
    if not meta_file.exists():
        print(f"❌ 未找到 meta.json")
        return False

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    print(f"\n🎴 {meta.get('name', slug)}\n")
    print("=" * 50)
    print(f"【封号】{meta.get('title', '无')}")
    print(f"【位分】{meta.get('rank', '无')}")
    print(f"【时代】{meta.get('era', '未知')}")
    print(f"【年龄】{meta.get('age', '未知')}")
    print(f"【居所】{meta.get('residence', '未知')}")
    print()
    print(f"【性格】{', '.join(meta.get('personality', []))}")
    print(f"【才艺】{', '.join(meta.get('skills', []))}")
    print()
    print(f"【外貌】{meta.get('appearance', '未知')}")
    print(f"【背景】{meta.get('background', '未知')}")
    print()
    print("【属性】")
    attrs = meta.get("attributes", {})
    print(f"  才情：{attrs.get('talent', 0)}/100")
    print(f"  容貌：{attrs.get('beauty', 0)}/100")
    print(f"  气质：{attrs.get('temperament', 0)}/100")
    print(f"  厨艺：{attrs.get('cooking', 0)}/100")
    print(f"  谋略：{attrs.get('strategy', 0)}/100")
    print(f"  健康：{attrs.get('health', 0)}/100")
    print()
    print(f"【好感度】{meta.get('affection', 0)}/100")
    print(f"【互动次数】{meta.get('chat_count', 0)}")
    print(f"【创建时间】{meta.get('created_at', '未知')}")
    print(f"【更新时间】{meta.get('updated_at', '未知')}")
    print("=" * 50)
    print()

    return True


def main():
    parser = argparse.ArgumentParser(description="后宫三千佳丽 - 角色管理工具")
    parser.add_argument(
        "--action",
        required=True,
        choices=["list", "delete", "export", "import", "info"],
        help="操作类型",
    )
    parser.add_argument("--base-dir", default="./后宫三千佳丽", help="基础目录")
    parser.add_argument("--slug", help="角色标识")
    parser.add_argument("--output", help="输出路径（导出时用）")
    parser.add_argument("--source", help="源路径（导入时用）")
    parser.add_argument("--no-confirm", action="store_true", help="跳过确认")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细信息")

    args = parser.parse_args()

    if args.action == "list":
        list_characters(args.base_dir, args.verbose)

    elif args.action == "delete":
        if not args.slug:
            print("❌ 删除操作需要 --slug 参数")
            sys.exit(1)
        success = delete_character(args.base_dir, args.slug, not args.no_confirm)
        sys.exit(0 if success else 1)

    elif args.action == "export":
        if not args.slug:
            print("❌ 导出操作需要 --slug 参数")
            sys.exit(1)
        if not args.output:
            print("❌ 导出操作需要 --output 参数")
            sys.exit(1)
        success = export_character(args.base_dir, args.slug, args.output)
        sys.exit(0 if success else 1)

    elif args.action == "import":
        if not args.source:
            print("❌ 导入操作需要 --source 参数")
            sys.exit(1)
        success = import_character(args.base_dir, args.source)
        sys.exit(0 if success else 1)

    elif args.action == "info":
        if not args.slug:
            print("❌ 详情操作需要 --slug 参数")
            sys.exit(1)
        success = show_character_info(args.base_dir, args.slug)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
