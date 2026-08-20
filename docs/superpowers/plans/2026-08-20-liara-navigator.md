# Liara Navigator MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ساخت و Deploy یک دستیار مستندات و عیب‌یابی Liara با Citation قابل‌اعتبارسنجی و اتصال Read-only به منابع واقعی کاربر.

**Architecture:** یک React/FastAPI Modular Monolith از یک Docker container سرو می‌شود. Knowledge یک Snapshot تغییرناپذیر BM25+FAISS است؛ Agent از State Machine و Policy مستقل استفاده می‌کند؛ Token فقط در Memory و Telemetry فقط به‌صورت Metadata در PostgreSQL قرار می‌گیرد.

**Tech Stack:** Python 3.12، FastAPI، Pydantic 2، SQLAlchemy 2، PostgreSQL، HTTPX، OpenAI-compatible AvalAI SDK، FAISS/BM25، React 19، TypeScript، Vite، Vitest، pytest و Playwright.

**Spec:** `specs/001-liara-navigator/spec.md`  
**Detailed tasks:** `specs/001-liara-navigator/tasks.md`  
**API contract:** `specs/001-liara-navigator/contracts/openapi.yaml`

## Global Constraints

- Ask: حداکثر یک Generation Call؛ Guide/Diagnose: حداکثر دو Generation Call در Turn.
- تمام Liara upstream calls فقط GET، registry-based و resource-owned هستند.
- هیچ API response field وارد Context نمی‌شود مگر در typed field allowlist باشد.
- Token، متن، IP، resource identity، raw log و snapshot هرگز Persist نمی‌شوند.
- Knowledge Snapshot فقط offline ساخته و قبل از Liara Docker build Commit می‌شود.
- یک Instance و یک Uvicorn Worker؛ CPU retrieval در bounded thread pool.
- هر behavior ابتدا با failing test و سپس minimal implementation ساخته می‌شود.
- Design System مرجع تمام UIهای RTL/LTR، focus، responsive و evidence است.

---

## Interface Map

```python
class AIProvider(Protocol):
    async def generate(self, request: GenerationRequest) -> GenerationResult: ...
    async def embed(self, texts: list[str]) -> EmbeddingBatch: ...

class Retriever(Protocol):
    async def search(self, query: str, *, limit: int = 10) -> RetrievalResult: ...

class ToolGateway(Protocol):
    async def execute(self, plan: ToolExecutionPlan, token: SecretStr) -> SanitizedProjectSnapshot: ...

class SessionVault(Protocol):
    async def create(self, token: SecretStr) -> AnonymousSession: ...
    async def get_active(self, session_id: UUID) -> AnonymousSession: ...
    async def delete(self, session_id: UUID) -> None: ...

class TelemetryRepository(Protocol):
    async def record_turn(self, record: TurnTelemetryCreate) -> None: ...
    async def record_feedback(self, request_id: UUID, outcome: FeedbackOutcome) -> None: ...
```

Domain code consumes these Protocols; adapters implement them. No adapter type appears in Domain signatures.

### Task 1: Reproducible Runtime Foundation — Spec Kit T001–T026

**Files:**

- Create: `backend/pyproject.toml`, `backend/app/config.py`, `backend/app/main.py`
- Create: `backend/app/api/{schemas,errors,middleware,dependencies}.py`
- Create: `frontend/package.json`, `frontend/src/app/App.tsx`, `frontend/src/styles/{tokens,global}.css`
- Test: `backend/tests/unit/test_config.py`, `backend/tests/security/test_middleware.py`

**Interfaces:** Produces `Settings`, `create_app(settings) -> FastAPI`, `create_anonymous_session() -> CreateSessionResponse`, `ErrorResponse`, `run_cpu_bound(callable)`.

- [ ] Write Settings tests for missing secret, invalid threshold and production wildcard config.
- [ ] Run `uv run --project backend pytest backend/tests/unit/test_config.py -q`; expect import/module failure.
- [ ] Implement strict Settings:

```python
class Settings(BaseSettings):
    app_env: Literal["development", "test", "production"]
    database_url: PostgresDsn
    session_hmac_secret: SecretStr
    ai_base_url: AnyHttpUrl
    avalai_api_key: SecretStr
    retrieval_semantic_threshold: Annotated[float, Field(ge=0, le=1)] = 0.62
    citation_semantic_threshold: Annotated[float, Field(ge=0, le=1)] = 0.72
```

- [ ] Run foundation Backend/Frontend tests; expect PASS.
- [ ] Commit only Phase 1–2 files with `chore: bootstrap secure monolith runtime`.

### Task 2: Offline Knowledge Snapshot — T027–T039

**Files:** `knowledge/sources.yaml`, `knowledge/pipeline/{fetch,clean,chunk,anchors,embed,build}.py`, `knowledge/snapshots/test-fixture/`.

**Interfaces:** Produces `SnapshotManifest`, `KnowledgeChunk`, CLI `create` and `validate`.

- [ ] Write source-policy, cleaning, chunking and anchor tests and run them red.
- [ ] Implement pipeline around explicit types:

```python
@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str
    content: str
    source_url: str
    heading_path: tuple[str, ...]
    anchor: str
    content_hash: str
```

- [ ] Build deterministic fixture twice and assert identical manifest hashes.
- [ ] Run `python -m knowledge.pipeline.build validate --snapshot knowledge/snapshots/test-fixture`; expect PASS.
- [ ] Commit with `feat: add reproducible official knowledge snapshot pipeline`.

### Task 3: Hybrid Retrieval — T040–T051

**Files:** `backend/app/retrieval/*.py`, related unit tests.

**Interfaces:** Produces `HybridRetriever.search(query, limit=10) -> RetrievalResult` and `EvidenceSufficiency.evaluate(result) -> SufficiencyDecision`.

- [ ] Write exact error, semantic Persian, RRF and conflict tests; run red.
- [ ] Implement normalizer preserving technical spans:

```python
def normalize_query(value: str) -> NormalizedQuery:
    """Normalize natural-language spans while preserving code/error tokens verbatim."""
```

- [ ] Implement RRF with a fixed `k=60` and deterministic metadata boosts.
- [ ] Execute search through `anyio.to_thread.run_sync` with a capacity limiter.
- [ ] Run retrieval tests plus concurrent health probe; expect PASS.
- [ ] Commit with `feat: add bounded hybrid retrieval`.

### Task 4: Ask and Citation Gate — T052–T073

**Files:** AI adapter، claims/citations domain، Ask orchestrator، turn/source routes، Chat/Evidence UI.

**Interfaces:** Produces `AskService.execute(TurnContext) -> AnswerOutcome` and SSE terminal events.

- [ ] Write tests for one generation, malformed output, core failure and supporting removal; run red.
- [ ] Implement strict model output:

```python
class ModelClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")
    slot: ClaimSlot
    text: Annotated[str, Field(min_length=1, max_length=2000)]
    citations: Annotated[list[ModelCitation], Field(min_length=1, max_length=5)]
```

- [ ] Implement validator with exact span, critical coverage, lexical 0.25 and semantic 0.72 gates.
- [ ] Stream progress only; emit answer text after validation.
- [ ] Run Ask integration, frontend and Playwright tests; expect PASS and generation count one.
- [ ] Commit with `feat: deliver cited ask experience`.

### Task 5: Session Vault Upgrade and Liara Connection — T074–T092

**Files:** session domain/service/routes، memory vault، rate limit، resource refs، Liara client/sanitizers، Connect UI.

**Interfaces:** Extends the anonymous vault and produces `connect(session_id, token) -> ConnectSessionResponse`, `resolve(resource_ref) -> ResourceBinding`.

- [ ] Write expiry, CSRF, rate-limit, cross-session and future-secret tests; run red.
- [ ] Implement memory-only secret entry with redacted representation:

```python
@dataclass(repr=False)
class SecretTokenEntry:
    vault_key: str
    token: SecretStr
    session_id: UUID
    expires_at: datetime
```

- [ ] Implement allowlist DTOs with `extra="ignore"` only inside upstream sanitizers; API request models remain `extra="forbid"`.
- [ ] Run US2 contract/security/E2E tests; inspect storage/log capture for token absence.
- [ ] Commit with `feat: add ephemeral personal liara connection`.

### Task 6: Policy-gated Diagnose — T093–T112

**Files:** router، tool policy، Liara registered tools، Diagnose orchestrator، refresh route/UI.

**Interfaces:** Produces `RouteDecision`, `ToolDecision`, `DiagnoseOutcome`.

- [ ] Write multi-label, low-confidence, method/path denial and three-family sanitizer tests; run red.
- [ ] Implement fail-closed policy:

```python
def authorize_tool(request: ToolRequest, session: AnonymousSession) -> ToolDecision:
    binding = session.resource_inventory.get(request.resource_ref)
    if binding is None or request.tool_name not in binding.allowed_tools:
        return ToolDecision.denied(ToolDecisionCode.RESOURCE_NOT_ALLOWED)
    return registry.resolve_get_only(request, binding)
```

- [ ] Implement Diagnose with at most two model calls and docs-only fallback.
- [ ] Implement explicit refresh only on POST; assert zero scheduler/polling calls.
- [ ] Run US3 tests and commit with `feat: add read-only project diagnosis`.

### Task 7: Guide, Unknown, Handoff and Feedback — T113–T136

**Files:** Guide/session state، scope degradation، handoff/scrubber، strict feedback route، corresponding UI.

**Interfaces:** Produces `GuideOutcome`, `HandoffSummary`, `FeedbackOutcome`.

- [ ] Write state-transition, partial-scope, unknown and feedback exclusivity tests; run red.
- [ ] Implement current-step-only Guide state transitions.
- [ ] Implement bounded handoff summary with no external write action.
- [ ] Reject unknown Feedback properties and `resolved && handoff_requested`.
- [ ] Run US4–US6 tests; commit with `feat: complete guided recovery and honest handoff`.

### Task 8: Privacy-safe Telemetry and Evaluation — T137–T152

**Files:** migrations، telemetry models/repository/maintenance/metrics، eval runner/baseline/cases.

**Interfaces:** Produces `TurnTelemetryCreate.from_execution(...)`, retention task and versioned evaluation report.

- [ ] Write schema/projection/retention/formula tests; run red.
- [ ] Implement an explicit projection constructor; never call `model_dump()` on TurnExecution:

```python
@classmethod
def from_execution(cls, turn: TurnExecution) -> "TurnTelemetryCreate":
    return cls(
        request_id=turn.request_id,
        mode=turn.route.mode,
        total_ms=turn.timings.total_ms,
        # No message, claims, resource refs, token, IP, or project facts.
    )
```

- [ ] Implement confirmed containment، feedback coverage و conservative lower bound separately.
- [ ] Run migration/integration/evaluation fixture tests; commit with `feat: add privacy-safe evaluation telemetry`.

### Task 9: Production UI and Accessibility — T155/T160 plus all story UI tasks

**Files:** React features/components/styles and accessibility tests.

**Interfaces:** Consumes OpenAPI/SSE schemas; produces keyboard-operable RTL UI.

- [ ] Write tests for focus order, dialogs, live regions, RTL/LTR isolation and contrast tokens; run red.
- [ ] Implement design-system components without duplicating backend policy.
- [ ] Run `npm --prefix frontend run test`, typecheck and Playwright; expect PASS.
- [ ] Commit with `feat: polish accessible liara-native interface`.

### Task 10: Container, Evaluation Gate and Liara Release — T153–T170

**Files:** `Dockerfile`, `.dockerignore`, health route, real snapshot, release reports.

**Interfaces:** Produces one port-8000 image and deployed URL.

- [ ] Write health/circuit/container smoke tests; run red.
- [ ] Implement non-root multi-stage image that never receives API keys as build args.
- [ ] Build real snapshot offline and run anchor validation.
- [ ] Run all suites and Golden/BM25 reports; block release if quality gates fail.
- [ ] Deploy one instance/worker on Liara, run live AvalAI and read-only Liara smoke tests.
- [ ] Commit release artifacts with `chore: prepare liara navigator demo release`.

## Execution Order

`Task 1 → Task 2/5 → Task 3 → Task 4 → Task 6 → Task 7 → Task 8/9 → Task 10`

هر Task فقط زمانی complete است که تمام checkboxهای متناظر در `specs/001-liara-navigator/tasks.md`، testهای همان Slice و Commit gate تکمیل شده باشند.
