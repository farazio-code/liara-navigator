# Liara Navigator — Product and Architecture Design

**Status:** Approved architecture, pre-implementation  
**Date:** 2026-08-20  
**Product:** Liara Navigator  
**Tagline:** از سؤال تا حل مسئله، با منبع دقیق

## 1. Executive Decision

Liara Navigator یک Documentation Chatbot نیست. محصول یک دستیار شواهد‌محور برای Ask، Guide و Diagnose است که پاسخ مستندات رسمی را، در صورت اجازه کاربر، با وضعیت Read-only واقعی منابع همان حساب Liara تطبیق می‌دهد.

معماری MVP یک Modular Monolith قابل Deploy روی Liara است:

- Frontend: React + TypeScript + Vite
- Backend: Python + FastAPI
- AI Provider: AvalAI از طریق OpenAI-compatible Adapter
- Retrieval: Snapshot ثابت و نسخه‌دار، BM25 + Vector Search
- Runtime state: حافظه یک Backend Instance
- Persistent storage: PostgreSQL فقط برای Telemetry و Evaluation Metadata
- Deployment: یک Docker Application، یک HTTP Port، یک Instance، یک Worker

## 2. Problem and Product Boundary

کاربر Liara معمولاً در یکی از این نقاط شکست می‌خورد:

1. سند مناسب را میان تعداد زیاد صفحات پیدا نمی‌کند.
2. سند را پیدا می‌کند اما پاسخ متناسب با سؤال یا خطای خود را استخراج نمی‌کند.
3. برای تکمیل یک Task باید چند منبع را ترکیب کند.
4. نمی‌داند وضعیت واقعی پروژه‌اش با پیش‌فرض‌های مستندات هم‌خوان است یا نه.
5. هنگام نبود شواهد کافی، ابزارهای عمومی پاسخ قطعی اما غیرقابل‌اعتماد می‌دهند.

MVP سه Mode دارد:

- **Ask:** پاسخ سریع روی کل Snapshot مستندات رسمی.
- **Guide:** راهنمای مرحله‌ای هدف‌محور برای Deployment، Domain/DNS/SSL و Database.
- **Diagnose:** عیب‌یابی چندمرحله‌ای با امکان خواندن وضعیت واقعی منابع کاربر.

Guide و Diagnose خارج از سه Task Family به‌طور شفاف به Ask تنزل می‌کنند. Intent می‌تواند چند Task Family را هم‌زمان فعال کند.

## 3. Architecture Options Considered

### Option A — Modular Monolith + Static Hybrid Index (Selected)

یک Deploy، Index ثابت، State موقت و PostgreSQL محدود. کمترین ریسک عملیاتی و بیشترین قابلیت Demo و تست را برای زمان مسابقه دارد.

### Option B — Separate Frontend/Backend + Elasticsearch

مقیاس‌پذیری Retrieval بیشتر، اما دو Deploy، CORS، هزینه و پیچیدگی عملیاتی اضافه دارد.

### Option C — Microservices + Vector Database + Redis

برای Production آینده مناسب است، ولی برای MVP باعث افزایش نقاط شکست و کاهش سرعت تحویل می‌شود.

Option A انتخاب شد. Microservice، Redis، Runtime Crawler و Vector DB مستقل خارج از Scope هستند.

## 4. System Context

```text
Browser
  │ HTTPS + Fetch/SSE
  ▼
FastAPI Modular Monolith
  ├── React Static UI
  ├── Session Vault (memory only)
  ├── Intent Router
  ├── Agent State Machine
  ├── Hybrid Retriever
  ├── Citation Validator
  ├── Tool Policy Layer
  ├── Liara Read-only Adapters
  ├── AvalAI Provider Adapter
  ├── Telemetry Writer
  └── Retention Maintenance Task
            │
            ▼
        PostgreSQL

External systems:
  - AvalAI API
  - Liara PaaS/Domain/DNS/DBaaS GET APIs
  - Versioned official knowledge snapshot bundled with release
```

## 5. Request Routing

Router خروجی ساختاریافته `mode`، آرایه `task_families`، پرچم `needs_project_state` و `confidence` را می‌سازد. Confidence خوداظهاری LLM استفاده نمی‌شود؛ امتیاز از انتخاب Mode توسط کاربر، قواعد قابل‌تست، سیگنال Error و شباهت Query Embedding با توصیف Task Familyها ساخته می‌شود.

- `confidence >= 0.65`: Route اجرا می‌شود.
- `confidence < 0.65`: یک سؤال کوتاه Clarification نمایش داده می‌شود.
- Threshold با Golden Set کالیبره و نسخه‌دار می‌شود.

### 5.1 Scope Matrix

- Ask: همه منابع رسمی موجود در Snapshot.
- Guide/Diagnose: Deployment، Domain/DNS/SSL و Database.
- Full coverage: Loop کامل.
- Partial coverage: Loop برای بخش پشتیبانی‌شده و Ask برای بخش باقی‌مانده.
- No workflow coverage: Ask با پیام محدودیت شفاف.
- Insufficient evidence: Unknown یا Handoff.

Static Site بر اساس وجود Playbook واقعی Deployment طبقه‌بندی می‌شود، نه صرفاً Keyword. Billing در MVP Workflow کامل ندارد و به Ask تنزل می‌کند.

## 6. Agent State Machine

### 6.1 Ask Fast Path

```text
Input Guard
→ Hybrid Retrieve
→ Reciprocal Rank Fusion
→ Evidence Sufficiency Gate
→ One Generation Call
→ Programmatic Citation Validation
→ Final Answer or Unknown
```

Ask Planning یا Project Tool Loop ندارد. یک Batch Embedding Call برای Query و یک Batch Embedding Call برای Claim Validation مجاز است و جدا از Generation اندازه‌گیری می‌شود.

### 6.2 Guide

```text
Scope Gate
→ Goal and Context Extraction
→ Clarification if Required
→ Multi-step Plan
→ Current-step Retrieval
→ Optional Read-only Inspection
→ Present One Step
→ User Confirmation
→ Validate or Continue in Next Turn
```

### 6.3 Diagnose

```text
Scope Gate
→ Collect Error Context
→ Read-only Project State
→ Retrieve Documentation
→ Rank Hypotheses
→ Select Safe Diagnostic Check
→ User Action
→ Explicit Refresh Trigger
→ Resolve, Recover, or Handoff
```

Refresh فقط پس از پیام بعدی کاربر مانند «انجام دادم» یا فشردن دکمه «بررسی مجدد وضعیت» رخ می‌دهد. Polling و Background Diagnosis وجود ندارد.

### 6.4 Model Call Budget

- Ask: حداکثر یک Generation Call در Turn.
- Guide/Diagnose: حداکثر دو Generation Call در Turn.
- فراخوانی سوم ممنوع است؛ ادامه به Turn بعد، Clarification یا Unknown منتقل می‌شود.
- Tool Call و Embedding Call جداگانه اندازه‌گیری می‌شوند.

## 7. Tool Execution Boundary

مدل فقط Tool Request Typed می‌سازد. Policy Layer قبل از اجرا Tool Registry، Host، GET Method، Path Template، تعلق `resource_ref` به Inventory همان Session، Rate Limit، Timeout و وجود Field Schema را بررسی می‌کند. مدل اجازه ارائه URL، Header یا API Token به Tool Executor ندارد.

اگر Tool Request رد شود، Tool اجرا و Retry نمی‌شود؛ پاسخ به Docs-only تنزل می‌کند، پیام شفاف نشان داده می‌شود و فقط کد پاک‌سازی‌شده مانند `POLICY_DENIED` ثبت می‌شود.

## 8. Read-only Project Inspector

Inspector سه خانواده را پوشش می‌دهد:

- **PaaS:** Project status، Releases، Applets، stop reason، Events و metric summaries.
- **Domain/DNS:** Project domains، SSL state، DNS zones و recordهای لازم برای Diagnose.
- **Database:** Inventory، type، version، status، network indicators و metric summaries.

Write operations، Console، Restart، Deploy، Scale، Env Update، DNS Update و Database Mutation ممنوع‌اند.

## 9. Allowlist-first Sanitization

```text
Raw Liara API Response
→ Typed Field Allowlist
→ Type and Range Validation
→ Sanitized Project State DTO
→ Agent Context
```

اصل پیش‌فرض: هیچ Fieldی عبور نمی‌کند مگر در Schema داخلی صراحتاً تعریف شده باشد. Unknown Field حذف می‌شود. Env Value، Password، Token، Connection String، Node IP، Root Password و Fieldهای آینده وارد Context نمی‌شوند.

Raw Response فقط در طول Request در حافظه وجود دارد و Log یا Persist نمی‌شود. Contract Test با تزریق Field حساس ناشناخته باید ثابت کند خروجی Sanitizer تغییر نمی‌کند.

## 10. Knowledge Sources and Supply-chain Safety

منابع مجاز شامل `docs.liara.ir`، `developers.liara.ir`، محتوای فنی صفحات رسمی و Default Branch مخازن رسمی `liara-cloud/*` در Commit مشخص هستند.

موارد ممنوع: GitHub Issues، PRها و Reviewها، Discussions، Comments، Forkها، مخازن غیررسمی، محتوای User-generated، Hidden Instructions و Executable Content.

Source همیشه Data است، نه Instruction. HTML/MDX پاک‌سازی و Script، Hidden Text و Navigation Noise حذف می‌شوند.

## 11. Offline Knowledge Snapshot

Snapshot هیچ Runtime Rebuild Endpointی ندارد. Pipeline در محیط Local کنترل‌شده یا CI جدا از Liara اجرا می‌شود، با AvalAI Embeddings فایل‌ها را می‌سازد و خروجی زیر را به Repository Commit می‌کند:

```text
knowledge/snapshots/<version>/
├── manifest.json
├── chunks.jsonl
├── bm25.index
└── vectors.index
```

Liara Docker Build هیچ API Key برای Embedding دریافت نمی‌کند و فقط Snapshot موجود را Copy می‌کند. Manifest شامل Source URL، Heading، Anchor، Commit SHA، Content Hash، Embedding Model، Chunker Version و زمان Build است.

در Build Snapshot، URL باید موفق، Heading حاضر و Anchor منطبق با DOM ID واقعی باشد. Chunk بدون Locator معتبر منتشر نمی‌شود و Anchor شکسته Build را Fail می‌کند.

## 12. Chunking and Hybrid Retrieval

- هدف Chunk: حدود ۴۵۰ Token؛ حداکثر ۸۰۰ Token.
- Overlap: حداکثر ۸۰ Token.
- Code Block با Heading و توضیح مرتبط نگه داشته می‌شود.
- Persian/English normalization روی متن طبیعی اعمال می‌شود.
- Error، Command، Identifier، Backtick text و Variable name بدون تغییر حفظ می‌شوند.
- Glossary نسخه‌دار برای معادل‌های فارسی/انگلیسی استفاده می‌شود.

```text
Normalize Query
→ BM25 Top 20
→ Vector Top 20
→ Reciprocal Rank Fusion
→ Metadata Boost
→ Top 10 Candidates
→ Evidence Sufficiency Gate
→ Top 6 Context Chunks
```

LLM Query Expansion، LLM Reranker و Cross-encoder در MVP وجود ندارند. BM25 و Vector/RRF در یک `ThreadPoolExecutor` محدود و خارج از Async Event Loop اجرا می‌شوند.

Evidence Sufficiency فقط وقتی Pass می‌شود که حداقل یک Chunk رسمی دارای Locator معتبر وجود داشته باشد و یکی از دو شرط زیر برقرار باشد: برای Queryهای Error/Identifier تمام Critical Tokenها در حداقل یک Candidate حاضر باشند؛ برای Queryهای معنایی Cosine Similarity بهترین Candidate از Threshold اولیه `0.62` عبور کند. این Threshold همراه Snapshot/Embedding Model نسخه‌دار و با Golden Set کالیبره می‌شود.

اگر Candidateهای هم‌سطح درباره Version، Command، Port یا مقدار Critical ناسازگار باشند، Router آن را `conflict_detected` علامت می‌زند. سیستم منابع را به یک پاسخ قطعی ادغام نمی‌کند و Conflict/Unknown همراه هر دو منبع نمایش می‌دهد؛ Source جدیدتر فقط وقتی ترجیح داده می‌شود که Version/Freshness Metadata صریح داشته باشد.

## 13. Citation Contract

مدل پاسخ را به شکل Claimهای ساختاریافته همراه `chunk_id` و `evidence_span` دقیق تولید می‌کند.

Core Claims عبارت‌اند از: `direct_answer` در Ask، `current_step` در Guide، `primary_finding` و `next_safe_check` در Diagnose، و هشدار ایمنی لازم برای صحت پاسخ. مثال و توضیح غیرضروری Supporting Claim است.

```text
valid =
  trusted_source
  AND chunk_in_current_retrieval_set
  AND exact_normalized_evidence_span
  AND critical_token_coverage == 1.0
  AND lexical_overlap >= 0.25
  AND semantic_similarity >= 0.72
```

Embedding Claimها در یک Batch Call ساخته می‌شود. Thresholdها Versioned هستند و فقط پس از Golden Set Regression قابل تغییرند.

- Core Claim invalid → کل Answer به Unknown تبدیل می‌شود.
- Supporting Claim invalid → فقط همان Claim حذف می‌شود.

Citation UI شامل عنوان، Heading Path، Evidence Preview، Deep Link به Anchor و Copy لینک/Excerpt است.

## 14. Unknown and Handoff

Unknown پیام «پاسخ قطعی و قابل‌استنادی در منابع رسمی پیدا نشد» را نشان می‌دهد و سپس منابع نزدیک را با برچسب «مرتبط، نه پاسخ قطعی»، پیشنهاد افزودن جزئیات و Handoff ارائه می‌کند.

Support Handoff در MVP Action خارجی انجام نمی‌دهد و یک Summary قابل Copy از Goal، Family، مراحل امتحان‌شده، منابع دیده‌شده و Errorهای پاک‌سازی‌شده می‌سازد.

## 15. Session and Credential Lifecycle

- حساب کاربری داخلی وجود ندارد.
- Session ID در Cookie با `HttpOnly`, `Secure`, `SameSite=Strict` نگهداری می‌شود.
- Liara Token در Backend Memory Vault نگهداری و از Browser State حذف می‌شود.
- Token در Cookie، Local Storage، PostgreSQL، Agent Context یا Log قرار نمی‌گیرد.
- Idle TTL: ۳۰ دقیقه؛ Absolute TTL: دو ساعت.
- Disconnect، Expiry، Restart یا Deploy، Session را حذف می‌کند.
- Python Secure Memory Wipe را تضمین نمی‌کند؛ حذف Reference best-effort است.
- فقط Snapshot پاک‌سازی‌شده فعلی و قبلی در Session Memory نگهداری می‌شوند.
- Responseها `Cache-Control: no-store` دارند.

## 16. API Contract Summary

```text
POST   /api/v1/sessions
POST   /api/v1/sessions/connect
DELETE /api/v1/sessions/current
DELETE /api/v1/sessions/connection
GET    /api/v1/sessions/resources
POST   /api/v1/turns/stream
POST   /api/v1/project-state/refresh
POST   /api/v1/feedback
GET    /api/v1/sources/{chunk_id}
GET    /api/v1/health/live
GET    /api/v1/health/ready
```

`POST /sessions` پیش از هر Token یک Session ناشناس می‌سازد تا Ask فعال باشد. `/sessions/connect` همان Session را با Token موقت ارتقا می‌دهد؛ Token نامعتبر Session و قابلیت Ask را حذف نمی‌کند.

`project-state/refresh` بازسازی Index نیست. این Endpoint با Session معتبر، Resource Ref مجاز، SameSite/CSRF protection و Rate Limit فقط یک Liara GET را اجرا و Sanitized State را تازه می‌کند. Knowledge Snapshot فقط Offline ساخته می‌شود و هیچ Admin یا Public HTTP Endpoint برای Rebuild ندارد.

`/turns/stream` با POST Fetch Streaming و SSE framing کار می‌کند. Eventها شامل accepted، route، retrieval progress، tool summary، final/unknown، failure و completed هستند. `client_turn_id` برای Idempotency الزامی است.

Feedback متن آزاد ندارد و فقط `request_id`، `resolved`، `handoff_requested` و Reason Enum اختیاری می‌پذیرد. `resolved=true` و `handoff_requested=true` هم‌زمان رد می‌شوند. اگر بعداً متن آزاد اضافه شود، Secret/PII Scrubber قبل از Persistence اجباری است و متن خام ذخیره نمی‌شود.

## 17. Rate Limiting and Abuse Controls

Rate Limiter در حافظه و مبتنی بر `HMAC(IP, process-secret)` است. IP خام Persist نمی‌شود و Bucketها حداکثر پس از ده دقیقه حذف می‌شوند.

- `/sessions`: حداکثر ۲۰ Session جدید در ۱۰ دقیقه برای هر IP-derived key.
- `/sessions/connect`: حداکثر ۱۰ درخواست کل و حداکثر ۵ تلاش ناموفق در ۱۰ دقیقه.
- `/turns/stream`: حداکثر ۲۰ درخواست در ۱۰ دقیقه.
- Liara tools: حداکثر ۱۰ فراخوانی در ۱۰ دقیقه.
- Concurrent turns: حداکثر دو مورد در هر Session.

درخواست محدودشده پیش از AvalAI یا Liara API متوقف می‌شود.

## 18. Telemetry and Retention

جدول `turn_telemetry` فقط شامل UUIDهای تصادفی Session/Request، Turn index/time، Mode، Task Families، Confidence، نیاز به Project State، پرچم `containment_eligible`، Tool outcome، Citation result/counts، Unknown، Handoff shown/requested و Resolved flags، Latencyها، Token/cost counts، Model IDs، Snapshot version و Error Code محدود است.

Confirmed Containment برابر Sessionهای واجد شرایط با Outcome صریح، `resolved=true` و بدون Handoff تقسیم بر Sessionهای واجد شرایط دارای Outcome صریح است. Feedback Coverage و Conservative Lower Bound روی تمام Sessionهای واجد شرایط جدا گزارش می‌شوند.

هیچ Mapping هویتی وجود ندارد. متن سؤال/پاسخ، IP، Resource ID/Name، Token، Raw Log و Project Snapshot Persist نمی‌شوند. Citation Gate نتیجه Operational است؛ Citation Accuracy معنایی فقط از Golden Set می‌آید.

Maintenance Task در Startup و هر شش ساعت با PostgreSQL Advisory Lock، داده قدیمی‌تر از ۳۰ روز را Batchی حذف می‌کند. نتیجه در `maintenance_runs` ثبت می‌شود و فاصله بیش از ۲۴ ساعت از آخرین موفقیت هشدار می‌دهد.

## 19. Platform Logging Limitation

Privacy guarantees مربوط به Application Layer است. Reverse Proxy یا زیرساخت Liara ممکن است Access Log مستقل شامل IP، Path و Timestamp داشته باشد. محتوا و Retention آن خارج از کنترل برنامه است و هنگام Deploy بررسی می‌شود. Application هرگز Authorization Header، Body یا Query حاوی Secret را Log نمی‌کند.

## 20. Error Handling and Observability

Error taxonomy:

```text
AUTH_INVALID
AUTH_RATE_LIMITED
LIARA_TIMEOUT
LIARA_UNAVAILABLE
POLICY_DENIED
RESOURCE_NOT_ALLOWED
AI_TIMEOUT
AI_RATE_LIMITED
AI_INVALID_OUTPUT
RETRIEVAL_EMPTY
CITATION_CORE_FAILED
SNAPSHOT_INCOMPATIBLE
INTERNAL_ERROR
```

- Liara failure یا Policy denial → Docs-only fallback.
- Retrieval insufficiency یا Invalid Ask output → Unknown بدون repair Generation.
- Provider timeout → حداکثر یک Retry پیش از خروجی و درون Call Budget.
- Stack Trace و Raw Provider Response به کاربر نمایش داده نمی‌شود.

Observability شامل Request ID، Structured content-free logs، Liveness/Readiness، Provider latency/failure، Snapshot state، Retention health، Circuit breaker و شمارنده Unknown/Handoff/Policy/Citation است. اختلال External Provider باعث Readiness failure و Restart Loop نمی‌شود.

## 21. Evaluation Strategy

Golden Set حدود ۱۰۰ سناریو دارد: ۴۰ Ask، ۲۵ Guide، ۲۰ Diagnose با Snapshot مصنوعی، ۱۰ Unanswerable/Out-of-scope و ۵ Conflict/Outdated-source.

اهداف اولیه:

- Containment Rate: حداقل ۶۰٪.
- Citation Accuracy: حداقل ۹۵٪.
- Citation Coverage: حداقل ۹۰٪.
- Correct Unknown: حداقل ۹۰٪.
- False-answer Rate: حداکثر ۵٪.
- Task Completion: حداقل ۷۰٪.
- Tool Selection Accuracy: حداقل ۹۰٪.
- Median Time-to-resolution: حداقل ۳۵٪ بهتر از BM25 baseline.
- Ask `p95 <= 8s`؛ Guide `p95 <= 12s`؛ Diagnose `p95 <= 15s`.

هر Evaluation Run نسخه Golden Set، Snapshot، Prompt، Model، Threshold، زمان و Failed Scenario IDs را ثبت می‌کند.

## 22. AI Provider Strategy

AvalAI با OpenAI-compatible Adapter:

```text
AI_BASE_URL=https://api.avalai.ir/v1
AI_FAST_MODEL=gpt-5.4-mini
AI_REASONING_MODEL=gpt-5.5
AI_EMBEDDING_MODEL=text-embedding-3-small
```

Ask از Fast Model و Guide/Diagnose از Reasoning Model استفاده می‌کنند. Model IDs در Release Smoke Test با Provider Catalog اعتبارسنجی می‌شوند؛ Readiness زمان اجرا به دسترس‌پذیری لحظه‌ای Provider وابسته نیست. تغییر Provider فقط از طریق Config و Adapter انجام می‌شود.

## 23. Repository and Deployment

```text
frontend/{src/components,src/features,src/api,src/styles}
backend/{app/api,app/domain,app/application,app/policies,app/retrieval,app/providers,app/telemetry,migrations}
knowledge/{sources.yaml,pipeline,snapshots/<version>}
evals/{golden-set,baselines,reports}
tests/{unit,contract,security,integration,e2e}
docs/design-system/
specs/001-liara-navigator/
Dockerfile
pyproject.toml
package.json
```

Multi-stage Docker: Node build، Python locked dependencies، Copy React artifact و committed Knowledge Snapshot، سپس Uvicorn روی port 8000 با یک Worker.

- One Liara Docker application and one HTTP port.
- One instance, one worker, no persistent disk.
- Managed PostgreSQL on private network.
- CPU-bound retrieval via bounded ThreadPoolExecutor.
- Same-origin frontend/API.
- Deploy یا Restart همه Sessionها را منقضی می‌کند.

## 24. Verification Matrix

- Router tests شامل multi-label و confidence پایین.
- Retrieval ranking/normalization tests.
- Citation Core/Supporting و Anchor integrity tests.
- Field Allowlist contract test با future-secret injection.
- GET-only، Resource ownership و Tool rejection tests.
- Session TTL، disconnect، rate limit و idempotency tests.
- Feedback no-free-text و Retention tests.
- AvalAI mock plus one live smoke test.
- Liara read-only mock plus one live test-token smoke test.
- Golden Set و BM25 baseline.
- RTL/accessibility/responsive checks.
- Docker build و deployed `liara.run` E2E.

## 25. Explicit Non-goals

- No autonomous write action, deploy, restart, scale or config mutation.
- No internal user accounts or persistent conversation history.
- No free-text feedback persistence.
- No user GitHub inspection or Issues/PR/comments indexing.
- No runtime crawler or knowledge rebuild endpoint.
- No multi-agent, microservices, Redis or dedicated vector database.
- No automatic support ticket creation in MVP.

## 26. Approval Record

Product Scope، Stack، Session policy، multilingual support، knowledge scope، three-family inspector، Provider strategy، State Machine، Retrieval/Citation، Security/Retention، Observability/Evaluation و Deployment طی گفت‌وگوی طراحی تأیید شده‌اند. این سند مرجع یکپارچه Spec Kit است و Implementation فقط پس از بازبینی Artifactهای Spec Kit آغاز می‌شود.
