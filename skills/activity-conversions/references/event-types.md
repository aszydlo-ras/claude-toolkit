# Event Types Reference

Complete reference for activity and conversion event types in AdPlatform.

## Activity Event Types

### Client-Side Events (via Ecommerce Pixel)

| Event Type | Description | Required Fields | Optional Fields |
|------------|-------------|-----------------|-----------------|
| `page_view` | User views a page | `actgid`, `network` | `du` (document URL), `dr` (referrer) |
| `product_detail` | User views product detail page | `actgid`, `network`, `products` | `du`, `dr` |
| `add_to_cart` | User adds product to cart | `actgid`, `network`, `products` | `qty` |
| `remove_from_cart` | User removes from cart | `actgid`, `network`, `products` | `qty` |
| `checkout_started` | User starts checkout | `actgid`, `network` | `products`, `cost` |
| `purchased` | User completes purchase | `actgid`, `network`, `cost`, `ord` | `products`, `tax`, `qty` |
| `lead` | Lead generation event | `actgid`, `network` | Custom fields |
| `signup` | User registration | `actgid`, `network` | `extids` |

### Server-Side Events

| Event Type | Description | Source |
|------------|-------------|--------|
| `conversion` | Attributed conversion | adp_activity mode |
| `potential_conversion` | Pre-attribution event | emission handler |
| `offer_conversion` | Offer-based conversion | adp_activity mode |

---

## Event Models Location

All event models are defined in `adplatform/src/python/adp_events_api/models/`:

| File | Event Class | Purpose |
|------|-------------|---------|
| `activity_event.py` | `ActivityEvent` | Raw activity from pixel |
| `conversion_event.py` | `ConversionEvent` | Attributed conversion |
| `adclick_event.py` | `AdclickEvent` | Ad click tracking |
| `offer_conversion_event.py` | `OfferConversionEvent` | Offer conversions |
| `potential_conversion_event.py` | `PotentialConversionEvent` | Pre-attribution |

---

## DataLake Tables

Events are stored in AWS Glue tables for DataLake queries:

| Table | Kinesis Stream | Events |
|-------|---------------|--------|
| `adp_activity` | `awsp-adp-activity` | ActivityEvent |
| `adp_conversions` | `awsp-adp-conversions2` | ConversionEvent |
| `adp_adclicks` | `awsp-adp-adclicks` | AdclickEvent |
| `adp_offer_conversions` | `awsp-adp-offer-conversions` | OfferConversionEvent |

Schema location: `data-lake-glue-datasources/json_schemas/adp/`

---

## Druid Datasources

Events are ingested into Druid for real-time analytics:

| Datasource | Events | Granularity |
|------------|--------|-------------|
| `adp-activity` | ActivityEvent | HOUR |
| `adp-conversions` | ConversionEvent | HOUR |
| `adp-adclicks` | AdclickEvent | HOUR |

Spec location: `adp-reports-defs/defs/`

---

## Event Flow by Type

### Purchase Conversion Flow

```
1. User clicks ad
   └─> AdclickEvent → Kinesis (adclicks)
   └─> Touchpoint → DynamoDB

2. User browses (optional)
   └─> ActivityEvent (page_view) → RabbitMQ → Kinesis (activity)

3. User adds to cart (optional)
   └─> ActivityEvent (add_to_cart) → RabbitMQ → Kinesis (activity)

4. User purchases
   └─> ActivityEvent (purchased) → RabbitMQ
       └─> adp_activity mode
           └─> Fetch touchpoints from DynamoDB
           └─> Match & attribute
           └─> ConversionEvent → Kinesis (conversions2)
```

### Lead Conversion Flow

```
1. User clicks ad
   └─> AdclickEvent → Kinesis (adclicks)
   └─> Touchpoint → DynamoDB

2. User submits lead form
   └─> ActivityEvent (lead) → RabbitMQ
       └─> adp_activity mode
           └─> ConversionEvent → Kinesis (conversions2)
```

---

## Products JSON Format

For events with products (product_detail, add_to_cart, purchased):

```json
[
  {
    "id": "SKU123",
    "name": "Product Name",
    "brand": "Brand Name",
    "category": "Category/Subcategory",
    "variant": "Color/Size",
    "price": 99.99,
    "qty": 1
  }
]
```

Sent as URL-encoded JSON in `products` parameter.

---

## Conversion Types

### By Attribution

| Type | Description |
|------|-------------|
| `full_conversion` | Matched touchpoint within attribution window |
| `fallback_conversion` | No touchpoint, fallback rules applied |
| `no_conversion` | Cannot be attributed |

### By Source

| Type | Description |
|------|-------------|
| `click` | Click-through conversion |
| `view` | View-through conversion |
| `paapi` | Privacy-preserving API conversion |

---

## Event Identifiers

### User Identifiers

| Field | Description | Source |
|-------|-------------|--------|
| `lu` | Local user ID | Cookie or localStorage |
| `aid` | Anonymous ID | Generated per session |
| `device_id` | Device identifier | Mobile apps |
| `extids` | External IDs | CRM, login systems |

### Event Identifiers

| Field | Description | Format |
|-------|-------------|--------|
| `event_id` | Unique event ID | UUID |
| `request_id` | HTTP request ID | UUID |
| `page_view_id` | Page view session | UUID |

### Ad Identifiers

| Field | Description |
|-------|-------------|
| `campaign_id` | Campaign ID |
| `lineitem_id` | Line item ID |
| `creative_id` | Creative ID |
| `network` | Publisher network ID |
| `slot` | Ad slot identifier |

---

## GDPR & Privacy Fields

Fields with PII annotations:

| Field | PII Level | GDPR Purpose |
|-------|-----------|--------------|
| `user_ip` | HIGH | Analytics |
| `device_id` | HIGH | Analytics |
| `lu` | MEDIUM | Attribution |
| `document_url` | LOW | Analytics |

Always check GDPR consent before processing PII fields.

---

## Schema Generation Commands

```bash
cd adplatform

# Generate DataLake schema (Glue)
./adp events get-table-schema

# Generate Druid schema
./adp events get-datasource-schema

# List all event fields
./adp events list-fields

# Validate event schema
./adp events validate-schema
```
