# Deployment Information

## Public URL

> **TODO:** Thay thế URL bên dưới bằng URL thật sau khi chạy `railway up`

```
https://your-app.railway.app
```

## Platform

**Railway** — deploy từ `06-lab-complete/` directory

## Deploy Steps

```bash
# 1. Cài Railway CLI (nếu chưa có)
npm i -g @railway/cli

# 2. Login
railway login

# 3. Vào thư mục lab hoàn chỉnh
cd 06-lab-complete

# 4. Khởi tạo project Railway
railway init

# 5. Set environment variables
railway variables set AGENT_API_KEY=my-secret-key-change-this
railway variables set ENVIRONMENT=production
railway variables set DAILY_BUDGET_USD=10.0
railway variables set RATE_LIMIT_PER_MINUTE=10

# 6. Deploy
railway up

# 7. Lấy domain
railway domain
```

## Environment Variables Set

| Variable | Value |
|----------|-------|
| `PORT` | Auto-injected by Railway |
| `ENVIRONMENT` | `production` |
| `AGENT_API_KEY` | *(secret — set via railway variables)* |
| `DAILY_BUDGET_USD` | `10.0` |
| `RATE_LIMIT_PER_MINUTE` | `10` |

## Test Commands

### Health Check
```bash
curl https://your-app.railway.app/health
# Expected: {"status":"ok","version":"1.0.0",...}
```

### Authentication required (no key)
```bash
curl -X POST https://your-app.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Expected: 401 Unauthorized
```

### API Test (with authentication)
```bash
curl -X POST https://your-app.railway.app/ask \
  -H "X-API-Key: my-secret-key-change-this" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Docker?"}'
# Expected: 200 OK with answer
```

### Rate Limit Test
```bash
for i in {1..12}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST https://your-app.railway.app/ask \
    -H "X-API-Key: my-secret-key-change-this" \
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

*Deploy bằng Railway từ `06-lab-complete/` với multi-stage Dockerfile, API key auth, rate limiting (10 req/min), cost guard ($10/day), health checks, và graceful shutdown.*
