# Day 12 Lab - Mission Answers

**Student Name:** Bùi Ngọc
**Date:** 17/04/2026

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found in `01-localhost-vs-production/develop/app.py`

1. **Hardcoded API key** — `OPENAI_API_KEY = "sk-hardcoded-fake-key-never-do-this"` nằm thẳng trong code, bất kỳ ai có quyền đọc source code đều thấy được secret.
2. **Hardcoded database URL** — `postgresql://admin:password123@localhost:5432/mydb` chứa username/password trong code, không dùng được trên môi trường khác.
3. **Debug mode luôn bật** — `DEBUG = True` và `reload=True` làm lộ stack trace, chạy chậm hơn và không an toàn trong production.
4. **Không có health check** — Không có endpoint `/health` hay `/ready`, platform không thể biết khi nào app sẵn sàng hoặc cần restart.
5. **Không xử lý graceful shutdown** — Không có SIGTERM handler, khi container bị stop thì các request đang xử lý sẽ bị cắt đứt đột ngột.
6. **Dùng `print()` thay vì logging** — Print không có timestamp, level, không thể filter, và có thể vô tình in ra secrets.
7. **Bind localhost thay vì 0.0.0.0** — `host="localhost"` chỉ nhận kết nối từ cùng máy, không hoạt động trong container.
8. **Port hardcoded 8000** — Cloud platforms (Railway, Render) inject `PORT` env var động, hardcode sẽ fail.

### Exercise 1.3: Comparison table

| Feature | Develop (❌) | Production (✅) | Why Important? |
|---------|-------------|-----------------|----------------|
| Config | Hardcode trong code | Đọc từ `os.getenv()` | Thay đổi giữa dev/staging/prod không cần sửa code |
| Secrets | Lộ trong source code | Từ environment variables | Bảo mật — không commit secret lên Git |
| Health check | Không có | `GET /health` + `GET /ready` | Platform biết khi nào restart hay route traffic |
| Logging | `print()` | JSON structured với level | Dễ aggregate, filter, alert trong log system |
| Port | Hardcoded 8000 | `int(os.getenv("PORT", "8000"))` | Cloud platforms inject PORT động |
| Host binding | `localhost` | `0.0.0.0` | Container cần bind all interfaces để nhận traffic |
| Shutdown | Đột ngột | SIGTERM handler + graceful drain | Không mất request đang xử lý |
| Debug mode | Luôn `True` | Từ `DEBUG` env var | Production không cần reload, ít lộ thông tin |

---

## Part 2: Docker

### Exercise 2.1: Dockerfile questions (`02-docker/develop/Dockerfile`)

1. **Base image là gì?** `FROM python:3.11` — Python 3.11 full image (~1 GB).
2. **Working directory là gì?** `WORKDIR /app` — Tất cả lệnh sau chạy trong `/app`.
3. **Tại sao COPY requirements.txt trước khi COPY toàn bộ code?** Docker layer caching — nếu requirements.txt không đổi, layer pip install được cache, build nhanh hơn nhiều. Nếu copy toàn bộ code trước, mỗi lần sửa code đều rebuild layer pip install.
4. **CMD vs ENTRYPOINT khác nhau thế nào?** `CMD` có thể bị override khi chạy `docker run image <command>`, còn `ENTRYPOINT` không thể override (chỉ thêm argument). Dùng `CMD` khi muốn cho phép thay đổi command khi chạy container.

### Exercise 2.3: Image size comparison

| Image | Dockerfile | Approx Size |
|-------|-----------|-------------|
| `my-agent:develop` | Single-stage `python:3.11` | ~850 MB |
| `my-agent:production` | Multi-stage `python:3.11-slim` | ~160 MB |
| Difference | | ~80% nhỏ hơn |

**Multi-stage build hoạt động như thế nào:**
- **Stage 1 (builder):** Dùng image đầy đủ với build tools (`gcc`, `libpq-dev`) để compile dependencies.
- **Stage 2 (runtime):** Dùng `python:3.11-slim` làm base, chỉ copy compiled packages từ stage 1. Không có build tools, không có source không cần thiết.
- Kết quả: Image nhỏ hơn 5x, ít attack surface hơn, deploy nhanh hơn.

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

- **URL:** `https://your-app.railway.app` *(điền URL thật sau khi deploy)*
- **Platform:** Railway
- **Deploy steps:**
  ```bash
  npm i -g @railway/cli
  railway login
  cd 06-lab-complete
  railway init
  railway variables set AGENT_API_KEY=my-secret-key-123
  railway variables set ENVIRONMENT=production
  railway up
  railway domain
  ```

**Screenshot:** *(xem `screenshots/` folder)*

---

## Part 4: API Security

### Exercise 4.1-4.3: Test results

**Authentication test:**
```bash
# Không có API key → 401 Unauthorized
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Response: {"detail":"Invalid or missing API key. Include header: X-API-Key: <key>"}

# Với API key đúng → 200 OK
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: dev-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Response: {"question":"Hello","answer":"...","model":"gpt-4o-mini","timestamp":"..."}
```

**Rate limiting test (10 req/min):**
```bash
for i in {1..12}; do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/ask \
    -H "X-API-Key: dev-key-change-me" \
    -H "Content-Type: application/json" \
    -d '{"question": "test"}'
done
# Output: 200 200 200 ... 429 429
# Request 11+ nhận 429 Too Many Requests với header Retry-After: 60
```

### Exercise 4.4: Cost guard implementation

**Cách tiếp cận:**
- Tracking daily cost bằng global variable `_daily_cost` trong `app/cost_guard.py`
- Tính cost dựa trên GPT-4o-mini pricing: $0.00015/1K input tokens, $0.0006/1K output tokens
- Tự động reset về 0 khi sang ngày mới (so sánh `time.strftime("%Y-%m-%d")`)
- Raise `HTTPException(503)` khi daily cost vượt `DAILY_BUDGET_USD`
- Endpoint `/metrics` cho phép monitor spending real-time

**File:** [`06-lab-complete/app/cost_guard.py`](06-lab-complete/app/cost_guard.py)

---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health checks implementation

Đã implement 2 endpoints trong `app/main.py`:

**Liveness probe `/health`** — "App còn sống không?"
```python
@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": settings.app_version,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": _request_count,
    }
```
Platform restart container nếu endpoint này fail.

**Readiness probe `/ready`** — "App sẵn sàng nhận traffic chưa?"
```python
@app.get("/ready")
def ready():
    if not _is_ready:
        raise HTTPException(503, "Not ready")
    return {"ready": True}
```
Load balancer không route traffic đến instance cho đến khi `/ready` trả về 200.

### Exercise 5.2: Graceful shutdown

```python
def _handle_signal(signum, _frame):
    logger.info(json.dumps({"event": "signal", "signum": signum}))

signal.signal(signal.SIGTERM, _handle_signal)
```

Uvicorn chạy với `timeout_graceful_shutdown=30` — khi nhận SIGTERM:
1. Dừng nhận request mới
2. Chờ tối đa 30 giây cho các request hiện tại hoàn thành
3. Thoát gracefully

### Exercise 5.3: Stateless design

**Anti-pattern (❌) — state trong memory:**
```python
conversation_history = {}  # mỗi instance có dict riêng

@app.post("/ask")
async def ask(user_id: str, question: str):
    history = conversation_history.get(user_id, [])  # chỉ hoạt động với 1 instance
```

**Pattern đúng (✅) — state trong Redis:**
```python
import redis

r = redis.from_url(settings.redis_url)

@app.post("/ask")
async def ask(user_id: str, question: str):
    history = r.lrange(f"history:{user_id}", 0, -1)  # shared across all instances
    r.rpush(f"history:{user_id}", question)
    r.expire(f"history:{user_id}", 3600)
```

**Tại sao quan trọng:** Khi scale lên 3 instances, request 1 có thể đến instance A, request 2 đến instance B. Nếu state trong memory, instance B không biết history từ instance A. Redis là single source of truth cho tất cả instances.

### Exercise 5.4: Load balancing với Nginx

```bash
# Khởi động 3 agent instances + Redis + Nginx
docker compose up --scale agent=3

# Test: requests được phân phối đều
for i in {1..9}; do
  curl http://localhost:8000/health
done

# Xem logs để thấy requests đến từng instance
docker compose logs agent | grep "request"
```

Nginx dùng **round-robin** (mặc định): request 1→agent_1, request 2→agent_2, request 3→agent_3, request 4→agent_1,...

### Exercise 5.5: Test stateless behavior

```bash
# 1. Tạo session
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: dev-key-change-me" \
  -d '{"question": "My name is Alice"}'

# 2. Kill một instance
docker compose stop agent_2

# 3. Tiếp tục conversation — vẫn hoạt động vì state trong Redis
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: dev-key-change-me" \
  -d '{"question": "What is my name?"}'
# Trả lời đúng vì Redis vẫn có session data
```
