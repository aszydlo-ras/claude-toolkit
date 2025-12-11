# Field Reference

Common fields used in activity and conversion events with their definitions and extractors.

## Field Definition Pattern

Fields are defined using the builder pattern in `adplatform/src/python/adp_events_api/fields/fields.py`:

```python
from adp_events_api.fields import string_field, int_field, float_field

MyField = string_field("my_field") \
    .with_description("Description of the field") \
    .extract_from_query_arguments(name='mf') \
    .set_as_datasource_dimension('MY_FIELD', {Datasources.activity, Datasources.conversions}) \
    .create()
```

---

## Core Fields

### Event Identifiers

| Field | Type | Extractor | Description |
|-------|------|-----------|-------------|
| `event_id` | string | Auto-generated | Unique event identifier (UUID) |
| `request_id` | string | Header | HTTP request ID |
| `page_view_id` | string | Cookie/Query | Page view session ID |
| `event_type` | string | Query `event` | Type of activity event |

### Timestamps

| Field | Type | Extractor | Description |
|-------|------|-----------|-------------|
| `timestamp` | datetime | Auto | Event timestamp (ISO 8601) |
| `timestamp_ms` | int | Auto | Unix timestamp in milliseconds |
| `server_timestamp` | datetime | Auto | Server processing time |

---

## User Fields

| Field | Type | Query Param | Description |
|-------|------|-------------|-------------|
| `lu` | string | `lu` | Local user identifier |
| `aid` | string | `aid` | Anonymous ID |
| `device_id` | string | `did` | Device identifier |
| `external_ids` | string | `extids` | External IDs (JSON) |
| `user_ip` | string | Header | User IP address |
| `user_agent` | string | Header | Browser user agent |

### GDPR Fields

| Field | Type | Query Param | Description |
|-------|------|-------------|-------------|
| `consent_purposes` | string | `cp` | GDPR consent purposes |
| `anonymized` | bool | - | Whether data is anonymized |
| `gdpr_consent_string` | string | `gdpr_cs` | TCF consent string |

---

## Activity Fields

| Field | Type | Query Param | Description |
|-------|------|-------------|-------------|
| `activity_id` | string | `actid` | Activity definition ID |
| `activity_group_id` | string | `actgid` | Activity group ID |
| `network` | string | URL path | Publisher network ID |
| `cost` | float | `cost` | Transaction value |
| `tax` | float | `tax` | Tax amount |
| `order_id` | string | `ord` | Order/transaction ID |
| `quantity` | int | `qty` | Item quantity |
| `products` | string | `products` | JSON array of products |

### URL Fields

| Field | Type | Query Param | Description |
|-------|------|-------------|-------------|
| `document_url` | string | `du` | Current page URL |
| `referrer` | string | `dr` | Referrer URL |
| `request_url` | string | Auto | Full request URL |

---

## Ad/Campaign Fields

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `advertiser_id` | string | GCTX | Advertiser ID |
| `campaign_id` | string | GCTX/Touchpoint | Campaign ID |
| `lineitem_id` | string | GCTX/Touchpoint | Line item ID |
| `creative_id` | string | GCTX/Touchpoint | Creative ID |
| `slot` | string | GCTX | Ad slot identifier |
| `slot_id` | string | GCTX | Slot definition ID |

### Revenue Fields

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `revenue` | float | Touchpoint | Revenue from conversion |
| `bid_rate` | float | Touchpoint | Bid rate at click |
| `cpa_rate` | float | Config | CPA rate for attribution |

---

## Touchpoint Fields

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `touchpoints` | string | DynamoDB | JSON array of touchpoints |
| `touched` | string | Query/DynamoDB | Touchpoint data |
| `touch_point_type` | string | Attribution | click/view |
| `conversion_type` | string | Attribution | full/fallback/none |
| `conversion_attribution_type` | string | Attribution | Attribution method |

---

## Traffic Source Fields

| Field | Type | Query Param | Description |
|-------|------|-------------|-------------|
| `traffic_source_referer` | string | `tsr` | Traffic source referrer |
| `utm_source` | string | `utm_source` | UTM source |
| `utm_medium` | string | `utm_medium` | UTM medium |
| `utm_campaign` | string | `utm_campaign` | UTM campaign |

---

## Geo Fields

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `country_iso` | string | GeoIP | Country code (ISO) |
| `region_id` | string | GeoIP | Region identifier |
| `city_id` | string | GeoIP | City identifier |

---

## Product Fields (in products JSON)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Product SKU/ID |
| `name` | string | Product name |
| `brand` | string | Brand name |
| `category` | string | Category path |
| `variant` | string | Variant (color, size) |
| `price` | float | Unit price |
| `qty` | int | Quantity |

---

## Extractor Types

### Query Arguments
```python
.extract_from_query_arguments(name='param_name')
```
Extracts from URL query parameters.

### GCTX (Global Context)
```python
.extract_from_gctx(key='gctx_key')
```
Extracts from decoded GCTX parameter.

### Cookie
```python
.extract_from_cookie(name='cookie_name')
```
Extracts from HTTP cookies.

### Header
```python
.extract_from_header(name='Header-Name')
```
Extracts from HTTP headers.

### Auto-generated
```python
.auto_generate()
```
Field is automatically generated (UUIDs, timestamps).

---

## Datasource Dimensions

Fields can be registered as dimensions in Druid datasources:

```python
.set_as_datasource_dimension('DIMENSION_NAME', {
    Datasources.activity,
    Datasources.conversions,
    Datasources.adclicks,
})
```

Available datasources (from `adp_events_api/datasources/__init__.py`):
- `Datasources.activity`
- `Datasources.conversions`
- `Datasources.adclicks`
- `Datasources.offers`
- `Datasources.impressions`

---

## DataLake Tables

Fields can be registered in Glue tables:

```python
.set_as_table_column('column_name', {
    Tables.activity,
    Tables.conversions,
})
```

Available tables (from `adp_events_api/tables/__init__.py`):
- `Tables.activity`
- `Tables.conversions`
- `Tables.adclicks`
- `Tables.impressions`

---

## Adding a New Field

1. **Define field** in `fields/fields.py`:
```python
NewField = string_field("new_field") \
    .with_description("New field description") \
    .extract_from_query_arguments(name='nf') \
    .set_as_datasource_dimension('NEW_FIELD', {Datasources.activity}) \
    .set_as_table_column('new_field', {Tables.activity}) \
    .create()
```

2. **Add to event model**:
```python
# In models/activity_event.py
from adp_events_api.fields import NewField

class ActivityEvent(Event):
    new_field: NewField = None
```

3. **Regenerate schemas**:
```bash
./adp events get-table-schema
./adp events get-datasource-schema
```

4. **Update Glue schema** in `data-lake-glue-datasources`

5. **Update Druid spec** in `adp-reports-defs` (if needed)

---

## Common Patterns

### Optional String Field
```python
OptionalField = string_field("optional_field") \
    .with_description("May be null") \
    .extract_from_query_arguments(name='of') \
    .create()
```

### Required Field with Default
```python
RequiredField = string_field("required_field") \
    .with_description("Always present") \
    .with_default("default_value") \
    .extract_from_query_arguments(name='rf') \
    .create()
```

### Numeric Field
```python
NumericField = float_field("numeric_field") \
    .with_description("Numeric value") \
    .extract_from_query_arguments(name='nf') \
    .create()
```

### GDPR Annotated Field
```python
PiiField = string_field("pii_field") \
    .with_description("Contains PII") \
    .with_gdpr_purpose(GdprPurpose.ANALYTICS) \
    .extract_from_query_arguments(name='pf') \
    .create()
```
