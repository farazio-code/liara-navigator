# Liara Navigator Constitution

## Core Principles

### I. Evidence Before Answer (NON-NEGOTIABLE)

هر ادعای فنی قابل‌بررسی MUST به یک منبع رسمی، نسخه‌دار و بازیابی‌شده متصل باشد. پاسخ بدون شواهد کافی MUST به Unknown، سؤال تکمیلی یا Handoff تبدیل شود؛ مدل حق ندارد خلأ مستندات را با حدس پر کند. Citation در سطح Claim شامل شناسه Chunk، Evidence Span دقیق، عنوان سند، مسیر Heading و لینک Anchor است. شکست اعتبارسنجی یک Core Claim کل پاسخ را Unknown می‌کند؛ شکست Supporting Claim فقط همان Claim را حذف می‌کند.

### II. Least Privilege, Allowlist-First, and Privacy-First

تمام ورودی‌های مدل، محتوای منابع و Tool Requestها Untrusted محسوب می‌شوند. ابزارهای Liara MUST فقط از Host، Method و Path Templateهای از پیش مجاز استفاده کنند و در MVP فقط GET باشند. پاسخ API به‌صورت پیش‌فرض هیچ Field مجازی برای ورود به Agent Context ندارد؛ فقط Fieldهای تعریف‌شده در Schema داخلی Typed و Allowlist‌شده عبور می‌کنند و Fieldهای جدید خودکار حذف می‌شوند. Token، متن مکالمه، Project ID/Name، IP، Log و Snapshot خام MUST در PostgreSQL ذخیره نشوند.

### III. Bounded Agentic Behavior and Cost

Ask MUST از مسیر سبک Retrieve → Cite → Answer استفاده کند و حداکثر یک Generation Call داشته باشد. Guide و Diagnose MUST در هر Turn حداکثر دو Generation Call داشته باشند. Embedding Callها جداگانه اندازه‌گیری می‌شوند. رسیدن به سقف MUST به Clarification، Unknown یا ادامه در Turn بعد منجر شود، نه فراخوانی پنهان اضافه. Polling پس‌زمینه وضعیت پروژه ممنوع است؛ Refresh فقط با اقدام صریح کاربر انجام می‌شود.

### IV. Deterministic Policy and Test-First Delivery

مدل هرگز مستقیماً Tool اجرا نمی‌کند. مدل فقط یک Tool Request ساختاریافته تولید می‌کند و Policy Layer مستقل درباره اجرا تصمیم می‌گیرد. Router، Sanitizer، Policy، Citation Gate، Rate Limiter و Retention MUST رفتار قابل‌تست و Fail-closed داشته باشند. برای هر Requirement امنیتی یا کیفیتی، Test باید پیش از Implementation متناظر نوشته و ابتدا Fail شود. Contract Test MUST ثابت کند Fieldهای ناشناخته و حساس وارد Context نمی‌شوند.

### V. Observable Without Content Surveillance

Observability MUST برای محاسبه Latency، هزینه، Containment، Unknown، Handoff، Policy Denial و Error Rate کافی باشد، بدون ذخیره محتوای واقعی کاربر. Telemetry فقط Schema مثبت مصوب را نگه می‌دارد. Citation Accuracy معنایی MUST از Golden Set نسخه‌دار محاسبه شود و نباید از Citation Gate عملیاتی استنتاج شود. Logهای Application MUST ساختاریافته، فاقد Body و Credential و دارای Request ID باشند.

### VI. Reproducible Knowledge and Provider Independence

Knowledge Corpus MUST فقط از منابع رسمی Allowlist‌شده ساخته شود. GitHub Issues، Pull Requests، Comments، Discussions، Forkها و محتوای User-generated وارد Corpus نمی‌شوند. Snapshot باید خارج از Liara Docker Build، با نسخه، Content Hash و Commit SHA ساخته و سپس به Repository اضافه شود. هسته Product MUST از AvalAI یا هر Provider خاص مستقل بماند و از Adapter و تنظیمات Environment استفاده کند.

### VII. Accessible Liara-Native Experience

رابط MUST فارسی‌اول، RTL، Responsive و منطبق با Design System مصوب پروژه باشد. Code، Error و شناسه‌های فنی MUST جهت LTR خود را حفظ کنند. وضعیت Route، Tool، منبع، Unknown و Handoff باید برای کاربر قابل‌فهم باشد. ظاهر Liara-native نباید باعث تقلید سطحی شود؛ Traceability و نمایش Evidence جزء هویت محصول است.

## Product and Architecture Constraints

- MVP یک Modular Monolith است: React + TypeScript + Vite در Frontend و Python + FastAPI در Backend.
- React Build و API از یک Docker Application و یک Origin ارائه می‌شوند.
- Deployment دارای یک Instance و یک Uvicorn Worker است؛ عملیات CPU-bound Retrieval در ThreadPool محدود اجرا می‌شود.
- Session پیش از Token به‌صورت ناشناس ساخته می‌شود تا Ask کار کند. Liara Token فقط برای ارتقای همان Session و فقط در حافظه Backend، با ۳۰ دقیقه Idle TTL و دو ساعت Absolute TTL نگهداری می‌شود.
- AvalAI API Key فقط در Environment Variable سرور نگهداری می‌شود.
- Ask تمام مستندات رسمی Snapshot را پوشش می‌دهد؛ Guide و Diagnose فقط Deployment، Domain/DNS/SSL و Database را پوشش می‌دهند.
- Intent Detection چندبرچسبی است و می‌تواند چند Task Family را هم‌زمان فعال کند.
- خارج از Scope بودن Guide/Diagnose باعث Degrade شفاف به Ask می‌شود.
- Knowledge Retrieval به‌صورت Hybrid BM25 + Vector و بدون LLM Reranker است.
- PostgreSQL فقط Telemetry و Evaluation Metadata مجاز را نگه می‌دارد؛ Vector Index داخل Snapshot تغییرناپذیر است.
- بازسازی Knowledge Snapshot هیچ Runtime Endpointی ندارد.
- `project-state/refresh` فقط Snapshot پاک‌سازی‌شده وضعیت پروژه را با Session معتبر و اقدام صریح کاربر تازه می‌کند.

## Quality Gates and Development Workflow

هر تغییر MUST از Gateهای مرتبط زیر عبور کند:

1. **Requirements Gate**: Requirement قابل‌تست، بدون Placeholder و دارای Acceptance Scenario باشد.
2. **Constitution Gate**: Plan و Tasks با تمام MUSTهای این سند سازگار باشند.
3. **Security Gate**: Threat Boundary، Field Allowlist، Secret Handling و Rate Limit تست شده باشند.
4. **Quality Gate**: Golden Set، Citation Validator و Unknown Handling بدون Regression باشند.
5. **Performance Gate**: بودجه Generation Call و Latency مسیرها اندازه‌گیری شده باشد.
6. **UX Gate**: RTL، Keyboard Navigation، Focus State، Responsive Layout و Evidence Rail بررسی شوند.
7. **Deployment Gate**: Docker Build، Health Check، Migration، Retention Job و Smoke Test واقعی روی Liara موفق باشند.

پیاده‌سازی MUST به Vertical Sliceهای مستقل و قابل Demo تقسیم شود. Complexity اضافه، Framework Agent سنگین، Microservice، Redis، Runtime Crawler و Write Tool تا زمانی که Requirement مصوبی نداشته باشند ممنوع‌اند.

## Governance

این Constitution بر تصمیم‌های موردی، Promptها و Conventionهای متناقض اولویت دارد. تغییر یک MUST نیازمند Rationale، بررسی اثر روی Security/Quality/Cost، به‌روزرسانی Spec و Plan و افزایش نسخه Constitution است. MAJOR برای حذف یا بازتعریف اصل، MINOR برای افزودن اصل یا الزام جدید و PATCH برای شفاف‌سازی غیرمعنایی استفاده می‌شود. هر Review باید انطباق با این سند را بررسی کند و نقض بدون توجیه، مانع Implementation است.

**Version**: 1.0.0 | **Ratified**: 2026-08-20 | **Last Amended**: 2026-08-20
