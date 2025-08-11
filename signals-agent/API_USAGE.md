# API Usage Guide

## Discovery Endpoint

The `/discovery` endpoint now has a configurable limit for the number of proposals returned.

### Default Behavior
- **Default limit**: 5 proposals
- **Maximum limit**: 10 proposals (capped for performance)
- **Minimum limit**: 1 proposal

### How to Use

#### Default (5 proposals)
```bash
curl -X POST http://127.0.0.1:8000/discovery \
  -H "Content-Type: application/json" \
  -d '{"query": "people on a diet"}'
```

#### Custom limit (1-10 proposals)
```bash
curl -X POST http://127.0.0.1:8000/discovery \
  -H "Content-Type: application/json" \
  -d '{"query": "people on a diet", "limit": 8}'
```

#### Maximum limit (10 proposals)
```bash
curl -X POST http://127.0.0.1:8000/discovery \
  -H "Content-Type: application/json" \
  -d '{"query": "people on a diet", "limit": 10}'
```

### Examples

#### Test with default limit (5 proposals)
```bash
curl -s -X POST http://127.0.0.1:8000/discovery \
  -H "Content-Type: application/json" \
  -d '{"query": "luxury cars"}' | jq '.total_proposals'
# Returns: 5
```

#### Test with custom limit (8 proposals)
```bash
curl -s -X POST http://127.0.0.1:8000/discovery \
  -H "Content-Type: application/json" \
  -d '{"query": "luxury cars", "limit": 8}' | jq '.total_proposals'
# Returns: 8
```

#### Test with limit higher than max (capped at 10)
```bash
curl -s -X POST http://127.0.0.1:8000/discovery \
  -H "Content-Type: application/json" \
  -d '{"query": "luxury cars", "limit": 15}' | jq '.total_proposals'
# Returns: 10
```

### Notes
- The limit controls both the number of ranked signals and the number of AI-generated proposals
- Higher limits may take longer to process due to AI generation time
- The limit is capped at 10 for performance reasons
- If no limit is specified, it defaults to 5 proposals

## Frontend Usage

The frontend now includes a dropdown to easily set the response limit:

1. **Navigate to the Discovery page** at `http://localhost:3000`
2. **Fill in your search query** (required)
3. **Select the Response Limit** from the dropdown:
   - Options range from 1 to 10 proposals
   - Default is 5 proposals
   - Maximum is 10 proposals
4. **Optionally select Principal and Platforms**
5. **Click "🔍 Discover Signals"** to search

The dropdown makes it easy to experiment with different numbers of proposals without needing to modify API calls manually.
