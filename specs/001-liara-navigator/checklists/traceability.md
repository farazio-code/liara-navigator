# Requirements Traceability Matrix: Liara Navigator MVP

**Reviewed**: 2026-08-20  
**Status**: PASS — every requirement group has an implementation task and verification path  
**Spec**: [spec.md](../spec.md)  
**Tasks**: [tasks.md](../tasks.md)

## Functional Requirements

| Requirements | Primary tasks | Verification |
|---|---|---|
| FR-001–FR-007 Modes، multi-label، confidence و degradation | T093، T102، T113–T129 | router/scope/Guide/Unknown unit and integration tests |
| FR-008–FR-010 Token connection، inventory و Resource Ref | T074–T092 | session vault، Liara inventory، cross-session security، Connect E2E |
| FR-011–FR-014 Inspector، explicit refresh، Policy و fallback | T094–T112 | three-family contracts، policy denial، refresh/no-polling، Diagnose E2E |
| FR-015 Retrieval bilingual/exact | T040–T051 | normalizer، indexes، fusion، sufficiency tests |
| FR-016–FR-020 Claim Citation، core/supporting و Unknown | T052–T073، T122–T129 | citation service، Ask integration، Unknown UI/E2E |
| FR-021 Handoff summary | T123، T127–T129 | bounded/scrubbed handoff security and UI tests |
| FR-022–FR-023 SSE و Idempotency | T063، T067، T069، T073 | stream contract and retry E2E |
| FR-024 Token disconnect and full session deletion | T074، T085، T089–T092 | anonymous-preserving disconnect، full deletion and expired-ref tests |
| FR-025 Structured feedback/handoff outcome | T130–T136 | strict schema، ownership، exclusivity tests |
| FR-026–FR-027 RTL، Responsive و technical LTR/copy | T024–T025، T065، T070–T073، T155، T160 | frontend unit، axe و Playwright |
| FR-028 Conflict handling | T043، T049، T055، T124، T128–T129 | conflict unit/integration/UI tests |
| FR-029 Evidence Sufficiency | T043، T049، T055 | exact/semantic threshold tests |
| FR-030 Anonymous Ask session and token upgrade | T013، T023، T067، T074–T092 | anonymous bootstrap، token-upgrade failure preservation and E2E |

## Agent Requirements

| Requirements | Primary tasks | Verification |
|---|---|---|
| AR-001 Ask one Generation | T052، T055، T059–T062 | mocked call counter equals one |
| AR-002–AR-003 Guide/Diagnose two-call cap and overflow | T098، T107، T114، T118، T121 | integration call counters and clarification outcome |
| AR-004 Programmatic confidence | T093، T102 | threshold and manual/auto mode tests |
| AR-005 No evidence → no answer | T043، T049، T054–T062 | sufficiency and core-citation failure tests |
| AR-006 Diagnose evidence + safe check | T098، T107، T112 | synthetic Diagnose scenario |
| AR-007 Snapshot comparison | T099، T108، T112 | previous/current and explicit refresh test |

## Security and Privacy Requirements

| Requirements | Primary tasks | Verification |
|---|---|---|
| SR-001–SR-003 endpoint/field allowlists | T077–T079، T094–T106 | future-secret injection and method/path denial |
| SR-004–SR-007 token/session/cache lifecycle | T013، T074–T075، T082، T085، T089–T092 | memory-only، expiry، disconnect، no-store tests |
| SR-008–SR-009 rate limits and ephemeral IP key | T076، T083، T092 | exact session/connect/turn/tool window tests |
| SR-010–SR-012 telemetry schema and retention | T137–T147 | migration، projection، deletion and health tests |
| SR-013–SR-015 source trust and no runtime rebuild | T015، T027–T039 | source policy، anchor/build and OpenAPI path tests |
| SR-016 platform log boundary | T171 | Liara setting review، release report and PrivacyNotice |

## Reliability and Performance Requirements

| Requirements | Primary tasks | Verification |
|---|---|---|
| NFR-001–NFR-003 latency budgets | T140، T145، T163، T165، T168–T170 | telemetry percentiles and release report |
| NFR-004 no Event Loop CPU blocking | T014، T022، T050–T051 | concurrent health probe during retrieval |
| NFR-005 provider outage readiness isolation | T153–T159 | health and circuit tests |
| NFR-006 restart reconnect behavior | T074، T080، T085، T091–T092 | session loss UI/E2E |
| NFR-007–NFR-008 reproducible snapshot/anchors | T027–T039، T164 | deterministic hashes and remote anchor validation |
| NFR-009 accessibility | T155، T160، T163 | axe، keyboard، focus and responsive checks |
| NFR-010 safe error format | T012، T020، T063 | ErrorResponse contract and no raw upstream tests |

## Evaluation Requirements

| Requirements | Primary tasks | Verification |
|---|---|---|
| ER-001 Golden Set categories | T148، T151–T152، T165 | case-schema/category-count validation |
| ER-002 version metadata | T137، T143، T149، T151 | evaluation report schema |
| ER-003 semantic Citation Accuracy separation | T138–T151 | telemetry projection and Golden metrics tests |
| ER-004 BM25 baseline | T150، T152، T165 | paired report |
| ER-005 containment formulas | T140، T145، T147 | confirmed/coverage/lower-bound unit tests |
| ER-006 route/tool/unknown/latency/cost report | T140، T145، T149–T152 | fixture and release reports |

## Success Criteria Evidence

| Criteria | Evidence task |
|---|---|
| SC-001–SC-007 Quality/containment/task/tool/time metrics | T148–T152، T165 |
| SC-008 Latency targets | T140، T145، T163، T165، T168–T170 |
| SC-009 Unknown/sensitive field exclusion | T078، T095–T097، T106 |
| SC-010 No writable Liara endpoint | T094، T104–T105 |
| SC-011 Live AvalAI E2E | T168 |
| SC-012 Live Liara read-only E2E | T169 |
| SC-013 Anchor validity | T030، T035، T039، T164 |
| SC-014 UX/RTL/accessibility | T155، T160، T163، T170 |

## Review Findings Resolved

- `project-state/refresh` از Knowledge Rebuild جدا و Runtime Rebuild حذف شده است.
- Feedback برای Containment دارای `handoff_requested` و mutual-exclusion با `resolved=true` است.
- Platform logging limitation Task مستقل دارد.
- Evidence Sufficiency و conflict behavior Task و Test مستقل دارند.
- تمام ۱۷۱ Task شناسه پیوسته و یکتا دارند.
- OpenAPI تمام Local `$ref`ها را resolve می‌کند.
