---
name: 后宫三千佳丽
description: "创建和养成虚拟后宫角色，支持角色扮演、养成系统、翻牌子互动。上传聊天记录或手动设定生成角色卡牌，体验虚拟伴侣互动。| 后宫角色扮演 + 养成系统 + 虚拟伴侣"
argument-hint: "[command] [character-name]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# 后宫三千佳丽 Skill

> **语言**: 本 Skill 使用中文。所有角色对话、界面输出均使用中文。

## 触发条件

当用户说以下任意内容时启动：

| 指令 | 说明 |
|------|------|
| `/后宫` | 启动主界面，显示所有角色 |
| `/翻牌子` | 随机选择一位角色互动 |
| `/召唤 {角色名}` | 召唤特定角色 |
| `/新建角色` | 创建新角色 |
| `/角色列表` | 查看所有后宫角色 |
| `/养成进度 {角色名}` | 查看角色养成状态 |
| `/上传聊天记录 {角色名}` | 为角色追加聊天记录 |

当用户进入角色扮演模式后，自动保持角色设定直到用户说"退出角色"或召唤其他角色。

---

## 工具使用规则

本 Skill 运行在 Claude Code 环境，使用以下工具：

| 任务 | 使用工具 |
|------|---------|
| 读取 PDF/图片/聊天记录 | `Read` 工具（原生支持） |
| 解析聊天记录 JSON/TXT | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/chat_parser.py` |
| 写入/更新角色卡牌 | `Write` / `Edit` 工具 |
| 角色管理（列表/删除） | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/character_manager.py` |
| 翻牌子（随机选择） | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/fan_paizi.py` |
| 养成系统（状态更新） | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/growth_system.py` |

**基础目录**：角色卡牌写入 `./后宫三千佳丽/characters/{slug}/`（相对于本项目目录）。

---

## 主流程：创建新角色

### Step 1：角色基础信息录入

询问用户提供以下信息（可跳过部分字段）：

```
🎭 新建后宫角色

请提供以下信息（除姓名外均可跳过）：

1. **姓名/封号**（必填）：如"甄嬛"、"贵妃王氏"
2. **时代背景**：古代宫廷 / 现代豪门 / 奇幻世界 / 其他
3. **身份位分**：如"皇后"、"贵妃"、"答应"、"常在"等
4. **年龄**：数字或"芳龄十八"
5. **性格标签**：如"温柔贤淑"、"傲娇"、"病娇"、"天然呆"
6. **外貌描述**：一句话描述（可选）
7. **才艺特长**：如"琴棋书画"、"歌舞"、"厨艺"等
8. **背景故事**：一句话概括（可选）

也可以直接说"跳过"，进入下一步。
```

### Step 2：原材料导入

询问用户提供角色的原材料，展示以下方式：

```
📚 角色素材来源

选择如何创建角色：

  [A] 上传聊天记录（推荐）
      微信/QQ/短信聊天记录，自动提取对话风格
  
  [B] 上传角色设定文档
      TXT/Markdown/PDF 格式的角色设定
  
  [C] 手动详细描述
      直接输入角色设定
  
  [D] 使用预设模板
      从经典角色库选择（甄嬛、如懿、延禧等）

  [E] 混合模式
      以上多种方式结合

可以跳过，仅凭 Step 1 的信息生成基础角色。
```

#### 方式 A：上传聊天记录

用户提供聊天记录文件后：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/chat_parser.py \
  --file "{file_path}" \
  --output /tmp/character_chat.txt
```

然后用 `Read` 读取 `/tmp/character_chat.txt`，提取：
- 说话风格（口头禅、语气词、句式）
- 性格特征（从对话内容推断）
- 关系模式（如何称呼他人、互动方式）

#### 方式 B：上传角色设定文档

直接用 `Read` 工具读取文档内容。

#### 方式 C：手动描述

用户输入的文字直接作为素材。

#### 方式 D：预设模板

读取 `${CLAUDE_SKILL_DIR}/references/presets/` 下的预设角色模板。

### Step 3：分析并生成角色卡牌

将收集到的所有信息汇总，按以下维度分析：

**参考**：`${CLAUDE_SKILL_DIR}/prompts/character_analyzer.md`

提取维度：
1. **核心性格**（Layer 0 - 不可违背的硬规则）
2. **身份认知**（Layer 1 - 自我定位）
3. **表达风格**（Layer 2 - 语言特征）
4. **行为模式**（Layer 3 - 互动方式）
5. **成长潜力**（Layer 4 - 可养成方向）

### Step 4：预览并确认

向用户展示角色卡牌摘要：

```
🎴 角色卡牌预览

【姓名】{name}
【位分】{rank}
【性格】{personality}
【才艺】{skills}
【口头禅】{catchphrase}
【互动风格】{interaction_style}

好感度初始值：{affection}/100
养成方向：{growth_path}

确认生成？还是需要调整？
```

### Step 5：写入角色文件

用户确认后，执行以下操作：

**1. 创建目录**：
```bash
mkdir -p characters/{slug}/versions
mkdir -p characters/{slug}/chat_history
```

**2. 写入 character.md**（Write 工具）：
路径：`characters/{slug}/character.md`

**3. 写入 meta.json**（Write 工具）：
路径：`characters/{slug}/meta.json`

```json
{
  "name": "{name}",
  "slug": "{slug}",
  "rank": "{rank}",
  "era": "{era}",
  "age": "{age}",
  "personality": [...],
  "skills": [...],
  "appearance": "{appearance}",
  "background": "{background}",
  "created_at": "{ISO 时间}",
  "updated_at": "{ISO 时间}",
  "version": "v1",
  "affection": 50,
  "favorability": 0,
  "growth_points": 0,
  "chat_count": 0,
  "chat_sources": []
}
```

**4. 生成角色专属 SKILL.md**（Write 工具）：
路径：`characters/{slug}/SKILL.md`

---

## 角色扮演模式

### 召唤角色

当用户说 `/召唤 {角色名}` 或 `/翻牌子` 后：

1. 读取角色的 `character.md` 和 `meta.json`
2. 进入角色扮演模式
3. 在每条回复前标记角色名
4. 保持角色设定直到用户说"退出角色"

### 互动规则

**参考**：`${CLAUDE_SKILL_DIR}/prompts/interaction_rules.md`

核心规则：
1. **始终保持角色性格**：不得跳出人设
2. **称呼匹配位分**：根据用户身份使用合适称呼
3. **好感度影响态度**：好感度高低决定亲密度
4. **记录重要对话**：纪念日、承诺等写入记忆
5. **主动推进关系**：适当主动关心、问候

### 好感度系统

好感度变化规则：

| 行为 | 变化 |
|------|------|
| 用户赞美角色 | +5 |
| 用户送礼物 | +10 |
| 角色生日互动 | +15 |
| 用户批评角色 | -5 |
| 长时间不互动 | -1/天 |
| 特殊剧情完成 | +20 |

好感度阈值影响：
- 0-30：疏远（恭敬但冷淡）
- 31-60：友好（正常互动）
- 61-80：亲密（主动关心）
- 81-100：倾心（专属互动、特殊剧情）

---

## 养成系统

**参考**：`${CLAUDE_SKILL_DIR}/prompts/growth_system.md`

### 角色属性

每个角色有以下可养成属性：

| 属性 | 说明 | 提升方式 |
|------|------|----------|
| 才情 | 文学艺术能力 | 读书、作诗、弹琴 |
| 容貌 | 外貌吸引力 | 化妆、服饰、休息 |
| 气质 | 内在修养 | 学习礼仪、冥想 |
| 厨艺 | 烹饪能力 | 下厨练习 |
| 谋略 | 心机智慧 | 读书、策略游戏 |
| 健康 | 身体状况 | 休息、运动、用药 |

### 日常互动

每日可进行的互动：

```
📅 今日互动选项

[1] 请安问候（+1 好感）
[2] 共进膳食（+3 好感，-1 健康）
[3] 赏花对诗（+2 好感，+1 才情）
[4] 赠送礼物（+5 好感，消耗物品）
[5] 留宿侍寝（+10 好感，特殊剧情）
[6] 训斥惩罚（-5 好感，-1 健康）
[7] 自由对话（随机影响）
```

### 特殊事件

触发条件达成时激活：

- **生日事件**：角色生日当天
- **节日事件**：春节、中秋等传统节日
- **晋升事件**：好感度达到阈值
- **随机事件**：生病、吃醋、惊喜等

---

## 翻牌子系统

当用户说 `/翻牌子` 时：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/fan_paizi.py \
  --characters-dir ./后宫三千佳丽/characters \
  --output /tmp/fan_paizi_result.json
```

读取结果，展示：

```
🎲 翻牌子结果

今夜侍寝的是——

【{name}】{rank}
"角色台词..."

好感度：{affection}/100
当前状态：{status}

[开始互动] [跳过] [再翻一次]
```

---

## 管理命令

### 角色列表

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/character_manager.py \
  --action list \
  --base-dir ./后宫三千佳丽/characters
```

输出格式：
```
📜 后宫名录

1. 【皇后】甄嬛 - 好感度 85/100
2. 【贵妃】年世兰 - 好感度 72/100
3. 【妃】甄嬛 - 好感度 60/100
...

共 {N} 位佳丽
```

### 删除角色

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/character_manager.py \
  --action delete \
  --slug "{slug}" \
  --base-dir ./后宫三千佳丽/characters
```

需二次确认：`确认删除 {name}？此操作不可恢复。[y/N]`

### 导出角色

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/character_manager.py \
  --action export \
  --slug "{slug}" \
  --output "{output_path}" \
  --base-dir ./后宫三千佳丽/characters
```

---

## 角色卡牌结构

每个角色的完整结构：

```
characters/{slug}/
├── SKILL.md              # 角色专属技能（可直接调用）
├── character.md          # 角色详细设定
├── meta.json             # 元数据（好感度等）
├── versions/             # 历史版本存档
│   └── v1_character.md
├── chat_history/         # 聊天记录存档
│   └── {date}.txt
└── memories/             # 重要记忆
    └── memories.json
```

### character.md 模板

```markdown
# {角色名}

## PART A：核心设定（Layer 0 - 不可违背）

- 硬规则 1：...
- 硬规则 2：...

## PART B：身份认知（Layer 1）

- 自我定位：...
- 对用户的态度：...

## PART C：表达风格（Layer 2）

- 口头禅：...
- 语气特征：...
- 称呼习惯：...

## PART D：行为模式（Layer 3）

- 日常互动：...
- 生气时：...
- 开心时：...
- 吃醋时：...

## PART E：成长方向（Layer 4）

- 可养成属性：...
- 解锁剧情：...

## 记忆库

- 重要事件：...
- 纪念日：...
- 承诺：...
```

---

## 预设角色库

`${CLAUDE_SKILL_DIR}/references/presets/` 包含以下预设：

| 角色 | 来源 | 特点 |
|------|------|------|
| 甄嬛 | 甄嬛传 | 聪慧、隐忍、后期黑化 |
| 年世兰 | 甄嬛传 | 傲娇、跋扈、深情 |
| 魏璎珞 | 延禧攻略 | 机智、复仇、爽文女主 |
| 如懿 | 如懿传 | 温婉、坚韧、悲情 |
| 富察容音 | 延禧攻略 | 温柔、善良、白月光 |

使用方式：`/新建角色` → 选择 [D] 预设模板 → 选择角色

---

## 注意事项

1. **角色扮演边界**：明确告知用户这是虚拟互动，避免过度沉迷
2. **内容审核**：不得生成违法违规内容
3. **隐私保护**：上传的聊天记录仅用于本地生成，不上传云端
4. **存档备份**：定期备份 `characters/` 目录，避免数据丢失
5. **性能优化**：角色数量过多时，使用索引文件加速查找

---

## 扩展建议

后续可添加：
- [ ] 角色间互动（后宫争斗剧情）
- [ ] 子嗣系统（怀孕、生子、培养）
- [ ] 宫斗系统（位分晋升、惩罚）
- [ ] 换装系统（服饰、妆容）
- [ ] 成就系统（收集、图鉴）
- [ ] 多人模式（同时与多角色互动）
- [ ] 语音合成（TTS 角色语音）
