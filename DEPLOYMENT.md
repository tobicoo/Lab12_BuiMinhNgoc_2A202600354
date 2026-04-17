# Deployment Information

## Public URL

```
https://lab12-buiminhngoc-2a202600354.onrender.com
```

## Platform

**Render** — deploy từ `06-lab-complete/` directory (Root Directory setting)

## Environment Variables Set

| Variable | Value |
|----------|-------|
| `PORT` | Auto-injected by Render |
| `ENVIRONMENT` | `production` |
| `AGENT_API_KEY` | *(secret — set via Render dashboard)* |
| `DAILY_BUDGET_USD` | `10.0` |
| `RATE_LIMIT_PER_MINUTE` | `10` |

## Test Commands

### Health Check
```bash
curl https://lab12-buiminhngoc-2a202600354.onrender.com/health
# Expected: {"status":"ok","version":"1.0.0",...}
```

### Authentication required (no key)
```bash
curl -X POST https://lab12-buiminhngoc-2a202600354.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Expected: 401 Unauthorized
```

### API Test (with authentication)
```bash
curl -X POST https://lab12-buiminhngoc-2a202600354.onrender.com/ask \
  -H "X-API-Key: BuiMinhNgoc2A202600354" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Docker?"}'
# Expected: 200 OK with answer
```

### Rate Limit Test
```bash
for i in {1..12}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST https://lab12-buiminhngoc-2a202600354.onrender.com/ask \
    -H "X-API-Key: BuiMinhNgoc2A202600354" \
    -H "Content-Type: application/json" \
    -d '{"question": "test"}'
done
# Expected: 200 × 10 times, then 429 × 2 times
```

## Screenshots

- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)

---

*Deploy bằng Render từ `06-lab-complete/` với multi-stage Dockerfile, API key auth, rate limiting (10 req/min), cost guard ($10/day), health checks, và graceful shutdown.*
