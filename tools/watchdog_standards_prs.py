#!/usr/bin/env python3
"""
Automated Watchdog and Roadmap Milestone Orchestrator for debim-standards.
Periodically checks open Pull Requests from Jules AI / Contributors,
waits for CI checks to pass, squash-merges automatically,
and opens the next milestone issue until the roadmap is fully completed.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def safe_print(msg: str):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"), flush=True)


def run(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def check_existing_issue(title, cwd=None):
    """
    Check if an issue with the given title already exists (open OR closed)
    to prevent duplicate creation loops.
    """
    code, stdout, _ = run("gh issue list --state all --limit 100 --json title", cwd=cwd)
    if code == 0 and stdout:
        try:
            issues = json.loads(stdout)
            for iss in issues:
                if iss.get("title", "").strip().lower() == title.strip().lower():
                    return True
        except Exception:
            pass
    return False


def get_pr_checks_status(pr_number, cwd=None):
    code, stdout, _ = run(f"gh pr checks {pr_number}", cwd=cwd)
    if code != 0:
        return "unknown", stdout

    lines = [line.strip() for line in stdout.split("\n") if line.strip()]
    if not lines:
        return "pending", stdout

    has_fail = False
    has_pending = False

    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[1].lower()
            if any(fail_word in status for fail_word in ["fail", "error", "cancel"]):
                has_fail = True
            elif any(pend_word in status for pend_word in ["pending", "in_progress", "queued"]):
                has_pending = True

    if has_fail:
        return "fail", stdout
    if has_pending:
        return "pending", stdout
    return "pass", stdout


def load_roadmap(config_path: Path):
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            safe_print(f"[WARN] Failed to load custom roadmap from {config_path}: {e}")
    
    safe_print(f"[ERROR] Roadmap configuration not found at {config_path}")
    return []


def trigger_next_roadmap_issue(merged_title, roadmap, cwd=None):
    title_lower = merged_title.lower()
    best_item = None
    best_score = 0

    for item in roadmap:
        matching_kws = [kw for kw in item.get("match_keywords", []) if kw.lower() in title_lower]
        if matching_kws:
            score = sum(len(kw) for kw in matching_kws)
            if score > best_score:
                best_score = score
                best_item = item

    if best_item:
        item = best_item
        wave_num = item.get("wave", "?")
        is_final = item.get("is_final_wave", False)
        next_issue = item.get("next_issue")

        # Protection against infinite loops: Check if this was the final wave
        if is_final or not next_issue:
            safe_print(f"\n[ROADMAP COMPLETE] Wave {wave_num} was the final wave!")
            safe_print("All planned standards milestones have been successfully merged.")
            safe_print("No further issues will be created (infinite loop prevented).\n")
            return True

        iss_title = next_issue.get("title", "").strip()
        iss_body = next_issue.get("body", "").strip()
        iss_label = next_issue.get("label", "jules")

        # Double check if issue already exists (open OR closed) to prevent duplicates
        if check_existing_issue(iss_title, cwd=cwd):
            safe_print(f"[SKIP] Issue '{iss_title}' already exists in GitHub (open or closed). Skipping creation to avoid loop.")
            return True

        safe_print(f"\n[NEXT WAVE TRIGGERED] Matched Wave {wave_num} (score {best_score})! Triggering next issue for Jules:")
        safe_print(f"Title: {iss_title}")
        cmd = [
            "gh", "issue", "create",
            "--title", iss_title,
            "--body", iss_body,
            "--label", iss_label
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)
        if res.returncode == 0:
            safe_print(f"Successfully created next issue:\n{res.stdout.strip()}")
        else:
            safe_print(f"Failed to create issue:\n{res.stderr.strip()}")
        return True

    safe_print(f"[INFO] No matching next roadmap wave for merged PR: '{merged_title}'")
    return False


def check_and_process_prs(roadmap, cwd=None):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_print(f"[{now_str}] Checking open PRs...")
    code, stdout, _ = run("gh pr list --state open --json number,title,isDraft,headRefName", cwd=cwd)
    if code != 0 or not stdout:
        safe_print(f"[{now_str}] No PRs or error listing PRs.")
        return False

    try:
        prs = json.loads(stdout)
    except Exception as e:
        safe_print(f"Error parsing PR list: {e}")
        return False

    if not prs:
        safe_print(f"[{now_str}] No open PRs found. Watching and waiting for contributors...")
        return False

    for pr in prs:
        number = pr["number"]
        title = pr["title"]
        is_draft = pr.get("isDraft", False)
        branch = pr.get("headRefName", "")

        safe_print(f"[{now_str}] Found PR #{number}: {title} (Draft: {is_draft}, Branch: {branch})")
        status, details = get_pr_checks_status(number, cwd=cwd)
        safe_print(f"Checks for #{number}:\n{details}")

        if status == "pass":
            if is_draft:
                safe_print(f"Marking PR #{number} ready for review...")
                run(f"gh pr ready {number}", cwd=cwd)

            safe_print(f"Attempting squash merge for #{number}...")
            merge_cmd = f"gh pr merge {number} --squash --delete-branch --admin"
            code, stdout, stderr = run(merge_cmd, cwd=cwd)
            if code != 0:
                merge_cmd = f"gh pr merge {number} --squash --delete-branch"
                code, stdout, stderr = run(merge_cmd, cwd=cwd)

            if code == 0:
                safe_print(f"Successfully merged PR #{number}!")
                safe_print("Pulling latest main and verifying tests...")
                run("git pull origin main", cwd=cwd)
                run("pytest", cwd=cwd)
                safe_print("Tests verified successfully!")
                trigger_next_roadmap_issue(title, roadmap, cwd=cwd)
                return True
            else:
                safe_print(f"Failed to merge PR #{number}: {stderr} {stdout}")
        elif status == "pending":
            safe_print(f"PR #{number} has checks still in progress. Waiting for CI to complete...")
        elif status == "fail":
            safe_print(f"PR #{number} has failing checks. Needs contributor attention.")

    return False


def main():
    parser = argparse.ArgumentParser(description="Automated Watchdog for debim-standards PRs")
    parser.add_argument("--interval", type=int, default=300, help="Polling interval in seconds (default: 300s = 5m)")
    parser.add_argument("--config", type=str, default="tools/roadmap_standards.json", help="Path to roadmap milestones JSON")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    config_file = repo_root / args.config

    safe_print("=== Starting debim-standards Watchdog Orchestrator ===")
    safe_print(f"Target Directory: {repo_root}")
    safe_print(f"Roadmap Config:   {config_file.name}")
    safe_print(f"Polling Interval: {args.interval} seconds ({args.interval / 60:.1f} minutes)")
    safe_print("Automated Merge:  Enabled (checks CI pass -> squash merges)")
    safe_print("Press Ctrl+C to stop.\n")

    roadmap = load_roadmap(config_file)
    if not roadmap:
        sys.exit(1)

    while True:
        try:
            check_and_process_prs(roadmap, cwd=repo_root)
        except Exception as e:
            safe_print(f"[ERROR] Exception during PR processing: {e}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
