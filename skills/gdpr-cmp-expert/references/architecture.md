# GDPR CMP Architecture

## Component Diagram

```
+-----------------------------------------------------------------------------+
|                              WEB BROWSER                                     |
+-----------------------------------------------------------------------------+
|  +---------------------+    +------------------+    +------------------+    |
|  |   Website (JS)      |--->| adp-datalayer-api|--->|   gdpr-popup     |    |
|  |                     |    |   (cmp.js)       |    |   (UI)           |    |
|  +---------------------+    +--------+---------+    +------------------+    |
|                                      |                                       |
|                                      | fetch vendor-list.json                |
|                                      v                                       |
|                              +------------------+                            |
|                              |   OCDN (CDN)     |                            |
|                              | vendor-list.json |                            |
|                              +------------------+                            |
+-----------------------------------------------------------------------------+

+-----------------------------------------------------------------------------+
|                           MOBILE APPLICATION                                 |
+-----------------------------------------------------------------------------+
|  +---------------------+    +------------------+    +------------------+    |
|  |   Mobile SDK        |--->| gdpr-mobile-api  |    |gdpr-mobile-frame |    |
|  |   (iOS/Android)     |    |   /verify        |    |   (WebView)      |    |
|  +---------------------+    +------------------+    +--------+---------+    |
|                                      |                       |              |
|                                      |                       v              |
|                                      |              +------------------+    |
|                                      |              | adp-datalayer-api|    |
|                                      |              | + gdpr-popup     |    |
|                                      |              +------------------+    |
+-----------------------------------------------------------------------------+

+-----------------------------------------------------------------------------+
|                           BACKEND SERVICES                                   |
+-----------------------------------------------------------------------------+
|  +---------------------+    +------------------+    +------------------+    |
|  | gdpr-admin-panel    |--->|      gdpr        |--->|      OCDN        |    |
|  | (React UI)          |    | cmp_coordinator  |    | vendor-list.json |    |
|  +---------------------+    +--------+---------+    +------------------+    |
|                                      |                                       |
|                                      |                                       |
|                                      v                                       |
|                              +------------------+                            |
|                              |     gdpr-db      |                            |
|                              |   (PostgreSQL)   |                            |
|                              +------------------+                            |
+-----------------------------------------------------------------------------+
```

## Data Flow Details

### Web Consent Collection

1. Website loads `adp-datalayer-api` (dlApi)
2. `cmp.js` module fetches vendor list from OCDN
3. Compares vendor list version with cookie (`euconsent-v2`)
4. If versions differ -> loads `gdpr-popup` iframe
5. User interacts with popup -> consent saved to cookie
6. Cookie contains TCF v2.2 compliant consent string

### Mobile Consent Verification

1. Mobile SDK (iOS/Android) stores consent string locally
2. SDK calls `gdpr-mobile-api /verify` endpoint
3. API decodes consent string, checks vendor list version
4. Returns status: OK | OUTDATED | EMPTY | INVALID
5. If not OK -> SDK opens WebView with `gdpr-mobile-frame`
6. WebView loads popup in forced mode (always shows)
7. New consent passed back to SDK via JavaScript bridge

### Vendor List Publication

1. Admin configures vendors in `gdpr-admin-panel`
2. Data saved via GraphQL to `gdpr-db`
3. `cmp_coordinator` triggered (manually or via n8n)
4. Coordinator generates `vendor-list.json`
5. JSON uploaded to OCDN S3 bucket
6. Accelerator proxy updated to point to new version

## Key Technologies

| Technology | Purpose |
|------------|---------|
| TCF v2.2 | IAB Transparency & Consent Framework - consent string format |
| IAB GVL | Global Vendor List - source of truth for vendor definitions |
| OCDN | Object CDN for static file hosting |
| Accelerator | Proxy/CDN layer for routing requests |
| PostgreSQL | Primary database for CMP data |
| GraphQL | API communication between admin panel and backend |

## Deployment Infrastructure

| Environment | Description |
|-------------|-------------|
| INT (Integration) | `C_DEV`, `B_c2a-int` - testing environment |
| PROD (Production) | `A_c2a` - production environment |

### Main Domains

| Domain | Purpose |
|--------|---------|
| `cmp.ringpublishing.com` | Main CMP domain |
| `cmp.dreamlab.pl` | Development/legacy domain |
| `lib.onet.pl/s.csr/` | dlApi hosting |

### URL Patterns

- Vendor list: `cmp.dreamlab.pl/vendor-list/v3/{tenant_id}/vendor-list.json?v={version}`
- Mobile endpoint: `cmp.ringpublishing.com/{tenant}/mobile`
- AMP endpoint: `cmp.ringpublishing.com/{tenant}/amp/get-source`
- dlApi init: `lib.onet.pl/s.csr/build/dlApi/dl.boot.min.js`
