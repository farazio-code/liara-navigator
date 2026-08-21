# Tasks: Liara Navigator MVP — Reduced Vertical-Slice Backlog

**Input**: Product workflow approved on 2026-08-21

**Design**: `docs/design-system/liara-intelligence-design-system.md` remains canonical and unchanged.

**Delivery rule**: Every slice must be independently testable and demoable. Tests precede behavior.

## Locked MVP decisions

- Entry flow is `Support ticket | Agentic assistant`.
- Agentic flow starts with an explicit topic: PaaS, CDN, SSL, DNS, or Other.
- Only PaaS receives runtime context in MVP: `platform -> app -> service -> bounded logs`.
- Runtime data comes from a deterministic Fake Liara Service; no personal Liara token is accepted.
- Documentation is progressively disclosed: search metadata first, then at most a bounded set of chunks.
- The agent loop is bounded to two model calls and one log fetch per turn.
- Support ticket submission is mocked; real support-system integration is outside MVP.
- Raw prompts, tickets, resource identities, and logs are never persisted in telemetry.

## Slice 1 — Foundation, workflow shell, and Fake Liara Service

**Exit**: The user can choose Ticket or Agentic; in Agentic/PaaS they can select platform, app, and service from deterministic mock data.

- [x] T001 Bootstrap locked Python/Node projects and source directories
- [x] T002 Implement typed settings, safe errors, security middleware, and bounded executor
- [x] T003 Implement anonymous session creation with memory-only CSRF and no-store responses
- [x] T004 Establish backend contract tests and frontend Vitest/Testing Library harness
- [x] T005 Write contract tests for platform, app, service, and bounded-log mock endpoints
- [x] T006 Implement typed Fake Liara fixtures, provider, opaque references, and ownership checks
- [x] T007 Expose session-scoped Fake Liara read endpoints with safe error mapping
- [x] T008 Write frontend workflow tests for Ticket/Agentic, topic, platform, app, and service selection
- [x] T009 Implement canonical LIDS tokens, RTL responsive shell, and accessible mode/topic controls
- [x] T010 Implement dependent PaaS selectors with loading, empty, error, retry, and downstream reset states
- [x] T011 Implement memory-only API client/session bootstrap for Fake Liara reads
- [x] T012 Run backend/frontend lint, typecheck, tests, and Slice 1 smoke verification

## Slice 2 — Offline knowledge, progressive read_doc, and citations

**Exit**: A fixture question returns a cited answer or an honest Unknown without loading the full documentation into model context.

- [x] T013 Test official-source allowlist, MDX cleaning, chunk boundaries, and rendered anchors
- [x] T014 Implement versioned source manifest, cleaner, heading-aware chunker, and anchor validator
- [x] T015 Build a deterministic official-doc fixture snapshot with topic/platform metadata
- [x] T016 Test Persian/English normalization and deterministic exact/semantic fusion
- [x] T017 Implement immutable hybrid search and topic-aware retrieval scoring
- [x] T018 Define progressive `search_docs` and `read_doc` contracts with per-turn chunk/character budgets
- [x] T019 Implement read-on-demand context assembly and reject arbitrary paths or non-manifest chunks
- [x] T020 Implement claim/citation validation, deep links, evidence previews, and Unknown outcomes
- [x] T021 Run snapshot, retrieval, citation, and token-budget regression suites

## Slice 3 — General topic-aware Agentic assistance

**Exit**: CDN/SSL/DNS/Other questions follow a bounded documentation-only agent loop with citations.

- [ ] T022 Test explicit topic routing, clarification, call budget, and docs-only degradation
- [ ] T023 Define typed agent state, tool request, tool decision, and terminal-result models
- [ ] T024 Implement deterministic router using the explicit topic before model inference
- [ ] T025 Implement AI provider adapter with timeout, circuit breaker, and maximum two calls per turn
- [ ] T026 Implement bounded agent loop: clarify, search, read selected chunks, answer/unknown, then stop
- [ ] T027 Implement typed SSE events, idempotent turns, and topic-aware composer/status UI
- [ ] T028 Run general Agentic E2E scenarios for CDN, SSL, DNS, Unknown, Conflict, and provider failure

## Slice 4 — PaaS service-log diagnosis

**Exit**: The selected service's sanitized recent logs and the user's question produce a cited diagnostic response without leaking or persisting raw logs.

- [ ] T029 Test service ownership, one-fetch-per-turn policy, timeout, and cross-session denial
- [ ] T030 Define bounded log DTO with timestamp, stream, line limit, freshness, and truncation metadata
- [ ] T031 Implement secret/PII redaction, control-character cleanup, and prompt-injection delimiters for logs
- [ ] T032 Test sanitizer against tokens, passwords, connection strings, malicious log instructions, and oversized lines
- [ ] T033 Implement PaaS context assembler combining user prompt, sanitized logs, and progressively read docs
- [ ] T034 Implement PaaS diagnosis orchestration with ranked hypotheses, evidence, safe next check, and Unknown fallback
- [ ] T035 Extend turn stream with log-fetch, sanitization, retrieval, and completion states
- [ ] T036 Implement selected-context chips, freshness label, manual refresh, and explicit log-use notice
- [ ] T037 Ensure changing topic/platform/app/service clears all stale downstream context
- [ ] T038 Add PaaS Golden cases for noisy, missing, stale, malicious, and sufficient logs
- [ ] T039 Run PaaS E2E and assert no raw log appears in storage, telemetry, errors, or server logs

## Slice 5 — Ticket, handoff, evaluation, and release

**Exit**: Ticket and Agentic paths are demo-ready, accessible, privacy-safe, containerized, and measured.

- [ ] T040 Define strict mock ticket schema with bounded fields, no attachments, and no secret-bearing payloads
- [ ] T041 Implement accessible Ticket form, validation, mock submission, success, retry, and draft preservation
- [ ] T042 Implement optional scrubbed Agentic-to-Ticket handoff summary without raw logs or resource identity
- [ ] T043 Implement positive-schema telemetry, retention, and separate Ticket/Agentic outcome metrics
- [ ] T044 Build versioned Golden Set and BM25 baseline for citations, routing, tool choice, Unknown, and log diagnosis
- [ ] T045 Run accessibility, keyboard, RTL/LTR, responsive, rate-limit, resilience, and security suites
- [ ] T046 Build multi-stage non-root production image and same-origin static fallback
- [ ] T047 Run full E2E demo: Ticket, general Agentic, PaaS logs, Unknown, handoff, and provider failure
- [ ] T048 Deploy to Liara and record content-free release verification and privacy limitations

## Progress

- Total: 48 tasks
- Completed: 21
- Active slice: Slice 3
