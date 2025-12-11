# Debugging Guide for Activity & Conversions

Step-by-step debugging procedures for the activity event collection and conversion tracking flow.

## Quick Diagnostic Commands

```bash
# Check all repos are available
python .claude/skills/activity-conversions/scripts/check_repos.py --task debugging

# Decode GCTX from URL
cd adplatform && ./adp events decode-gctx "<gctx_string>"

# Check adp_activity mode logs
kubectl logs -l app=adp-activity -n adp --tail=100

# Check emission CSR logs
kubectl logs -l app=emission -n adp --tail=100 | grep activity
```

---

## 1. Pixel Not Firing

**Symptoms**: No network requests to `/<network>/activity` in browser DevTools

**Debug Steps**:

### 1.1 Check Pixel Script Loaded
```javascript
// Browser console
console.log(window.adpEcommercePixel)  // Should be defined
console.log(document.querySelector('script[src*="ecommerce-pixel"]'))
```

### 1.2 Check Configuration
```javascript
// Browser console - check pixel config
localStorage.getItem('adp_config')
```

### 1.3 Verify Activity Group ID
```javascript
// The actgid must be configured for this site
// Check if actgid is passed in pixel initialization
```

### 1.4 Console Errors
```
Look for JavaScript errors related to:
- CORS issues
- Script loading failures
- Network errors
```

---

## 2. Activity Events Not Reaching Backend

**Symptoms**: Pixel fires (200/204 response) but events don't appear in RabbitMQ

**Debug Steps**:

### 2.1 Check CSR Handler Logs
```bash
kubectl logs -l app=emission -n adp --tail=200 | grep -i "activity"
kubectl logs -l app=emission -n adp --tail=200 | grep -i "error"
```

### 2.2 Verify RabbitMQ Connection
```bash
# Check RabbitMQ management UI
# Queue: adp.activity.events
# Exchange: activity-events
```

### 2.3 Check Request Parameters
Required parameters in activity request:
- `actgid` or `actid` - Activity group/activity ID
- `event` - Event type (page_view, add_to_cart, purchased, etc.)
- `network` - Network ID (in URL path)

Optional but important:
- `cost` - For purchase events
- `ord` - Order ID (for deduplication)
- `products` - JSON array of products
- `lu` - User identifier

### 2.4 Validate Activity Group Exists
```bash
# Check if activity group is configured in AdPanel
# Activity groups are managed per advertiser
```

---

## 3. Conversions Not Attributed

**Symptoms**: Activity events arrive but conversions don't appear in reports

**Debug Steps**:

### 3.1 Check Touchpoint Exists
```bash
# DynamoDB query for user touchpoint
aws dynamodb query \
  --table-name adp-touchpoints-prod \
  --key-condition-expression "lu = :lu" \
  --expression-attribute-values '{":lu":{"S":"<user_lu_value>"}}'
```

### 3.2 Verify Tracking Parameters
```javascript
// Browser console - check localStorage for tracking data
localStorage.getItem('adp_tracking')
// Should contain: lu, aid, touchpoint data from adclick
```

### 3.3 Check adp_activity Mode
```bash
# Look for attribution logic logs
kubectl logs -l app=adp-activity -n adp --tail=200 | grep "touchpoint"
kubectl logs -l app=adp-activity -n adp --tail=200 | grep "conversion"
```

### 3.4 Verify Attribution Window
- Default attribution window is 30 days
- Check if touchpoint timestamp is within window
- Check activity group configuration for custom windows

### 3.5 Check Conversion Type Configuration
Activity groups can be configured for different conversion types:
- `click` - Only click-through conversions
- `view` - View-through conversions
- `both` - Click and view-through

---

## 4. Missing Data in Reports

**Symptoms**: Conversions tracked but missing fields in Druid/DataLake

**Debug Steps**:

### 4.1 Check Kinesis Stream
```bash
# Verify event structure in Kinesis
# Stream: awsp-adp-conversions2
aws kinesis describe-stream --stream-name awsp-adp-conversions2
```

### 4.2 Verify Field Definitions
```bash
# Check if field is defined in events API
cd adplatform
grep -r "field_name" src/python/adp_events_api/
```

### 4.3 Check DataLake Schema
```bash
# Verify Glue schema includes the field
cd data-lake-glue-datasources
cat json_schemas/adp/conversions.json | jq '.properties.field_name'
```

### 4.4 Check Druid Datasource
```bash
# Verify Druid spec includes the dimension
cd adp-reports-defs
grep -r "FIELD_NAME" defs/
```

---

## 5. Duplicate Conversions

**Symptoms**: Same conversion appears multiple times

**Debug Steps**:

### 5.1 Check Order ID
- `ord` parameter must be unique per conversion
- Used for deduplication in Activity DB

### 5.2 Verify Deduplication Logic
```bash
# Check Activity DB for duplicates
# adp_activity mode checks for existing order_id before saving
kubectl logs -l app=adp-activity -n adp --tail=200 | grep "duplicate"
```

### 5.3 Check Pixel Firing Multiple Times
```javascript
// Browser console - check for multiple pixel calls
// Network tab → filter "activity" → check for duplicate requests
```

---

## 6. Cookieless Tracking Issues

**Symptoms**: Conversions not tracked for users without 3rd party cookies

**Debug Steps**:

### 6.1 Verify URL Hash Parameters
After adclick, URL should contain:
```
https://landing-page.com/#adp_lu=...&adp_tp=...&adp_aid=...
```

### 6.2 Check localStorage
```javascript
// Browser console
localStorage.getItem('adp_tracking')
// Should contain parsed values from URL hash
```

### 6.3 Verify Pixel Reads localStorage
```javascript
// Check pixel sends lu/aid from localStorage
// Network tab → activity request → check parameters
```

### 6.4 Cross-Domain Issues
- localStorage is per-domain
- If user clicks ad on domain A, converts on domain B - tracking may fail
- Solution: Use server-side tracking or first-party cookies

---

## 7. Common Error Patterns

### 7.1 "Activity group not found"
```
Cause: Invalid actgid in request
Fix: Verify activity group exists in AdPanel
```

### 7.2 "No touchpoints for user"
```
Cause: User has no recorded ad clicks
Fix: Check adclick handler, DynamoDB touchpoints table
```

### 7.3 "Event validation failed"
```
Cause: Missing required fields or invalid format
Fix: Check event schema in adp_events_api
```

### 7.4 "RabbitMQ connection refused"
```
Cause: RabbitMQ not accessible from emission pod
Fix: Check K8s service configuration, network policies
```

---

## 8. Useful Queries

### 8.1 Recent Activity Events (Druid)
```sql
SELECT __time, event_type, network, actgid, lu, cost
FROM "adp-activity"
WHERE __time > CURRENT_TIMESTAMP - INTERVAL '1' HOUR
ORDER BY __time DESC
LIMIT 100
```

### 8.2 Recent Conversions (Druid)
```sql
SELECT __time, conversion_type, network, revenue, order_id
FROM "adp-conversions"
WHERE __time > CURRENT_TIMESTAMP - INTERVAL '1' HOUR
ORDER BY __time DESC
LIMIT 100
```

### 8.3 Touchpoints by User (DynamoDB)
```bash
aws dynamodb query \
  --table-name adp-touchpoints-prod \
  --key-condition-expression "lu = :lu" \
  --expression-attribute-values '{":lu":{"S":"<lu_value>"}}' \
  --projection-expression "lu, timestamp_ms, campaign_id, lineitem_id"
```

---

## 9. Log Locations

| Component | Location | Command |
|-----------|----------|---------|
| Emission CSR | K8s pod | `kubectl logs -l app=emission -n adp` |
| adp_activity | K8s pod | `kubectl logs -l app=adp-activity -n adp` |
| RabbitMQ | Management UI | `<rabbitmq-url>:15672` |
| Kinesis | AWS Console | CloudWatch metrics |
| Druid | Druid Console | `<druid-url>/unified-console.html` |

---

## 10. Escalation Path

1. **First**: Check logs in emission and adp_activity pods
2. **Then**: Verify data in DynamoDB and RabbitMQ
3. **Next**: Check Kinesis stream for events
4. **Finally**: Verify Druid/DataLake ingestion

Contact team channels:
- `#adp-tech` - General AdPlatform issues
- `#adp-data` - DataLake/Druid issues
