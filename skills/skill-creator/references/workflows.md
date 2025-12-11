# Workflow Patterns for Skills

Structure complex tasks into manageable, repeatable processes.

## Sequential Workflow

Ordered steps with clear progression. Best for predictable, linear tasks.

### Structure

```markdown
## Workflow Overview

This skill follows a 5-step process:
1. **Analyze** - Understand input requirements
2. **Prepare** - Gather necessary resources
3. **Execute** - Perform core operation
4. **Validate** - Verify results
5. **Deliver** - Format and present output

## Step-by-Step Instructions

### Step 1: Analyze
[Detailed instructions for analysis phase]
- Check for X
- Identify Y
- Note Z

### Step 2: Prepare
[Detailed instructions for preparation]
...
```

### Example: PDF Form Filling

```markdown
## Workflow

### 1. Analyze Form Structure
- Read PDF to identify all form fields
- Note field types (text, checkbox, dropdown, signature)
- Map required vs optional fields

### 2. Map User Data to Fields
- Match provided data to form field names
- Flag any missing required data
- Ask user for missing information

### 3. Validate Before Filling
- Confirm data types match field requirements
- Check value constraints (length, format)
- Preview mapping for user approval

### 4. Fill Form
- Execute field population in order
- Handle special fields (dates, signatures) appropriately
- Preserve original formatting

### 5. Verify and Deliver
- Re-read filled PDF to confirm accuracy
- Generate summary of filled fields
- Provide filled PDF to user
```

## Conditional Workflow

Branching logic with decision points. Best for tasks with multiple paths.

### Structure

```markdown
## Decision Tree

First, determine which scenario applies:

### Scenario A: [Condition 1]
If [condition], follow these steps:
1. [Step A1]
2. [Step A2]

### Scenario B: [Condition 2]
If [condition], follow these steps:
1. [Step B1]
2. [Step B2]

### Scenario C: Default
If none of the above:
1. [Default step 1]
2. [Default step 2]
```

### Example: Content Creation

```markdown
## Workflow Selection

Determine content type and follow appropriate branch:

### Branch: New Content Creation
**Trigger**: User wants to create something from scratch

1. Clarify content goals and audience
2. Create outline for approval
3. Draft full content
4. Revise based on feedback

### Branch: Content Editing
**Trigger**: User has existing content to improve

1. Analyze current content
2. Identify improvement areas
3. Suggest specific changes
4. Apply approved changes

### Branch: Content Transformation
**Trigger**: User wants to convert format or style

1. Identify source and target formats
2. Map content elements between formats
3. Transform while preserving meaning
4. Verify nothing lost in translation
```

## Iterative Workflow

Loops with validation checkpoints. Best for refinement tasks.

### Structure

```markdown
## Iterative Process

### Initial Pass
1. [Generate first version]
2. [Apply basic checks]

### Refinement Loop
Repeat until quality threshold met:
1. [Evaluate against criteria]
2. [Identify gaps]
3. [Apply improvements]
4. [Re-evaluate]

### Completion Criteria
Stop iterating when:
- [ ] Criterion A met
- [ ] Criterion B met
- [ ] User approves OR max iterations reached
```

### Example: Code Review

```markdown
## Iterative Review Process

### Pass 1: Critical Issues
Scan for blockers:
- Security vulnerabilities
- Logic errors
- Breaking changes

→ If found: Stop and report immediately

### Pass 2: Quality Issues
Check for:
- Code style violations
- Missing error handling
- Performance concerns
- Test coverage gaps

### Pass 3: Improvements
Suggest (non-blocking):
- Readability enhancements
- Better naming
- Documentation additions

### Completion
Provide summary with:
- Blocking issues (must fix)
- Quality issues (should fix)
- Suggestions (could improve)
```

## Parallel Workflow

Independent tasks that can run simultaneously. Best for multi-faceted analysis.

### Structure

```markdown
## Parallel Analysis

Run these analyses independently, then synthesize:

### Track A: [Analysis Type 1]
[Instructions for first analysis]

### Track B: [Analysis Type 2]
[Instructions for second analysis]

### Track C: [Analysis Type 3]
[Instructions for third analysis]

### Synthesis
Combine findings from all tracks:
- Identify correlations
- Note conflicts
- Provide unified recommendation
```

## Validation Checkpoints

Add explicit validation at critical points:

```markdown
## Checkpoint Pattern

After [operation]:

**Validation**:
1. Check: [What to verify]
2. Expected: [What success looks like]
3. If failed: [Recovery action]

**Only proceed when validation passes.**
```

### Example

```markdown
### Step 3: Apply Database Migration

Run: `python manage.py migrate`

**Validation Checkpoint**:
1. Check: Migration output shows "OK" for all migrations
2. Expected: No errors, all migrations applied
3. If failed:
   - Capture error message
   - Run `python manage.py showmigrations` to identify state
   - Report to user before proceeding

**Do NOT proceed to Step 4 until migration validates successfully.**
```

## Choosing the Right Pattern

| Task Type | Pattern | Example |
|-----------|---------|---------|
| Form processing | Sequential | PDF filling, data entry |
| Content work | Conditional | Writing, editing, transforming |
| Quality tasks | Iterative | Code review, proofreading |
| Analysis | Parallel | Multi-criteria evaluation |
| Complex ops | Combined | Use multiple patterns together |
