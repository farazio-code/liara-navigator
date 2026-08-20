# Quickstart: Liara Navigator MVP

**Purpose**: راه‌اندازی Local، اجرای تست‌ها، ساخت Snapshot خارج از Liara و Deployment قابل‌بازتولید  
**Spec**: [spec.md](./spec.md)  
**API**: [contracts/openapi.yaml](./contracts/openapi.yaml)

## 1. Prerequisites

- Python 3.12
- `uv`
- Node.js 22 LTS و npm
- Docker Engine با Compose
- AvalAI API Key برای Live AI و ساخت Snapshot واقعی
- Liara API Token آزمایشی فقط برای manual read-only smoke test
- Liara CLI یا دسترسی Console برای Deploy

هرگز Key یا Token واقعی را در command history اشتراکی، `.env.example`، Screenshot، Repository یا Chat قرار ندهید.

## 2. Install Dependencies

```bash
uv sync --project backend --all-extras --dev
npm --prefix frontend ci
```

Expected:

- `backend/.venv` یا uv-managed environment آماده باشد.
- `frontend/node_modules` از lockfile نصب شود.
- هیچ package version خارج از lockfile resolve نشود.

## 3. Configure Local Environment

```bash
cp .env.example .env.local
```

`.env.local` را فقط روی سیستم خود با این متغیرها پر کنید:

```text
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
DATABASE_URL=postgresql+asyncpg://navigator:navigator@127.0.0.1:5432/navigator
SESSION_HMAC_SECRET=<random-minimum-32-bytes>
AI_BASE_URL=https://api.avalai.ir/v1
AVALAI_API_KEY=<set-locally>
AI_FAST_MODEL=gpt-5.4-mini
AI_REASONING_MODEL=gpt-5.5
AI_EMBEDDING_MODEL=text-embedding-3-small
KNOWLEDGE_SNAPSHOT_VERSION=test-fixture
RETRIEVAL_SEMANTIC_THRESHOLD=0.62
CITATION_SEMANTIC_THRESHOLD=0.72
CITATION_LEXICAL_THRESHOLD=0.25
```

Generate the session secret without printing other environment variables:

```bash
openssl rand -hex 32
```

`.env.local` باید در `.gitignore` باشد.

## 4. Start PostgreSQL

```bash
docker compose -f compose.local.yaml up -d postgres
docker compose -f compose.local.yaml ps
```

Expected: service `postgres` is healthy.

Apply migrations:

```bash
uv run --project backend alembic -c backend/alembic.ini upgrade head
```

## 5. Use the Test Knowledge Snapshot

Unit/integration development باید بدون External AI Key قابل اجرا باشد. Repository یک fixture کوچک در مسیر زیر خواهد داشت:

```text
knowledge/snapshots/test-fixture/
```

Validate its manifest and anchors:

```bash
uv run --project backend python -m knowledge.pipeline.build validate \
  --snapshot knowledge/snapshots/test-fixture
```

Expected: hashes، dimensions، chunk count و source locators PASS شوند.

## 6. Run Backend and Frontend

Terminal 1:

```bash
uv run --project backend uvicorn app.main:app \
  --app-dir backend \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 1 \
  --reload
```

Terminal 2:

```bash
npm --prefix frontend run dev
```

Vite در development درخواست‌های `/api` را به `http://127.0.0.1:8000` proxy می‌کند. Production از FastAPI same-origin استفاده می‌کند.

Open:

```text
http://127.0.0.1:5173
```

در اولین Load، UI باید `POST /api/v1/sessions` را اجرا و Anonymous Session بسازد. Ask پیش از واردکردن Liara Token باید قابل‌استفاده باشد؛ Connect بعداً همان Session را ارتقا می‌دهد.

## 7. Run Test Suites

Backend fast tests:

```bash
uv run --project backend pytest backend/tests/unit backend/tests/contract backend/tests/security -q
```

Backend integration:

```bash
uv run --project backend pytest backend/tests/integration -q
```

Frontend:

```bash
npm --prefix frontend run test
npm --prefix frontend run lint
npm --prefix frontend run typecheck
```

OpenAPI validation:

```bash
uv run --project backend openapi-spec-validator \
  specs/001-liara-navigator/contracts/openapi.yaml
```

E2E with mocked upstreams:

```bash
npm --prefix frontend run build
npx playwright test
```

## 8. Required Security Checks

Run focused tests:

```bash
uv run --project backend pytest \
  backend/tests/security/test_tool_policy.py \
  backend/tests/security/test_field_allowlist.py \
  backend/tests/security/test_session_vault.py \
  backend/tests/security/test_rate_limit.py \
  backend/tests/security/test_no_sensitive_telemetry.py \
  -q
```

Expected guarantees:

- POST/PATCH/DELETE upstream tools cannot be registered or executed.
- Unknown/future-secret fields are discarded.
- Cross-session resource refs are rejected.
- Token is absent from repr/log/telemetry/model context.
- Feedback rejects every unknown/free-text property.

## 9. Build a Real Knowledge Snapshot Offline

این مرحله روی سیستم Local امن یا CI جدا انجام می‌شود؛ هرگز داخل Liara Docker Build اجرا نمی‌شود.

```bash
read -r -s AVALAI_API_KEY
export AVALAI_API_KEY
uv run --project backend python -m knowledge.pipeline.build create \
  --sources knowledge/sources.yaml \
  --output knowledge/snapshots/2026-08-20.1 \
  --embedding-model text-embedding-3-small
unset AVALAI_API_KEY
```

Validate:

```bash
uv run --project backend python -m knowledge.pipeline.build validate \
  --snapshot knowledge/snapshots/2026-08-20.1 \
  --verify-remote-anchors
```

Review the manifest, then add only generated artifacts and source configuration:

```bash
git add knowledge/sources.yaml knowledge/snapshots/2026-08-20.1
git diff --cached --stat
```

قبل از Commit بررسی کنید هیچ `.env`، token، raw crawl cache یا user content stage نشده باشد.

## 10. Run Golden Set and Baseline

```bash
uv run --project backend python -m evals.runner \
  --cases evals/golden-set/cases.jsonl \
  --snapshot knowledge/snapshots/2026-08-20.1 \
  --output evals/reports/2026-08-20.1.json

uv run --project backend python -m evals.baselines.bm25 \
  --cases evals/golden-set/cases.jsonl \
  --snapshot knowledge/snapshots/2026-08-20.1 \
  --output evals/reports/2026-08-20.1-bm25.json
```

Acceptance before Demo:

- Citation Accuracy ≥ 95%
- Citation Coverage ≥ 90%
- Correct Unknown ≥ 90%
- False-answer ≤ 5%
- Tool Selection ≥ 90%
- Median Time-to-resolution improvement ≥ 35%

Threshold تغییر نمی‌کند مگر هر دو report بعد از تغییر دوباره تولید شوند.

## 11. Build Production Image

Docker build نباید AvalAI Key یا Liara Token دریافت کند:

```bash
docker build \
  --build-arg KNOWLEDGE_SNAPSHOT_VERSION=2026-08-20.1 \
  -t liara-navigator:2026-08-20.1 .
```

Verify image locally:

```bash
docker run --rm \
  --env-file .env.local \
  --add-host host.docker.internal:host-gateway \
  --env DATABASE_URL=postgresql+asyncpg://navigator:navigator@host.docker.internal:5432/navigator \
  -p 8000:8000 \
  liara-navigator:2026-08-20.1
```

```bash
curl --fail http://127.0.0.1:8000/api/v1/health/live
curl --fail http://127.0.0.1:8000/api/v1/health/ready
```

## 12. Deploy to Liara

1. در Liara یک Docker Application با port `8000`، یک Instance و شبکه خصوصی مناسب بسازید.
2. PostgreSQL مدیریت‌شده را در همان private network ایجاد کنید.
3. Environment Variables production را در Console تنظیم کنید؛ Liara user token متغیر محیطی نیست.
4. Migration را با release/pre-start command یک‌بار اجرا کنید.
5. Repository/zip را Deploy کنید؛ Liara فقط Dockerfile و committed snapshot را Build می‌کند.
6. Health endpoints، Snapshot version و retention status را بررسی کنید.

Environment production:

```text
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
DATABASE_URL=<private-postgresql-url>
SESSION_HMAC_SECRET=<production-random-secret>
AI_BASE_URL=https://api.avalai.ir/v1
AVALAI_API_KEY=<production-key>
AI_FAST_MODEL=gpt-5.4-mini
AI_REASONING_MODEL=gpt-5.5
AI_EMBEDDING_MODEL=text-embedding-3-small
KNOWLEDGE_SNAPSHOT_VERSION=2026-08-20.1
```

## 13. Live Smoke Tests

### AI

از UI یک Ask ساده ارسال کنید و بررسی کنید:

- Ask بدون واردکردن Liara Token اجرا می‌شود؛
- status events دیده می‌شوند؛
- Final Answer Citation دارد؛
- Provider request ID فقط در operational log پاک‌سازی‌شده ثبت می‌شود؛
- Ask بیش از یک Generation Call ندارد.

### Liara read-only

با یک Token آزمایشی:

1. Connect کنید.
2. Resource را انتخاب کنید.
3. Diagnose اجرا کنید.
4. Tool summary و Citation را ببینید.
5. «بررسی مجدد وضعیت» را بزنید.
6. Disconnect کنید و مطمئن شوید Resource Ref قبلی 401/404 امن می‌دهد.

هیچ Write endpoint یا Production-critical token برای Smoke Test استفاده نشود.

## 14. Demo Readiness

- [ ] Golden report و BM25 comparison آماده است.
- [ ] Ask، Guide، Diagnose و Unknown هرکدام یک سناریوی rehearsed دارند.
- [ ] Project Inspector روی یک Resource آزمایشی واقعی کار می‌کند.
- [ ] Liara/AvalAI failure fallback نمایش داده شده است.
- [ ] Privacy limitation مربوط به platform access log در توضیحات موجود است.
- [ ] Deploy URL، health و snapshot version ثبت شده‌اند.
- [ ] Token قبل و بعد Demo در Browser storage وجود ندارد.
