# Data Model: Liara Navigator MVP

**Date**: 2026-08-20  
**Spec**: [spec.md](./spec.md)  
**Contract**: [contracts/openapi.yaml](./contracts/openapi.yaml)

## 1. Storage Classes

هر Entity دقیقاً یکی از این Storage Classها را دارد:

| Class | Location | Lifetime | Content rule |
|---|---|---|---|
| `EPHEMERAL_SECRET` | Process memory | session TTL | Token؛ هرگز log/persist/model context نمی‌شود |
| `EPHEMERAL_STATE` | Process memory | request یا session TTL | Conversation state و sanitized project snapshots |
| `IMMUTABLE_ARTIFACT` | Release filesystem | release lifetime | Knowledge snapshot بدون user data |
| `PERSISTED_METADATA` | PostgreSQL | حداکثر ۳۰ روز | Positive telemetry/evaluation schema بدون content |
| `STATIC_SPEC` | Repository | version-controlled | Golden set مصنوعی، source config و contracts |

## 2. Ephemeral Entities

### 2.1 AnonymousSession

**Storage**: `EPHEMERAL_STATE`

| Field | Type | Rule |
|---|---|---|
| `session_id` | UUID | random 128-bit، فقط cookie/reference |
| `created_at` | UTC datetime | immutable |
| `last_activity_at` | UTC datetime | روی درخواست معتبر update می‌شود |
| `idle_expires_at` | UTC datetime | last activity + 30 minutes |
| `absolute_expires_at` | UTC datetime | created + 2 hours |
| `status` | SessionStatus | active/disconnected/expired |
| `connection_state` | ConnectionState | anonymous/validating/connected |
| `csrf_token_hash` | SHA-256/HMAC digest | raw CSRF token فقط در frontend memory |
| `liara_token_ref` | opaque memory key or null | خود Token داخل Entity serialization نیست |
| `resource_inventory` | map<ResourceRef, ResourceBinding> | فقط memory |
| `agent_state` | AgentSessionState | فقط Guide/Diagnose state لازم |
| `current_snapshot` | SanitizedProjectSnapshot or null | حداکثر یک مورد |
| `previous_snapshot` | SanitizedProjectSnapshot or null | حداکثر یک مورد |
| `active_turns` | set<UUID> | max size 2 |

**Invariants**:

- `idle_expires_at <= absolute_expires_at`.
- Session غیرactive هیچ Tool یا Turn جدیدی نمی‌پذیرد.
- Serialization عمومی هرگز `liara_token_ref` یا internal binding را برنمی‌گرداند.
- Deploy/restart کل collection را حذف می‌کند.

### 2.2 SecretTokenEntry

**Storage**: `EPHEMERAL_SECRET`

| Field | Type | Rule |
|---|---|---|
| `vault_key` | random opaque string | internal only |
| `token` | secret string | log/repr disabled |
| `session_id` | UUID | ownership |
| `created_at` | UTC datetime | immutable |
| `expires_at` | UTC datetime | never beyond session absolute expiry |

**Transitions**: `created → active → deleted`. Delete در disconnect، expiry، failed validation و shutdown انجام می‌شود.

### 2.3 ResourceBinding

**Storage**: `EPHEMERAL_STATE`

| Field | Type | Rule |
|---|---|---|
| `resource_ref` | string | `res_` + random URL-safe value |
| `family` | ResourceFamily | paas/domain/dns/database |
| `upstream_id` | string | internal memory only |
| `display_label` | string | sanitized for UI؛ never persisted |
| `allowed_tools` | set<ToolName> | derived server-side |
| `discovered_at` | UTC datetime | session-scoped |

**Invariant**: Client-provided upstream ID هرگز پذیرفته نمی‌شود؛ Tool فقط `resource_ref` را resolve می‌کند.

### 2.4 AgentSessionState

**Storage**: `EPHEMERAL_STATE`

| Field | Type | Description |
|---|---|---|
| `mode` | Mode or null | ask/guide/diagnose |
| `task_families` | ordered set<TaskFamily> | multi-label |
| `goal` | string or null | in-memory user goal |
| `plan_steps` | list<PlanStep> | Guide only |
| `current_step_index` | integer or null | zero-based |
| `steps_tried` | list<StepOutcome> | session only |
| `awaiting` | AwaitingState | none/clarification/user_action/refresh |
| `last_request_id` | UUID or null | idempotency/context |

### 2.5 RouteDecision

| Field | Type | Validation |
|---|---|---|
| `mode` | Mode | required |
| `task_families` | unique list<TaskFamily> | may be empty only for general Ask |
| `needs_project_state` | boolean | true only Guide/Diagnose |
| `confidence` | decimal 0..1 | programmatic score |
| `scope_coverage` | ScopeCoverage | full/partial/ask_only |
| `clarification_required` | boolean | true when confidence < 0.65 |
| `containment_eligible` | boolean | supported task and not policy-excluded |

### 2.6 ToolRequest

| Field | Type | Validation |
|---|---|---|
| `tool_name` | ToolName enum | registry member |
| `resource_ref` | string | current session inventory |
| `parameters` | discriminated typed object | no URL/header/method fields |
| `reason` | bounded string | max 240 chars; not logged |

### 2.7 ToolDecision

| Field | Type | Description |
|---|---|---|
| `allowed` | boolean | policy outcome |
| `code` | ToolDecisionCode | allowed/policy_denied/resource_not_allowed/rate_limited |
| `resolved_tool` | ToolExecutionPlan or null | server-owned host/path/method |

### 2.8 SanitizedProjectSnapshot

**Storage**: `EPHEMERAL_STATE`

| Field | Type | Rule |
|---|---|---|
| `snapshot_id` | UUID | random |
| `resource_ref` | string | session-scoped |
| `family` | ResourceFamily | required |
| `captured_at` | UTC datetime | required |
| `schema_version` | string | sanitizer schema version |
| `facts` | typed union | allowlist fields only |
| `tool_names` | list<ToolName> | provenance |

Typed facts:

- `PaasFacts`: status، is_deployed، platform، release state/time، applet state/reason، metric summary.
- `DomainFacts`: domain status، SSL status، mapping status.
- `DnsFacts`: nameserver status و sanitized required records.
- `DatabaseFacts`: type، version، status، public_network، metric summary.

**Forbidden fields**: env values، passwords، credentials، connection strings، raw IPs، node objects، billing values و unknown extras.

### 2.9 Claim and Citation

```text
Claim
├── claim_id: UUID
├── role: core | supporting
├── slot: direct_answer | current_step | primary_finding | next_safe_check | explanation | safety_warning
├── text: string
└── citations: Citation[]

Citation
├── chunk_id: string
├── evidence_span: string
└── validation: CitationValidation
```

`CitationValidation` fields:

- `trusted_source: bool`
- `retrieved_chunk: bool`
- `exact_span: bool`
- `critical_token_coverage: decimal`
- `lexical_overlap: decimal`
- `semantic_similarity: decimal`
- `valid: bool`
- `threshold_version: string`

**Invariant**: core claim invalid → `AnswerOutcome.UNKNOWN`; supporting claim invalid → omitted from rendered output.

### 2.10 TurnExecution

**Storage**: `EPHEMERAL_STATE` during request; only metadata projection persists.

| Field | Type |
|---|---|
| `request_id` | UUID |
| `client_turn_id` | UUID |
| `session_id` | UUID |
| `message` | string, max 4000 chars |
| `requested_mode` | auto/ask/guide/diagnose |
| `resource_refs` | list<string>, max 5 |
| `route` | RouteDecision or null |
| `budget` | CallBudget |
| `status` | TurnStatus |
| `answer` | RenderableAnswer or null |
| `error_code` | ErrorCode or null |
| `timings` | StageTimings |

`message` و `answer` هیچ persistent projectionی ندارند.

## 3. Immutable Knowledge Entities

### 3.1 KnowledgeSnapshotManifest

| Field | Type |
|---|---|
| `snapshot_version` | semver/date-hash string |
| `created_at` | UTC datetime |
| `source_manifest_hash` | SHA-256 |
| `chunks_hash` | SHA-256 |
| `bm25_hash` | SHA-256 |
| `vectors_hash` | SHA-256 |
| `embedding_model` | string |
| `embedding_dimensions` | integer |
| `chunker_version` | string |
| `normalizer_version` | string |
| `threshold_version` | string |
| `source_count` | integer |
| `chunk_count` | integer |

### 3.2 KnowledgeChunk

| Field | Type | Validation |
|---|---|---|
| `chunk_id` | stable string | unique within snapshot |
| `content` | string | sanitized |
| `source_url` | HTTPS URL | allowlisted host |
| `document_title` | string | required |
| `heading_path` | list<string> | non-empty |
| `anchor` | string | validated against rendered HTML |
| `source_type` | enum | docs/openapi/github/product |
| `repository` | string or null | official only |
| `commit_sha` | string or null | required for GitHub source |
| `content_hash` | SHA-256 | required |
| `indexed_at` | UTC datetime | required |
| `trust_tier` | primary/secondary | explicit |
| `version_metadata` | map<string,string> | bounded keys |

## 4. Persistent PostgreSQL Entities

### 4.1 turn_telemetry

| Column | PostgreSQL type | Null | Constraint |
|---|---|---:|---|
| `id` | uuid | no | primary key |
| `session_id` | uuid | no | random, no identity mapping |
| `request_id` | uuid | no | unique |
| `turn_index` | integer | no | >= 1 |
| `occurred_at` | timestamptz | no | indexed |
| `mode` | varchar(16) | no | enum check |
| `task_families` | jsonb | no | array of enum strings |
| `route_confidence` | numeric(4,3) | no | 0..1 |
| `needs_project_state` | boolean | no | |
| `containment_eligible` | boolean | no | |
| `tool_invoked` | boolean | no | |
| `tool_result` | varchar(32) | yes | bounded enum |
| `citation_result` | varchar(32) | no | valid/unknown/supporting_removed |
| `core_claim_count` | smallint | no | >= 0 |
| `valid_core_claim_count` | smallint | no | >= 0 |
| `supporting_claims_removed` | smallint | no | >= 0 |
| `unknown_shown` | boolean | no | |
| `handoff_shown` | boolean | no | |
| `handoff_requested` | boolean | no | |
| `user_reported_resolved` | boolean | yes | null until feedback |
| `feedback_reason` | varchar(32) | yes | bounded enum only |
| `retrieval_ms` | integer | no | >= 0 |
| `embedding_ms` | integer | no | >= 0 |
| `generation_ms` | integer | no | >= 0 |
| `tool_ms` | integer | no | >= 0 |
| `total_ms` | integer | no | >= 0 |
| `input_tokens` | integer | no | >= 0 |
| `output_tokens` | integer | no | >= 0 |
| `embedding_tokens` | integer | no | >= 0 |
| `estimated_cost` | numeric(14,8) | no | >= 0 |
| `model_id` | varchar(96) | yes | configured model ID |
| `embedding_model_id` | varchar(96) | yes | configured model ID |
| `snapshot_version` | varchar(96) | no | |
| `prompt_version` | varchar(48) | no | |
| `threshold_version` | varchar(48) | no | |
| `error_code` | varchar(48) | yes | bounded enum |

**Indexes**:

- `(occurred_at)` for retention.
- `(session_id, occurred_at)` for containment/time-to-resolution.
- `(mode, occurred_at)` for latency dashboards.
- `(snapshot_version, prompt_version, model_id)` for regression grouping.

### 4.2 maintenance_runs

| Column | Type | Rule |
|---|---|---|
| `id` | uuid | PK |
| `job_name` | varchar(48) | `telemetry_retention` |
| `started_at` | timestamptz | required |
| `finished_at` | timestamptz | nullable while running |
| `status` | varchar(16) | running/succeeded/failed/skipped_lock |
| `rows_deleted` | integer | >= 0 |
| `error_code` | varchar(48) | bounded, no stack trace |

Retention برای این جدول نیز ۳۰ روز است، جز آخرین رکورد موفق که تا جایگزینی رکورد موفق جدید حفظ می‌شود.

### 4.3 evaluation_runs

| Column | Type | Rule |
|---|---|---|
| `id` | uuid | PK |
| `started_at` | timestamptz | required |
| `finished_at` | timestamptz | required |
| `golden_set_version` | varchar(48) | required |
| `snapshot_version` | varchar(96) | required |
| `prompt_version` | varchar(48) | required |
| `model_id` | varchar(96) | required |
| `embedding_model_id` | varchar(96) | required |
| `threshold_version` | varchar(48) | required |
| `metrics` | jsonb | aggregate numbers only |
| `failed_scenario_ids` | jsonb | IDs only, no user content |

## 5. Static Golden Set Entity

`GoldenCase` in `evals/golden-set/cases.jsonl`:

```json
{
  "scenario_id": "ASK-001",
  "category": "ask_answerable",
  "input": "synthetic question",
  "requested_mode": "ask",
  "expected_families": ["deployment"],
  "expected_core_facts": ["fact-id-1"],
  "allowed_chunk_ids": ["docs-123"],
  "expected_tool": null,
  "expected_outcome": "answer",
  "max_generation_calls": 1
}
```

Golden Set فقط داده مصنوعی یا دستی پاک‌سازی‌شده دارد و Credential/production log نمی‌پذیرد.

## 6. State Transitions

### Session

```text
NEW → ACTIVE_ANONYMOUS
ACTIVE_ANONYMOUS → TOKEN_VALIDATING → ACTIVE_CONNECTED
TOKEN_VALIDATING → TOKEN_REJECTED → ACTIVE_ANONYMOUS
ACTIVE_CONNECTED → TOKEN_DISCONNECTED → ACTIVE_ANONYMOUS
ACTIVE_ANONYMOUS | ACTIVE_CONNECTED → SESSION_DISCONNECTED → DELETED
ACTIVE_ANONYMOUS | ACTIVE_CONNECTED → IDLE_EXPIRED → DELETED
ACTIVE_ANONYMOUS | ACTIVE_CONNECTED → ABSOLUTE_EXPIRED → DELETED
ACTIVE_ANONYMOUS | ACTIVE_CONNECTED → PROCESS_STOPPED → DELETED
```

### Turn

```text
ACCEPTED
→ ROUTING
→ CLARIFICATION_REQUIRED | RETRIEVING
→ TOOL_POLICY (Guide/Diagnose optional)
→ GENERATING
→ VALIDATING_CITATIONS
→ ANSWERED | UNKNOWN | FAILED
→ COMPLETED
```

### Guide

```text
GOAL_CAPTURED → CLARIFYING → PLANNED → STEP_PRESENTED
→ AWAITING_USER → VALIDATING → NEXT_STEP | COMPLETED | RECOVERY | HANDOFF
```

### Diagnose

```text
CONTEXT_CAPTURED → INSPECTING → HYPOTHESES_READY → CHECK_PRESENTED
→ AWAITING_USER → REFRESH_REQUESTED → COMPARING
→ RESOLVED | NEXT_HYPOTHESIS | UNKNOWN | HANDOFF
```

## 7. Enumerations

- `Mode`: auto, ask, guide, diagnose
- `TaskFamily`: deployment, domain_dns_ssl, database, general_docs, billing, other
- `ResourceFamily`: paas, domain, dns, database
- `ScopeCoverage`: full, partial, ask_only
- `AnswerOutcome`: answer, unknown, conflict, failed
- `ToolResult`: success, timeout, unavailable, policy_denied, resource_not_allowed, rate_limited, not_needed
- `CitationResult`: valid, unknown, supporting_removed
- `FeedbackReason`: solved, partially_solved, not_relevant, unclear, source_missing, tool_unavailable
- `AwaitingState`: none, clarification, user_action, refresh
- `ConnectionState`: anonymous, validating, connected
- `ErrorCode`: values defined in architecture Error Taxonomy

## 8. Deletion and Projection Rules

1. Persisted telemetry از `TurnExecution` با explicit constructor ساخته می‌شود؛ object serialization عمومی ممنوع است.
2. Constructor فقط fieldهای `turn_telemetry` را می‌پذیرد و extra input را reject می‌کند.
3. Request message، response claims، evidence spans و project facts هیچ column مقصدی ندارند.
4. Feedback فقط `resolved`، `reason` و `handoff_requested` bounded را روی telemetry request متناظر update می‌کند؛ resolved و handoff هم‌زمان مجاز نیستند.
5. Retention query: `occurred_at < now() - interval '30 days'`، batch limit ثابت و transaction کوتاه.
6. Session cleanup قبل و بعد از هر lookup expiry را بررسی می‌کند تا stale token استفاده نشود.
