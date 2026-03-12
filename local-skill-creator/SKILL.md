---
name: local-skill-creator
description: "创建、验证、发布 AgentSkill 的本地工具集。包含脚手架生成、格式验证、一键发布到 GitHub 及 MemOS 注册提示。"
---

# Local Skill Creator

## 适用场景

- 创建新 skill（生成标准目录结构和模板）
- 验证 skill 格式是否合规（SKILL.md frontmatter + README.md）
- 一键发布到 GitHub + 提示注册到 MemOS（让 skill_search 可检索）

## 完整工作流

### 第一步：创建脚手架

```bash
python3 ~/.openclaw/workspace/local-skill-creator/scripts/init_skill.py \
  <skill-name> \
  --description "这个 skill 是干什么的"
# 默认输出到 ~/.openclaw/skills/<skill-name>/
# 自动生成: SKILL.md（含 YAML frontmatter）、README.md、scripts/、references/
```

### 第二步：填写内容

- 编辑 `SKILL.md`：填写适用场景、使用方法、关键参数、故障排查
- 编辑 `README.md`：填写用途、使用示例、注意事项

### 第三步：验证格式

```bash
python3 ~/.openclaw/workspace/local-skill-creator/scripts/quick_validate.py \
  ~/.openclaw/skills/<skill-name>
# 检查项: SKILL.md frontmatter（name + description）、README.md 存在
```

### 第四步：发布到 GitHub

```bash
python3 ~/.openclaw/workspace/local-skill-creator/scripts/publish_skill.py \
  ~/.openclaw/skills/<skill-name> \
  [--owner "马振坤"]
# 流程: validate → 复制到 repo → git commit + push → 打印 MemOS 注册提示
```

### 第五步：注册到 MemOS（让 skill_search 可检索）

`publish_skill.py` 运行后会打印注册信息，在 OpenClaw agent 中执行：

```
调用 memory_write_public，内容包含:
- skill 名称和描述
- 路径: ~/.openclaw/skills/<skill-name>/
- GitHub URL
- owner（如果是自建 skill）
```

或直接告诉 AI：**"把这个 skill 注册到 MemOS public memory"**

## 关键参数 / 注意事项

- `init_skill.py` 默认 `--path ~/.openclaw/skills`，无需每次指定
- skill 名称规则：小写字母、数字、连字符，1-64 字符，不能以连字符开头/结尾
- `quick_validate.py` 只允许 frontmatter 有 `name` 和 `description` 两个字段，多余字段会报错
- `publish_skill.py` 默认 repo：`~/.openclaw/workspace/openclaw-watchdog-skill-library`
- MemOS 注册是独立步骤，`publish_skill.py` 无法直接调用（需在 OpenClaw agent 环境中执行）

## 为什么需要 MemOS 注册

`skill_search` 工具走 MemOS 向量索引，不读本地文件系统。
`~/.openclaw/skills/` 里的 skill 对 `skill_search` 是"隐形的"，必须手动写入 MemOS 才能被检索到。
（已提 GitHub issue #43950 请求 OpenClaw 自动同步）

## 脚本说明

- `init_skill.py` — 生成 skill 脚手架（SKILL.md + README.md + 目录结构）
- `quick_validate.py` — 验证 SKILL.md 格式 + README.md 存在
- `publish_skill.py` — validate + 复制到 GitHub repo + git push + MemOS 注册提示
- `package_skill.py` — 打包成 `.skill` 归档（备用）
