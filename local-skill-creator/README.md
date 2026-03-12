# local-skill-creator

创建、验证、发布 AgentSkill 的本地工具集。

## 用途

解决 OpenClaw skill 创建流程不规范的问题，提供标准化的脚手架生成、格式验证、一键发布到 GitHub，以及 MemOS 注册提示。

## 使用方法

```bash
# 1. 创建脚手架
python3 scripts/init_skill.py <skill-name> --description "..."

# 2. 填写 SKILL.md 和 README.md

# 3. 验证格式
python3 scripts/quick_validate.py ~/.openclaw/skills/<skill-name>

# 4. 发布到 GitHub + 获取 MemOS 注册提示
python3 scripts/publish_skill.py ~/.openclaw/skills/<skill-name> --owner "马振坤"

# 5. 在 OpenClaw agent 中执行 MemOS 注册（让 skill_search 可检索）
```

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `init_skill.py` | 生成 skill 脚手架（SKILL.md + README.md + 目录） |
| `quick_validate.py` | 验证 SKILL.md frontmatter + README.md 存在 |
| `publish_skill.py` | validate + git push + MemOS 注册提示 |
| `package_skill.py` | 打包成 .skill 归档（备用） |

## 注意事项

- skill 名称：小写字母、数字、连字符，1-64 字符
- `skill_search` 不读本地文件，需额外注册到 MemOS public memory 才能被检索
- 默认输出路径：`~/.openclaw/skills/`
- 默认 GitHub repo：`~/.openclaw/workspace/openclaw-watchdog-skill-library`
