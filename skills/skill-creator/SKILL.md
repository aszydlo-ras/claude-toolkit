---
name: skill-creator
description: Guide for creating Claude Code skills. Use when user wants to create, update, or improve a skill that extends Claude's capabilities. Triggers: "create skill", "new skill", "build skill", "skill for", "extend Claude with".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Skill Creator for Claude Code

Create modular capability packages that extend Claude's functionality through specialized knowledge, workflows, and tool integrations.

## Quick Start

1. Run `python ~/.claude/skills/skill-creator/scripts/init_skill.py <skill-name> --scope <personal|project>`
2. Edit generated `SKILL.md` with domain-specific instructions
3. Validate with `python ~/.claude/skills/skill-creator/scripts/validate_skill.py <path>`
4. Skill auto-loads on next Claude Code session

## Core Principles

### The Context Window is a Public Good
Every token must earn its place. Before adding content, ask: "Does Claude already know this?" If yes, omit it. A 50-token example beats a 150-token explanation.

### Three Levels of Freedom

| Level | When to Use | Example |
|-------|-------------|---------|
| **High** | Flexible approaches, creative tasks | "Use appropriate formatting for the context" |
| **Medium** | Preferred patterns with variation | "Follow this structure, adapt details as needed" |
| **Low** | Error-prone operations, exact commands | "Run EXACTLY: `cmd --flag value`" |

Match specificity to task fragility. More critical = less freedom.

## Skill Anatomy

```
skill-name/
├── SKILL.md              # Required: frontmatter + instructions
├── scripts/              # Optional: executable Python/Bash
│   └── helper.py
├── references/           # Optional: domain documentation
│   └── api-spec.md
├── templates/            # Optional: output templates
└── assets/               # Optional: binary files
```

### SKILL.md Structure

```yaml
---
name: my-skill-name                    # Required: max 64 chars, hyphen-case
description: What it does + triggers   # Required: max 1024 chars
allowed-tools: Read, Write, Bash       # Optional: Claude Code specific
license: MIT                           # Optional
---

# Skill Title

## Quick Start
[Immediate actionable steps]

## Instructions
[Clear guidance for Claude]

## Examples
[Concrete input/output pairs]

## Constraints
[What NOT to do]
```

## Writing Effective Descriptions

The description determines if Claude invokes your skill. Include:
1. **What** the skill does (capabilities)
2. **When** to use it (trigger phrases)

### Good Examples
```yaml
description: Extract and analyze data from PDF files including forms, tables, and text. Use when working with PDFs, filling forms, or extracting document content.

description: Generate git commit messages by analyzing staged changes. Use when user asks for commit message help or runs "git diff --staged".

description: Query ACME's data warehouse for business metrics. Use for revenue analysis, customer segments, ARR calculations, or product usage data.
```

### Bad Examples
```yaml
description: Helps with documents.           # Too vague, no triggers
description: A useful skill for data.        # No specificity
description: Does many things with files.    # No clear purpose
```

## Workflow Patterns

See `references/workflows.md` for detailed patterns:
- **Sequential**: Ordered steps with clear progression
- **Conditional**: Branching logic with decision points
- **Iterative**: Loops with validation checkpoints

## Output Patterns

See `references/output-patterns.md` for:
- **Strict templates**: For APIs, data formats (zero variation)
- **Flexible templates**: For content with adaptation allowed
- **Example-driven**: Input/output pairs over descriptions

## Claude Code Specifics

See `references/claude-code-specifics.md` for:
- `allowed-tools` configuration
- Auto-loading behavior
- Personal vs project skills
- Integration with slash commands

## Validation Checklist

Before finalizing, verify:
- [ ] Name: lowercase, hyphen-case, max 64 chars
- [ ] Description: max 1024 chars, includes triggers
- [ ] Body: under 5000 tokens (~500 lines)
- [ ] No hardcoded secrets or credentials
- [ ] Examples are concrete and testable
- [ ] Instructions use appropriate freedom level

Run: `python ~/.claude/skills/skill-creator/scripts/validate_skill.py <skill-path>`

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Fix |
|--------------|--------------|-----|
| Mega-skills | Too broad, token waste | Split into focused skills |
| Vague descriptions | Claude won't invoke | Add specific triggers |
| Explaining basics | Claude already knows | Only add novel info |
| Missing examples | Unclear expectations | Add input/output pairs |
| Hardcoded paths | Not portable | Use relative paths or params |

## Skill Creation Workflow

```
1. UNDERSTAND
   └─> Gather concrete examples of desired behavior

2. PLAN
   └─> Identify: triggers, instructions, resources needed

3. INITIALIZE
   └─> Run init_skill.py to scaffold structure

4. WRITE
   └─> Fill SKILL.md, add scripts/references as needed

5. VALIDATE
   └─> Run validate_skill.py, fix issues

6. TEST
   └─> Use skill in real scenarios, iterate
```

## Version History
- v1.0.0 (2024-12): Initial release for Claude Code CLI
