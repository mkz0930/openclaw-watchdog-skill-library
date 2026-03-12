---
name: local-skill-creator
description: "创建、验证、发布 AgentSkill 的本地工具集。包含脚手架生成、格式验证、一键发布到 GitHub 及自动注册到 MemOS。"
---

# Local Skill Creator

## 适用场景

- 创建新 skill（生成标准目录结构和模板）
- 验证 skill 格式是否合规（SKILL.md frontmatter + README.md）
- 一键发布到 GitHub + 自动注册到 MemOS（让 skill_search 可检索）

## 完整工作流（4步）

### 第一步：创建脚手架

```bash
python3 ~/.openclaw/workspace/local-skill-creator/scripts/init_skill.py \
  <skill-name> \
  --description "这个 skill 是干什么的"
# 默认输出到 ~/.openclaw/skills/<skill-name>/
# 自动生成: SKILL.md（含 YAML frontmatter）、README.md
```

### 第二步：填写内容

- 编辑 `SKILL.md`：填写适用场景、使用方法、关键参数、故障排查
- 编辑 `README.md`：填写用途、使用示例、注意事项

### 第三步：发布到 GitHub

```bash
python3 ~/.openclaw/workspace/local-skill-creator/scripts/publish_skill.py \
  ~/.openclaw/skills/<skill-name> \
  [--owner "马振坤"]
# 流程: validate → 复制到 repo → git commit + push → 写入 .pending-memos.json
```

### 第四步：注册到 MemOS（AI agent 自动执行）

```bash
# 读取待注册队列
python3 ~/.openclaw/workspace/local-skill-creator/scripts/register_memos.py
# → 输出 JSON，AI agent 调用 memory_write_public 完成注册
# → 注册完成后清空队列
python3 ~/.openclaw/workspace/local-skill-creator/scripts/register_memos.py --clear
```

**AI agent 标准操作：**
1. `exec register_memos.py` → 读队列
2. 对每条记录调用 `memory_write_public(content, summary)`
3. `exec register_memos.py --clear` → 清空队列
4. 回复 GitHub 链接给用户

## 关键参数 / 注意事项

- skill 名称规则：小写字母、数字、连字符，1-64 字符，不能以连字符开头/结尾
- `quick_validate.py` 只允许 frontmatter 有 `name` 和 `description` 两个字段
- `publish_skill.py` 默认 repo：`~/.openclaw/workspace/openclaw-watchdog-skill-library`
- pending 队列文件：`~/.openclaw/skills/.pending-memos.json`（同名 skill 自动去重覆盖）
- description 优先从 SKILL.md frontmatter 读，fallback 到 `_meta.json`

## 为什么需要 MemOS 注册

`skill_search` 走 MemOS 向量索引，不读本地文件系统。
`~/.openclaw/skills/` 里的 skill 对 `skill_search` 是"隐形的"，必须写入 MemOS 才能被检索到。
（已提 GitHub issue #43950 请求 OpenClaw 自动同步）

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `init_skill.py` | 生成 skill 脚手架（SKILL.md + README.md） |
| `quick_validate.py` | 验证 SKILL.md frontmatter + README.md 存在 |
| `publish_skill.py` | validate + git push + 写 pending 队列 |
| `register_memos.py` | 读/清空 pending 队列，供 AI agent 注册 MemOS |
| `package_skill.py` | 打包成 `.skill` 归档（备用） |
