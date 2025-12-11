# Claude Code Specifics

Features and behaviors unique to Claude Code CLI that differ from API-based skills.

## Auto-Loading Behavior

Skills are automatically loaded when Claude Code starts. No manual invocation needed.

### Loading Process

1. **Startup**: Claude Code scans skill directories
2. **Metadata**: Reads `name` and `description` from all SKILL.md files (~100 tokens each)
3. **Invocation**: When Claude determines skill is relevant, loads full SKILL.md body
4. **Resources**: Scripts/references loaded only during execution

### Skill Locations

| Scope | Path | Use Case |
|-------|------|----------|
| Personal | `~/.claude/skills/<name>/` | Your workflows, available everywhere |
| Project | `.claude/skills/<name>/` | Team skills, shared via git |

Personal skills load first, project skills can override.

## The `allowed-tools` Field

**Claude Code exclusive** - restricts which tools Claude can use when skill is active.

### Syntax

```yaml
---
name: read-only-analyzer
description: Analyze code without modifications
allowed-tools: Read, Glob, Grep
---
```

### Available Tools

| Tool | Purpose |
|------|---------|
| `Read` | Read file contents |
| `Write` | Create new files |
| `Edit` | Modify existing files |
| `MultiEdit` | Multiple edits in one file |
| `Bash` | Execute shell commands |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents |
| `WebFetch` | Fetch URL content |
| `WebSearch` | Search the web |
| `Task` | Launch sub-agents |
| `TodoWrite` | Manage task lists |
| `AskUserQuestion` | Prompt user for input |
| `NotebookEdit` | Edit Jupyter notebooks |

### Use Cases

**Read-only analysis**:
```yaml
allowed-tools: Read, Glob, Grep
```

**Documentation generation**:
```yaml
allowed-tools: Read, Write, Glob, Grep
```

**Full automation**:
```yaml
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
```

**Safe exploration**:
```yaml
allowed-tools: Read, Glob, Grep, WebFetch, WebSearch
```

## Skill vs Slash Command

| Feature | Skill | Slash Command |
|---------|-------|---------------|
| Invocation | Automatic (model decides) | Manual (`/command`) |
| Trigger | Based on description | Explicit user action |
| Scope | Domain expertise | Specific action |
| Complexity | Can be extensive | Usually simple |
| Best for | Specialized workflows | Quick actions |

### When to Use Which

**Use Skill when**:
- Claude should automatically recognize when to apply expertise
- Domain knowledge should be available implicitly
- Multi-step workflows need consistent handling

**Use Slash Command when**:
- User wants explicit control
- Action is discrete and one-time
- No automatic triggering needed

## Project vs Personal Skills

### Personal Skills (`~/.claude/skills/`)

```
~/.claude/skills/
├── my-workflow/
│   └── SKILL.md
└── personal-helper/
    └── SKILL.md
```

- Available in all projects
- Private to you
- Not version controlled with projects
- Good for: personal preferences, universal tools

### Project Skills (`.claude/skills/`)

```
project/
└── .claude/
    └── skills/
        └── project-specific/
            └── SKILL.md
```

- Available only in this project
- Shared via git with team
- Version controlled
- Good for: team standards, project-specific knowledge

## Integration with CLAUDE.md

Skills complement `CLAUDE.md` project instructions:

| File | Purpose | Scope |
|------|---------|-------|
| `CLAUDE.md` | Project-wide instructions | Always active |
| `SKILL.md` | Domain expertise | Active when triggered |

### Example Interaction

`CLAUDE.md`:
```markdown
# Project Instructions
- Use TypeScript for all code
- Follow ESLint rules
```

`skills/api-design/SKILL.md`:
```yaml
---
name: api-design
description: Design REST APIs following company standards. Use for API design, endpoint planning, or schema work.
---
# API Design Standards
[Detailed API patterns...]
```

Claude uses both: general rules from CLAUDE.md + specialized API knowledge when designing endpoints.

## Script Execution

Scripts in `scripts/` directory execute via Bash tool.

### Best Practices

```python
#!/usr/bin/env python3
"""
Script description.
Usage: python script.py <args>
"""

import sys
import argparse

def main():
    # Use argparse for clear interface
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    args = parser.parse_args()

    # Output to stdout for Claude to capture
    print(f"Result: {process(args.input)}")

if __name__ == "__main__":
    main()
```

### Execution Pattern in SKILL.md

```markdown
## Usage

To process data, run:
```bash
python ~/.claude/skills/my-skill/scripts/processor.py <input>
```

The script outputs JSON that can be used for further analysis.
```

## Debugging Skills

### Skill Not Loading

1. Check path: `ls ~/.claude/skills/` or `ls .claude/skills/`
2. Verify SKILL.md exists and has valid frontmatter
3. Restart Claude Code to reload skills

### Skill Not Triggering

1. Check description includes trigger phrases
2. Description must explain WHEN to use, not just WHAT it does
3. Try more specific trigger keywords

### Validation

Run validator to check structure:
```bash
python ~/.claude/skills/skill-creator/scripts/validate_skill.py <path>
```

## Token Optimization

Claude Code skills should be lean. Optimization strategies:

### Progressive Disclosure

```
skill/
├── SKILL.md          # Overview + navigation (~500 tokens)
└── references/
    ├── api-spec.md   # Loaded only when needed
    ├── examples.md   # Loaded only when needed
    └── advanced.md   # Loaded only when needed
```

### Reference Instead of Embed

❌ Bad (bloats SKILL.md):
```markdown
## API Documentation
[500 lines of API docs]
```

✓ Good (loads on demand):
```markdown
## API Documentation
See `references/api-spec.md` for complete API documentation.
```

### Concise Instructions

❌ Bad:
```markdown
When you need to analyze code for potential security vulnerabilities,
you should carefully examine each function and look for common patterns
that might indicate security issues such as...
```

✓ Good:
```markdown
## Security Analysis
Check for: SQL injection, XSS, command injection, path traversal.
See `references/security-checklist.md` for patterns.
```
