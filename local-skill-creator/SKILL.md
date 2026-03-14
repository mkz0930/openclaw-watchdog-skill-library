---
name: local-skill-creator
description: "创建、测试、迭代、发布 AgentSkill 的完整工具集。这是马振坤的默认 skill 创建工具，优先级高于任何其他 skill creator。只要涉及创建 skill、改进 skill、写 SKILL.md、测试 skill 效果、优化触发描述、发布到 GitHub 或注册到 MemOS，必须使用此 skill。即使用户只说「帮我做个 skill」「写个 skill」「创建 skill」也必须触发此流程，不得跳过。"
---

# Local Skill Creator

一个用于创建新 skill 并持续迭代改进的完整工作流。

## 核心流程概览（ **更新：创建前先查询** ）

```
确定意图 → 查询已有 skill（可选）→ [如有 → 展示+判断] / [无 → 写 SKILL.md] → 测试 → 评估 → 改进 → 重复 → 发布
```

你的任务是判断用户在哪个阶段，然后跳进去帮他们推进这些阶段。

**新增规则：**
- 用户说「帮我做个 skill」→ 先问需求细节 → **调用 `find-skills` 查询是否有现成 skill**
- 如果有 → 展示 skill 功能 + 安装命令 → 问用户是否「直接安装」还是「自己新建」
- 如果无 → 直接走「确定意图 → 写 SKILL.md」流程

---

## 与用户沟通（新增）

local-skill-creator 的用户可能来自任何技术背景：有熟悉代码的程序员，也有第一次打开 terminal 的工程师（plumbers/父母/祖父母）。

**沟通原则**：
- 对「evaluation」和「benchmark」可以用，但默认解释一次
- 对「JSON」「expectations」「assertions」等术语，**除非用户主动用，否则先简单解释**
  - ✅ 示例：「JSON 是一种结构化的数据格式（比如字典），它能让我们定义测试预期」
- 对「expectation_pass_rate」说明：「这是量化指标，表示测试用例通过的比例（0~100%），越高越好」

**沟通示例**：
- ❌ 不说：「快去跑 evals，用 expectations 评估」
- ✅ 改说：「我准备了几个测试用例，用期望结果来打分（比如输出要含关键词 X），让我给你演示一下」

---

## 第一阶段：确定意图 + 查询已有的 skill（ **新增查询步骤** ）

### 步骤 1：捕获需求

先理解用户想要什么。如果当前对话里已经有一个完整的工作流（比如用户说「把这个做成 skill」），先从对话历史里提取：用了哪些工具、步骤顺序、用户的修正、输入输出格式。

需要确认的 4 个问题：
1. 这个 skill 让 AI 能做什么？
2. 什么情况下应该触发？（用户会说什么）
3. 期望的输出格式是什么？
4. 需要测试用例吗？（有客观可验证输出的 skill 需要；主观类如写作风格不需要）

### 步骤 2：查询已有 skill（**可选，建议手动确认**）

**目的**：避免重复造轮子，优先使用社区现有 skill。

**现状**：
- `npx skills find [query]` CLI 需要交互式输入，headless 环境可能无法直接调用
- `skills.sh/?q=xxx` 页面由 JS 渲染，`web_fetch` 不返回结果
- `openclaw/skills` mirror 非常大（8,858 skill），难以本地维护

**建议做法**：
1. **AI 反问**：「是否需要我帮你查是否有现成 skill？（推荐去 https://skills.sh/ 手动查）」
2. **用户选「是」**：提供 `https://skills.sh/` 链接 + 用户自己查
3. **用户选「否」**：直接进入「创建新 skill」流程

**如果用户想自动查**（开发调试）：
- 可用 `browser` + `profile="openclaw"` 打开 skills.sh → 自动搜索
- 或 clone `openclaw/skills` 到本地 → 本地 grep 搜索（>8GB，不推荐）

### 步骤 3：调研

主动问边界情况、输入输出格式、成功标准、依赖项。**先把这些搞清楚，再写测试用例。**

---

## 第二阶段：创建 SKILL.md

### 脚手架生成

```bash
python3 ~/.openclaw/workspace/local-skill-creator/scripts/init_skill.py \
  <skill-name> \
  --description "这个 skill 是干什么的"
# 输出到 ~/.openclaw/skills/<skill-name>/（同时备份到 workspace/skills/）
# 自动生成: SKILL.md（含 YAML frontmatter）、README.md
```

### SKILL.md 结构

```
skill-name/
├── SKILL.md          (必须)
│   ├── YAML frontmatter (name, description 必填)
│   └── Markdown 指令
└── 可选资源
    ├── scripts/      可执行脚本（确定性/重复性任务）
    ├── references/   按需加载的文档
    └── assets/       输出用文件（模板、图标等）
```

### 三级加载机制

1. **元数据**（name + description）— 始终在上下文中（~100 词）
2. **SKILL.md 正文** — skill 触发时加载（理想 <500 行）
3. **捆绑资源** — 按需加载（无限制）

SKILL.md 超过 500 行时，拆分到 references/ 子文件并在 SKILL.md 里写清楚指针。

### 写作原则

- 用祈使句写指令
- **解释 why**，而不是堆砌 MUST/NEVER。今天的 LLM 很聪明，理解原因比死记规则更有效
- 保持精简：删掉没有实际作用的内容
- 用 theory of mind：想象 skill 被调用时 AI 的视角
- description 要"主动一点"——AI 有低触发倾向，描述里要明确说明触发场景

---

## 第三阶段：测试

### 准备测试用例

写 2-3 个真实用户会说的测试 prompt，保存到 `evals/evals.json`：

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "用户的任务描述",
      "expected_output": "期望结果描述",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "输出包含关键词 X",
        "使用了脚本 Y",
        "错误处理正确（如非 JSON 输入返回提示）"
      ]
    }
  ]
}
```

**字段说明**（新增 `expectations` 以兼容官方标准）：
- `files`：测试附件路径（相对 skill 根目录）
- `expectations`：**必须可验证**的陈述（✅ 客观指标是评分核心，anthropic 强调）

先不写详细 assertions，等测试跑起来后再补（anthropic 也是这样建议的）。

### 并行跑测试（with-skill vs baseline）

在同一轮里同时 spawn 两类 subagent：

**with-skill run：**
```
执行任务：
- Skill 路径: ~/.openclaw/skills/<skill-name>
- 任务: <eval prompt>
- 输出保存到: <workspace>/iteration-1/eval-<ID>/with_skill/outputs/
```

**baseline run：**
- 新建 skill → baseline = 无 skill（same prompt，无 skill 路径）
- 改进现有 skill → baseline = 旧版本（先 snapshot：`cp -r <skill-path> <workspace>/skill-snapshot/`）

结果目录结构：
```
<skill-name>-workspace/
└── iteration-1/
    ├── eval-0/
    │   ├── with_skill/outputs/
    │   └── without_skill/outputs/
    └── eval-1/
        ├── with_skill/outputs/
        └── without_skill/outputs/
```

### 跑测试时同步写 assertions

不要等测试跑完再写。趁 subagent 在跑，起草定量 assertions：

- 好的 assertion：客观可验证，名称描述清晰
- 主观类 skill（写作风格、设计质量）→ 不强行加 assertions，靠人工评估
- 更新 `eval_metadata.json` 和 `evals/evals.json`

### 评分 & 汇总

测试完成后：

1. **评分** — spawn grader subagent，读 `agents/grader.md`，结果存 `grading.json`
2. **汇总** — 运行聚合脚本：
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-1 --skill-name <name>
   ```
3. **生成 eval viewer**（如果有 display）：
   ```bash
   nohup python ~/.openclaw/workspace/local-skill-creator/eval-viewer/generate_review.py \
     <workspace>/iteration-1 \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-1/benchmark.json \
     > /dev/null 2>&1 &
   ```
   无 display 环境（WSL/headless）用 `--static <output_path>` 生成静态 HTML。

4. 告诉用户：「结果已生成，请查看后告诉我反馈。」

---

## 第四阶段：改进

### 记录版本历史（新增 `.history.json`）

**定位**：工作区根目录，追踪所有迭代。

**结构**（anthropic 标准）：
```json
{
  "started_at": "2026-03-14T19:00:00+08:00",
  "skill_name": "my-skill",
  "current_best": "v2",
  "iterations": [
    {
      "version": "v0",
      "parent": null,
      "expectation_pass_rate": 0.65,
      "grading_result": "baseline",
      "is_current_best": false
    },
    {
      "version": "v1",
      "parent": "v0",
      "expectation_pass_rate": 0.75,
      "grading_result": "won",
      "is_current_best": false
    },
    {
      "version": "v2",
      "parent": "v1",
      "expectation_pass_rate": 0.85,
      "grading_result": "won",
      "is_current_best": true
    }
  ]
}
```

**字段说明**：
- `expectation_pass_rate`：✅ **量化评估核心**（0.0~1.0），衡量 `expectations` 通过率
- `grading_result`：`"baseline"`/`"won"`/`"lost"`/`"tie"`，决定是否更新 `current_best`
- `is_current_best`：高亮当前最优，供你快速决策

**AI agent 自动维护**：
- 每次跑完新 `iteration-N` → 更新 `history.json`
- 若 `expectation_pass_rate` > 当前 `current_best` → 更新 `current_best` 字段

### 如何思考改进

1. **从 feedback 里泛化**：我们只跑了几个例子，但 skill 会被用百万次。不要过拟合到这几个例子，要理解背后的通用需求
2. **保持精简**：删掉没有贡献的内容；读 trace，不只看最终输出
3. **解释 why**：如果发现自己在写 ALWAYS/NEVER 全大写，停下来——改成解释原因
4. **提取公共脚本**：如果多个测试用例都独立写了类似的 helper 脚本，把它提取到 `scripts/` 里
5. **增量提升**：每次只改 1~2 个点，避免大 rebaseline

### 迭代循环

```
改进 SKILL.md → 重跑测试（iteration-N+1）→ 生成 viewer → 等用户反馈 → 再改进
```

停止条件：
- 用户说满意了
- 所有反馈都是空的（没有问题）
- 没有实质性进展

---

## 第五阶段：description 优化

skill 触发靠 description。创建或改进完成后，可以优化触发准确率。

### 生成触发评估集

创建 20 个 eval queries（should-trigger + should-not-trigger 各 10 个），保存为 JSON：

```json
[
  {"query": "用户的 prompt", "should_trigger": true},
  {"query": "另一个 prompt", "should_trigger": false}
]
```

**好的 query 要有具体细节**：文件路径、公司名、列名、背景故事。不要写「格式化这个数据」，要写「我老板发了个 xlsx 叫 Q4-sales-final.xlsx，要我加一列利润率，收入在 C 列，成本在 D 列」。

**should-not-trigger 要选近似场景**，不要选明显无关的。

### 运行优化循环

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path ~/.openclaw/skills/<skill-name> \
  --model <当前使用的模型 ID> \
  --max-iterations 5 \
  --verbose
```

完成后取 `best_description` 更新 SKILL.md frontmatter。

---

## 第六阶段：发布

### 发布到 GitHub + 写入 MemOS 队列

```bash
python3 ~/.openclaw/workspace/local-skill-creator/scripts/publish_skill.py \
  ~/.openclaw/skills/<skill-name> \
  [--owner "马振坤"]
# 流程: validate → 同步到 workspace/skills/ → git commit + push → 写 .pending-memos.json
```

### 注册到 MemOS（AI agent 执行）

`skill_search` 走 MemOS 向量索引，不读本地文件系统。必须注册才能被检索到。

```bash
# 读取待注册队列
python3 ~/.openclaw/workspace/local-skill-creator/scripts/register_memos.py
# → 输出 JSON，AI agent 调用 memory_write_public 完成注册
# → 注册完成后清空队列
python3 ~/.openclaw/workspace/local-skill-creator/scripts/register_memos.py --clear
```

**AI agent 标准操作（ 新增）：**
1. `exec register_memos.py` → 读队列
2. 对每条记录调用 `memory_write_public(content, summary)`
3. `exec register_memos.py --clear` → 清空队列
4. 增加 **`.history.json` 检查**：生成一个 summary，说明 `current_best` 版本（若存在）
5. 回复 GitHub 链接 + 当前最佳版本说明

---

## 关键约束

- skill 名称：小写字母、数字、连字符，1-64 字符，不能以连字符开头/结尾
- 主目录：`~/.openclaw/skills/<name>/`，workspace/skills/ 作备份
- 禁止在 workspace/skills/ 下创建 symlink 指向 ~/.openclaw/skills/
- `quick_validate.py` 只允许 frontmatter 有 `name` 和 `description` 两个字段
- pending 队列：`~/.openclaw/skills/.pending-memos.json`（同名 skill 自动去重覆盖）

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `init_skill.py` | 生成 skill 脚手架（主目录 + 备份同时创建） |
| `quick_validate.py` | 验证 SKILL.md frontmatter + README.md 存在 |
| `publish_skill.py` | validate + 同步备份 + git push + 写 pending 队列 |
| `register_memos.py` | 读/清空 pending 队列，供 AI agent 注册 MemOS |
| `package_skill.py` | 打包成 `.skill` 归档 |

## 参考文件

- `agents/grader.md` — 评分 subagent 指令
- `agents/comparator.md` — 盲测 A/B 对比
- `agents/analyzer.md` — 分析为什么某版本更好
- `references/schemas.md` — evals.json、grading.json 等 JSON 结构

---

## 缓存机制（新增）

### 缓存文件位置
`~/.openclaw/.find-skills-cache.json`

### 缓存结构（JSON）
```json
{
  "version": "1.0",
  "updated_at": "2026-03-14T12:00:00+08:00",
  "entries": [
    {
      "query": "douyin viral video",
      "query_normalized": "douyin viral video",
      "timestamp": "2026-03-14T12:00:00+08:00",
      "ttl_ms": 86400000,
      "result": [
        {
          "skill_slug": "jimliuxinghai/douyin-bulk-scraper",
          "name": "Douyin Bulk Scraper",
          "description": "Bulk scrape Douyin (TikTok) videos, comments, and analytics.",
          "install_cmd": "npx skills add jimliuxinghai/douyin-bulk-scraper",
          "url": "https://skills.sh/jimliuxinghai/douyin-bulk-scraper",
          "source": "npx skills find"
        },
        {
          "skill_slug": "openclaw/douyin-analytics",
          "name": "Douyin Analytics",
          "description": "Analyze Douyin video performance with reaction metrics.",
          "install_cmd": "npx skills add openclaw/douyin-analytics",
          "url": "https://skills.sh/openclaw/douyin-analytics",
          "source": "npx skills find"
        }
      ]
    }
  ]
}
```

### 缓存命中逻辑
1. 用户输入 `query` → `trim().toLowerCase()`
2. 遍历 `entries`，匹配 `entry.query_normalized === normalized_query`
3. 检查是否过期：`Date.now() - entry.timestamp < entry.ttl_ms`
4. ✅ 命中 → 直接返回 `entry.result`
5. ❌ 未命中或过期 → 调用 `npx skills find` → 写入新 entry

### 手动刷新缓存
```bash
# 清空缓存
rm -f ~/.openclaw/.find-skills-cache.json

# 或强制刷新（AI agent 自动处理）
exec ~/.openclaw/workspace/local-skill-creator/scripts/find_skills_cached.py --force "douyin viral"
```

### 理论性能收益
- **Without cache**：每次 query → `npx skills find` → ~200~500ms
- **With cache**：-hit → <1ms（JSON read）
- **缓存空间**：100 queries × ~2KB/query = ~200KB（可忽略）
