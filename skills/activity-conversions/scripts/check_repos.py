#!/usr/bin/env python3
"""
Check and optionally clone required repositories for activity/conversions flow.
Uses GitHub CLI (gh) for cloning.

Usage:
    python check_repos.py [--auto-clone] [--workspace /path/to/workspace]
    python check_repos.py --task debugging
    python check_repos.py --task pixel-modification --auto-clone
    python check_repos.py --repo adplatform --check-only
    python check_repos.py --json
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

REQUIRED_REPOS: Dict[str, dict] = {
    "adplatform": {
        "github": "Ringier-Axel-Springer-PL/adplatform",
        "description": "Main monorepo with emission handlers, modes, events API",
        "tasks": ["schema-change", "attribution-logic", "debugging", "reports", "pixel-modification"],
        "key_paths": [
            "src/python/emission/csr/activity.py",
            "src/python/emission/csr/adclick.py",
            "src/python/emission/csr/tracking.py",
            "src/python/adp/modes/adp_activity/",
            "src/python/adp_events_api/",
        ],
    },
    "datalayer-api": {
        "github": "Ringier-Axel-Springer-PL/adp-datalayer-api",
        "description": "Ad request and display layer",
        "tasks": ["debugging"],
        "key_paths": [],
    },
    "adp-ecommerce-pixel": {
        "github": "Ringier-Axel-Springer-PL/adp-ecommerce-pixel",
        "description": "Client-side ecommerce tracking pixel",
        "tasks": ["pixel-modification", "debugging"],
        "key_paths": [
            "src/modules/activity/",
            "src/pixel.ts",
        ],
    },
    "adp-reports-defs": {
        "github": "Ringier-Axel-Springer-PL/adp-reports-defs",
        "description": "Druid datasource definitions for reports",
        "tasks": ["schema-change", "reports"],
        "key_paths": ["defs/"],
    },
    "data-lake-glue-datasources": {
        "github": "Ringier-Axel-Springer-PL/data-lake-glue-datasources",
        "description": "AWS Glue JSON schemas for DataLake",
        "tasks": ["schema-change"],
        "key_paths": ["json_schemas/adp/"],
    },
    "eks-ns-adp": {
        "github": "Ringier-Axel-Springer-PL/eks-ns-adp",
        "description": "K8s configs, fluent.conf for Kinesis routing",
        "tasks": ["deployment", "schema-change"],
        "key_paths": ["c2a/fluentd-kinesis/"],
    },
}

VALID_TASKS = [
    "schema-change",
    "pixel-modification",
    "attribution-logic",
    "debugging",
    "reports",
    "deployment",
]


def check_gh_cli() -> bool:
    """Check if GitHub CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def repo_exists(workspace: Path, repo_name: str) -> bool:
    """Check if repository exists in workspace."""
    repo_path = workspace / repo_name
    return repo_path.is_dir() and (repo_path / ".git").is_dir()


def clone_repo(workspace: Path, repo_name: str, github_path: str) -> bool:
    """Clone repository using GitHub CLI."""
    try:
        result = subprocess.run(
            ["gh", "repo", "clone", github_path, str(workspace / repo_name)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  Successfully cloned {repo_name}")
            return True
        else:
            print(f"  Error cloning {repo_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"  Exception cloning {repo_name}: {e}")
        return False


def prompt_clone(repo_name: str, description: str) -> bool:
    """Prompt user for confirmation to clone."""
    print(f"\nRepository '{repo_name}' is required but not found locally.")
    print(f"  Purpose: {description}")
    response = input(f"Clone it? [y/N]: ").strip().lower()
    return response in ("y", "yes")


def filter_repos_by_task(task: Optional[str]) -> Dict[str, dict]:
    """Filter repositories by task type."""
    if task is None or task == "all":
        return REQUIRED_REPOS
    return {
        name: info
        for name, info in REQUIRED_REPOS.items()
        if task in info.get("tasks", [])
    }


def filter_repos_by_name(repo_name: str) -> Dict[str, dict]:
    """Filter to a specific repository by name."""
    if repo_name in REQUIRED_REPOS:
        return {repo_name: REQUIRED_REPOS[repo_name]}
    return {}


def get_repo_status(workspace: Path, repos: Dict[str, dict]) -> Dict[str, dict]:
    """Get status of all repositories."""
    status = {}
    for repo_name, info in repos.items():
        exists = repo_exists(workspace, repo_name)
        repo_path = workspace / repo_name if exists else None
        status[repo_name] = {
            "exists": exists,
            "path": str(repo_path) if repo_path else None,
            "github": info["github"],
            "description": info["description"],
            "tasks": info.get("tasks", []),
            "key_paths": info.get("key_paths", []),
        }
    return status


def output_json(status: Dict[str, dict], workspace: Path) -> None:
    """Output status as JSON."""
    output = {
        "workspace": str(workspace),
        "repositories": status,
        "summary": {
            "total": len(status),
            "present": sum(1 for s in status.values() if s["exists"]),
            "missing": sum(1 for s in status.values() if not s["exists"]),
        },
    }
    print(json.dumps(output, indent=2))


def output_text(status: Dict[str, dict], workspace: Path) -> List[str]:
    """Output status as human-readable text. Returns list of missing repos."""
    print(f"Workspace: {workspace}\n")

    missing = []
    for repo_name, info in status.items():
        if info["exists"]:
            print(f"[OK] {repo_name}")
            if info["key_paths"]:
                for kp in info["key_paths"][:2]:  # Show max 2 key paths
                    print(f"     └─ {kp}")
        else:
            missing.append(repo_name)
            print(f"[MISSING] {repo_name} - {info['description']}")
            print(f"           Tasks: {', '.join(info['tasks'])}")

    return missing


def main():
    parser = argparse.ArgumentParser(
        description="Check and clone required repositories for activity/conversions flow"
    )
    parser.add_argument(
        "--auto-clone",
        action="store_true",
        help="Clone missing repos without prompting",
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=os.getcwd(),
        help="Workspace directory (default: current directory)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check, don't offer to clone",
    )
    parser.add_argument(
        "--task",
        type=str,
        choices=VALID_TASKS + ["all"],
        help="Filter repos by task type (e.g., debugging, pixel-modification, schema-change)",
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="Check/clone specific repo only",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON for programmatic use",
    )
    parser.add_argument(
        "--list-tasks",
        action="store_true",
        help="List available task types and exit",
    )
    args = parser.parse_args()

    # Handle --list-tasks
    if args.list_tasks:
        print("Available task types:")
        for task in VALID_TASKS:
            repos = filter_repos_by_task(task)
            repo_names = ", ".join(repos.keys())
            print(f"  {task}: {repo_names}")
        return 0

    workspace = Path(args.workspace).resolve()

    # Filter repos based on arguments
    if args.repo:
        repos = filter_repos_by_name(args.repo)
        if not repos:
            print(f"Error: Unknown repository '{args.repo}'")
            print(f"Available repos: {', '.join(REQUIRED_REPOS.keys())}")
            return 1
    elif args.task:
        repos = filter_repos_by_task(args.task)
    else:
        repos = REQUIRED_REPOS

    # Get status
    status = get_repo_status(workspace, repos)

    # JSON output mode
    if args.json_output:
        output_json(status, workspace)
        missing_count = sum(1 for s in status.values() if not s["exists"])
        return 0 if missing_count == 0 else 1

    # Text output mode
    missing = output_text(status, workspace)

    if not missing:
        print("\nAll required repositories are present.")
        return 0

    if args.check_only:
        print(f"\n{len(missing)} repository(ies) missing.")
        return 1

    # Check gh CLI before cloning
    if not check_gh_cli():
        print("\nError: GitHub CLI (gh) not found or not authenticated.")
        print("Install: https://cli.github.com/")
        print("Authenticate: gh auth login")
        sys.exit(1)

    print(f"\n{len(missing)} repository(ies) missing.")

    cloned = 0
    for repo_name in missing:
        info = REQUIRED_REPOS[repo_name]
        should_clone = args.auto_clone or prompt_clone(repo_name, info["description"])

        if should_clone:
            print(f"Cloning {repo_name}...")
            if clone_repo(workspace, repo_name, info["github"]):
                cloned += 1

    print(f"\nSummary: {cloned}/{len(missing)} repositories cloned.")
    return 0 if cloned == len(missing) else 1


if __name__ == "__main__":
    sys.exit(main())
