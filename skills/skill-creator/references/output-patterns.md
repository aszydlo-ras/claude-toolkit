# Output Patterns for Skills

Patterns for consistent, high-quality outputs from Claude.

## Template Pattern

Provide structured frameworks for output formatting. Match strictness to requirements.

### Strict Templates

Use for APIs, data formats, and critical consistency requirements. Zero variation allowed.

```markdown
## Output Format

ALWAYS use this exact structure:

### Analysis: [Title]

**Executive Summary**
[2-3 sentence overview]

**Key Findings**
1. [Finding with metric]
2. [Finding with metric]
3. [Finding with metric]

**Recommendations**
- [Actionable item 1]
- [Actionable item 2]

**Data**
| Metric | Value | Change |
|--------|-------|--------|
| [name] | [val] | [+/-]  |
```

### Flexible Templates

Use when adaptation provides value. Provide structure as guidance, not mandate.

```markdown
## Output Format

Use this structure as a sensible default, adapt as needed:

### [Descriptive Title]

**Summary**: [Brief overview of findings]

**Details**:
[Organize content logically - bullets, paragraphs, or tables as appropriate]

**Next Steps**: [If applicable]
```

## Examples Pattern

Show Claude what you want through input/output pairs. More effective than descriptions.

```markdown
## Examples

### Commit Message Style

**Input** (git diff):
```diff
- const MAX_RETRIES = 3;
+ const MAX_RETRIES = 5;
+ const RETRY_DELAY_MS = 1000;
```

**Output**:
```
feat(retry): increase resilience with configurable retry delay

- Bump MAX_RETRIES from 3 to 5 for better fault tolerance
- Add RETRY_DELAY_MS constant for backoff configuration
```

### Another Example

**Input**:
```
[Show realistic input]
```

**Output**:
```
[Show exact expected output]
```
```

## Choosing the Right Pattern

| Scenario | Pattern | Reason |
|----------|---------|--------|
| API responses | Strict template | Consumers expect exact format |
| Reports | Flexible template | Content varies, structure helps |
| Code generation | Examples | Style better shown than described |
| Data extraction | Strict template | Downstream processing needs consistency |
| Creative content | Flexible or none | Rigid structure harms quality |

## Anti-Patterns

### Over-specified Templates

❌ Bad:
```markdown
Output EXACTLY 3 paragraphs of EXACTLY 4 sentences each...
```

✓ Good:
```markdown
Provide a concise analysis in 2-4 paragraphs covering...
```

### Examples Without Context

❌ Bad:
```markdown
Example: "Hello" -> "Hi there!"
```

✓ Good:
```markdown
### Greeting Transformation
**Context**: Formal to casual tone conversion
**Input**: "Hello, how may I assist you today?"
**Output**: "Hey! What can I help you with?"
```

## Combining Patterns

For complex skills, combine templates with examples:

```markdown
## Output Format

Use this structure:

### [Analysis Type]: [Subject]

**Summary**: [1-2 sentences]
**Rating**: [1-5 stars]
**Details**: [Bulleted findings]

### Example

**Input**: Analyze security of login.py
**Output**:

### Security Analysis: login.py

**Summary**: Critical SQL injection vulnerability in user authentication.
**Rating**: ★★☆☆☆ (2/5)
**Details**:
- Line 45: Raw SQL query with string interpolation
- Line 67: Password stored in plaintext
- Line 89: No rate limiting on login attempts
```
