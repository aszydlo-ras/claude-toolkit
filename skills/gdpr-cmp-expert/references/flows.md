# GDPR CMP Detailed Flows

## Flow 1: Web User First Visit

```
User -> Website
       |
       v
Website loads dlApi (adp-datalayer-api)
       |
       v
dlApi/cmp.js initializes
       |
       v
Fetches vendor-list.json from OCDN
       |
       v
Checks for euconsent-v2 cookie
       |
       v
Cookie missing OR version mismatch?
       |
       v
YES -> Load gdpr-popup in iframe (portal.html)
       |
       v
User sees consent dialog
       |
       v
User clicks "Accept All" / "Reject" / configures
       |
       v
gdpr-popup generates TCF consent string
       |
       v
Saves to euconsent-v2 cookie
       |
       v
Fires consent events for advertisers
```

### Key Code Locations

| Step | Repository | File |
|------|------------|------|
| dlApi init | adp-datalayer-api | `dlApi/dllib/cmp.js` |
| Vendor list fetch | adp-datalayer-api | `dlApi/dllib/cmp-config-manager.js` |
| Cookie check | adp-datalayer-api | `dlApi/dllib/consent-api.js` |
| Popup load | gdpr-popup | `src/index.js` |
| Consent string | gdpr-popup | `src/lib/` |

---

## Flow 2: Vendor List Publication

```
Admin -> gdpr-admin-panel
        |
        v
Configures vendors, translations, styles
        |
        v
Panel calls GraphQL API -> gdpr-db
        |
        v
Data persisted in PostgreSQL
        |
        v
Admin clicks "Publish" or n8n triggers
        |
        v
gdpr/cmp_coordinator starts
        |
        v
Reads vendor config from database
        |
        v
Merges with IAB Global Vendor List
        |
        v
Generates vendor-list.json
        |
        v
Uploads to OCDN S3 bucket
        |
        v
Updates Accelerator proxy configuration
        |
        v
New version live at:
cmp.dreamlab.pl/vendor-list/v3/{tenant_id}/vendor-list.json?v={version}
```

### Key Code Locations

| Step | Repository | File |
|------|------------|------|
| Admin UI | gdpr-admin-panel | `src/` |
| Publication trigger | gdpr | `src/python/adp/modes/cmp_coordinator/__init__.py` |
| Vendor list generation | gdpr | `services/vendor_list_publisher_service.py` |
| Translation merging | gdpr | `services/gdpr_translation_service.py` |

---

## Flow 3: Mobile App Consent Check

```
Mobile App starts
        |
        v
SDK reads stored consent from local storage
        |
        v
SDK calls: GET /1746213/func/verify?
           pubconsent={cookie}&adpconsent={cookie}
        |
        v
gdpr-mobile-api receives request
        |
        v
Decodes consent strings (TCF v2.2)
        |
        v
Fetches current vendor list version
        |
        v
Compares versions
        |
        v
Returns JSON: {"status": "OK|OUTDATED|EMPTY|INVALID"}
        |
        v
Status not OK?
        |
        v
YES -> SDK opens WebView
        |
        v
Loads gdpr-mobile-frame HTML
        |
        v
Frame loads adp-datalayer-api?webview=1
        |
        v
dlApi loads gdpr-popup (forced mode)
        |
        v
User consents
        |
        v
SDK receives new consent via JS bridge
```

### Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| OK | Consent valid and current | No action needed |
| OUTDATED | Consent from older vendor list | Show consent dialog |
| EMPTY | No consent stored | Show consent dialog |
| INVALID | Consent string malformed | Show consent dialog |

### Key Code Locations

| Step | Repository | File |
|------|------------|------|
| Verify endpoint | gdpr-mobile-api | `adpcmp/` |
| WebView frame | gdpr-mobile-frame | `src/` |
| Forced mode trigger | adp-datalayer-api | `dlApi/dllib/cmp.js` |

---

## Flow 4: Global Vendor List Sync

```
IAB publishes new Global Vendor List (GVL)
        |
        v
n8n scheduled job triggers (periodic)
        |
        v
gdpr/smartdev/CmpCoordinator runs sync
        |
        v
Fetches latest GVL from IAB endpoint
        |
        v
Compares with internal vendors in gdpr-db
        |
        v
New vendors or changes detected?
        |
        v
YES -> Updates vendor records in database
        |
        v
If our published version > 2 versions behind global
        |
        v
Triggers automatic publication
```

### IAB GVL Endpoint

- URL: `https://vendor-list.consensu.org/v2/vendor-list.json`
- Updated periodically by IAB Europe

### Key Code Locations

| Step | Repository | Path |
|------|------------|------|
| Sync logic | gdpr | `smartdev/CmpCoordinator` |
| Vendor comparison | gdpr | `services/attributes_loader_service.py` |
| Auto-publish trigger | n8n | External workflow |

---

## Flow 5: AMP Website Consent

```
AMP page loads
        |
        v
Includes amp-consent component
        |
        v
Component calls: POST /amp/verify-consent
        |
        v
gdpr-mobile-api checks consent
        |
        v
Returns {"consentRequired": true/false}
        |
        v
If required -> shows amp-consent modal
        |
        v
Modal loads: /amp/index.html (from gdpr-mobile-api)
        |
        v
User consents
        |
        v
Consent stored in AMP storage
```

### AMP Integration Points

| Endpoint | Purpose |
|----------|---------|
| `/amp/verify-consent` | Check if consent dialog needed |
| `/amp/get-source` | Get consent frame HTML |
| `/amp/index.html` | Consent dialog in AMP iframe |

### Key Code Locations

| Step | Repository | Path |
|------|------------|------|
| AMP endpoints | gdpr-mobile-api | `adpcmp/` |
| AMP HTML | gdpr-popup | `build/amp.index.html` |

---

## Flow 6: Consent Cookie Structure

### euconsent-v2 Cookie

```
TC String format (IAB TCF v2.2):
CPz...AA (base64 encoded)

Decoded contains:
- Version: 2
- Created: timestamp
- LastUpdated: timestamp
- CmpId: 28 (Ringier CMP ID)
- CmpVersion: current version
- ConsentScreen: 1
- VendorListVersion: current vendor list version
- PolicyVersion: 4
- PurposeConsents: bitfield
- VendorConsents: bitfield
```

### Cookie Flow

1. Popup generates TC String using `@iabtcf/core`
2. String encoded and stored in `euconsent-v2` cookie
3. Domain: `.{site_domain}`
4. Expiry: 365 days
5. Read by dlApi on subsequent visits
6. Compared against current vendor list version

---

## Decision Points Summary

| Decision | Check | If True | If False |
|----------|-------|---------|----------|
| Show popup (web) | cookie version != vendor list version | Load popup | Silent, use cached consent |
| Show popup (mobile) | verify returns !OK | Open WebView | Continue in app |
| Auto-publish | internal version > 2 behind global | Trigger publication | Wait |
| AMP consent | verify-consent returns required | Show amp-consent | Silent |
