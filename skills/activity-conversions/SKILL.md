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
# Check all repositories
python .claude/skills/activity-conversions/scripts/check_repos.py

# Check repos for specific task type
python .claude/skills/activity-conversions/scripts/check_repos.py --task debugging
python .claude/skills/activity-conversions/scripts/check_repos.py --task pixel-modification
python .claude/skills/activity-conversions/scripts/check_repos.py --task schema-change

# Auto-clone missing repos without prompting
python .claude/skills/activity-conversions/scripts/check_repos.py --auto-clone

# Check only (no clone prompts)
python .claude/skills/activity-conversions/scripts/check_repos.py --check-only

# JSON output for programmatic use
python .claude/skills/activity-conversions/scripts/check_repos.py --json

# List available task types
python .claude/skills/activity-conversions/scripts/check_repos.py --list-tasks
```

**When this skill is invoked, ALWAYS run the check script first if working on implementation tasks.**

## Reference Documentation

Detailed documentation is available in `references/`:
- **[debugging-guide.md](references/debugging-guide.md)** - Step-by-step debugging procedures
- **[event-types.md](references/event-types.md)** - All activity and conversion event types
- **[field-reference.md](references/field-reference.md)** - Field definitions and extractors

## Required Repositories

| Repository | GitHub URL | Tasks |
|------------|-----------|-------|
| adplatform | `Ringier-Axel-Springer-PL/adplatform` | schema-change, attribution, debugging, reports, pixel |
| datalayer-api | `Ringier-Axel-Springer-PL/adp-datalayer-api` | debugging |
| adp-ecommerce-pixel | `Ringier-Axel-Springer-PL/adp-ecommerce-pixel` | pixel-modification, debugging |
| adp-reports-defs | `Ringier-Axel-Springer-PL/adp-reports-defs` | schema-change, reports |
| data-lake-glue-datasources | `Ringier-Axel-Springer-PL/data-lake-glue-datasources` | schema-change |
| eks-ns-adp | `Ringier-Axel-Springer-PL/eks-ns-adp` | deployment, schema-change |

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

## Examples

### Example 1: Adding a New Field to Activity Events

**Task**: Add `referrer_category` field to track referring page type (e.g., 'homepage', 'product', 'checkout')

**Steps**:

1. Define field in `adplatform/src/python/adp_events_api/fields/fields.py`:
```python
ReferrerCategory = string_field("referrer_category") \
    .with_description("Category of the referring page") \
    .extract_from_query_arguments(name='refcat') \
    .set_as_datasource_dimension('REFERRER_CATEGORY', {Datasources.conversions}) \
    .create()
```

2. Add to event model in `adplatform/src/python/adp_events_api/models/activity_event.py`:
```python
from adp_events_api.fields import ReferrerCategory

class ActivityEvent(Event):
    # ... existing fields ...
    referrer_category: ReferrerCategory = None
```

3. Register in tables and datasources:
```python
# tables/__init__.py - for DataLake
# datasources/__init__.py - for Druid
```

4. Generate schemas:
```bash
./adp events get-table-schema
./adp events get-datasource-schema
```

5. Update pixel to send the new field (if client-side):
```typescript
// adp-ecommerce-pixel/src/modules/activity/services/activity-event-service.ts
type ActivityEvent = {
    // ... existing fields ...
    refcat?: string;  // referrer category
};
```

### Example 2: Debugging Missing Conversions

**Symptoms**: Conversions not appearing in reports despite user completing purchase

**Debug Flow**:

1. **Check pixel fires** (Browser DevTools):
```
Network tab → Filter "activity" → Verify:
- Request URL contains /<network>/activity
- Parameters include: actgid, event=purchased, cost, ord (order_id)
- Response is 200/204
```

2. **Verify tracking params in localStorage**:
```javascript
// In browser console
localStorage.getItem('adp_tracking')
// Should contain: lu, aid, touchpoint data from adclick
```

3. **Check touchpoint in DynamoDB**:
```bash
# Query touchpoint by user identifier (lu)
aws dynamodb query \
  --table-name adp-touchpoints-prod \
  --key-condition-expression "lu = :lu" \
  --expression-attribute-values '{":lu":{"S":"<user_lu_value>"}}'
```

4. **Check RabbitMQ queue**:
```
Access RabbitMQ management UI
Queue: adp.activity.events
Verify message is published with correct payload
```

5. **Review adp_activity mode logs**:
```bash
kubectl logs -l app=adp-activity -n adp --tail=100 | grep "conversion"
kubectl logs -l app=adp-activity -n adp --tail=100 | grep "<order_id>"
```

6. **Check Kinesis stream**:
```bash
# Verify conversion event reached awsp-adp-conversions2 stream
aws kinesis get-shard-iterator --stream-name awsp-adp-conversions2 ...
```

### Example 3: Decoding GCTX Context

**Task**: Decode compressed GCTX parameter from ad click URL

**Input**:
```
gctx=H4sIAAAAAAAAA6tWKkktLlGyUlAqS8wpTtVRSs7PS0nNK1GyMjJQ0lFKTi0uzszPUbIyNDJR0lFKSS1OLUpVslIqS8wpTlWyUirIL0oBMpRsAOXdkuBKAAAA
```

**Command**:
```bash
cd adplatform
./adp events decode-gctx "H4sIAAAAAAAAA6tWKkktLlGyUlAqS8wpTtVRSs7PS0nNK1GyMjJQ0lFKTi0uzszPUbIyNDJR0lFKSS1OLUpVslIqS8wpTlWyUirIL0oBMpRsAOXdkuBKAAAA"
```

**Output**:
```json
{
  "campaign_id": "12345",
  "lineitem_id": "67890",
  "creative_id": "11111",
  "network": "1746213",
  "publisher_id": "9999",
  "enable_conversion_tracking": true,
  "tpl_code": "click_tpl_1"
}
```

**Alternative** (Python):
```python
from emission.csr.gctx_codec import GCTXCodec
decoded = GCTXCodec.decode_context("H4sIAAAAAAAAA6tW...")
print(decoded)
```

### Example 4: Modifying Ecommerce Pixel

**Task**: Add custom event type to pixel

**Steps**:

1. Update event types in `adp-ecommerce-pixel/src/modules/activity/services/activity-event-service.ts`:
```typescript
export type EventName =
    | 'page_view'
    | 'product_detail'
    | 'add_to_cart'
    | 'purchased'
    | 'my_custom_event';  // NEW
```

2. Add handler in corresponding service file

3. Build and test locally:
```bash
cd adp-ecommerce-pixel
npm install
npm run build
npm start  # local dev server
```

4. Update handler in `adplatform/src/python/emission/csr/activity.py` to process new event type

5. Deploy pixel via Bamboo or:
```bash
npm run deploy-prod
```

## Constraints

- **Do NOT** modify event schemas without coordinating DataLake/Druid schema updates
- **Do NOT** remove fields from events (breaks backwards compatibility)
- **Always** use the EventField builder pattern for new fields
- **Always** include GDPR purpose annotation for PII-related fields
