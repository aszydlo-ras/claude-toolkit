#!/usr/bin/env python3
"""
Validate a Claude Code skill structure and content.

Usage:
    python validate_skill.py <skill-path>

Examples:
    python validate_skill.py ~/.claude/skills/my-skill
    python validate_skill.py .claude/skills/project-skill
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


class ValidationError:
    def __init__(self, level: str, message: str, fix: Optional[str] = None):
        self.level = level  # 'error' or 'warning'
        self.message = message
        self.fix = fix

    def __str__(self):
        icon = "✗" if self.level == "error" else "⚠"
        result = f"{icon} [{self.level.upper()}] {self.message}"
        if self.fix:
            result += f"\n  Fix: {self.fix}"
        return result


class SkillValidator:
    ALLOWED_FRONTMATTER_KEYS = {
        'name', 'description', 'license', 'allowed-tools', 'metadata',
        'model', 'disable-model-invocation'
    }

    VALID_TOOLS = {
        'Read', 'Write', 'Edit', 'MultiEdit', 'Bash', 'Glob', 'Grep',
        'WebFetch', 'WebSearch', 'Task', 'TodoWrite', 'AskUserQuestion',
        'NotebookEdit'
    }

    def __init__(self, skill_path: Path):
        self.skill_path = Path(skill_path).expanduser().resolve()
        self.errors: list[ValidationError] = []
        self.frontmatter: dict = {}
        self.body: str = ""

    def validate(self) -> bool:
        """Run all validations. Returns True if no errors (warnings OK)."""
        self._check_structure()
        if not self.errors or all(e.level == 'warning' for e in self.errors):
            self._parse_skill_md()
            self._validate_frontmatter()
            self._validate_body()
            self._validate_scripts()
            self._validate_references()

        return not any(e.level == 'error' for e in self.errors)

    def _check_structure(self):
        """Check basic directory structure."""
        if not self.skill_path.exists():
            self.errors.append(ValidationError(
                'error',
                f"Skill path does not exist: {self.skill_path}"
            ))
            return

        if not self.skill_path.is_dir():
            self.errors.append(ValidationError(
                'error',
                f"Skill path is not a directory: {self.skill_path}"
            ))
            return

        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            self.errors.append(ValidationError(
                'error',
                "Missing required SKILL.md file",
                "Create SKILL.md with frontmatter and instructions"
            ))

    def _parse_skill_md(self):
        """Parse SKILL.md into frontmatter and body."""
        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            return

        content = skill_md.read_text()

        # Check for frontmatter
        if not content.startswith('---'):
            self.errors.append(ValidationError(
                'error',
                "SKILL.md must start with YAML frontmatter (---)",
                "Add '---' at the beginning of the file"
            ))
            return

        # Parse frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            self.errors.append(ValidationError(
                'error',
                "Invalid frontmatter format - missing closing '---'",
                "Ensure frontmatter is enclosed between two '---' lines"
            ))
            return

        frontmatter_str = parts[1].strip()
        self.body = parts[2].strip()

        # Simple YAML parsing (key: value)
        for line in frontmatter_str.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                self.frontmatter[key.strip()] = value.strip()

    def _validate_frontmatter(self):
        """Validate frontmatter fields."""
        # Check for unknown keys
        for key in self.frontmatter:
            if key not in self.ALLOWED_FRONTMATTER_KEYS:
                self.errors.append(ValidationError(
                    'warning',
                    f"Unknown frontmatter key: '{key}'",
                    f"Allowed keys: {', '.join(sorted(self.ALLOWED_FRONTMATTER_KEYS))}"
                ))

        # Validate 'name'
        name = self.frontmatter.get('name', '')
        if not name:
            self.errors.append(ValidationError(
                'error',
                "Missing required 'name' field in frontmatter"
            ))
        else:
            self._validate_name(name)

        # Validate 'description'
        description = self.frontmatter.get('description', '')
        if not description:
            self.errors.append(ValidationError(
                'error',
                "Missing required 'description' field in frontmatter"
            ))
        else:
            self._validate_description(description)

        # Validate 'allowed-tools' if present
        allowed_tools = self.frontmatter.get('allowed-tools', '')
        if allowed_tools:
            self._validate_allowed_tools(allowed_tools)

    def _validate_name(self, name: str):
        """Validate skill name."""
        if len(name) > 64:
            self.errors.append(ValidationError(
                'error',
                f"Name exceeds 64 characters (got {len(name)})",
                "Shorten the skill name"
            ))

        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            self.errors.append(ValidationError(
                'error',
                "Name must be hyphen-case (lowercase letters, numbers, hyphens)",
                "Use format like: my-skill-name"
            ))

        for forbidden in ['claude', 'anthropic']:
            if forbidden in name.lower():
                self.errors.append(ValidationError(
                    'error',
                    f"Name cannot contain '{forbidden}'"
                ))

        # Check directory name matches
        if self.skill_path.name != name:
            self.errors.append(ValidationError(
                'warning',
                f"Directory name '{self.skill_path.name}' doesn't match skill name '{name}'",
                "Rename directory or update 'name' in frontmatter"
            ))

    def _validate_description(self, description: str):
        """Validate skill description."""
        if len(description) > 1024:
            self.errors.append(ValidationError(
                'error',
                f"Description exceeds 1024 characters (got {len(description)})",
                "Shorten the description"
            ))

        if '<' in description or '>' in description:
            self.errors.append(ValidationError(
                'error',
                "Description cannot contain XML/HTML tags (< or >)"
            ))

        # Check for placeholder text
        placeholders = ['[REQUIRED]', '[TODO]', '[FILL IN]', 'describe what']
        for placeholder in placeholders:
            if placeholder.lower() in description.lower():
                self.errors.append(ValidationError(
                    'warning',
                    f"Description contains placeholder text: '{placeholder}'",
                    "Replace with actual description"
                ))
                break

        # Check for trigger phrases
        trigger_keywords = ['use when', 'trigger', 'invoke', 'activate', 'for', 'helps with']
        has_trigger = any(kw in description.lower() for kw in trigger_keywords)
        if not has_trigger:
            self.errors.append(ValidationError(
                'warning',
                "Description lacks trigger phrases",
                "Add 'Use when...' or similar to help Claude know when to invoke"
            ))

    def _validate_allowed_tools(self, tools_str: str):
        """Validate allowed-tools field."""
        tools = [t.strip() for t in tools_str.split(',')]
        for tool in tools:
            if tool and tool not in self.VALID_TOOLS:
                self.errors.append(ValidationError(
                    'warning',
                    f"Unknown tool in allowed-tools: '{tool}'",
                    f"Valid tools: {', '.join(sorted(self.VALID_TOOLS))}"
                ))

    def _validate_body(self):
        """Validate SKILL.md body content."""
        if not self.body:
            self.errors.append(ValidationError(
                'error',
                "SKILL.md body is empty",
                "Add instructions for Claude to follow"
            ))
            return

        # Check approximate token count (rough estimate: 1 token ≈ 4 chars)
        estimated_tokens = len(self.body) / 4
        if estimated_tokens > 5000:
            self.errors.append(ValidationError(
                'warning',
                f"Body may exceed 5000 tokens (estimated: {int(estimated_tokens)})",
                "Consider splitting into references/ files"
            ))

        # Check line count
        line_count = len(self.body.split('\n'))
        if line_count > 500:
            self.errors.append(ValidationError(
                'warning',
                f"Body exceeds 500 lines ({line_count} lines)",
                "Consider splitting into references/ files"
            ))

        # Check for examples section
        if '## example' not in self.body.lower() and '### example' not in self.body.lower():
            self.errors.append(ValidationError(
                'warning',
                "No examples section found",
                "Add ## Examples with concrete input/output pairs"
            ))

    def _validate_scripts(self):
        """Validate scripts directory."""
        scripts_dir = self.skill_path / 'scripts'
        if not scripts_dir.exists():
            return

        for script in scripts_dir.glob('*.py'):
            content = script.read_text()

            # Check for hardcoded secrets
            secret_patterns = [
                r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ]
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.errors.append(ValidationError(
                        'error',
                        f"Potential hardcoded secret in {script.name}",
                        "Use environment variables or config files"
                    ))

    def _validate_references(self):
        """Validate references directory."""
        refs_dir = self.skill_path / 'references'
        if not refs_dir.exists():
            return

        for ref_file in refs_dir.glob('*.md'):
            content = ref_file.read_text()
            if len(content) < 50:
                self.errors.append(ValidationError(
                    'warning',
                    f"Reference file '{ref_file.name}' appears empty or minimal",
                    "Add meaningful content or remove the file"
                ))

    def print_report(self):
        """Print validation report."""
        print(f"\nValidating skill: {self.skill_path}\n")
        print("-" * 60)

        if not self.errors:
            print("✓ All checks passed!")
            return

        error_count = sum(1 for e in self.errors if e.level == 'error')
        warning_count = sum(1 for e in self.errors if e.level == 'warning')

        for error in self.errors:
            print(error)
            print()

        print("-" * 60)
        print(f"Summary: {error_count} error(s), {warning_count} warning(s)")

        if error_count == 0:
            print("✓ Skill is valid (warnings are non-blocking)")
        else:
            print("✗ Skill has errors that must be fixed")


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Claude Code skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ~/.claude/skills/my-skill
  %(prog)s .claude/skills/project-skill
  %(prog)s ./my-skill-directory
        """
    )
    parser.add_argument(
        'skill_path',
        help="Path to the skill directory"
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help="Only output errors, no summary"
    )

    args = parser.parse_args()

    validator = SkillValidator(args.skill_path)
    is_valid = validator.validate()

    if not args.quiet:
        validator.print_report()

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
