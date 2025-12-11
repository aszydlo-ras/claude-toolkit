#!/usr/bin/env python3
"""
Initialize a new Claude Code skill with proper structure.

Usage:
    python init_skill.py <skill-name> --scope <personal|project> [--path <custom-path>]

Examples:
    python init_skill.py pdf-analyzer --scope personal
    python init_skill.py code-reviewer --scope project
    python init_skill.py my-skill --scope personal --path ~/custom/location
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional


# === TEMPLATES ===

SKILL_MD_TEMPLATE = '''---
name: {skill_name}
description: [REQUIRED] Describe what this skill does AND when Claude should use it. Include trigger phrases. Max 1024 chars.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# {skill_title}

[Brief description of the skill's purpose]

## Quick Start

1. [First step to use this skill]
2. [Second step]
3. [Third step]

## Instructions

### When to Use
- [Trigger condition 1]
- [Trigger condition 2]

### How It Works
[Explain the workflow Claude should follow]

### Constraints
- [What NOT to do]
- [Limitations to be aware of]

## Examples

### Example 1: [Scenario Name]
**Input:**
```
[Example user request]
```

**Output:**
```
[Expected Claude response/action]
```

### Example 2: [Scenario Name]
**Input:**
```
[Example user request]
```

**Output:**
```
[Expected Claude response/action]
```

## Version History
- v1.0.0 ({date}): Initial release
'''

EXAMPLE_SCRIPT_TEMPLATE = '''#!/usr/bin/env python3
"""
Helper script for {skill_title}.

Usage:
    python {script_name} <args>
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="{skill_title} helper")
    parser.add_argument("input", help="Input to process")
    args = parser.parse_args()

    # TODO: Implement functionality
    print(f"Processing: {{args.input}}")


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE_TEMPLATE = '''# {skill_title} Reference

## Overview
[Detailed documentation for the skill domain]

## Key Concepts
- **Concept 1**: [Explanation]
- **Concept 2**: [Explanation]

## API Reference
[If applicable, document any APIs or interfaces]

## Troubleshooting
| Issue | Solution |
|-------|----------|
| [Common problem] | [How to fix] |
'''

GITKEEP_CONTENT = '''# This directory contains [describe contents]
# Add your files here
'''


def validate_skill_name(name: str) -> tuple[bool, str]:
    """Validate skill name according to spec."""
    if not name:
        return False, "Skill name cannot be empty"

    if len(name) > 64:
        return False, f"Skill name must be max 64 characters (got {len(name)})"

    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        return False, "Skill name must be hyphen-case (lowercase letters, numbers, hyphens only, no leading/trailing/consecutive hyphens)"

    forbidden = ['claude', 'anthropic']
    for word in forbidden:
        if word in name.lower():
            return False, f"Skill name cannot contain '{word}'"

    return True, "Valid"


def to_title_case(skill_name: str) -> str:
    """Convert hyphen-case to Title Case."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def get_skill_path(skill_name: str, scope: str, custom_path: Optional[str] = None) -> Path:
    """Determine the skill installation path."""
    if custom_path:
        return Path(custom_path).expanduser() / skill_name

    if scope == 'personal':
        return Path.home() / '.claude' / 'skills' / skill_name
    else:  # project
        return Path.cwd() / '.claude' / 'skills' / skill_name


def create_skill(skill_name: str, scope: str, custom_path: Optional[str] = None) -> Path:
    """Create a new skill with proper structure."""
    from datetime import date

    skill_path = get_skill_path(skill_name, scope, custom_path)
    skill_title = to_title_case(skill_name)
    today = date.today().strftime("%Y-%m")

    if skill_path.exists():
        raise FileExistsError(f"Skill already exists at: {skill_path}")

    # Create directory structure
    skill_path.mkdir(parents=True, exist_ok=True)
    (skill_path / 'scripts').mkdir(exist_ok=True)
    (skill_path / 'references').mkdir(exist_ok=True)
    (skill_path / 'templates').mkdir(exist_ok=True)

    # Write SKILL.md
    skill_md = SKILL_MD_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title,
        date=today
    )
    (skill_path / 'SKILL.md').write_text(skill_md)

    # Write example script
    script_content = EXAMPLE_SCRIPT_TEMPLATE.format(
        skill_title=skill_title,
        script_name='helper.py'
    )
    script_path = skill_path / 'scripts' / 'helper.py'
    script_path.write_text(script_content)
    script_path.chmod(0o755)

    # Write example reference
    reference_content = EXAMPLE_REFERENCE_TEMPLATE.format(skill_title=skill_title)
    (skill_path / 'references' / 'reference.md').write_text(reference_content)

    # Write .gitkeep for templates
    (skill_path / 'templates' / '.gitkeep').write_text(GITKEEP_CONTENT)

    return skill_path


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new Claude Code skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s pdf-analyzer --scope personal
  %(prog)s code-reviewer --scope project
  %(prog)s my-skill --scope personal --path ~/my-skills
        """
    )
    parser.add_argument(
        'skill_name',
        help="Skill name in hyphen-case (e.g., 'pdf-analyzer')"
    )
    parser.add_argument(
        '--scope',
        choices=['personal', 'project'],
        required=True,
        help="'personal' (~/.claude/skills/) or 'project' (./.claude/skills/)"
    )
    parser.add_argument(
        '--path',
        help="Custom path to create skill (overrides --scope location)"
    )

    args = parser.parse_args()

    # Validate skill name
    is_valid, message = validate_skill_name(args.skill_name)
    if not is_valid:
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)

    # Create skill
    try:
        skill_path = create_skill(args.skill_name, args.scope, args.path)
        print(f"✓ Skill '{args.skill_name}' created at: {skill_path}")
        print()
        print("Next steps:")
        print(f"  1. Edit {skill_path / 'SKILL.md'} - fill in description and instructions")
        print(f"  2. Add scripts to {skill_path / 'scripts'} if needed")
        print(f"  3. Add references to {skill_path / 'references'} if needed")
        print(f"  4. Validate: python ~/.claude/skills/skill-creator/scripts/validate_skill.py {skill_path}")
        print(f"  5. Restart Claude Code to load the skill")
    except FileExistsError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error creating skill: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
