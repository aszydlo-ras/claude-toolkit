---
name: gdpr-cmp-expert
description: Expert knowledge for GDPR Consent Management Platform (CMP) architecture at Ringier Axel Springer. Use when discussing GDPR popup, vendor list publication, mobile consent flow, CMP features, consent conversions, or planning GDPR-related functionality. Triggers: "gdpr", "rodo", "cmp", "consent", "vendor list", "popup", "mobile consent", "tcf", "plansza rodo", "publikacja", "zgody", "vendorzy", "wyświetlanie planszy", "popup display", "shouldInitCmp", "verify consent", "OUTDATED".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# GDPR CMP Expert

Domain expertise for Ringier Axel Springer's Consent Management Platform ecosystem.

## Quick Start

1. **Identify functionality area** from user's request
2. **Check required repos** from the mapping below
3. **If missing**, ask user permission to clone via `gh repo clone Ringier-Axel-Springer-PL/{repo_name}`
4. **Provide architecture-aware guidance**

## Functionality → Repository Mapping


### Vendor List Publication (publikacja listy vendorów)

**Repositories:**
- `gdpr` (cmp_coordinator) - generates and uploads vendor-list.json
- `gdpr-admin-panel` - manual publication UI
- `gdpr-db` - stores publication metadata

**Key Files:**
| Repo | File | Purpose |
|------|------|---------|
| `gdpr` | `src/python/adp/modes/cmp_coordinator/tasks/publish_vendor_list.py` | Main publication task |
| `gdpr` | `src/python/adp/modes/cmp_coordinator/tasks/automatic_vendor_list_updater.py` | Auto-publication (n8n) |
| `gdpr` | `src/python/adp/modes/cmp_coordinator/models/vendor_list.py` | Builds vendor-list.json |
| `gdpr-admin-panel` | `src/gql/publication/publish-vendor-list.graphql` | GraphQL mutation |

**Publication Types:**
- **Manual**: triggered from admin panel, `pvl_cre_user` = admin username
- **Automatic**: triggered by n8n/CmpCoordinator, `pvl_cre_user` = "CmpCoordinator"

---

### Popup Display Logic (logika wyświetlania planszy)

**IMPORTANT: Changes to popup display conditions require modifications in BOTH web and mobile!**

**Repositories:**
- `adp-datalayer-api` - **WEB**: decides when to show popup in browsers
- `gdpr-mobile-api` - **MOBILE**: decides when to show popup in native apps (via /verify endpoint)

**Key Files:**
| Repo | File | Function | Purpose |
|------|------|----------|---------|
| `adp-datalayer-api` | `dlApi/dllib/cmp.js` | `shouldInitCmp()` | Web popup display decision |
| `gdpr-mobile-api` | `adpcmp/cmp.py` | `_verify_consent()` | Mobile popup display decision |
| `gdpr-mobile-api` | `adpcmp/vendor_list.py` | `VendorList` | Fetches vendor list with properties |

**Display Logic Flow:**
```
WEB:
  Browser loads page -> adp-datalayer-api -> shouldInitCmp() checks:
    - publicationVersion changed?
    - consent exists?
  -> If true: load gdpr-popup

MOBILE:
  App SDK calls -> gdpr-mobile-api/verify -> _verify_consent() checks:
    - publicationVersion changed?
    - consent valid?
  -> Returns OUTDATED/OK -> SDK decides to show WebView with popup
```

**When modifying display conditions (e.g., version thresholds, new flags):**
1. Add new property to `vendor-list.json` via `gdpr/vendor_list.py`
2. Update `adp-datalayer-api/cmp.js` - `shouldInitCmp()` for web
3. Update `gdpr-mobile-api/cmp.py` - `_verify_consent()` for mobile
4. Update `gdpr-mobile-api/vendor_list.py` to read new property

---

### Popup UI/Styling (wygląd planszy)

**Repositories:**
- `gdpr-popup` - popup components, styles
- `gdpr-admin-panel` - configurable styles (optional)

**Key Files:**
| Repo | File | Purpose |
|------|------|---------|
| `gdpr-popup` | `src/styles/` | CSS/styling |
| `gdpr-popup` | `src/components/` | React components |
| `gdpr-admin-panel` | `src/` | Style configuration UI |

---

### Mobile Consent Flow (zgody mobilne)

**Repositories:**
- `gdpr-mobile-api` - verify endpoint for SDK
- `gdpr-mobile-frame` - WebView wrapper
- `adp-datalayer-api` - loaded in WebView

**Key Files:**
| Repo | File | Purpose |
|------|------|---------|
| `gdpr-mobile-api` | `adpcmp/handlers.py` | `/verify` endpoint |
| `gdpr-mobile-api` | `adpcmp/cmp.py` | Verification logic |
| `gdpr-mobile-api` | `adpcmp/vendor_list.py` | Vendor list fetching |
| `gdpr-mobile-frame` | - | WebView wrapper for apps |

**Flow:**
```
Mobile SDK -> gdpr-mobile-api/verify -> OUTDATED/OK
-> If OUTDATED -> SDK loads gdpr-mobile-frame (WebView)
-> Frame loads adp-datalayer-api?webview=1 -> gdpr-popup in forced mode
```

---

### Vendor Management (zarządzanie vendorami)

**Repositories:**
- `gdpr-admin-panel` - vendor CRUD UI
- `gdpr-db` - database schema
- `gdpr` (cmp_coordinator) - vendor processing

**Key Files:**
| Repo | File | Purpose |
|------|------|---------|
| `gdpr-admin-panel` | `src/` | React admin UI |
| `gdpr-db` | `changelog/changesets/` | DB migrations |

---

### Translations (tłumaczenia)

**Repositories:**
- `gdpr-admin-panel` - translation management UI
- `gdpr-db` - translation storage
- `gdpr` (cmp_coordinator) - translation URLs in vendor-list.json

---

### Metrics/Statistics (statystyki)

**Repositories:**
- `gdpr-ls-processor` - live statistics processing

---

## All Repositories

| Repository | GitHub Path | Purpose |
|------------|-------------|---------|
| `gdpr` | `Ringier-Axel-Springer-PL/gdpr` | Backend coordinator, publication |
| `gdpr-popup` | `Ringier-Axel-Springer-PL/gdpr-popup` | Web popup UI |
| `adp-datalayer-api` | `Ringier-Axel-Springer-PL/adp-datalayer-api` | JS library, CMP logic |
| `gdpr-mobile-api` | `Ringier-Axel-Springer-PL/gdpr-mobile-api` | Mobile SDK verification API |
| `gdpr-mobile-frame` | `Ringier-Axel-Springer-PL/gdpr-mobile-frame` | WebView wrapper |
| `gdpr-admin-panel` | `Ringier-Axel-Springer-PL/gdpr-admin-panel` | Admin UI |
| `gdpr-db` | `Ringier-Axel-Springer-PL/gdpr-db` | Database schema |
| `gdpr-ls-processor` | `Ringier-Axel-Springer-PL/gdpr-ls-processor` | Metrics processing |
| `gdpr-dsa-pages` | `Ringier-Axel-Springer-PL/gdpr-dsa-pages` | DSA pages |
| `gdpr-dsa-db` | `Ringier-Axel-Springer-PL/gdpr-dsa-db` | DSA database |
| `gdpr-uptime` | `Ringier-Axel-Springer-PL/gdpr-uptime` | Uptime monitoring |
| `gdpr-iab-files` | `Ringier-Axel-Springer-PL/gdpr-iab-files` | IAB files |

## Vendor List Structure

URL pattern: `cmp.dreamlab.pl/vendor-list/v3/{tenant_id}/vendor-list.json?v={version}`

Key properties:
```json
{
  "gvlSpecificationVersion": 3,
  "vendorListVersion": 300,
  "publicationVersion": 1500,
  "tcfPolicyVersion": 4,
  "lastUpdated": "2024-01-01T00:00:00Z",
  "purposes": {...},
  "vendors": {...},
  "customVendors": {...},
  "translations": {...}
}
```

## Deployment Order

When changes span multiple repos:
1. **Database** (`gdpr-db`) - schema changes first
2. **Backend** (`gdpr` cmp_coordinator) - API/publication changes
3. **Mobile API** (`gdpr-mobile-api`) - mobile verification
4. **Frontend** (`adp-datalayer-api`, `gdpr-popup`) - web display

## Constraints

- **Never** modify vendor-list.json directly on OCDN
- **Always** check repo availability before referencing files
- **Always** ask before cloning repositories
- Follow existing code conventions (English comments, camelCase)
- Consider IAB TCF v2.2 compliance for consent-related changes
- All code comments and function names must be in English
