# Tasks: Liara Navigator MVP

**Input**: Design documents from `/specs/001-liara-navigator/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/openapi.yaml](./contracts/openapi.yaml)

**Tests**: الزامی؛ هر رفتار ابتدا با Test شکست‌خورده تعریف و سپس Implement می‌شود.  
**Organization**: Taskها به Vertical Slice و User Story گروه‌بندی شده‌اند تا هر Story مستقل قابل تست و Demo باشد.

## Format

`[ID] [P?] [Story?] Description with exact path`

- `[P]`: بدون تعارض فایل و قابل اجرا در موازات Taskهای هم‌مرحله.
- `[USn]`: اتصال مستقیم به User Story شماره n در Spec.
- هر Test task باید پیش از implementation متناظر اجرا و Fail شود.

## Phase 1 — Setup and Reproducible Tooling

**Purpose**: Repository قابل Build با dependency lock، lint/typecheck و بدون Application behavior.

- [x] T001 ایجاد ساختار source مطابق plan در `backend/app/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`, `knowledge/pipeline/`, `evals/`, و `tests/e2e/`
- [x] T002 ایجاد `backend/pyproject.toml` با Python 3.12، dependency groups مصوب و commandهای pytest/ruff/mypy
- [x] T003 ایجاد lockfile Python با `uv lock --project backend` و ثبت نسخه‌های resolve‌شده در `backend/uv.lock`
- [x] T004 [P] ایجاد `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts` با React/Vite/Vitest/Testing Library/axe
- [x] T005 [P] ایجاد `frontend/package-lock.json` با `npm --prefix frontend install --package-lock-only`
- [x] T006 [P] ایجاد `.editorconfig`, `.gitignore`, `.dockerignore` با ممنوعیت `.env*`, `venv`, `node_modules`, raw crawl cache و test artifacts
- [x] T007 [P] ایجاد `.env.example` فقط با نام متغیرها و مقدارهای غیرSecret مطابق quickstart
- [x] T008 [P] ایجاد `compose.local.yaml` فقط برای PostgreSQL local با healthcheck و بدون expose credential production
- [x] T009 اجرای `uv run --project backend ruff check backend` و `npm --prefix frontend run typecheck` و رفع تمام خطاهای setup
- [x] T010 ثبت Checkpoint setup با `docker compose -f compose.local.yaml config` و بررسی اینکه هیچ Secret در فایل‌های stage‌شده وجود ندارد

**Checkpoint**: Dependency installation و static checks از صفر قابل‌بازتولید باشند.

---

## Phase 2 — Foundational Runtime and Security Boundaries

**Purpose**: اجزایی که تمام User Storyها به آن‌ها نیاز دارند؛ تا پایان این Phase هیچ Story شروع نمی‌شود.

### Tests first

- [x] T011 [P] نوشتن test تنظیمات required/forbidden values در `backend/tests/unit/test_config.py`
- [x] T012 [P] نوشتن test mapping ErrorCode به ErrorResponse فاقد detail حساس در `backend/tests/unit/test_api_errors.py`
- [x] T013 [P] نوشتن test ساخت Anonymous Session، Cookie/CSRF، `Cache-Control: no-store` و عدم log شدن Authorization در `backend/tests/security/test_middleware.py`
- [x] T014 [P] نوشتن test bounded ThreadPool و non-blocking health request در `backend/tests/unit/test_executor.py`
- [x] T015 [P] نوشتن contract test اولیه OpenAPI paths/schema در `backend/tests/contract/test_openapi_contract.py`
- [x] T016 اجرای T011–T015 و ثبت Fail مورد انتظار به‌علت نبود runtime modules

### Implementation

- [x] T017 [P] پیاده‌سازی Settings typed و startup validation در `backend/app/config.py`
- [x] T018 [P] تعریف enumهای Domain و Error taxonomy در `backend/app/domain/errors.py`, `backend/app/domain/routing.py`, `backend/app/domain/tools.py`
- [x] T019 [P] تعریف API request/response schemaهای مشترک با `extra='forbid'` در `backend/app/api/schemas.py`
- [x] T020 پیاده‌سازی امن error mapping در `backend/app/api/errors.py` با `request_id`, `retryable` و bounded message
- [x] T021 پیاده‌سازی request-id/cache/security-header middleware و content-free logger در `backend/app/api/middleware.py`
- [x] T022 پیاده‌سازی bounded executor dependency در `backend/app/api/dependencies.py` و shutdown hook
- [x] T023 ایجاد FastAPI factory، Anonymous Session Vault پایه، `POST /api/v1/sessions` و `/api/v1/health/live` در `backend/app/main.py`, `backend/app/domain/sessions.py`, `backend/app/security/session_vault.py`, `backend/app/api/routes/sessions.py`, `backend/app/api/routes/health.py`
- [ ] T024 [P] ایجاد React shell، error boundary و RTL root در `frontend/src/app/App.tsx`, `frontend/src/main.tsx`, `frontend/src/styles/global.css`
- [ ] T025 [P] انتقال tokenهای Design System به `frontend/src/styles/tokens.css` مطابق `docs/design-system/liara-intelligence-design-system.md`
- [ ] T026 اجرای T011–T015 و frontend smoke test؛ همه باید PASS شوند

**Checkpoint**: `/health/live` هنگام یک CPU task مصنوعی پاسخ‌گو باشد و UI shell RTL render شود.

---

## Phase 3 — User Story 1: Ask with Verifiable Sources (P1) 🎯 First Deployable Slice

**Goal**: Ask روی Snapshot fixture، پاسخ Claim-based، Citation UI و Unknown صادقانه.

**Independent Test**: سؤال Golden fixture بدون Liara Token باید پاسخ معتبر یا Unknown قابل‌پیش‌بینی بدهد.

### 3A — Offline knowledge build

- [ ] T027 [P] [US1] نوشتن test source allowlist و رد Issues/PR/Comments در `backend/tests/security/test_source_policy.py`
- [ ] T028 [P] [US1] نوشتن test HTML/MDX cleaning و حذف hidden/script/nav content در `backend/tests/unit/test_knowledge_clean.py`
- [ ] T029 [P] [US1] نوشتن test heading-aware chunk limits و حفظ code block در `backend/tests/unit/test_knowledge_chunk.py`
- [ ] T030 [P] [US1] نوشتن test URL/heading/DOM anchor validation و broken-anchor failure در `backend/tests/contract/test_anchor_integrity.py`
- [ ] T031 [US1] اجرای T027–T030 و تأیید Fail
- [ ] T032 [P] [US1] تعریف source manifest schema و official sources در `knowledge/sources.yaml` و `knowledge/pipeline/fetch.py`
- [ ] T033 [P] [US1] پیاده‌سازی cleaner در `knowledge/pipeline/clean.py`
- [ ] T034 [P] [US1] پیاده‌سازی heading-aware chunker در `knowledge/pipeline/chunk.py`
- [ ] T035 [P] [US1] پیاده‌سازی rendered anchor validator در `knowledge/pipeline/anchors.py`
- [ ] T036 [US1] پیاده‌سازی AvalAI batch embedding و artifact hashing در `knowledge/pipeline/embed.py`
- [ ] T037 [US1] پیاده‌سازی create/validate CLI و manifest در `knowledge/pipeline/build.py`
- [ ] T038 [US1] ساخت fixture رسمی کوچک و deterministic در `knowledge/snapshots/test-fixture/`
- [ ] T039 [US1] اجرای T027–T030 و snapshot validation؛ همه PASS

### 3B — Runtime retrieval

- [ ] T040 [P] [US1] نوشتن test Persian/English normalization با حفظ error/identifier در `backend/tests/unit/test_normalizer.py`
- [ ] T041 [P] [US1] نوشتن test BM25 top-20 و FAISS top-20 loaders در `backend/tests/unit/test_indexes.py`
- [ ] T042 [P] [US1] نوشتن test deterministic RRF/metadata boost/top-10 در `backend/tests/unit/test_fusion.py`
- [ ] T043 [P] [US1] نوشتن test exact/semantic sufficiency و conflict detection در `backend/tests/unit/test_sufficiency.py`
- [ ] T044 [P] [US1] نوشتن test manifest hash/model/dimension mismatch در `backend/tests/unit/test_snapshot_loader.py`
- [ ] T045 [US1] اجرای T040–T044 و تأیید Fail
- [ ] T046 [P] [US1] پیاده‌سازی normalizer/glossary در `backend/app/retrieval/normalizer.py`
- [ ] T047 [P] [US1] پیاده‌سازی immutable BM25/FAISS loaders در `backend/app/retrieval/bm25_index.py`, `backend/app/retrieval/vector_index.py`
- [ ] T048 [P] [US1] پیاده‌سازی RRF و metadata boost در `backend/app/retrieval/fusion.py`
- [ ] T049 [P] [US1] پیاده‌سازی sufficiency/conflict rules در `backend/app/retrieval/sufficiency.py`
- [ ] T050 [US1] پیاده‌سازی startup snapshot loader و bounded-thread search در `backend/app/retrieval/snapshot_loader.py`
- [ ] T051 [US1] اجرای T040–T044 و تأیید PASS و عدم block شدن health

### 3C — AI, claims and citations

- [ ] T052 [P] [US1] نوشتن test `AIProvider` contract و AvalAI request budgets در `backend/tests/contract/test_ai_provider.py`
- [ ] T053 [P] [US1] نوشتن test Claim slot→role mapping در `backend/tests/unit/test_claims.py`
- [ ] T054 [P] [US1] نوشتن test citation validity thresholds/core/supporting outcomes در `backend/tests/unit/test_citation_service.py`
- [ ] T055 [P] [US1] نوشتن Ask integration tests برای answer/unknown/conflict/invalid-output در `backend/tests/integration/test_ask_flow.py`
- [ ] T056 [US1] اجرای T052–T055 و تأیید Fail
- [ ] T057 [P] [US1] تعریف Provider protocol و typed completion result در `backend/app/providers/ai/base.py`
- [ ] T058 [P] [US1] تعریف Claim/Citation domain models در `backend/app/domain/claims.py`, `backend/app/domain/citations.py`
- [ ] T059 [US1] پیاده‌سازی AvalAI adapter با one-generation enforcement، timeout و batch embeddings در `backend/app/providers/ai/avalai.py`
- [ ] T060 [US1] پیاده‌سازی programmatic Citation Service در `backend/app/application/citation_service.py`
- [ ] T061 [US1] پیاده‌سازی Ask orchestrator در `backend/app/application/ask.py`
- [ ] T062 [US1] اجرای T052–T055 و تأیید PASS؛ Assert generation count=1

### 3D — Ask API and UI

- [ ] T063 [P] [US1] نوشتن contract/integration test `POST /turns/stream` event order و idempotency در `backend/tests/contract/test_turn_stream.py`
- [ ] T064 [P] [US1] نوشتن source endpoint test و جلوگیری از path traversal در `backend/tests/security/test_source_endpoint.py`
- [ ] T065 [P] [US1] نوشتن frontend tests برای answer، evidence rail، unknown، code LTR و copy در `frontend/tests/ask.test.tsx`
- [ ] T066 [US1] اجرای T063–T065 و تأیید Fail
- [ ] T067 [P] [US1] پیاده‌سازی Anonymous Session bootstrap، memory-only CSRF، Fetch/SSE parser و Zod event validation در `frontend/src/api/client.ts`, `frontend/src/api/events.ts`
- [ ] T068 [P] [US1] پیاده‌سازی source lookup route در `backend/app/api/routes/sources.py`
- [ ] T069 [US1] پیاده‌سازی Ask-only turn stream و idempotency cache در `backend/app/api/routes/turns.py`
- [ ] T070 [P] [US1] پیاده‌سازی chat composer/status/answer components در `frontend/src/features/chat/`
- [ ] T071 [P] [US1] پیاده‌سازی citation card/evidence rail/copy/deep-link در `frontend/src/features/sources/`
- [ ] T072 [US1] اتصال Ask UI به stream و source endpoint در `frontend/src/app/App.tsx`
- [ ] T073 [US1] اجرای T063–T065، frontend typecheck و US1 Playwright در `tests/e2e/ask.spec.ts`

**Checkpoint**: US1 مستقل Deploy می‌شود و Ask/Unknown/Citation end-to-end کار می‌کنند.

---

## Phase 4 — User Story 2: Safe Personal Liara Connection (P1)

**Goal**: Token موقت، Inventory پاک‌سازی‌شده، Resource Ref و lifecycle امن.

**Independent Test**: connect/invalid/disconnect/expiry با fake Liara client و future-secret fixture.

### Tests first

- [ ] T074 [P] [US2] نوشتن Session Vault token-upgrade، TTL، token-disconnect و shutdown tests در `backend/tests/security/test_session_vault.py`
- [ ] T075 [P] [US2] نوشتن CSRF header، token-upgrade و no-store tests در `backend/tests/security/test_session_csrf.py`
- [ ] T076 [P] [US2] نوشتن IP-HMAC/session rate-limit tests برای anonymous-session creation، token connect، turn، tool و سقف دو Turn هم‌زمان در `backend/tests/security/test_rate_limit.py`
- [ ] T077 [P] [US2] نوشتن Liara inventory contract fixtures برای valid/401/429/5xx در `backend/tests/contract/test_liara_inventory.py`
- [ ] T078 [P] [US2] نوشتن allowlist-first sanitizer tests با env/password/future_token fields در `backend/tests/security/test_field_allowlist.py`
- [ ] T079 [P] [US2] نوشتن cross-session Resource Ref tests در `backend/tests/security/test_resource_refs.py`
- [ ] T080 [P] [US2] نوشتن frontend connect/disconnect/expiry tests در `frontend/tests/session.test.tsx`
- [ ] T081 [US2] اجرای T074–T080 و تأیید Fail

### Implementation

- [ ] T082 [P] [US2] تکمیل `AnonymousSession` با anonymous/validating/connected transitions و TTL clock rules در `backend/app/domain/sessions.py`
- [ ] T083 [P] [US2] پیاده‌سازی token bucket با ephemeral HMAC IP keys در `backend/app/security/rate_limit.py`
- [ ] T084 [P] [US2] پیاده‌سازی Resource Ref generator/resolver در `backend/app/security/resource_refs.py`
- [ ] T085 [US2] گسترش Memory Session Vault با SecretTokenEntry، token upgrade/disconnect و best-effort cleanup در `backend/app/security/session_vault.py`
- [ ] T086 [P] [US2] تعریف Liara client protocol/timeout error mapping در `backend/app/providers/liara/base.py`
- [ ] T087 [US2] پیاده‌سازی HTTPX Liara client با fixed base URLs و redacted diagnostics در `backend/app/providers/liara/client.py`
- [ ] T088 [US2] پیاده‌سازی typed allowlist sanitizers برای inventory در `backend/app/providers/liara/sanitizers.py`
- [ ] T089 [US2] پیاده‌سازی token-upgrade/list/token-disconnect service بدون حذف Anonymous Ask session در `backend/app/application/session_service.py`
- [ ] T090 [US2] تکمیل connect/resources/token-disconnect/full-session-delete routes و CSRF validation در `backend/app/api/routes/sessions.py`
- [ ] T091 [P] [US2] پیاده‌سازی Connect Dialog، resource picker و memory-only CSRF state در `frontend/src/features/session/`
- [ ] T092 [US2] اجرای T074–T080 و Playwright `tests/e2e/connect.spec.ts`; تأیید absence token در storage/log fixtures

**Checkpoint**: US2 مستقل است؛ Token پس از disconnect/expiry قابل استفاده نیست و raw fields نشت نمی‌کنند.

---

## Phase 5 — User Story 3: Diagnose with Real Read-only State (P1)

**Goal**: multi-label routing، Policy-gated tools، three-family state و explicit refresh.

**Independent Test**: synthetic Deployment+Database scenario با tool success، denial، timeout و state comparison.

### Tests first

- [ ] T093 [P] [US3] نوشتن router tests برای auto/manual mode، multi-label و confidence<0.65 در `backend/tests/unit/test_router.py`
- [ ] T094 [P] [US3] نوشتن Tool Policy tests برای GET-only/host/path/ownership/parameters در `backend/tests/security/test_tool_policy.py`
- [ ] T095 [P] [US3] نوشتن PaaS sanitizer contract با release/applet/events/metrics و forbidden envs در `backend/tests/contract/test_liara_paas.py`
- [ ] T096 [P] [US3] نوشتن Domain/DNS sanitizer contract با SSL/zone/records در `backend/tests/contract/test_liara_domain_dns.py`
- [ ] T097 [P] [US3] نوشتن Database sanitizer contract بدون root_password/connection fields در `backend/tests/contract/test_liara_database.py`
- [ ] T098 [P] [US3] نوشتن Diagnose integration برای success/docs-only/unknown/call-cap در `backend/tests/integration/test_diagnose_flow.py`
- [ ] T099 [P] [US3] نوشتن refresh contract test برای explicit POST، previous/current state و no polling در `backend/tests/contract/test_project_state_refresh.py`
- [ ] T100 [P] [US3] نوشتن frontend project-state/tool-summary tests در `frontend/tests/diagnose.test.tsx`
- [ ] T101 [US3] اجرای T093–T100 و تأیید Fail

### Implementation

- [ ] T102 [P] [US3] پیاده‌سازی RouteDecision/scoring/task-family classifier در `backend/app/application/router.py`
- [ ] T103 [P] [US3] تکمیل ToolRequest/ToolDecision/project facts models در `backend/app/domain/tools.py`, `backend/app/domain/project_state.py`
- [ ] T104 [US3] پیاده‌سازی deterministic Tool Policy در `backend/app/application/tool_policy.py`
- [ ] T105 [US3] پیاده‌سازی registered PaaS/Domain/DNS/Database GET tools در `backend/app/providers/liara/tools.py`
- [ ] T106 [US3] تکمیل field sanitizers سه خانواده در `backend/app/providers/liara/sanitizers.py`
- [ ] T107 [US3] پیاده‌سازی Diagnose orchestrator، hypothesis ordering، fallback و two-call cap در `backend/app/application/diagnose.py`
- [ ] T108 [US3] پیاده‌سازی explicit project-state refresh route در `backend/app/api/routes/project_state.py`
- [ ] T109 [US3] گسترش turn stream برای router/tool events و Diagnose در `backend/app/api/routes/turns.py`
- [ ] T110 [P] [US3] پیاده‌سازی tool status، resource context و refresh button در `frontend/src/features/project-state/`
- [ ] T111 [US3] اتصال Diagnose mode و clarification UI در `frontend/src/features/chat/`
- [ ] T112 [US3] اجرای T093–T100 و Playwright `tests/e2e/diagnose.spec.ts`; assert no background polling

**Checkpoint**: US3 Agentic demo با State واقعی/مصنوعی و Policy fallback قابل اجرا است.

---

## Phase 6 — User Story 4: Supported Goal Guidance (P2)

**Goal**: Plan مرحله‌ای برای سه Family با current-step evidence و validation در Turn بعد.

**Independent Test**: Guide scenario با clarification، partial scope، step progression و call-cap.

- [ ] T113 [P] [US4] نوشتن PlanStep/AgentSessionState transition tests در `backend/tests/unit/test_guide_state.py`
- [ ] T114 [P] [US4] نوشتن Guide integration برای clarification/full/partial/call-cap در `backend/tests/integration/test_guide_flow.py`
- [ ] T115 [P] [US4] نوشتن frontend plan/current-step/progress tests در `frontend/tests/guide.test.tsx`
- [ ] T116 [US4] اجرای T113–T115 و تأیید Fail
- [ ] T117 [US4] پیاده‌سازی Guide state models و invariants در `backend/app/domain/sessions.py`
- [ ] T118 [US4] پیاده‌سازی Guide orchestrator با one-step rendering در `backend/app/application/guide.py`
- [ ] T119 [US4] اتصال Guide route/events/state persistence موقت در `backend/app/api/routes/turns.py`
- [ ] T120 [US4] پیاده‌سازی Guide plan/current-step UI در `frontend/src/features/chat/GuidePanel.tsx`
- [ ] T121 [US4] اجرای T113–T115 و Guide E2E scenario؛ assert max two Generation calls/turn

**Checkpoint**: US4 بدون Diagnose dependency قابل تست است و partial scope صریح نمایش داده می‌شود.

---

## Phase 7 — User Story 5: Unknown, Scope Degradation and Handoff (P2)

**Goal**: هیچ failure یا خارج-Scope به پاسخ حدسی/صفحه خالی تبدیل نشود.

**Independent Test**: Billing Guide → Ask؛ unanswerable → Unknown؛ policy failure → Docs-only؛ handoff summary بدون secret.

- [ ] T122 [P] [US5] نوشتن scope matrix/degradation tests در `backend/tests/unit/test_scope_degradation.py`
- [ ] T123 [P] [US5] نوشتن Handoff scrub/field-bound tests در `backend/tests/security/test_handoff.py`
- [ ] T124 [P] [US5] نوشتن Unknown/conflict/related-source UI tests در `frontend/tests/unknown_handoff.test.tsx`
- [ ] T125 [US5] اجرای T122–T124 و تأیید Fail
- [ ] T126 [US5] پیاده‌سازی scope matrix و degradation response در `backend/app/application/router.py`
- [ ] T127 [US5] پیاده‌سازی bounded Handoff builder و scrubber در `backend/app/security/scrubber.py`, `backend/app/application/handoff_service.py`
- [ ] T128 [US5] پیاده‌سازی Unknown/Conflict/Handoff UI در `frontend/src/features/chat/UnknownPanel.tsx`
- [ ] T129 [US5] اجرای T122–T124 و Playwright `tests/e2e/unknown.spec.ts`

**Checkpoint**: US5 رفتار «حدس نزن» را در Scope، Evidence و Tool failure enforce می‌کند.

---

## Phase 8 — User Story 6: Structured Outcome Feedback (P3)

**Goal**: resolved/not-resolved/handoff-requested بدون متن آزاد و قابل اتصال به Containment.

**Independent Test**: valid bounded feedback ذخیره شود؛ extra/free-text field و resolved+handoff هم‌زمان با 422 رد شوند.

- [ ] T130 [P] [US6] نوشتن feedback schema/ownership/no-free-text/resolved-handoff exclusivity tests در `backend/tests/contract/test_feedback.py`
- [ ] T131 [P] [US6] نوشتن feedback UI tests در `frontend/tests/feedback.test.tsx`
- [ ] T132 [US6] اجرای T130–T131 و تأیید Fail
- [ ] T133 [US6] پیاده‌سازی FeedbackRequest strict schema و route در `backend/app/api/routes/feedback.py`
- [ ] T134 [US6] پیاده‌سازی Feedback service با bounded enum update در `backend/app/application/feedback_service.py`
- [ ] T135 [US6] پیاده‌سازی resolved/reason controls در `frontend/src/features/feedback/FeedbackBar.tsx`
- [ ] T136 [US6] اجرای T130–T131 و تأیید PASS

**Checkpoint**: Containment input بدون ذخیره متن جمع‌آوری می‌شود.

---

## Phase 9 — Telemetry, Retention and Evaluation

**Purpose**: اندازه‌گیری Rubric بدون content surveillance.

- [ ] T137 [P] نوشتن migration/model tests برای positive telemetry schema در `backend/tests/contract/test_telemetry_schema.py`
- [ ] T138 [P] نوشتن no-sensitive-projection tests برای message/answer/token/resource/IP در `backend/tests/security/test_no_sensitive_telemetry.py`
- [ ] T139 [P] نوشتن retention startup/6h/advisory-lock/batch tests در `backend/tests/integration/test_retention.py`
- [ ] T140 [P] نوشتن metrics formula tests برای containment/latency/cost در `backend/tests/unit/test_metrics.py`
- [ ] T141 اجرای T137–T140 و تأیید Fail
- [ ] T142 ایجاد Alembic setup و migration `backend/migrations/versions/0001_telemetry.py` مطابق data-model
- [ ] T143 پیاده‌سازی SQLAlchemy models و explicit telemetry projection در `backend/app/telemetry/models.py`, `backend/app/telemetry/repository.py`
- [ ] T144 پیاده‌سازی retention task و maintenance health در `backend/app/telemetry/maintenance.py`
- [ ] T145 پیاده‌سازی aggregate metric formulas در `backend/app/telemetry/metrics.py`
- [ ] T146 اتصال telemetry writer به turn terminal paths بدون content در `backend/app/api/routes/turns.py`
- [ ] T147 اجرای T137–T140 و database integration suite؛ تأیید PASS
- [ ] T148 [P] تعریف Golden Case schema و 100-case structure در `evals/golden-set/cases.jsonl`
- [ ] T149 [P] پیاده‌سازی citation/route/tool/unknown/call-budget metrics در `evals/metrics.py`
- [ ] T150 [P] پیاده‌سازی BM25-only baseline در `evals/baselines/bm25.py`
- [ ] T151 پیاده‌سازی versioned evaluation runner/report writer در `evals/runner.py`
- [ ] T152 اجرای fixture evaluation و ثبت deterministic report در `evals/reports/test-fixture.json`

**Checkpoint**: Metricها از Schema مجاز محاسبه و semantic quality فقط از Golden Set گزارش شود.

---

## Phase 10 — Production Hardening and Liara Deployment

**Purpose**: Release قابل‌دفاع، امن و قابل Demo.

- [ ] T153 [P] نوشتن readiness tests برای config/index/database و independence از AvalAI/Liara transient health در `backend/tests/integration/test_health.py`
- [ ] T154 [P] نوشتن circuit-breaker/timeout/retry budget tests در `backend/tests/unit/test_provider_resilience.py`
- [ ] T155 [P] نوشتن accessibility tests برای RTL/focus/keyboard/contrast در `frontend/tests/accessibility.test.tsx`
- [ ] T156 [P] نوشتن full Docker smoke script assertions در `tests/smoke/test_container.sh`
- [ ] T157 اجرای T153–T156 و تأیید Fail
- [ ] T158 پیاده‌سازی readiness/provider-health/retention state در `backend/app/api/routes/health.py`
- [ ] T159 پیاده‌سازی bounded circuit breaker و retry policy در `backend/app/providers/ai/avalai.py`, `backend/app/providers/liara/client.py`
- [ ] T160 تکمیل responsive/accessibility behavior براساس Design System در `frontend/src/styles/global.css` و componentها
- [ ] T161 ایجاد multi-stage `Dockerfile` با frontend build، backend runtime، committed snapshot و non-root user
- [ ] T162 ایجاد production static-file/fallback routing در `backend/app/main.py`
- [ ] T163 اجرای تمام unit/contract/security/integration/frontend/E2E suites و ثبت summary در `evals/reports/release-verification.md`
- [ ] T164 ساخت Snapshot واقعی offline، validation همه Anchorها و Commit `knowledge/snapshots/2026-08-20.1/`
- [ ] T165 اجرای Golden Set واقعی و BM25 baseline و ثبت versioned reports در `evals/reports/`
- [ ] T166 Build production image بدون secret build args و اجرای local container smoke
- [ ] T167 Deploy Docker app و PostgreSQL private connection روی Liara مطابق `quickstart.md`
- [ ] T168 اجرای live AvalAI Ask smoke و ثبت request/call-budget/latency outcome بدون prompt content
- [ ] T169 اجرای live Liara read-only connect/diagnose/refresh/disconnect smoke با test resource
- [ ] T170 اجرای Demo rehearsal شامل Ask، Guide، Diagnose، Unknown، provider failure و metrics report
- [ ] T171 بررسی تنظیمات و Retention دسترس‌پذیر Access Log در Liara، ثبت محدودیت تأییدشده در `evals/reports/release-verification.md` و نمایش Privacy note در `frontend/src/features/session/PrivacyNotice.tsx`

**Final Checkpoint**: تمام SC-001 تا SC-014 evidence قابل ارائه دارند و URL واقعی Liara آماده Demo است.

---

## Dependencies and Execution Order

### Phase Dependencies

```text
Phase 1 Setup
  → Phase 2 Foundation
    → Phase 3 US1 Ask
    → Phase 4 US2 Connection
      → Phase 5 US3 Diagnose
    → Phase 6 US4 Guide
    → Phase 7 US5 Unknown/Handoff
    → Phase 8 US6 Feedback
      → Phase 9 Telemetry/Evaluation
        → Phase 10 Deploy
```

- US1 و US2 پس از Foundation می‌توانند موازی توسعه یابند، ولی US3 به هر دو وابسته است.
- US4 به Router/Session foundation وابسته است اما برای تست از fake tools استفاده می‌کند.
- US5 از Ask/Router contracts استفاده می‌کند.
- US6 از Session و telemetry request identity استفاده می‌کند.
- Phase 9 پس از تثبیت terminal outcomes اجرا می‌شود.
- Phase 10 پس از تمام Storyهای انتخاب‌شده و Evaluation اجرا می‌شود.

### Parallel Examples

پس از T026:

```text
Track A: T027–T039 knowledge build
Track B: T040–T051 retrieval runtime after fixture schema is fixed
Track C: T074–T092 session/Liara connection
```

در US3:

```text
T095 PaaS contract
T096 Domain/DNS contract
T097 Database contract
T100 Frontend Diagnose tests
```

## Implementation Strategy

### Minimal Demonstrable Product

1. Phase 1–2.
2. Phase 3 US1.
3. Deploy Ask-only checkpoint.
4. Phase 4–5 برای Agentic demo.
5. Phase 7 Unknown/Handoff.
6. Phase 9–10 برای score evidence و final deployment.

### Scope Cut Order if Time Is Constrained

مواردی که آخر حذف می‌شوند: US1 Citation، US2 Connection، US3 Diagnose، Unknown، security tests، Liara deploy.

موارد قابل کاهش بدون نقض Core MVP:

1. تعداد Golden Cases از 100 به 60، بدون حذف categoryها.
2. Guide UI animation/polish، نه Guide correctness.
3. metric charts؛ JSON/Markdown report کافی است.
4. Domain/DNS metric depth؛ inventory/status حفظ می‌شود.

موارد غیرقابل حذف: Field Allowlist، GET-only Policy، Token lifecycle، Citation Gate، Unknown behavior، Rate Limits، live AvalAI و Liara smoke.

## Completion Rule

هیچ Task فقط با «کد نوشته شد» Complete نیست. Completion نیازمند Test سبز متناظر، عدم Regression، به‌روزرسانی Contract/Spec در صورت تغییر interface و یک Commit کوچک با پیام توصیفی است.
