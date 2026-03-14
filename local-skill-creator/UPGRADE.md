# 📦 local-skill-creator Upgrade (Anthropics Workflow)

> Last updated: 2026-03-13  
> This script now supports **Anthropics-style iterative evaluation**

---

## 🔄 What's New

| Feature | Old | New |
|---------|-----|-----|
| **Test runner** | None | `run_tests.py` (Anthropics loop) |
| **Assertion runner** | None | `assertions.py` (generic + eval-specific) |
| **Update workflow** | Manual | `update-skill.sh` (one-command) |
| **Baseline comparison** | None | with-skill + without-skill (parallel) |
| **Timing capture** | None | `timing.json` (tokens, duration_ms) |

---

## 🧰 Updated Scripts

### 1. `init_skill.py` (Updated)

**Changes**:
- Added tests section to `SKILL.md` template
- Added evals/README.md hint to `README.md` template

**Example output**:
```markdown
## Tests (Anthropics Workflow)

| ID | Name | Assertions |
|----|------|------------|
| `my-skill-basic` | Basic usage | Output contains ABC |
| `my-skill-edge-case` | Edge case | Handles X gracefully |
| `my-skill-fail-case` | Failure mode | Error message with XYZ |

See `evals/README.md` for full Anthropics workflow.
```

---

### 2. `assertions.py` (NEW)

**Purpose**: Run assertions on eval outputs and generate `grading.json`

**Usage**:
```bash
# Generic assertions (applies to most skills)
python3 assertions.py --eval-id my-skill-basic --output-dir outputs

# Or use eval-specific check function (if defined)
# def check_my-skill-basic(outputs_dir: Path) -> dict: ...
```

**Generic checks**:
- ✅ Output files created
- ✅ JSON outputs valid
- ✅ No error logs
- ✅ Timing data captured

---

### 3. `run_tests.py` (NEW)

**Purpose**: Implement full Anthropics iterative evaluation loop

**Usage**:
```bash
python3 run_tests.py \
    --skill-path ~/.openclaw/skills/my-skill \
    --workspace ~/test-workspace/my-skill \
    --static ~/test-workspace/my-skill/viewer.html
```

**What it does**:
1. **Spawn parallel runs**: `with-skill` + `without-skill` (baseline)
2. **Capture timing**: `total_tokens`, `duration_ms`
3. **Run assertions**: Generate `grading.json`
4. **Aggregate benchmark**: Calculate pass rate, token savings
5. **Generate viewer**: Static HTML or server

**Output structure**:
```
workspace/
└── eval-0-my-skill-basic/
    ├── with_skill/
    │   ├── response.json
    │   ├── timing.json
    │   └── logs.txt
    ├── without_skill/
    │   └── ...
    ├── eval_metadata.json
    └── grading.json
```

---

### 4. `update-skill.sh` (NEW)

**Purpose**: One-command update + test + review

**Usage**:
```bash
./update-skill.sh my-skill
```

**Workflow**:
1. `git pull` latest changes
2. `quick_validate.py` (format check)
3. `run_tests.py` (Anthropics loop)
4. Generate static `viewer.html`
5. Show next steps

---

## 🎯 Anthropics Workflow Step-by-Step

### Step 1: Create Skill
```bash
SCRIPTS=~/.openclaw/workspace/local-skill-creator/scripts
python3 $SCRIPTS/init_skill.py my-skill --description "do X Y Z"
```

### Step 2: Write SKILL.md
Fill in:
- Name, description
- Use cases, methods
- Parameters, gotchas
- **Tests section** (auto-generated from template)

### Step 3: Create evals
Create `evals/evals.json`:
```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": "my-skill-basic",
      "name": "Basic usage",
      "prompt": "User says... do X",
      "expected_output": "Should return Y",
      "assertions": [
        "Output contains expected data",
        "No errors"
      ]
    }
  ]
}
```

### Step 4: Run Tests
```bash
cd ~/.openclaw/skills/my-skill

# Run all evals
python3 $SCRIPTS/run_tests.py \
    --skill-path ~/.openclaw/skills/my-skill \
    --workspace ~/test-workspace/my-skill \
    --static ~/test-workspace/my-skill/viewer.html

# Or run specific eval
python3 assertions.py --eval-id my-skill-basic \
    --output-dir ~/test-workspace/my-skill/eval-0-my-skill-basic/with_skill
```

### Step 5: Review Results
1. Open `viewer.html` in browser
2. Click prev/next to review each eval
3. Leave feedback (auto-saves)
4. Download `feedback.json`

### Step 6: Iterate
1. Read `feedback.json`
2. Identify improvements
3. Edit `SKILL.md` + `scripts/`
4. Run `update-skill.sh` again
5. Loop until `pass_rate >= 90%`

---

## 📊 Expected Output

### Run Tests Output
```
🚀 Running 1 eval(s) with Anthropics workflow
📁 Workspace: /home/claw/test-workspace/my-skill

🔍 Eval 1/1: my-skill-basic - Basic usage
   ✅ with_skill: .../with_skill
   ✅ baseline:   .../without_skill
   📊 Grading:    .../grading.json
   📋 Assertions: 2 passed

📊 Benchmark summary:
{
  "total_evals": 1,
  "total_with_skill_tokens": 2345,
  "total_baseline_tokens": 3456,
  "avg_token_savings": 1111
}
```

### Benchmark JSON
```json
{
  "skill_name": "my-skill",
  "evals": [{
    "id": "my-skill-basic",
    "name": "Basic usage",
    "with_skill_tokens": 2345,
    "baseline_tokens": 3456,
    "improvement": -1111
  }],
  "summary": {
    "total_evals": 1,
    "total_with_skill_tokens": 2345,
    "total_baseline_tokens": 3456,
    "avg_token_savings": 1111
  }
}
```

---

## 🎓 Best Practices

### 1. Start Simple
- 2-3 evals per skill (basic + edge + fail)
- Gradually expand to 10-20 as skill matures

### 2. Use Generic Assertions First
- `assertions.py` has generic checks that work for most skills
- Add eval-specific `check_<eval-id>()` only if needed

### 3. Compare Token Usage
- `with-skill` should use **fewer tokens** than `without-skill`
- If worse, refine your skill's instructions

### 4. Human Review is Key
- Pass rate alone is not enough
- Use `feedback.json` to catch "feels wrong" cases

---

## 🆚 Old vs New Workflow

| Step | Old | New |
|------|-----|-----|
| 1 | `init_skill.py` | ✅ Same |
| 2 | Write SKILL.md | ✅ Same (with tests section auto-added) |
| 3 | Test manually | ❌ `python3 run_tests.py` (parallel with-skill + baseline) |
| 4 | Manual grading | ✅ `assertions.py` → `grading.json` |
| 5 | No iteration loop | ✅ Loop with `update-skill.sh` |
| 6 | No benchmark | ✅ `benchmark.json` with pass rate, tokens |

---

## 📁 File Structure

```
.local-skill-creator/
└── scripts/
    ├── init_skill.py          (updated)
    ├── publish_skill.py       (unchanged)
    ├── quick_validate.py      (unchanged)
    ├── register_memos.py      (unchanged)
    ├── package_skill.py       (unchanged)
    ├── assertions.py          ✨ NEW
    ├── run_tests.py           ✨ NEW
    ├── update-skill.sh        ✨ NEW
    └── upgrade-local-skill-creator.sh  ✨ NEW
```

---

## 🚀 Quick Start

```bash
# 1. Upgrade local-skill-creator
./upgrade-local-skill-creator.sh

# 2. Create new skill with tests
python3 init_skill.py my-skill --description "do stuff"

# 3. Fill SKILL.md

# 4. Create evals/evals.json

# 5. Run Anthropics workflow
python3 run_tests.py \
    --skill-path ~/.openclaw/skills/my-skill \
    --static ~/test-workspace/my-skill/viewer.html

# 6. Review + submit feedback

# 7. Iterate with update-skill.sh
./update-skill.sh my-skill
```

---

## ✅ Benefits

1. **Faster Development**: Parallel runs (with-skill + baseline)
2. **Quantitative Analysis**: Token savings, pass rate
3. **Human-in-the-loop**: Feedback.json captures subjective judgment
4. **Reproducibility**: Each eval has eval_metadata.json
5. **One-command workflow**: `update-skill.sh`

---

> 💡 Tip: Add `--static viewer.html` for headless/CI environments  
> ✅ Recommended: `run_tests.py` + `assertions.py` + `update-skill.sh`
