#!/usr/bin/env python3
"""
assertions.py — Generic assertion runner for skills

Usage:
  python3 assertions.py --eval-id <id> --output-dir <path>

Generic assertions (apply to most skills):
- Output file exists
- JSON structure valid (if applicable)
- No error in logs
- Timing data captured
"""

import argparse
import json
import re
from pathlib import Path


def check_output_exists(outputs_dir: Path) -> dict:
    """Check if any output files were created"""
    files = list(outputs_dir.glob("*"))
    passed = len(files) > 0
    evidence = f"Output files: {[f.name for f in files]}"
    return {
        "text": "Output files created",
        "passed": passed,
        "evidence": evidence
    }


def check_json_valid(outputs_dir: Path) -> dict:
    """Check if JSON outputs are valid"""
    json_files = list(outputs_dir.glob("*.json"))
    errors = []
    for f in json_files:
        try:
            json.loads(f.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{f.name}: {e}")
    
    passed = len(errors) == 0
    evidence = f"JSON files: {len(json_files)}, errors: {errors or 'None'}"
    return {
        "text": "JSON outputs valid",
        "passed": passed,
        "evidence": evidence
    }


def check_no_error_logs(outputs_dir: Path) -> dict:
    """Check if error patterns in logs"""
    log_files = list(outputs_dir.glob("*.txt")) + list(outputs_dir.glob("*.log"))
    error_patterns = ["error", "Exception", "Traceback", "404", "timeout", "failed"]
    
    for f in log_files:
        content = f.read_text().lower()
        for pattern in error_patterns:
            if pattern in content:
                return {
                    "text": "No errors in logs",
                    "passed": False,
                    f"evidence": f"Found '{pattern}' in {f.name}"
                }
    
    return {
        "text": "No errors in logs",
        "passed": True,
        "evidence": "Logs checked, no error patterns found"
    }


def check_timing_captured(outputs_dir: Path) -> dict:
    """Check if timing.json exists with required fields"""
    timing_file = outputs_dir / "timing.json"
    if not timing_file.exists():
        return {
            "text": "Timing data captured",
            "passed": False,
            "evidence": "timing.json not found"
        }
    
    try:
        data = json.loads(timing_file.read_text())
        required = ["total_tokens", "duration_ms"]
        missing = [k for k in required if k not in data]
        if missing:
            return {
                "text": "Timing data captured",
                "passed": False,
                "evidence": f"Missing fields: {missing}"
            }
        return {
            "text": "Timing data captured",
            "passed": True,
            "evidence": f"tokens={data.get('total_tokens')}, duration={data.get('duration_ms')}ms"
        }
    except json.JSONDecodeError:
        return {
            "text": "Timing data captured",
            "passed": False,
            "evidence": "timing.json invalid JSON"
        }


def run_generic_assertions(outputs_dir: Path) -> list:
    """Run all generic assertions"""
    checkers = [
        check_output_exists,
        check_json_valid,
        check_no_error_logs,
        check_timing_captured,
    ]
    
    return [checker(outputs_dir) for checker in checkers]


def main():
    p = argparse.ArgumentParser(description="Run generic skill assertions")
    p.add_argument("--eval-id", required=True, help="eval ID")
    p.add_argument("--output-dir", required=True, help="run output directory")
    p.add_argument("--all", action="store_true", help="Run all generic checks")
    args = p.parse_args()
    
    output_dir = Path(args.output_dir)
    
    if args.all:
        results = run_generic_assertions(output_dir)
    else:
        # Custom check per eval-id
        func_name = f"check_{args.eval_id}"
        checker = globals().get(func_name, check_output_exists)
        results = [checker(output_dir)]
    
    # Save grading.json
    grading_path = output_dir.parent / "grading.json"
    grading_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    
    print(f"Grading results saved to {grading_path}")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
