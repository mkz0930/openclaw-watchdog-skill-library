---
name: local-skill-creator
description: "创建、验证、发布 AgentSkill 的本地工具集。包含脚手架生成、格式验证、一键发布到 GitHub 及自动注册到 MemOS。"
---

# Local Skill Creator

## 用途

标准化 skill 创建流程：脚手架生成 → 内容填写 → GitHub 发布 → MemOS 自动注册，全程 4 步完成。

## 快速开始

```bash
SCRIPTS=~/.openclaw/workspace/local-skill-creator/scripts

# 1. 创建脚手架
python3 $SCRIPTS/init_skill.py my-skill --description "这个 skill 做什么"

# 2. 填写 ~/.openclaw/skills/my-skill/SKILL.md 和 README.md

# 3. 发布到 GitHub（自动 validate + git push + 写注册队列）
python3 $SCRIPTS/publish_skill.py ~/.openclaw/skills/my-skill --owner "马振坤"

# 4. AI agent 读队列 → memory_write_public → 清空队列
python3 $SCRIPTS/register_memos.py        # 读队列（AI agent 处理）
python3 $SCRIPTS/register_memos.py --clear  # 清空
```

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `init_skill.py` | 生成 skill 脚手架（SKILL.md + README.md） |
| `quick_validate.py` | 验证格式（frontmatter + README.md） |
| `publish_skill.py` | validate + git push + 写 pending 队列 |
| `register_memos.py` | 读/清空 pending 队列，供 AI agent 注册 MemOS |
| `package_skill.py` | 打包成 .skill 归档（备用） |

## 注意事项

- skill 名称：小写字母、数字、连字符，1-64 字符
- pending 队列：`~/.openclaw/skills/.pending-memos.json`
- 默认 GitHub repo：`~/.openclaw/workspace/openclaw-watchdog-skill-library`
- `skill_search` 不读本地文件，必须注册到 MemOS 才能被检索

---

## 注册与调用（AI 自动发现）

### 安装后如何让 AI 自动调用

本 skill 已注册到 MemOS public memory，AI agent 可通过 `skill_search` 检索到。

**触发关键词：** 创建 skill、发布 skill、skill creator、local skill、注册 MemOS

**AI 调用方式：**
```
skill_search("创建 skill")
→ 找到 local-skill-creator
→ 工具路径: /home/claw/.openclaw/workspace/local-skill-creator/scripts/
→ 按照上方 4 步流程执行
```

### 手动注册（如果 skill_search 找不到）

```bash
# 直接调用 memory_write_public，内容如下：
# skill: local-skill-creator
# description: 创建、验证、发布 AgentSkill 的本地工具集
# path: /home/claw/.openclaw/workspace/local-skill-creator/
# github: https://github.com/mkz0930/openclaw-watchdog-skill-library/tree/master/local-skill-creator
```

### GitHub

https://github.com/mkz0930/openclaw-watchdog-skill-library/tree/master/local-skill-creator
