# 后宫三千佳丽 - 安装指南

## 📋 系统要求

| 项目 | 要求 |
|------|------|
| Python 版本 | 3.9 或更高 |
| 操作系统 | Windows / macOS / Linux |
| 磁盘空间 | 至少 100MB |
| Claude Code | 已安装并配置 |

---

## 🚀 快速安装

### 方式一：克隆仓库（推荐）

```bash
# 进入你的项目目录
cd F:\Obsidian\my-vault

# 克隆技能仓库
git clone https://github.com/your-username/hougong-skill.git 后宫三千佳丽
```

### 方式二：手动复制

```bash
# 将整个后宫三千佳丽目录复制到项目根目录
# 确保目录结构如下：

后宫三千佳丽/
├── SKILL.md
├── README.md
├── requirements.txt
├── prompts/
├── tools/
├── references/
└── characters/
```

---

## 📦 依赖安装

### 基础安装（推荐）

本技能主要使用 Python 标准库，**无需安装任何额外依赖**即可使用全部核心功能。

```bash
# 验证 Python 版本
python --version

# 应显示 Python 3.9.x 或更高
```

### 可选依赖（按需安装）

如需支持 PDF 读取、图片 OCR 等扩展功能，可安装以下依赖：

```bash
# 安装可选依赖
pip install -r 后宫三千佳丽/requirements.txt
```

#### 可选功能说明

| 功能 | 依赖 | 用途 |
|------|------|------|
| PDF 读取 | PyPDF2>=3.0.0 | 读取 PDF 格式的角色设定 |
| 图片 OCR | pytesseract>=0.3.10, Pillow>=9.0.0 | 识别截图中的聊天记录 |

---

## 🔧 工具脚本测试

安装完成后，运行以下命令测试工具脚本：

```bash
# 测试角色管理工具
python 后宫三千佳丽/tools/character_manager.py --action list --base-dir 后宫三千佳丽

# 测试翻牌子工具
python 后宫三千佳丽/tools/fan_paizi.py --characters-dir 后宫三千佳丽/characters --mode weighted

# 测试聊天记录解析工具
python 后宫三千佳丽/tools/chat_parser.py --help
```

---

## ⚙️ Claude Code 配置

### 技能触发

在 Claude Code 中，技能会自动触发当用户输入：

- `/后宫`
- `/后宫三千佳丽`
- `/翻牌子`
- `/召唤 {角色名}`
- `/新建角色`
- `/角色列表`

### 手动调用

如需手动调用技能：

```
@后宫三千佳丽
```

---

## 📁 目录结构说明

```
后宫三千佳丽/
├── SKILL.md                 # 技能主文件（不要修改）
├── README.md                # 使用说明
├── requirements.txt         # 依赖列表
├── INSTALL.md              # 安装指南（本文件）
├── prompts/                # Prompt 模板（高级用户可自定义）
│   ├── intake.md
│   ├── character_analyzer.md
│   ├── character_builder.md
│   ├── interaction_rules.md
│   └── growth_system.md
├── tools/                  # Python 工具脚本
│   ├── character_manager.py
│   ├── fan_paizi.py
│   └── chat_parser.py
├── references/             # 预设角色模板
│   └── presets/
│       └── zhenhuan.md
├── characters/             # 生成的角色（自动创建）
│   ├── zhenhuan/
│   │   ├── character.md
│   │   └── meta.json
│   └── weiyingluo/
│       ├── character.md
│       └── meta.json
└── logs/                   # 日志文件（自动创建）
```

---

## ⚠️ 常见问题

### Q1: Python 版本过低怎么办？

**A:** 请升级 Python 到 3.9 或更高版本。

下载地址：https://www.python.org/downloads/

### Q2: Windows 命令行显示乱码怎么办？

**A:** 这是编码问题，可以：

1. 使用 PowerShell 代替 CMD
2. 或设置编码：`chcp 65001`
3. 或直接使用 Claude Code 调用技能

### Q3: 工具脚本无法运行怎么办？

**A:** 检查以下几点：

1. Python 是否已添加到系统 PATH
2. 是否在正确的目录运行命令
3. 文件路径是否包含中文字符（某些系统可能不支持）

### Q4: 技能不触发怎么办？

**A:** 确保：

1. SKILL.md 文件存在于正确位置
2. 使用正确的触发词（如 `/后宫`）
3. Claude Code 已重新加载技能

---

## 🔄 更新技能

```bash
# 如果是 git 克隆的
cd 后宫三千佳丽
git pull

# 如果是手动复制的
# 重新下载并覆盖原有文件
```

---

## 📞 获取帮助

如遇到问题：

1. 查看本安装指南
2. 查看 README.md 使用说明
3. 检查工具脚本的 --help 输出
4. 在 GitHub 提交 Issue

---

## 📄 许可证

MIT License - 自由使用，修改和分享

---

<div align="center">

**后宫三千佳丽** - 你的虚拟后宫世界

安装愉快！🎉

</div>
