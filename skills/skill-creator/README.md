# Skill Creator for Claude Code

Personal skill for creating and validating Claude Code skills.

## Structure

```
~/.claude/skills/skill-creator/
├── SKILL.md                           # Main instructions for Claude
├── scripts/
│   ├── init_skill.py                  # Initialize new skills
│   └── validate_skill.py              # Validate skill structure
├── references/
│   ├── output-patterns.md             # Output formatting patterns
│   ├── workflows.md                   # Workflow design patterns
│   └── claude-code-specifics.md       # Claude Code specific features
└── templates/                         # Reserved for future use
```

## Quick Start

### Create a new skill

```bash
# Personal skill (available in all projects)
python ~/.claude/skills/skill-creator/scripts/init_skill.py my-skill --scope personal

# Project skill (shared via git)
python ~/.claude/skills/skill-creator/scripts/init_skill.py team-skill --scope project

# Custom location
python ~/.claude/skills/skill-creator/scripts/init_skill.py custom-skill --scope personal --path ~/my-skills
```

### Validate a skill

```bash
python ~/.claude/skills/skill-creator/scripts/validate_skill.py ~/.claude/skills/my-skill
```

## Key Differences from API Version

This skill is optimized for **Claude Code CLI**, not the Anthropic API.

| Aspect | API (anthropic/skills) | This Version (Claude Code) |
|--------|------------------------|---------------------------|
| `package_skill.py` | Required for upload | **Removed** - not needed |
| `allowed-tools` | Not used | **Supported** with tool list |
| Locations | API upload only | Personal + Project paths |
| Validation | Basic | **Extended** - triggers, placeholders |
| References | Generic | **Claude Code specifics** added |

## Skill Locations

| Scope | Path | Use Case |
|-------|------|----------|
| Personal | `~/.claude/skills/<name>/` | Your workflows, available everywhere |
| Project | `.claude/skills/<name>/` | Team skills, shared via git |

## SKILL.md Format

```yaml
---
name: my-skill-name                    # Required: max 64 chars, hyphen-case
description: What it does + triggers   # Required: max 1024 chars, include "Use when..."
allowed-tools: Read, Write, Bash       # Optional: restrict available tools
---

# Skill Title

## Quick Start
[Immediate actionable steps]

## Instructions
[Clear guidance for Claude]

## Examples
[Concrete input/output pairs]
```

## Available Tools for `allowed-tools`

```
Read, Write, Edit, MultiEdit, Bash, Glob, Grep,
WebFetch, WebSearch, Task, TodoWrite, AskUserQuestion, NotebookEdit
```

## References

- `references/output-patterns.md` - Strict vs flexible templates, example patterns
- `references/workflows.md` - Sequential, conditional, iterative workflows
- `references/claude-code-specifics.md` - Auto-loading, allowed-tools, project vs personal

## Validation Checks

The validator checks for:
- ✓ Valid hyphen-case name (max 64 chars)
- ✓ Description present (max 1024 chars)
- ✓ Trigger phrases in description
- ✓ No placeholder text remaining
- ✓ Body under 5000 tokens / 500 lines
- ✓ Examples section present
- ✓ No hardcoded secrets in scripts
- ✓ Directory name matches skill name

## Version

- **v1.0.0** (2024-12): Initial release for Claude Code CLI
