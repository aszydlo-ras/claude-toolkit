---
name: activity-conversions
description: Expert guide for activity event collection and conversion tracking flow in AdPlatform. Use when planning, discussing, or implementing features related to activity events, conversions, touchpoints, retargeting, or ecommerce pixel integration. Triggers: "activity", "conversion", "touchpoint", "ecommerce pixel", "tracking", "adclick".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Activity & Conversions Flow Guide

Expert knowledge for understanding and extending the activity event collection and conversion tracking system in AdPlatform.

## Quick Start

Before working on activity/conversion features, ensure required repositories are available:

```bash
# Check repositories and prompt to clone missing ones
python .claude/skills/activity-conversions/scripts/check_repos.py

# Check only (no clone prompts)
python .claude/skills/activity-conversions/scripts/check_repos.py --check-only

# Auto-clone missing repos without prompting
python .claude/skills/activity-conversions/scripts/check_repos.py --auto-clone
```

**When this skill is invoked, ALWAYS run the check script first if working on implementation tasks.**

## Required Repositories

| Repository | GitHub URL | Purpose |
|------------|-----------|---------|
| adplatform | `git@github.com:Ringier-Axel-Springer-PL/adplatform.git` | Main monorepo with emission handlers, modes, events API |
| datalayer-api | `git@github.com:Ringier-Axel-Springer-PL/adp-datalayer-api.git` | Ad request and display layer |
| adp-ecommerce-pixel | `git@github.com:Ringier-Axel-Springer-PL/adp-ecommerce-pixel.git` | Client-side ecommerce tracking pixel |

### Repository Check & Clone

Before proceeding with any task, verify repositories exist locally. If missing, prompt user:

```
Repository [name] is required but not found locally.
Clone it? (gh repo clone Ringier-Axel-Springer-PL/[repo-name])
```

Use GitHub CLI for cloning:
```bash
gh repo clone Ringier-Axel-Springer-PL/adplatform
gh repo clone Ringier-Axel-Springer-PL/adp-datalayer-api
gh repo clone Ringier-Axel-Springer-PL/adp-ecommerce-pixel
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ACTIVITY & CONVERSION FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

1. AD SERVING
   ┌──────────────┐     ┌────────────────────────┐     ┌─────────────────┐
   │ datalayer-api│────>│ emission/ (csr.py)     │────>│ adp_provider/   │
   │ (ad request) │     │                        │     │ OR das-bidder   │
   └──────────────┘     └────────────────────────┘     └─────────────────┘
                                   │
                                   │ gctx, lctx (all tracking data)
                                   ▼
2. AD CLICK & TOUCHPOINT CREATION
   ┌────────────────────────────────────────────────────────────────────────┐
   │ adclick.py + tracking.py                                               │
   │  - Records click with (lu, id) user identifiers                        │
   │  - Saves touchpoint to DynamoDB                                        │
   │  - Appends tracking params to URL hash (#adp_...)                      │
   │  - Redirects to landing page                                           │
   └────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ URL hash params stored in localStorage
                                   ▼
3. ACTIVITY EVENT COLLECTION
   ┌────────────────────────────────────────────────────────────────────────┐
   │ adp-ecommerce-pixel (client JS)                                        │
   │  - Reads tracking params from localStorage                             │
   │  - Attaches identifiers to every activity event                        │
   │  - Enables conversion tracking without 3rd party cookies               │
   └────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ POST activity event
                                   ▼
4. ACTIVITY PROCESSING
   ┌────────────────────────────────────────────────────────────────────────┐
   │ activity.py (CSR handler)                                              │
   │  - Receives activity event                                             │
   │  - Validates & enriches event                                          │
   │  - Publishes to RabbitMQ queue                                         │
   └────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ RabbitMQ message
                                   ▼
5. CONVERSION ATTRIBUTION
   ┌────────────────────────────────────────────────────────────────────────┐
   │ adp_activity mode                                                      │
   │  - Consumes from RabbitMQ                                              │
   │  - Fetches touchpoint data from DynamoDB by user identifiers           │
   │  - Matches activity to ad click (conversion attribution)               │
   │  - Publishes attributed conversion to Kinesis                          │
   └────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ Kinesis → DataLake (Glue) / Druid (real-time analytics)               │
   └────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Ad Emission Layer
**Location**: `adplatform/src/python/emission/`

- `csr.py` / `csr005.py` - Main CSR (Client-Side Rendering) handler
- `adclick.py` - Ad click processing, touchpoint creation
- `tracking.py` - Tracking parameter management
- `activity.py` - Activity event handler (receives from pixel)

### 2. Activity Mode
**Location**: `adplatform/src/python/adp/modes/adp_activity/`

- Consumes activity events from RabbitMQ
- Performs conversion attribution
- Writes to Kinesis for analytics

### 3. Events API
**Location**: `adplatform/src/python/adp_events_api/`

Event definitions used across all handlers:
- `models/activity_event.py` - Activity event schema
- `models/conversion_event.py` - Conversion event schema
- `models/adclick_event.py` - Ad click event schema
- `fields/fields.py` - Field definitions with extractors

### 4. Ecommerce Pixel
**Location**: `adp-ecommerce-pixel/`

Client-side JavaScript that:
- Reads tracking params from URL hash/localStorage
- Sends activity events (page view, add to cart, purchase, etc.)
- Enables cookieless conversion tracking

### 5. Datalayer API
**Location**: `datalayer-api/`

- Handles ad requests from publishers
- Orchestrates ad serving flow

## Context Objects

### gctx (Global Context)
Compressed context passed through the entire flow containing:
- Campaign/lineitem/creative identifiers
- Publisher/network information
- Targeting data
- Tracking configuration

### lctx (Local Context)
Request-specific context with:
- User identifiers (lu, id)
- Session data
- Request metadata

**Decode gctx:**
```bash
./adp events decode-gctx <gctx_string>
```

## Conversion Attribution Flow

1. **Touchpoint Creation** (at ad click):
   - User clicks ad
   - `adclick.py` generates unique identifiers
   - Stores touchpoint in DynamoDB: `{user_id, campaign, lineitem, timestamp, ...}`
   - Appends tracking params to landing page URL hash

2. **Identifier Persistence** (on landing page):
   - Ecommerce pixel reads URL hash params
   - Stores in localStorage for persistence
   - Attaches to all subsequent activity events

3. **Activity Event** (user action):
   - Pixel sends event with stored identifiers
   - `activity.py` receives and queues to RabbitMQ

4. **Attribution** (async processing):
   - `adp_activity` mode consumes event
   - Fetches touchpoints from DynamoDB by user identifiers
   - Matches activity to eligible touchpoints
   - Generates conversion event if match found

## Common Tasks

### Adding New Activity Event Type

1. Define event model in `adp_events_api/models/`:
```python
class MyNewActivityEvent(Event):
    event_type: EventType = ...
    # Add fields using builder pattern
```

2. Register in `tables/__init__.py` for DataLake
3. Register in `datasources/__init__.py` for Druid
4. Generate schemas:
```bash
./adp events get-table-schema
./adp events get-datasource-schema
```

### Adding New Field to Activity Events

1. Define field in `adp_events_api/fields/fields.py`:
```python
MyField = string_field("my_field") \
    .with_description("Description") \
    .extract_from_query_arguments(name='mf') \
    .set_as_datasource_dimension('MY_FIELD', {Datasources.conversions}) \
    .create()
```

2. Add to relevant event model
3. Regenerate schemas

### Debugging Conversion Flow

1. Check touchpoint creation in DynamoDB
2. Verify pixel sends identifiers (browser dev tools)
3. Check RabbitMQ queue for activity events
4. Review `adp_activity` mode logs for attribution

## Testing

```bash
# Run emission tests
cd adplatform/src/python/emission
tox

# Run events API tests
cd adplatform/src/python/adp_events_api
tox

# Run specific mode tests
PYTHONPATH=lib:src/python:tests/python \
  .tox/python_3.11.6.1/bin/python -m py.test \
  tests/python/test_adp/modes/test_adp_activity/
```

## Related Documentation

- Events API: `adplatform/src/python/adp_events_api/CLAUDE.md`
- Emission: `adplatform/src/python/emission/README.md`
- DataLake schemas: https://doc.ringieraxelspringer.pl/pages/viewpage.action?pageId=185542752

## Constraints

- **Do NOT** modify event schemas without coordinating DataLake/Druid schema updates
- **Do NOT** remove fields from events (breaks backwards compatibility)
- **Always** use the EventField builder pattern for new fields
- **Always** include GDPR purpose annotation for PII-related fields
