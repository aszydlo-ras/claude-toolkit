# AdPlatform Development Rules - Detailed Reference

## CHANGELOG Requirements

### Version Format (Semantic Versioning)
- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

### Entry Format
```markdown
## [2.9.2] - 2025-10-22
### Changed
- Optimisation using cached_properties in line item model [@aszydlo]

### Fixed
- Bug fix description [@aszydlo]
```

### Categories (Keep a Changelog standard)
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes

## Testing Requirements

### AdPlatform2 (Python)
```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_function():
    mock_service = AsyncMock()
    mock_service.get_data.return_value = {"id": "123"}

    result = await my_function(mock_service)

    assert result["id"] == "123"
    mock_service.get_data.assert_called_once()
```

### AdPlatform Python (Tornado)
```python
from tornado.testing import gen_test

class MyModeTest(TestCase):
    @gen_test
    async def test_feature(self):
        result = await self.mode.process()
        assert result['status'] == 'ok'
```

### AdPlatform Go
```go
func TestMyFunction(t *testing.T) {
    tests := []struct {
        name     string
        input    string
        expected string
    }{
        {"valid input", "test", "result"},
        {"empty input", "", "default"},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := MyFunction(tt.input)
            assert.Equal(t, tt.expected, result)
        })
    }
}
```

## Code Style Rules

### Python Type Hints (Required)
```python
from typing import Optional, List

async def process_items(
    items: List[dict],
    config: Optional[dict] = None
) -> dict:
    ...
```

### Docstring Format
```python
async def calculate_budget(
    line_item_id: int,
    date_range: tuple[datetime, datetime]
) -> float:
    """
    Calculate budget for a line item.

    Args:
        line_item_id: The line item identifier
        date_range: Start and end datetime tuple

    Returns:
        Calculated budget amount

    Raises:
        ValueError: If date_range is invalid
    """
    ...
```

### Import Order
```python
# Standard library
import asyncio
from datetime import datetime

# Third-party
import aiohttp
from pydantic import BaseModel

# Local/internal
from adp_observability import MetricsBase
from .services import MyService
```

## Security Rules

### Secrets Management

**WRONG:**
```python
api_key = "sk-1234567890"
db_password = "secret123"
```

**CORRECT (AdPlatform2):**
```python
from adp_config import config
api_key = config.api_key
```

**CORRECT (AdPlatform):**
```python
api_key = self.config_worker.get('api_key')
```

### Files to NEVER commit
- `.env` files with real credentials
- `credentials.json`
- Private keys (`*.pem`, `*.key`)
- `.secrets/` directory contents

## CI/CD Requirements

### Version Tag Format
```
[rel|dev|rc1]-{version}-{timestamp}
```
- `rel` - Production release (from master)
- `dev` - Development release
- `rcX` - Release candidate

### GitHub Actions Workflow Pattern
```yaml
on:
  push:
    paths:
      - "projects/my_project/**"
    branches:
      - master
  pull_request:
    paths:
      - "projects/my_project/**"
```

## Shared Libraries Usage

### AdPlatform2 Libraries
| Library | Purpose | Import |
|---------|---------|--------|
| `adp_observability` | Metrics | `from adp_observability import MetricsBase` |
| `adp_queue` | SQS/RabbitMQ | `from adp_queue import SQSMessageDispatcher` |
| `adp_dynamodb` | DynamoDB | `from adp_dynamodb import DynamoDBClient` |
| `adp_elasticache` | Redis | `from adp_elasticache import RedisClient` |
| `adp_config` | Configuration | `from adp_config import AdpConfigModel` |
| `adp_starlette` | HTTP server | `from adp_starlette import AdpStarlette` |

### AdPlatform Libraries
| Component | Import |
|-----------|--------|
| Mode base | `from adp_sdk36.mode import AbstractMode` |
| Config | `from adp.services.abstractions.configurable_service import ConfigurableService` |
| Queue | `from adp.services.abstractions.queue_message_dispatcher import RmqMessageDispatcher` |
| Metrics | `import aio_maas as maas` |

## Angular Rules (das-panel)

### Required Patterns
```typescript
@Component({
    selector: 'app-my-component',
    changeDetection: ChangeDetectionStrategy.OnPush,  // REQUIRED
    standalone: true,
    imports: [CommonModule, ...],
})
export class MyComponent {
    // Signal-based inputs (REQUIRED)
    public data = input<any[]>([]);
    public required = input.required<string>();

    // Computed signals for derived state
    protected filteredData = computed(() =>
        this.data().filter(item => item.active)
    );
}
```

### Control Flow (use new syntax)
```html
@if (loading()) {
    <app-loading/>
} @else {
    <app-content [data]="data()"/>
}

@for (item of items(); track item.id) {
    <app-item [item]="item"/>
}
```

## Go Rules

### Clean Architecture
```
api/http/          # API Layer
internal/          # Domain Layer
infrastructure/    # Infrastructure Layer
```

### Required Practices
- Use `fiber.New()` for HTTP servers
- Use `uber-go/zap` for logging
- Run tests with `-race` flag
- Use table-driven tests
