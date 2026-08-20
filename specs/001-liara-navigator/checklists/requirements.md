# Requirements Quality Checklist: Liara Navigator MVP

**Purpose**: بازبینی کامل‌بودن، صراحت، قابلیت آزمون و انطباق Requirements پیش از تولید Plan  
**Created**: 2026-08-20  
**Feature**: [spec.md](../spec.md)  
**Review Ownership**: این Checklist یک Artifact بازبینی Requirements است؛ علامت `[x]` فقط به معنی تأیید کیفیت Requirement است، نه تکمیل Implementation.

## Product Scope

- [x] CHK001 مرز Ask در برابر Guide/Diagnose صریح و بدون تداخل تعریف شده است.
- [x] CHK002 رفتار Full، Partial و Out-of-scope coverage قابل‌آزمون است.
- [x] CHK003 سه Task Family مجاز Guide/Diagnose دقیقاً نام برده شده‌اند.
- [x] CHK004 Non-goalها مانع ورود Write Action و Scope creep می‌شوند.
- [x] CHK005 هر User Story یک Independent Test و Acceptance Scenario دارد.

## Agent and Routing

- [x] CHK006 Intent چندبرچسبی و Confidence پایین رفتار قطعی دارند.
- [x] CHK007 Ask، Guide و Diagnose Call Budget صریح دارند.
- [x] CHK008 رفتار پس از مصرف Call Budget تعریف شده است.
- [x] CHK009 Tool Request مدل از Tool Execution Policy جدا شده است.
- [x] CHK010 Refresh وضعیت پروژه فقط Trigger صریح کاربر دارد.
- [x] CHK011 Tool denial/timeout به Fallback مشخص منجر می‌شود.

## Retrieval and Citation

- [x] CHK012 Source trust boundary و منابع ممنوع صریح هستند.
- [x] CHK013 Chunking، Retrieval و Candidate limits در Design مستند شده‌اند.
- [x] CHK014 Core و Supporting Claim براساس Schema قابل‌تشخیص‌اند.
- [x] CHK015 Citation validity یک تابع قابل‌تست با Threshold نسخه‌دار است.
- [x] CHK016 Core failure، Supporting failure و Unknown behavior بدون ابهام‌اند.
- [x] CHK017 Citation UI هر سه سطح سند، Heading و Evidence را پوشش می‌دهد.
- [x] CHK018 Anchor integrity پیش از انتشار Snapshot بررسی می‌شود.
- [x] CHK019 Runtime Knowledge Rebuild صریحاً وجود ندارد.

## Security and Privacy

- [x] CHK020 Endpoint، Host، Method و Field allowlist هم‌زمان تعریف شده‌اند.
- [x] CHK021 Unknown Field به‌صورت Fail-closed حذف می‌شود.
- [x] CHK022 Token lifecycle، TTL، Disconnect و Restart behavior صریح‌اند.
- [x] CHK023 Resource ownership با Session-scoped reference enforce می‌شود.
- [x] CHK024 ساخت Session ناشناس، Connect، Turn و Tool rate limit عدد مشخص دارند.
- [x] CHK025 IP فقط به‌صورت مشتق موقت در Memory استفاده می‌شود.
- [x] CHK026 Feedback متن آزاد ندارد و Future scrub rule تعریف شده است.
- [x] CHK027 مرز Application privacy و Platform access logging صریح است.
- [x] CHK028 هیچ داده حساس در Telemetry positive schema وجود ندارد.

## Data, Telemetry, and Retention

- [x] CHK029 Positive telemetry schema برای تمام Metricهای هدف کافی است.
- [x] CHK030 Telemetry عملیاتی از semantic Citation Accuracy تفکیک شده است.
- [x] CHK031 Retention window و deletion mechanism دقیق هستند.
- [x] CHK032 Maintenance failure قابل‌رصد است.
- [x] CHK033 Session ID به هویت واقعی قابل نگاشت نیست.

## Reliability, Cost, and Performance

- [x] CHK034 Generation Call budgets با State Machine سازگارند.
- [x] CHK035 Embedding Callها جدا از Generation اندازه‌گیری می‌شوند.
- [x] CHK036 عملیات CPU-bound از Async Event Loop جدا شده‌اند.
- [x] CHK037 Provider outage باعث Restart Loop نمی‌شود.
- [x] CHK038 Idempotency از هزینه تکراری Retry مرورگر جلوگیری می‌کند.
- [x] CHK039 Latency targets برای هر Mode قابل‌اندازه‌گیری‌اند.

## Evaluation and Demo

- [x] CHK040 Success Criteria همگی کمّی و قابل‌تأیید هستند.
- [x] CHK041 Golden Set تمام Routeها، Unknown، Conflict و Tool cases را پوشش می‌دهد.
- [x] CHK042 BM25 baseline و تعریف Time-to-resolution مشخص‌اند.
- [x] CHK043 Containment denominator فقط Sessionهای واجد شرایط را شامل می‌شود.
- [x] CHK044 Live AvalAI و Live Liara read-only smoke tests تعریف شده‌اند.
- [x] CHK045 Deployment E2E روی URL واقعی Liara تعریف شده است.

## UX and Accessibility

- [x] CHK046 RTL، LTR technical content و Responsive behavior Requirement دارند.
- [x] CHK047 Unknown و Handoff خروجی مفید و غیرخالی دارند.
- [x] CHK048 Source preview، Deep Link و Copy behavior قابل‌آزمون‌اند.
- [x] CHK049 Keyboard navigation و visible focus Requirement دارند.
- [x] CHK050 Feature Spec با Design System موجود تناقض ندارد.

## Notes

- Self-review و تحلیل Cross-artifact در 2026-08-20 انجام شد؛ پوشش Requirementها در [traceability.md](traceability.md) ثبت شده است.
- علامت `[x]` فقط کیفیت و قابلیت پیاده‌سازی Specification را تأیید می‌کند و به معنی تکمیل Implementation نیست.
