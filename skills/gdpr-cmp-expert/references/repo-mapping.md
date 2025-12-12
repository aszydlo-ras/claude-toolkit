# Repository to Scenario Mapping

## Quick Reference

| Scenario | Primary Repos | Secondary Repos |
|----------|---------------|-----------------|
| Web popup UI changes | `gdpr-popup` | `adp-datalayer-api` |
| Consent logic changes | `adp-datalayer-api` | `gdpr-popup` |
| Mobile integration | `gdpr-mobile-api` | `gdpr-mobile-frame` |
| Publication process | `gdpr` | `gdpr-db` |
| Admin panel features | `gdpr-admin-panel` | `gdpr-db` |
| Monitoring/metrics | `gdpr-ls-processor` | - |
| DSA compliance | `gdpr-dsa-pages` | `gdpr-dsa-db` |
| Uptime monitoring | `gdpr-uptime` | - |

## Repository Details

### gdpr-popup

- **URL**: `https://github.com/Ringier-Axel-Springer-PL/gdpr-popup`
- **Tech**: JavaScript, Preact, Webpack, Babel
- **Purpose**: Consent popup UI component displayed on websites
- **Key paths**:
  - `src/` - Main source code
  - `src/components/` - React/Preact components
  - `src/styles/` - CSS styling
  - `src/lib/` - Utility libraries
- **Build output**: `cmp.bundle.js`, `portal.html`, `amp.index.html`

### adp-datalayer-api

- **URL**: `https://github.com/Ringier-Axel-Springer-PL/adp-datalayer-api`
- **Tech**: JavaScript, Webpack, Grunt, Mocha/Chai
- **Purpose**: Frontend JS library that loads on websites, manages CMP initialization
- **Key paths**:
  - `dlApi/dllib/cmp.js` - **Main CMP logic** (~2300 lines)
  - `dlApi/dllib/cmp-stub.js` - CMP stub implementation
  - `dlApi/dllib/cmp-config-manager.js` - Configuration management
  - `dlApi/dllib/consent-api.js` - Consent API handler
  - `dlApi/dllib/iabtcf-stub.js` - IAB TCF implementation
- **Build output**: `dl.boot.min.js`, `dl.init.min.js`

### gdpr (cmp_coordinator)

- **URL**: `https://github.com/Ringier-Axel-Springer-PL/gdpr`
- **Tech**: Python, Tornado, AsyncIO
- **Purpose**: Backend services for CMP - vendor list publication, synchronization
- **Key paths**:
  - `src/python/adp/modes/cmp_coordinator/` - **Publication logic**
  - `src/python/adp/modes/cmp_coordinator/services/vendor_list_publisher_service.py`
  - `src/python/adp/modes/cmp_coordinator/services/gdpr_translation_service.py`
  - `src/python/adp/modes/cmp_config_api/` - Configuration API
  - `src/python/adp/modes/cmp_cookies/` - Cookie management
- **Deployment**: aiorunner mode

### gdpr-admin-panel

- **URL**: `https://github.com/Ringier-Axel-Springer-PL/gdpr-admin-panel`
- **Tech**: React 17, TypeScript, Apollo Client, Material-UI, GraphQL
- **Purpose**: Admin UI for managing CMP configuration
- **Key paths**:
  - `src/` - Main source code (16 directories)
  - `config/` - Environment configuration
  - `tests/` - Cypress/Jest tests
- **Features**: Vendor management, translations, styles, publication triggers

### gdpr-mobile-api

- **URL**: `https://github.com/Ringier-Axel-Springer-PL/gdpr-mobile-api`
- **Tech**: Python, Tornado
- **Purpose**: API for mobile SDK consent verification
- **Key paths**:
  - `adpcmp/` - Main handlers (12 directories)
  - `templates/` - Response templates
  - `tests/` - Test suite
- **Endpoints**:
  - `GET /mobile` - Mobile app verification
  - `GET /amp/verify-consent` - AMP verification
  - `GET /amp/get-source` - AMP consent frame source

### gdpr-mobile-frame

- **URL**: `https://github.com/Ringier-Axel-Springer-PL/gdpr-mobile-frame`
- **Tech**: HTML, JavaScript, CSS, Grunt
- **Purpose**: Static HTML page for WebView in mobile apps
- **Key paths**:
  - `src/` - Source files
- **Features**: Lightweight wrapper that loads dlApi and popup in forced mode

### gdpr-db

- **URL**: `https://github.com/Ringier-Axel-Springer-PL/gdpr-db`
- **Tech**: PostgreSQL, Liquibase/Flyway
- **Purpose**: Database schema and migrations for CMP
- **Key paths**:
  - `functions/` - Database functions
  - `templates/` - Firestore templates
  - `tests/` - Database tests

### gdpr-ls-processor

- **URL**: `https://github.com/Ringier-Axel-Springer-PL/gdpr-ls-processor`
- **Tech**: TypeScript, Node.js
- **Purpose**: Live statistics processing for CMP metrics
- **Key paths**:
  - `src/` - TypeScript source
  - `tests/` - Test suite
- **Integration**: Tag Manager, Grafana

### Supporting Repositories

| Repo | Tech | Purpose |
|------|------|---------|
| `gdpr-dsa-pages` | JavaScript, Webpack | Digital Services Act compliance pages |
| `gdpr-dsa-db` | PostgreSQL, Liquibase | DSA-related database |
| `gdpr-uptime` | JavaScript, Cypress | Monitoring and health checks |
| `gdpr-iab-files` | Python | IAB specification files processing |

## Scenario-Based Repository Selection

### Scenario: "Change popup button color"

1. **Primary**: `gdpr-popup` - styles in `src/styles/`
2. **Check**: Is it configurable via admin panel?
3. **If yes**: Also need `gdpr-admin-panel` for style settings

### Scenario: "Add new vendor category"

1. **Primary**: `gdpr-db` - schema changes
2. **Secondary**: `gdpr-admin-panel` - UI for new category
3. **Also**: `gdpr` (cmp_coordinator) - publication logic

### Scenario: "Debug mobile consent issue"

1. **Primary**: `gdpr-mobile-api` - verify endpoint logic
2. **Secondary**: `gdpr-mobile-frame` - WebView implementation
3. **If popup issue**: Also `gdpr-popup` and `adp-datalayer-api`

### Scenario: "Investigate vendor list not updating"

1. **Primary**: `gdpr` (cmp_coordinator) - publication service
2. **Secondary**: `gdpr-db` - vendor data storage
3. **Check**: n8n workflow configuration (external)
