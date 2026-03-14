# local-skill-creator

创建、验证、发布 AgentSkill 的本地工具集（**Anthropics iteration enabled + MemOS registration**），
**最新更新：增加了 `.history.json` 版本跟踪 + 用户沟通指南 + 查询已有 skill 流程**。

## 用途

标准化 skill 创建流程：脚手架生成 → 内容填写 → **测试验证**（Anthropics）→ GitHub 发布 → MemOS 自动注册。
新增：量化评估（expectation_pass_rate）、版本迭代追踪、用户友好沟通策略。

---

## 查询已有 skill（ **说明** ）

由于以下原因，**暂不自动调用 `npx skills find` 或 `skills.sh` 查询**：

1. `npx skills` CLI 需要交互式输入，headless 环境可能卡住
2. `skills.sh/?q=xxx` 页面由 JS 渲染，`web_fetch` 不返回结果
3. `openclaw/skills` mirror 很大（8,858 skill），难以本地维护

**推荐做法**：
- 用户说「帮我做个 skill」→ AI 先反问「是否需要我帮你查是否有现成 skill？」
- 用户确认「是」→ 提供 `https://skills.sh/` 链接让用户自己查
- 用户确认「否」→ 直接进入「创建新 skill」流程

**如果需要调试**：
- 可手动用 `browser` + `profile="openclaw"` 打开 skills.sh → 搜索
- 或 clone `openclaw/skills` 到本地 → 本地 grep 搜索（不推荐，>8GB）

## 快速开始

```bash
SCRIPTS=~/.openclaw/workspace/local-skill-creator/scripts

# 1. 创建脚手架（含 anthropics tests section）
python3 $SCRIPTS/init_skill.py my-skill --description "这个 skill 做什么"

# 2. 填写 ~/.openclaw/skills/my-skill/SKILL.md 和 README.md

# 3. 创建 evals/evals.json（Anthropics workflow）
#    每个 eval 需要: id, name, prompt, expected_output, assertions

# 4. 运行 Human-in-the-loop test（Anthropics loop）
python3 $SCRIPTS/run_tests.py \
    --skill-path ~/.openclaw/skills/my-skill \
    --workspace ~/test-workspace/my-skill \
    --static ~/test-workspace/my-skill/viewer.html

# 5. 使用 update-skill.sh 一键更新 + 测试（推荐）
./$SCRIPTS/update-skill.sh my-skill

# 6. 发布到 GitHub（自动 validate + git push + 写注册队列）
python3 $SCRIPTS/publish_skill.py ~/.openclaw/skills/my-skill --owner "马振坤"

# 7. AI agent 读队列 → memory_write_public → 清空队列
python3 $SCRIPTS/register_memos.py        # 读队列（AI agent 处理）
python3 $SCRIPTS/register_memos.py --clear  # 清空
```

## 脚本说明

| 脚本 | 功能 | 新增功能 |
|------|------|----------|
| `init_skill.py` | 生成 skill 脚手架（SKILL.md + README.md） | ✅ 自动添加 tests section |
| `quick_validate.py` | 验证格式（frontmatter + README.md） | - |
| `publish_skill.py` | validate + git push + 写 pending 队列 | - |
| `register_memos.py` | 读/清空 pending 队列，供 AI agent 注册 MemOS | - |
| `package_skill.py` | 打包成 .skill 归档（备用） | - |
| `assertions.py` | ✨ 运行 assertions 生成 grading.json | 新增 |
| `run_tests.py` | ✨ Anthropics workflow runner | 新增 |
| `update-skill.sh` | ✨ 一键更新 + 测试 + viewer | 新增 |

## Anthropics Workflow (New!)

| 阶段 | 说明 | 命令 |
|------|------|------|
| 1️⃣ 创建 | 生成脚手架 | `python3 init_skill.py my-skill` |
| 2️⃣ 测试 | 并行 with-skill + baseline | `python3 run_tests.py ...` |
| 3️⃣ 评估 | 运行 assertions + `expectations` 检查 | `python3 assertions.py ...` |
| 4️⃣ 对比 | viewer.html (prev/next iteration) | `--static viewer.html` |
| 5️⃣ 反馈 | 提交 feedback.json | 点击 viewer 按钮 |
| 6️⃣ 迭代 | 编辑 → 重测 → 循环 | `./update-skill.sh my-skill` |
| 7️⃣ version track | 每次 iteration 更新 `.history.json` | ✨ Auto-created by runner |

## Upgrade

Run `scripts/upgrade-local-skill-creator.sh` to add Anthropics features to existing local-skill-creator.

See `UPGRADE.md` for full details.

## 注意事项

- skill 名称：小写字母、数字、连字符，1-64 字符
- pending 队列：`~/.openclaw/skills/.pending-memos.json`
- 默认 GitHub repo：`~/.openclaw/workspace/openclaw-watchdog-skill-library`
- `skill_search` 不读本地文件，必须注册到 MemOS 才能被检索
- `run_tests.py` 需要桌面环境打开 viewer；headless 环境：`--static`
