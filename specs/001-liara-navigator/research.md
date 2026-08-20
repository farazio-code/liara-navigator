# Technical Research: Liara Navigator MVP

**Date**: 2026-08-20  
**Status**: Complete  
**Spec**: [spec.md](./spec.md)  
**Architecture**: [approved design](../../docs/superpowers/specs/2026-08-20-liara-navigator-architecture-design.md)

## Decision 1 — Deployment Topology

**Decision**: یک Modular Monolith در یک Liara Docker Application، یک Origin، یک HTTP port، یک Instance و یک Uvicorn Worker.

**Rationale**: کمترین هزینه و ریسک Deployment را دارد، CORS و هماهنگی چند سرویس حذف می‌شوند و حذف Sessionهای Memory-only پس از Restart رفتاری صریح است. Liara Dockerfile را Build می‌کند و هر Docker Application یک HTTP web server expose می‌کند.

**Alternatives rejected**:

- Frontend/Backend جدا: دو Deploy و CORS بدون ارزش ضروری MVP.
- Microservices: نقاط شکست و Observability cost بیش از نیاز.
- Serverless: برای SSE، Session memory و Index startup نامتناسب.

## Decision 2 — Frontend and Backend Stack

**Decision**: React 19 + TypeScript 5.x + Vite 7.x؛ Python 3.12 + FastAPI + Pydantic 2.x.

**Rationale**: React/Vite برای UI تعاملی RTL و streaming مناسب است. FastAPI قرارداد Typed، SSE/streaming، Async I/O و OpenAPI را با سربار کم فراهم می‌کند. Python 3.12 با محیط موجود پروژه هم‌راستاست.

**Alternatives rejected**:

- Vue: قابل‌استفاده است ولی Design/implementation conventions پروژه روی React قفل شد.
- Next.js: SSR و Node server دوم برای MVP لازم نیست.
- Django: Admin/ORM کامل ارزش اضافه‌ای برای این محصول ندارد.

## Decision 3 — AI Provider Abstraction

**Decision**: AvalAI از طریق `AIProvider` interface و OpenAI-compatible Python SDK.

**Default routing**:

- Ask: `gpt-5.4-mini`
- Guide/Diagnose: `gpt-5.5`
- Embeddings: `text-embedding-3-small`

**Rationale**: AvalAI Key موجود است و API رسمی آن Responses/Chat، SSE، Function Calling و Embeddings را ارائه می‌دهد. Adapter مانع وابستگی Domain به Provider می‌شود.

**Alternatives rejected**:

- Provider-specific calls در Orchestrator: مهاجرت و تست را دشوار می‌کند.
- یک Reasoning model برای همه Routeها: هزینه Ask را بی‌دلیل بالا می‌برد.
- Local LLM: منابع Docker و زمان مسابقه را افزایش می‌دهد.

**Release rule**: مدل‌ها در Smoke Test با catalog همان Provider اعتبارسنجی می‌شوند؛ Availability لحظه‌ای Provider وارد Readiness نمی‌شود.

## Decision 4 — Knowledge Snapshot Lifecycle

**Decision**: Snapshot خارج از Liara Build در Local/CI کنترل‌شده ساخته، Hash-verified و در `knowledge/snapshots/<version>/` Commit می‌شود. Dockerfile فقط Artifact را Copy می‌کند.

**Rationale**: Build قابل‌بازتولید است، Embedding API Key وارد Docker layer نمی‌شود و Demo به Crawl زنده وابسته نیست.

**Alternatives rejected**:

- Crawl در startup: کند، شکننده و غیرقابل‌بازتولید.
- Runtime rebuild endpoint: مسیر DoS و Secret exposure.
- Managed vector database: سرویس و هزینه اضافه بدون نیاز MVP.

## Decision 5 — Source Trust Model

**Decision**: Domain/repository allowlist، Default Branch و Commit SHA؛ فقط محتوای رسمی Merge‌شده.

**Allowed**: `docs.liara.ir`، `developers.liara.ir`، محتوای فنی رسمی و repositoryهای رسمی `liara-cloud`.

**Denied**: Issues، PRs، Reviews، Comments، Discussions، Forkها، مخزن غیررسمی و user-generated content.

**Rationale**: ریسک prompt injection و knowledge poisoning کاهش می‌یابد و provenance قابل دفاع می‌ماند.

## Decision 6 — Chunking and Indexes

**Decision**: Heading-aware chunks با target 450، max 800 و overlap max 80 token. خروجی شامل `chunks.jsonl`، BM25 index، FAISS vector index و manifest است.

**Rationale**: محدوده برای حفظ توضیح و Code Block کافی است ولی Context را متورم نمی‌کند. Index ثابت برای Corpus کوچک/متوسط مسابقه کم‌هزینه است.

**Alternatives rejected**:

- Fixed-character splitting: Heading و Code relationship را می‌شکند.
- PostgreSQL/pgvector: پشتیبانی افزونه در Liara صریحاً تأیید نشده و برای MVP لازم نیست.
- Elasticsearch: هزینه و سرویس اضافه.

## Decision 7 — Retrieval and Reranking

**Decision**: BM25 top 20 + vector top 20 → Reciprocal Rank Fusion → metadata boost → top 10 → sufficiency gate → top 6 context chunks.

**Rationale**: BM25 برای Error/identifier و Vector برای مفهوم فارسی/انگلیسی مکمل‌اند. RRF مشکل ناهم‌مقیاس بودن scoreها را حل می‌کند.

**Alternatives rejected**:

- LLM reranker: Generation Call و latency اضافه.
- Cross-encoder: dependency/compute اضافه و ریسک کیفیت فارسی.
- Vector-only: Errorهای exact را از دست می‌دهد.

**Execution**: تمام scoringهای CPU-bound با bounded ThreadPool اجرا می‌شوند.

## Decision 8 — Evidence Sufficiency and Conflicts

**Decision**: Candidate رسمی با Locator معتبر الزامی است. Query exact باید critical-token coverage کامل داشته باشد؛ Query معنایی باید top cosine اولیه `>= 0.62` داشته باشد. Threshold با embedding model و Golden Set نسخه‌دار است.

تعارض در Version، Command، Port یا مقدار critical میان منابع هم‌سطح به `conflict_detected` و Conflict/Unknown منجر می‌شود. Freshness فقط با metadata صریح مجاز به ترجیح Source است.

**Rationale**: یک score مبهم برای پاسخ قطعی کافی نیست و منابع متعارض نباید بی‌صدا ادغام شوند.

## Decision 9 — Citation Validation

**Decision**: مدل Claim، نقش و Evidence Span می‌دهد؛ Backend اعتبار را programmatic بررسی می‌کند:

```text
trusted source
AND retrieved chunk
AND exact normalized evidence span
AND critical token coverage == 1.0
AND lexical overlap >= 0.25
AND semantic similarity >= 0.72
```

Claim embeddings در یک Batch request ساخته می‌شوند.

**Rationale**: Citation وجودی به‌تنهایی support را ثابت نمی‌کند. Span دقیق و دو signal مکمل false positive را کاهش می‌دهند. Golden Set همچنان مرجع semantic accuracy است.

**Failure behavior**: Core invalid → Unknown؛ Supporting invalid → حذف همان Claim.

## Decision 10 — Routing and State Machine

**Decision**: Router غیرخوداظهاری و multi-label؛ threshold اولیه `0.65`. Ask یک Generation و Guide/Diagnose حداکثر دو Generation در Turn.

**Rationale**: Route شفاف، قابل‌تست و cost-bounded است. Intentهای Deployment+Database از دست نمی‌روند.

**Out-of-scope**: Guide/Diagnose به Ask تنزل می‌کند. اگر Ask هم evidence کافی نداشته باشد Unknown/Handoff ارائه می‌شود.

## Decision 11 — Liara Tool Safety

**Decision**: مدل فقط Typed Tool Request تولید می‌کند. Policy host، GET method، path template، session resource ownership، timeout، rate limit و output schema را enforce می‌کند.

**Rationale**: Model output untrusted است و نباید مستقیم action اجرا کند.

**Field policy**: allowlist-first typed DTO؛ unknown fields drop؛ raw response request-scoped و non-persistent.

**Failure behavior**: Policy denial/API failure → Docs-only، بدون endpoint retry توسط مدل.

## Decision 12 — Session and Token Storage

**Decision**: برنامه ابتدا یک anonymous session بدون Token می‌سازد تا Ask کار کند؛ Connect همان Session را با Liara Token موجود فقط در process memory ارتقا می‌دهد. Cookie امن برای session ID است. Idle TTL 30 دقیقه و absolute TTL دو ساعت است. Token نامعتبر Session ناشناس را حذف نمی‌کند.

**Rationale**: نیاز به account، encryption-at-rest و token database را حذف می‌کند. برای یک Instance مسابقه کافی است.

**Accepted limitation**: Restart/deploy session را حذف می‌کند. Python secure memory zeroing را تضمین نمی‌کند.

**Alternatives rejected**:

- Token in PostgreSQL: ریسک و key-management اضافه.
- Token in browser storage: XSS exposure.
- Redis: سرویس اضافه و ناسازگار با تصمیم memory-only.

## Decision 13 — API Streaming

**Decision**: same-origin `POST /api/v1/turns/stream` با Fetch streaming و SSE framing. `client_turn_id` idempotency key است.

**Rationale**: POST payload typed است و status eventها UX انتظار را بهبود می‌دهند. Idempotency از هزینه duplicate request جلوگیری می‌کند.

**Alternatives rejected**:

- WebSocket: state/reconnect complexity غیرضروری.
- EventSource GET: payload و secret-safe request semantics نامناسب.
- polling: latency و request count بیشتر.

## Decision 14 — Feedback

**Decision**: فقط `resolved`, optional bounded `reason`, `handoff_requested` و `request_id`. متن آزاد وجود ندارد. ترکیب `resolved=true` با `handoff_requested=true` رد می‌شود.

**Rationale**: برای Containment کافی است و مسیر accidental secret persistence را حذف می‌کند.

**Future rule**: هر free-text آینده باید قبل از persistence scrub شود و raw text ذخیره نشود.

## Decision 15 — Telemetry and Retention

**Decision**: Positive schema بدون content؛ random unlinkable session ID؛ `containment_eligible`؛ route/tool/citation outcomes؛ `handoff_shown` و `handoff_requested`؛ latency/token/cost؛ retention 30 روز.

Confirmed Containment فقط میان Sessionهای واجد شرایط با Outcome صریح محاسبه می‌شود. Feedback Coverage و Conservative Lower Bound با denominator تمام Sessionهای واجد شرایط کنار آن گزارش می‌شوند تا نبود Feedback به‌عنوان موفقیت فرض نشود.

Cleanup هنگام startup و هر شش ساعت با PostgreSQL advisory lock اجرا می‌شود و `maintenance_runs` را ثبت می‌کند.

**Rationale**: Containment، latency و operational quality قابل‌اندازه‌گیری می‌شوند بدون conversation surveillance.

**Boundary**: Platform access logs ممکن است خارج از کنترل Application شامل IP/path باشند؛ این محدودیت در Privacy copy ذکر می‌شود.

## Decision 16 — Rate Limits

**Decision**: in-memory token buckets keyed by `HMAC(IP, process-secret)` و session ID.

- Anonymous session creation: 20 / 10 minutes.
- Connect: 10 total / 10 minutes; 5 failed / 10 minutes.
- Turns: 20 / 10 minutes.
- Liara tools: 10 / 10 minutes.
- Concurrent turns: 2 / session.

**Rationale**: قبل از provider call سوءاستفاده و هزینه مهار می‌شود؛ IP خام Persist نمی‌شود.

## Decision 17 — PostgreSQL Scope

**Decision**: PostgreSQL فقط Telemetry، feedback outcome، evaluation-run metadata و maintenance state را نگه می‌دارد. Alembic migrations و SQLAlchemy 2 async استفاده می‌شوند.

**Rationale**: Schema کوچک و purpose-limited است. Chat، user account و knowledge vectors وارد DB نمی‌شوند.

## Decision 18 — Testing and Evaluation

**Decision**: pytest برای Backend، Vitest/Testing Library برای Frontend، Playwright برای E2E، contract/security tests برای Liara boundary و Golden Set برای semantic quality.

**Golden Set**: حدود 100 سناریو؛ results به model/prompt/snapshot/threshold versions متصل می‌شوند.

**Baseline**: BM25-only search روی همان tasks.

**Rationale**: Unit test به‌تنهایی hallucination و end-to-end traceability را اثبات نمی‌کند.

## Decision 19 — Deployment and Runtime

**Decision**: multi-stage Docker؛ port 8000؛ one Uvicorn worker؛ no persistent disk؛ managed PostgreSQL private connection؛ React static files توسط FastAPI.

**Health**:

- Liveness: process loop.
- Readiness: config، snapshot loaded، database reachable.
- AvalAI/Liara transient health: metrics/circuit breaker، نه readiness.

**Rationale**: External outage نباید restart storm ایجاد کند.

## Decision 20 — Technology Boundaries

### Backend dependency families

- FastAPI, Uvicorn, Pydantic Settings
- SQLAlchemy 2, asyncpg, Alembic
- HTTPX and OpenAI-compatible SDK
- NumPy, FAISS CPU and a compact BM25 implementation
- pytest, pytest-asyncio, respx, coverage, openapi-spec-validator

### Frontend dependency families

- React, React DOM, TypeScript, Vite
- TanStack Query only for request lifecycle/cache control
- Zod for runtime response validation
- Vitest, Testing Library, axe and Playwright

### Deliberately absent

- LangChain/LangGraph
- Redux
- Redis/Celery
- Elasticsearch/Qdrant
- Next.js
- Runtime crawler

YAGNI rule: dependency جدید فقط وقتی پذیرفته می‌شود که یک Requirement مشخص را ساده‌تر و قابل‌تست‌تر کند.

## Official References

- Liara Docker deployment: https://docs.liara.ir/paas/docker/how-tos/deploy-app/
- Liara Docker environment variables: https://docs.liara.ir/paas/docker/how-tos/set-envs/
- Liara API index: https://developers.liara.ir/llms.txt
- AvalAI quickstart: https://docs.avalai.org/en/index
- AvalAI streaming: https://docs.avalai.org/en/guides/streaming-responses
- AvalAI embeddings: https://docs.avalai.ir/en/api-reference/embeddings
- GitHub Spec Kit: https://github.com/github/spec-kit
