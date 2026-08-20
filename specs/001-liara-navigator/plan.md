# Implementation Plan: Liara Navigator MVP

**Branch**: `001-liara-navigator` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-liara-navigator/spec.md`

## Summary

ساخت یک Modular Monolith فارسی‌اول که Ask مستند و سریع، Guide مرحله‌ای و Diagnose متصل به وضعیت Read-only حساب کاربر را ارائه دهد. React UI و FastAPI API از یک Docker Application روی Liara سرو می‌شوند؛ Knowledge به‌صورت Snapshot ثابت BM25+FAISS همراه Release است؛ AvalAI از Adapter مستقل استفاده می‌شود؛ Token فقط در Memory و Telemetry فقط در PostgreSQL ذخیره می‌شود.

## Technical Context

**Language/Version**: Python 3.12؛ TypeScript 5.x؛ Node.js 22 LTS  
**Primary Dependencies**: FastAPI 0.x، Pydantic 2.x، Uvicorn، SQLAlchemy 2.x، asyncpg، Alembic، HTTPX، OpenAI Python SDK، NumPy، FAISS CPU، React 19، Vite 7، TanStack Query 5، Zod 4  
**Storage**: PostgreSQL برای Telemetry/Evaluation؛ immutable JSONL/BM25/FAISS files برای Knowledge؛ process memory برای Session/Token  
**Testing**: pytest + pytest-asyncio + respx + coverage؛ Vitest + Testing Library + axe؛ Playwright؛ Golden Set evaluation runner  
**Target Platform**: Linux Docker container روی Liara PaaS، یک HTTP port 8000  
**Project Type**: Single-deploy web application با frontend/backend مجزا در source tree  
**Performance Goals**: Ask p95 ≤ 8s؛ Guide ≤ 12s؛ Diagnose ≤ 15s؛ health endpoint بدون Event Loop blocking  
**Constraints**: یک Instance/Worker؛ GET-only tools؛ Session-only token؛ no runtime crawl؛ Ask یک و Guide/Diagnose دو Generation در Turn؛ Privacy-first telemetry  
**Scale/Scope**: مسابقه/MVP روی یک Instance؛ سه Task Family برای Workflow کامل و کل Snapshot رسمی برای Ask؛ ظرفیت Production SLA نیست و concurrency فقط در محدوده Rate Limitهای مصوب اندازه‌گیری می‌شود

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Gate | Evidence |
|---|---|---|
| Evidence Before Answer | PASS | Claim schema، Citation Gate، Golden Set و Unknown behavior در spec/research تعریف شده‌اند. |
| Least Privilege and Privacy | PASS | GET/path/field allowlists، memory-only token و positive telemetry schema قفل شده‌اند. |
| Bounded Agentic Behavior | PASS | Call budget و explicit refresh trigger Requirement دارند. |
| Deterministic Policy and Test-first | PASS | هر Slice با failing tests شروع می‌شود؛ model هیچ Tool را مستقیم اجرا نمی‌کند. |
| Observable Without Surveillance | PASS | content-free telemetry و evaluation separation تعریف شده‌اند. |
| Reproducible Knowledge | PASS | Snapshot offline، committed و hash/versioned است. |
| Liara-native Accessible UX | PASS | Design System، RTL/LTR و accessibility gates مرجع‌اند. |

**Post-design re-check**: PASS. هیچ Complexity exception نیاز نیست.

## Architecture Boundaries

### Domain

Domain هیچ importی از FastAPI، SQLAlchemy، HTTPX، OpenAI SDK یا React ندارد. Types و rules خالص برای Route، Claims، Citation، Tool Request، Project State و Session lifecycle را نگه می‌دارد.

### Application

Use caseها و orchestratorهای Ask/Guide/Diagnose را اجرا می‌کند و فقط به Protocolهای Provider، Retriever، Tool Gateway، Session Vault و Telemetry متکی است.

### Infrastructure

AvalAI، Liara، PostgreSQL، filesystem indexes و clocks/rate-limit storage را پیاده می‌کند. Raw external payload قبل از خروج از Adapter Sanitized می‌شود.

### API/UI

FastAPI فقط validation، session/cookie، stream framing و error mapping را انجام می‌دهد. React فقط event/state presentation دارد و policy/business logic را تکرار نمی‌کند.

## Project Structure

### Documentation

```text
specs/001-liara-navigator/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── errors.py
│   │   ├── middleware.py
│   │   ├── schemas.py
│   │   └── routes/
│   │       ├── sessions.py
│   │       ├── turns.py
│   │       ├── project_state.py
│   │       ├── feedback.py
│   │       ├── sources.py
│   │       └── health.py
│   ├── domain/
│   │   ├── routing.py
│   │   ├── claims.py
│   │   ├── citations.py
│   │   ├── tools.py
│   │   ├── project_state.py
│   │   ├── sessions.py
│   │   ├── telemetry.py
│   │   └── errors.py
│   ├── application/
│   │   ├── router.py
│   │   ├── ask.py
│   │   ├── guide.py
│   │   ├── diagnose.py
│   │   ├── tool_policy.py
│   │   ├── citation_service.py
│   │   ├── session_service.py
│   │   ├── handoff_service.py
│   │   └── feedback_service.py
│   ├── retrieval/
│   │   ├── normalizer.py
│   │   ├── bm25_index.py
│   │   ├── vector_index.py
│   │   ├── fusion.py
│   │   ├── sufficiency.py
│   │   └── snapshot_loader.py
│   ├── providers/
│   │   ├── ai/base.py
│   │   ├── ai/avalai.py
│   │   ├── liara/base.py
│   │   ├── liara/client.py
│   │   ├── liara/sanitizers.py
│   │   └── liara/tools.py
│   ├── security/
│   │   ├── session_vault.py
│   │   ├── rate_limit.py
│   │   ├── resource_refs.py
│   │   └── scrubber.py
│   └── telemetry/
│       ├── models.py
│       ├── repository.py
│       ├── maintenance.py
│       └── metrics.py
├── migrations/
│   ├── env.py
│   └── versions/0001_telemetry.py
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── security/
│   ├── integration/
│   └── fixtures/
└── pyproject.toml

frontend/
├── src/
│   ├── app/App.tsx
│   ├── api/client.ts
│   ├── api/events.ts
│   ├── features/session/
│   ├── features/chat/
│   ├── features/sources/
│   ├── features/project-state/
│   ├── features/feedback/
│   ├── components/
│   ├── styles/tokens.css
│   └── styles/global.css
├── tests/
├── package.json
├── tsconfig.json
└── vite.config.ts

knowledge/
├── sources.yaml
├── pipeline/
│   ├── fetch.py
│   ├── clean.py
│   ├── chunk.py
│   ├── anchors.py
│   ├── embed.py
│   └── build.py
└── snapshots/<version>/
    ├── manifest.json
    ├── chunks.jsonl
    ├── bm25.index
    └── vectors.index

evals/
├── golden-set/cases.jsonl
├── baselines/bm25.py
├── runner.py
├── metrics.py
└── reports/

tests/e2e/
├── ask.spec.ts
├── connect.spec.ts
├── diagnose.spec.ts
└── unknown.spec.ts

Dockerfile
.dockerignore
.env.example
compose.local.yaml
```

**Structure Decision**: Web application source tree با Domain/Application/Infrastructure boundaries در Backend و feature-oriented React tree. Knowledge pipeline و Evaluation به‌عنوان tooling جدا هستند ولی Artifactهایشان توسط همان release مصرف می‌شود.

## Implementation Phases

### Phase 1 — Repository and Runtime Foundation

Bootstrap locked Python/Node projects، config validation، FastAPI/React same-origin shell، anonymous Session/CSRF، PostgreSQL migration، typed errors، secure cookies، content-free logging و Docker skeleton.

**Exit criteria**: health endpoints و React shell در Docker کار کنند؛ migration اجرا شود؛ secret در logs ظاهر نشود.

### Phase 2 — Offline Knowledge and Ask Slice

Source allowlist، cleaner/chunker/anchor validator، AvalAI embedding build، immutable snapshot loader، hybrid retrieval، Ask provider call، structured Claim response، Citation Gate و Evidence UI.

**Exit criteria**: US1 مستقل، با mock provider و sample snapshot، valid/unknown/supporting-removal cases را پاس کند.

### Phase 3 — Session and Read-only Connection Slice

گسترش Anonymous Session Vault با Token upgrade، TTL، connect rate limit، Liara client، resource inventory/ref mapping، allowlist-first sanitizers و Connect UI.

**Exit criteria**: US2 مستقل با fixtures شامل future-secret field و invalid/expired token پاس شود.

### Phase 4 — Diagnose Slice

Tool registry/policy، three-family tools، project-state refresh، current/previous snapshot، multi-label route، hypotheses و docs-only fallback.

**Exit criteria**: US3 با synthetic project state و policy denial/timeout/refresh cases پاس شود.

### Phase 5 — Guide, Scope Degradation, Handoff and Feedback

Plan state، clarification، one-step presentation، partial/out-of-scope behavior، Unknown/Handoff UI و structured feedback.

**Exit criteria**: US4–US6 مستقل و call budgets enforce شوند.

### Phase 6 — Telemetry, Evaluation and Hardening

Positive telemetry، retention job، metrics، Golden Set runner، BM25 baseline، accessibility/security/performance tests و circuit breakers.

**Exit criteria**: report نسخه‌دار همه Success Criteria را محاسبه کند؛ retention observable باشد.

### Phase 7 — Liara Release

Production Docker build، committed real snapshot، environment configuration، database private connection، migrations، smoke/E2E و demo rehearsal.

**Exit criteria**: URL واقعی `liara.run` Ask و read-only Diagnose را end-to-end اجرا کند.

## Interface Decisions

جزئیات HTTP در [contracts/openapi.yaml](./contracts/openapi.yaml) و Entityها در [data-model.md](./data-model.md) مرجع هستند. هر تغییر signature باید هم‌زمان این سه Artifact و tests را به‌روزرسانی کند.

## Test Strategy

1. **Unit**: pure routing، normalization، fusion، sufficiency، citation، TTL و policy.
2. **Contract**: OpenAPI payloads، AvalAI structured output و Liara field sanitization.
3. **Security**: method/path denial، cross-session resource، secret injection، rate limit و cache headers.
4. **Integration**: orchestrators با fake adapters و PostgreSQL test database.
5. **Evaluation**: Golden Set و BM25 baseline.
6. **E2E**: browser flows و deployed smoke tests.

Tests در هر Task پیش از implementation نوشته و Fail می‌شوند. Live tests با secrets فقط manual/release هستند و در CI عمومی skip می‌شوند.

## Deployment Plan

- Snapshot قبل از Docker build ساخته و Commit می‌شود.
- Frontend در Node stage build می‌شود.
- Python runtime فقط production dependencies و artifacts را دریافت می‌کند.
- Startup migration با یک explicit release command یا pre-start step انجام می‌شود؛ app process migration race ندارد.
- Uvicorn با host `0.0.0.0`، port `8000` و one worker اجرا می‌شود.
- Environment شامل AvalAI config، database URL، session secret، snapshot version و thresholds است.
- Readiness فقط config/index/database را بررسی می‌کند.
- Deploy session loss را در UI با reconnect state مدیریت می‌کند.

## Complexity Tracking

هیچ نقض Constitution وجود ندارد. دو Chat Model به‌جای یک مدل تنها، Complexity محدود و توجیه‌شده داخل Adapter config است و Requirement Cost Optimization را بدون افزودن subsystem جدید پوشش می‌دهد.
