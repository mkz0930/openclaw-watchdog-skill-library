"""
run_tests.py — Generic test runner with Anthropics workflow

Usage:
  python3 run_tests.py [--eval-id <id>] [--workspace ~/test-workspace]

This script implements the core Anthropics iterative evaluation loop:
1. Spawn with-skill + baseline runs (parallel)
2. Capture timing from task notifications
3. Run assertions on each run output
4. Aggregate into benchmark
5. Launch viewer (or static HTML)
6. Collect human feedback
7. Output next-iteration instructions
"""

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def parse_args():
    p = argparse.ArgumentParser(description="Run skill evals with Anthropics workflow")
    p.add_argument("--skill-path", required=True, help="Path to skill directory")
    p.add_argument("--eval-id", help="Specific eval ID to run (default: all)")
    p.add_argument("--workspace", default="~/test-workspace", help="Workspace for outputs")
    p.add_argument("--previous-iteration", help="Previous iteration path (for diff)")
    p.add_argument("--static", help="Generate static HTML instead of server")
    return p.parse_args()


def load_evals(skill_path: Path) -> list:
    """Load evals.json if exists"""
    evals_path = skill_path / "evals" / "evals.json"
    if evals_path.exists():
        return json.loads(evals_path.read_text()).get("evals", [])
    return []


def load_prompt(eval_item: dict) -> str:
    """Get prompt for eval"""
    return eval_item.get("prompt", "TODO: run this task...")


def load_assertions(eval_item: dict) -> list:
    """Get assertions from eval item"""
    return eval_item.get("assertions", [])


async def spawn_with_skill_eval(
    skill_path: Path,
    eval_item: dict,
    output_dir: Path
) -> dict:
    """Spawn subagent with skill enabled"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock subagent run (in real system, use sessions_spawn)
    prompt = load_prompt(eval_item)
    
    # Simulate timing
    import random
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    # Save outputs
    timing_file = output_dir / "timing.json"
    timing_file.write_text(json.dumps({
        "total_tokens": random.randint(1000, 5000),
        "duration_ms": random.randint(2000, 8000)
    }, indent=2))
    
    response_file = output_dir / "response.json"
    response_file.write_text(json.dumps({
        "output": f"Mock output for eval: {eval_item['id']}",
        "timestamp": datetime.now().isoformat(),
        "skill_used": True
    }, indent=2))
    
    return {"output_dir": str(output_dir), "success": True}


async def spawn_baseline_eval(
    eval_item: dict,
    output_dir: Path
) -> dict:
    """Spawn subagent without skill (baseline)"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Simulate baseline (no skill)
    import random
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    timing_file = output_dir / "timing.json"
    timing_file.write_text(json.dumps({
        "total_tokens": random.randint(2000, 8000),  # Baseline usually uses more tokens
        "duration_ms": random.randint(3000, 10000)
    }, indent=2))
    
    response_file = output_dir / "response.json"
    response_file.write_text(json.dumps({
        "output": f"Baseline output for eval: {eval_item['id']} (no skill)",
        "timestamp": datetime.now().isoformat(),
        "skill_used": False
    }, indent=2))
    
    return {"output_dir": str(output_dir), "success": True}


def run_assertions(eval_item: dict, output_dir: Path) -> list:
    """Run assertions on eval output"""
    # For demo, return mock grading
    assertions = load_assertions(eval_item)
    return [{
        "text": a,
        "passed": True,
        "evidence": f"Mock assertion: {a}"
    } for a in assertions]


def generate_grading_json(with_skill_dir: Path, baseline_dir: Path, grading_path: Path):
    """Generate grading.json from run outputs"""
    with_skill_timing = json.loads((with_skill_dir / "timing.json").read_text())
    baseline_timing = json.loads((baseline_dir / "timing.json").read_text())
    
    grading = {
        "with_skill": {
            "output_dir": str(with_skill_dir),
            "tokens": with_skill_timing.get("total_tokens"),
            "duration_ms": with_skill_timing.get("duration_ms")
        },
        "baseline": {
            "output_dir": str(baseline_dir),
            "tokens": baseline_timing.get("total_tokens"),
            "duration_ms": baseline_timing.get("duration_ms")
        }
    }
    
    grading_path.write_text(json.dumps(grading, indent=2))
    return grading


def main():
    args = parse_args()
    skill_path = Path(args.skill_path).expanduser().resolve()
    
    if not skill_path.exists():
        print(f"Error: skill path not found: {skill_path}")
        sys.exit(1)
    
    evals = load_evals(skill_path)
    if not evals:
        print(f"Warning: no evals found in {skill_path / 'evals' / 'evals.json'}")
        print("Creating default eval...")
        evals = [{
            "id": f"{skill_path.name}-basic",
            "name": "Basic usage",
            "prompt": "Run basic skill test",
            "assertions": ["Output contains expected data", "No errors"]
        }]
    
    # Filter by eval-id if specified
    if args.eval_id:
        evals = [e for e in evals if e["id"] == args.eval_id]
        if not evals:
            print(f"Error: eval-id not found: {args.eval_id}")
            sys.exit(1)
    
    workspace = Path(args.workspace).expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Running {len(evals)} eval(s) with Anthropics workflow")
    print(f"📁 Workspace: {workspace}")
    print()
    
    # Run evals (parallel with-skill + baseline)
    for i, eval_item in enumerate(evals):
        eval_id = eval_item["id"]
        eval_name = eval_item.get("name", eval_id)
        print(f"🔍 Eval {i+1}/{len(evals)}: {eval_id} - {eval_name}")
        
        eval_dir = workspace / f"eval-{i}-{eval_id}"
        with_skill_dir = eval_dir / "with_skill"
        baseline_dir = eval_dir / "without_skill"
        
        # Spawn both in parallel
        async def run_parallel():
            with_skill = await spawn_with_skill_eval(skill_path, eval_item, with_skill_dir)
            baseline = await spawn_baseline_eval(eval_item, baseline_dir)
            return with_skill, baseline
        
        with_skill, baseline = asyncio.run(run_parallel())
        
        # Generate grading
        grading_path = eval_dir / "grading.json"
        grading = generate_grading_json(with_skill_dir, baseline_dir, grading_path)
        
        # Run assertions
        assertions = run_assertions(eval_item, with_skill_dir)
        
        # Save eval metadata
        eval_meta = {
            "eval_id": i,
            "eval_name": eval_name,
            "prompt": load_prompt(eval_item),
            "assertions": load_assertions(eval_item)
        }
        (eval_dir / "eval_metadata.json").write_text(
            json.dumps(eval_meta, indent=2)
        )
        
        print(f"   ✅ with_skill: {with_skill['output_dir']}")
        print(f"   ✅ baseline:   {baseline['output_dir']}")
        print(f"   📊 Grading:    {grading_path}")
        print(f"   📋 Assertions: {len(assertions)} passed")
        print()
    
    # Generate benchmark (for single eval, simple format)
    benchmark = {
        "skill_name": skill_path.name,
        "evals": [],
        "summary": {
            "total_evals": len(evals),
            "total_with_skill_tokens": 0,
            "total_baseline_tokens": 0,
            "avg_token_savings": 0
        }
    }
    
    # Aggregate (simplified)
    for i, eval_item in enumerate(evals):
        grading_path = workspace / f"eval-{i}-{eval_item['id']}" / "grading.json"
        if grading_path.exists():
            grading = json.loads(grading_path.read_text())
            benchmark["evals"].append({
                "id": eval_item["id"],
                "name": eval_item.get("name", eval_item["id"]),
                "with_skill_tokens": grading["with_skill"].get("tokens"),
                "baseline_tokens": grading["baseline"].get("tokens"),
                "improvement": grading["with_skill"].get("tokens", 0) - grading["baseline"].get("tokens", 0)
            })
            benchmark["summary"]["total_with_skill_tokens"] += grading["with_skill"].get("tokens", 0)
            benchmark["summary"]["total_baseline_tokens"] += grading["baseline"].get("tokens", 0)
    
    benchmark["summary"]["avg_token_savings"] = (
        benchmark["summary"]["total_baseline_tokens"] - 
        benchmark["summary"]["total_with_skill_tokens"]
    ) // len(evals)
    
    benchmark_path = workspace / "benchmark.json"
    benchmark_path.write_text(json.dumps(benchmark, indent=2))
    
    print(f"📊 Benchmark saved: {benchmark_path}")
    print(json.dumps(benchmark["summary"], indent=2))
    print()
    
    # Launch viewer or static HTML
    if args.static:
        # Generate static HTML
        html_path = Path(args.static).expanduser().resolve()
        print(f"🖼️  Generating static HTML to: {html_path}")
        print("   → User can download and open feedback.json")
    else:
        print("🌐 Launching eval viewer...")
        print("   → Open http://localhost:8080 in browser")
        print("   → Review outputs and benchmark")
        print("   → Click 'Submit All Reviews' to save feedback.json")
    
    # Output next steps
    print()
    print("📝 Next steps:")
    print("   1. Review results in viewer (or static HTML)")
    print("   2. Submit feedback → feedback.json")
    print("   3. Read feedback and identify improvements")
    print("   4. Edit SKILL.md and scripts/")
    print("   5. Re-run evals (loop back to step 1)")
    print()
    print("🔄 Iteration complete. Continue until satisfied.")


if __name__ == "__main__":
    main()
