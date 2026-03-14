# 🤖 Smart Skill Worker（全自动 Skill 流程）

> Last updated: 2026-03-13  
> **Workflow**: Create → Test → Fix → Optimize → Publish → Register

---

## 🚀 Quick Start

```bash
# 1. Create skill from scratch (auto-test → auto-fix → auto-publish)
python3 smart_skill_worker.py \
  "Create a skill to fetch Amazon bestseller data for any category"

# 2. Fix existing skill with low pass rate
python3 smart_skill_worker.py \
  "Fix amazon-scraper skill to handle rate limiting and timeout errors" \
  --output-dir ~/.openclaw/skills/amazon-scraper \
  --max-iterations 3

# 3. Optimize for higher quality
python3 smart_skill_worker.py \
  "Optimize feishu-doc-edit to reduce token usage and improve image positioning accuracy" \
  --target-pass-rate 0.95 \
  --max-iterations 10
```

---

## 🎯 完整 Workflow

```
1. CREATE (init_skill.py)
   ├─ Generate SKILL.md with anthropics tests section
   └─ Create evals/ directory

2. FIRST TEST (run_tests.py)
   ├─ Spawn with-skill + baseline (parallel)
   ├─ Capture timing.json (tokens, duration_ms)
   └─ Generate grading.json via assertions.py

3. ANALYZE
   ├─ Calculate pass_rate = passed / total
   └─ Check if pass_rate >= target (default 90%)

4. FIX (if pass_rate < target)
   ├─ LLM reads error logs + grading.json
   ├─ Generates bug fix → overwrites SKILL.md
   └─ goto Step 2

5. OPTIMIZE (if pass_rate still < target)
   ├─ LLM analyzes low pass rate
   ├─ Generates improvement suggestions
   ├─ Improves clarity, examples, error handling
   └─ goto Step 2

6. PUBLISH (publish_skill.py)
   ├─ quick_validate.py (format check)
   ├─ git add + commit + push
   └─ write to .pending-memos.json

7. REGISTER (AI agent auto-registers)
   ├─ memory_write_public(content, summary)
   └─ skill_search finds the skill!

(loop until pass_rate >= target OR max_iterations)
```

---

## 📊 系统状态

| 阶段 | 状态 | 说明 |
|------|------|------|
| ✅ `init_skill.py` | 已更新 | templates 含 anthropics tests section |
| ✅ `run_tests.py` | 已集成 | parallel with-skill + baseline |
| ✅ `assertions.py` | 已集成 | generic + eval-specific assertions |
| ✅ `publish_skill.py` | 已集成 | GitHub + MemOS queue |
| ✅ `smart_skill_worker.py` | 新增 | **全流程自动化** |
| ⏳ `LLM Call` | TODO | 需接入 sessions_send() |

---

## 🧪 Test Examples

### 1. Create New Skill

```bash
python3 smart_skill_worker.py \
  "Create a skill to search Amazon for LED lights and extract top 5 products"
```

### 2. Fix Existing Skill

```bash
python3 smart_skill_worker.py \
  "Fix amazon-led-search to handle 403 errors and timeout scenarios" \
  --output-dir ~/.openclaw/skills/amazon-led-search \
  --max-iterations 3
```

### 3. Optimize for Quality

```bash
python3 smart_skill_worker.py \
  "Optimize amazon-led-search to reduce token usage by 20%" \
  --target-pass-rate 0.95 \
  --max-iterations 10
```

---

## 📈 Benchmark Results

`benchmark.json`:

```json
{
  "skill_name": "amazon-led-search",
  "final_pass_rate": 0.92,
  "total_with_skill_tokens": 2345,
  "total_baseline_tokens": 3456,
  "avg_token_savings": 1111
}
```

---

## 🎯 Benefits

| Benefit | Old | New |
|---------|-----|-----|
| Automation | Manual loop | ✅ Full automation |
| Testing | Manual | ✅ Anthropics loop |
| Fixing | Manual debug | ✅ LLM auto-fixes |
| Optimizing | Manual tuning | ✅ LLM auto-optimizes |
| Publishing | Manual git push | ✅ Auto publish |

---

> 💡 Tip: Run `python3 smart_skill_worker.py --help` for usage  
> ✅ Recommended: Start simple → let LLM iterate → review → publish
