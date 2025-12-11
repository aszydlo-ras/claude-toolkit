#!/usr/bin/env python3
"""
Check and optionally clone required repositories for activity/conversions flow.
Uses GitHub CLI (gh) for cloning.

Usage:
    python check_repos.py [--auto-clone] [--workspace /path/to/workspace]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

REQUIRED_REPOS = {
    "adplatform": {
        "github": "Ringier-Axel-Springer-PL/adplatform",
        "description": "Main monorepo with emission handlers, modes, events API",
        "key_paths": [
            "src/python/emission/csr/activity.py",
            "src/python/emission/csr/adclick.py",
            "src/python/adp/modes/adp_activity/",
            "src/python/adp_events_api/",
        ],
    },
    "datalayer-api": {
        "github": "Ringier-Axel-Springer-PL/adp-datalayer-api",
        "description": "Ad request and display layer",
        "key_paths": [],
    },
    "adp-ecommerce-pixel": {
        "github": "Ringier-Axel-Springer-PL/adp-ecommerce-pixel",
        "description": "Client-side ecommerce tracking pixel",
        "key_paths": [],
    },
}


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
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    print(f"Workspace: {workspace}\n")

    if not args.check_only and not check_gh_cli():
        print("Error: GitHub CLI (gh) not found or not authenticated.")
        print("Install: https://cli.github.com/")
        print("Authenticate: gh auth login")
        sys.exit(1)

    missing = []
    present = []

    for repo_name, info in REQUIRED_REPOS.items():
        if repo_exists(workspace, repo_name):
            present.append(repo_name)
            print(f"[OK] {repo_name}")
        else:
            missing.append(repo_name)
            print(f"[MISSING] {repo_name} - {info['description']}")

    if not missing:
        print("\nAll required repositories are present.")
        return 0

    if args.check_only:
        print(f"\n{len(missing)} repository(ies) missing.")
        return 1

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
