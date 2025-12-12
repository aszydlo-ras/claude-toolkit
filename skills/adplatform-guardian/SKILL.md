---
name: adplatform-guardian
description: |
  MANDATORY code quality guardian for ALL Ringier Axel Springer repositories.
  This skill MUST be invoked AUTOMATICALLY whenever Claude Code makes ANY code changes (edits, writes, new files).
  Ensures CHANGELOG updates, test coverage, and code standards compliance.
  Auto-triggers on: Edit tool, Write tool, any code modification.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, TodoWrite
---

# AdPlatform Guardian - Universal Code Quality Enforcer

**CRITICAL: This skill enforces mandatory requirements for ALL code changes in RAS repositories.**

## Automatic Activation

This skill MUST be applied whenever:
- Using the `Edit` tool to modify code files
- Using the `Write` tool to create new code files
- Making any changes to: `.py`, `.js`, `.ts`, `.go`, `.java`, `.yaml`, `.json` files
- Working in ANY of these repositories:
  - `gdpr`, `gdpr-*` (GDPR/CMP ecosystem)
  - `adp-datalayer-api` (advertising library)
  - `adplatform`, `adplatform2` (ad platform)
  - Any other RAS repository

## MANDATORY Checklist - BEFORE Completing ANY Task

### 1. CHANGELOG.md Update (REQUIRED)

**Find the correct CHANGELOG:**
```
Repository Type          | CHANGELOG Location
-------------------------|------------------------------------------
adp-datalayer-api        | /CHANGELOG.md
gdpr-mobile-api          | /CHANGELOG.md
gdpr-popup               | /CHANGELOG.md
gdpr (cmp_coordinator)   | /src/python/adp/modes/cmp_coordinator/CHANGELOG.md
gdpr (other modes)       | /src/python/adp/modes/{mode_name}/CHANGELOG.md
adplatform2 projects     | /projects/{project_name}/CHANGELOG.md
```

**Format:**
```markdown
## [X.Y.Z] - YYYY-MM-DD
### Added|Changed|Fixed|Removed
- Description of change [@username]
```

**Version Bump Rules:**
- MAJOR (X): Breaking changes
- MINOR (Y): New features, backward compatible
- PATCH (Z): Bug fixes, small changes

### 2. Tests (REQUIRED)

**Find and run tests based on repository:**

| Repository | Test Location | Run Command |
|------------|---------------|-------------|
| `gdpr` | `tests/` | `tox` or `pytest` |
| `gdpr-mobile-api` | `tests/` | `tox` or `pytest` |
| `adp-datalayer-api` | `tests/unit/`, `tests/browser/` | `npm test` |
| `gdpr-popup` | `src/__tests__/` | `npm test` |
| `adplatform2` | `projects/*/tests/` | `sh test_me.sh` |

**If adding new functionality:**
- Add new test file or extend existing tests
- Cover edge cases and error scenarios

### 3. Code Standards (REQUIRED)

- [ ] All comments in English
- [ ] All function/variable names in English
- [ ] Type hints for Python functions
- [ ] JSDoc for JavaScript functions
- [ ] No hardcoded secrets/credentials
- [ ] No console.log/print statements (except logging)

## Repository-Specific Rules

### GDPR Repositories (`gdpr`, `gdpr-mobile-api`, `gdpr-popup`)

**Python (gdpr, gdpr-mobile-api):**
```bash
# Run tests
cd {repo} && tox

# Or with pytest directly
pytest tests/ -v
```

**JavaScript (gdpr-popup, adp-datalayer-api):**
```bash
# Run tests
npm test

# Run linting
npm run lint
```

### adp-datalayer-api

**Special requirements:**
- Follow `CLAUDE.md` instructions in the repo
- Use 4-space indentation
- Never use global variables directly (pass as parameters)
- Run `npm run lint` before commit

**CHANGELOG format follows Keep a Changelog:**
```markdown
## [6.43.0] - 2025-12-12
### Added
- Auto publication version threshold for CMP popup display [@aszydlo]
```

### gdpr-mobile-api

**CHANGELOG format:**
```markdown
## [4.2.0] - 2025-12-12
### Added
- Support for isAutomaticPublication flag in vendor list [@aszydlo]
```

## Verification Commands

Before marking task as complete, run:

```bash
# Check CHANGELOG was updated
grep -q "$(date +%Y-%m-%d)" {path_to_changelog}

# Run appropriate tests
# Python repos:
tox  # or pytest

# JavaScript repos:
npm test
npm run lint
```

## Final Checklist Template

Copy and verify before completing task:

```
## Pre-Completion Checklist
- [ ] CHANGELOG.md updated with new version and today's date
- [ ] Tests added/updated for new functionality
- [ ] Existing tests still pass
- [ ] No linting errors
- [ ] Comments and names in English
- [ ] No hardcoded secrets
- [ ] Type hints present (Python)
```

## Constraints

- **NEVER** complete a task without updating CHANGELOG
- **NEVER** skip running tests
- **NEVER** use Polish in code (comments, names, strings meant for developers)
- **NEVER** commit secrets or credentials
- **ALWAYS** bump version appropriately (major/minor/patch)
- **ALWAYS** include [@username] in CHANGELOG entries

## Example: Complete Feature Implementation

When user asks to implement a feature:

1. **Plan changes** - identify all files to modify
2. **Make code changes** - implement the feature
3. **Update CHANGELOG** - add entry with new version
4. **Add/update tests** - ensure coverage
5. **Run tests** - verify nothing is broken
6. **Report completion** - show checklist status
