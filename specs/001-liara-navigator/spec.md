# Feature Specification: Liara Navigator MVP

**Feature Branch**: `001-liara-navigator`  
**Created**: 2026-08-20  
**Status**: Ready for review  
**Input**: ساخت یک MVP قابل Deploy برای Liara که کاربران را در یافتن، فهمیدن و به‌کارگیری مستندات رسمی کمک کند و بتواند با اجازه کاربر، وضعیت واقعی منابع همان حساب را فقط به‌صورت Read-only بررسی کند.

## Product Outcome

کاربر باید بتواند از یک سؤال یا خطای واقعی به پاسخ یا اقدام بعدی مستند برسد، دقیقاً ببیند هر ادعا از کدام سند و کدام بخش آمده است، و هنگام کافی نبودن شواهد با Unknown شفاف روبه‌رو شود. محصول باید در سناریوهای Guide و Diagnose از وضعیت واقعی منابع کاربر استفاده کند، بدون آنکه اجازه تغییر آن‌ها را داشته باشد.

## User Scenarios & Testing

### User Story 1 — Ask with verifiable sources (Priority: P1)

به‌عنوان کاربر Liara می‌خواهم سؤال فارسی، انگلیسی یا ترکیبی خود را درباره هر بخش از مستندات رسمی بپرسم و یک پاسخ کوتاه و کاربردی همراه منبع دقیق دریافت کنم تا مجبور نباشم صفحات متعدد را جست‌وجو و ترکیب کنم.

**Why this priority**: این کوچک‌ترین Vertical Slice ارزشمند و Baseline مقایسه با جست‌وجوی ساده است.

**Independent Test**: با پرسیدن مجموعه‌ای از سؤال‌های Golden Set، پاسخ باید در یک Turn، با Citation معتبر و بدون Project Connection ارائه شود.

**Acceptance Scenarios**:

1. **Given** سؤال پاسخ‌پذیر در منابع رسمی، **When** کاربر آن را در Ask می‌پرسد، **Then** پاسخ مستقیم همراه Citation سطح Claim نمایش داده می‌شود.
2. **Given** سؤال شامل متن فارسی و Error انگلیسی، **When** کاربر آن را ارسال می‌کند، **Then** Error دقیق در Retrieval حفظ و منابع مرتبط پیدا می‌شوند.
3. **Given** شواهد ناکافی، **When** Core Claim اعتبارسنجی نمی‌شود، **Then** Unknown همراه منابع صرفاً مرتبط و گزینه افزودن جزئیات نمایش داده می‌شود.
4. **Given** Supporting Claim نامعتبر، **When** Core Claim معتبر است، **Then** فقط Claim فرعی حذف و پاسخ اصلی حفظ می‌شود.

---

### User Story 2 — Connect personal Liara resources safely (Priority: P1)

به‌عنوان کاربر می‌خواهم Liara API Token خودم را موقتاً وارد کنم و فقط پروژه‌ها، دامنه‌ها و دیتابیس‌های متعلق به همان حساب را برای بررسی انتخاب کنم تا Agent بتواند پاسخ را با وضعیت واقعی من تطبیق دهد.

**Why this priority**: این قابلیت محصول را از RAG متنی به Agent متصل به State واقعی تبدیل می‌کند.

**Independent Test**: با یک Token آزمایشی، Inventory حساب نمایش داده شود، یک Resource Ref موقت ساخته شود و پس از Disconnect یا Expiry دیگر قابل‌استفاده نباشد.

**Acceptance Scenarios**:

1. **Given** Token معتبر، **When** کاربر Connect می‌کند، **Then** Inventory پاک‌سازی‌شده منابع همان حساب نمایش داده می‌شود.
2. **Given** Token نامعتبر، **When** اتصال انجام می‌شود، **Then** پیام امن و قابل‌فهم نمایش داده شده و Token ذخیره نمی‌شود.
3. **Given** Session منقضی یا Disconnect‌شده، **When** Resource Ref قبلی استفاده می‌شود، **Then** درخواست رد و اتصال مجدد خواسته می‌شود.
4. **Given** API Response شامل Field ناشناخته یا حساس، **When** Sanitizer اجرا می‌شود، **Then** Field وارد State داخلی، Context مدل، Telemetry یا UI نمی‌شود.

---

### User Story 3 — Diagnose using docs plus real project state (Priority: P1)

به‌عنوان کاربری که با خطای Production یا Deployment روبه‌رو شده‌ام می‌خواهم Agent شواهد مستندات را با وضعیت Read-only پروژه، دامنه یا دیتابیس خودم ترکیب کند و یک Check امن بعدی پیشنهاد دهد.

**Why this priority**: بیشترین ارزش Agentic، پتانسیل کاهش Support و اثر Demo را ایجاد می‌کند.

**Independent Test**: یک Diagnose Golden Scenario با Snapshot مصنوعی باید Tool صحیح را انتخاب، فرضیه‌های مستند را رتبه‌بندی و بعد از Refresh صریح نتیجه را ارزیابی کند.

**Acceptance Scenarios**:

1. **Given** Resource متصل و سؤال در Scope، **When** Diagnose اجرا می‌شود، **Then** Tool Request ساختاریافته از Policy عبور و فقط GET مجاز اجرا می‌شود.
2. **Given** مسئله هم‌زمان Deployment و Database است، **When** Intent تشخیص داده می‌شود، **Then** هر دو Task Family فعال می‌شوند.
3. **Given** Tool توسط Policy رد یا API ناموجود است، **When** Agent ادامه می‌دهد، **Then** به Docs-only تنزل کرده و محدودیت را شفاف اعلام می‌کند.
4. **Given** کاربر اقدام پیشنهادی را انجام داده، **When** «بررسی مجدد» را انتخاب می‌کند، **Then** Snapshot جدید فقط در همان لحظه دریافت و با Snapshot قبلی مقایسه می‌شود.

---

### User Story 4 — Complete a supported goal step by step (Priority: P2)

به‌عنوان کاربر می‌خواهم برای هدفی در Deployment، Domain/DNS/SSL یا Database یک Plan مرحله‌ای بگیرم، هر بار فقط اقدام فعلی را انجام دهم و سپس ادامه یا Recovery دریافت کنم.

**Why this priority**: Time-to-resolution را برای Taskهای چندصفحه‌ای کاهش می‌دهد و Goal Completion را نمایش می‌دهد.

**Independent Test**: یک Guide Scenario باید Clarification ضروری، Plan، Current Step، Evidence و Validation در Turn بعد را بدون عبور از Call Budget انجام دهد.

**Acceptance Scenarios**:

1. **Given** Context ناقص، **When** Guide شروع می‌شود، **Then** فقط سؤال‌های Decision-critical پرسیده می‌شوند.
2. **Given** Context کافی، **When** Plan ساخته می‌شود، **Then** فقط Current Step همراه Evidence نمایش داده می‌شود.
3. **Given** بخشی از Goal خارج Scope است، **When** Route تعیین می‌شود، **Then** بخش پشتیبانی‌شده Guide و بخش دیگر Ask می‌شود.
4. **Given** سقف دو Generation در Turn مصرف شده، **When** اطلاعات هنوز کافی نیست، **Then** سیستم Clarification یا ادامه در Turn بعد را انتخاب می‌کند.

---

### User Story 5 — Honest scope degradation and support handoff (Priority: P2)

به‌عنوان کاربر می‌خواهم وقتی Workflow کامل یا پاسخ قطعی در دسترس نیست، محصول دقیقاً محدودیت خود را توضیح دهد و راه ادامه یا Handoff قابل‌استفاده بدهد.

**Why this priority**: False confidence را کم می‌کند و تجربه Unknown را به خروجی مفید تبدیل می‌کند.

**Independent Test**: درخواست Billing Guide و یک سؤال Unanswerable باید بدون اجرای Loop یا ادعای قطعی، Ask/Unknown مناسب و Summary قابل Copy تولید کنند.

**Acceptance Scenarios**:

1. **Given** درخواست Guide خارج از Capability Matrix، **When** Route اجرا می‌شود، **Then** پیام Degrade و پاسخ Ask مستند نمایش داده می‌شود.
2. **Given** پاسخ قطعی موجود نیست، **When** Unknown نمایش داده می‌شود، **Then** منابع نزدیک با برچسب غیرقطعی، افزودن جزئیات و Handoff ارائه می‌شوند.
3. **Given** کاربر Handoff را انتخاب می‌کند، **When** Summary ساخته می‌شود، **Then** Goal، Task Family، مراحل امتحان‌شده و منابع بدون Secret قابل Copy هستند.

---

### User Story 6 — Provide structured outcome feedback (Priority: P3)

به‌عنوان کاربر می‌خواهم اعلام کنم پاسخ مشکل را حل کرد یا نه تا معیار Containment قابل‌اندازه‌گیری باشد، بدون اینکه مجبور به ارسال متن یا داده حساس باشم.

**Why this priority**: برای Evaluation محصول ضروری است اما مانع ارزش اصلی Ask/Diagnose نیست.

**Independent Test**: کاربر باید بتواند resolved/not-resolved و یک Reason محدود را ثبت کند و هیچ Field متن آزاد پذیرفته نشود.

**Acceptance Scenarios**:

1. **Given** پاسخ نهایی، **When** کاربر نتیجه را انتخاب می‌کند، **Then** Feedback ساختاریافته به Request و Session ناشناس متصل می‌شود.
2. **Given** Payload دارای Field متن آزاد، **When** Endpoint آن را دریافت می‌کند، **Then** Schema درخواست را رد می‌کند.

### Edge Cases

- سؤال فقط شامل Error Code یا یک خط Log است.
- سؤال فارسی شامل URL، Command، Variable و Code Block انگلیسی است.
- دو Task Family هم‌زمان امتیاز بالا دارند.
- Mode confidence پایین‌تر از Threshold است.
- Sourceهای معتبر درباره موضوع متفاوت یا ناسازگارند.
- Anchor یک Source در Snapshot Build شکسته است.
- AvalAI قبل یا حین تولید پاسخ Timeout می‌شود.
- Liara API پاسخ 401، 404، 429 یا 5xx می‌دهد.
- مدل Tool یا Resource خارج از Policy درخواست می‌کند.
- API Field جدیدی با نام نامعلوم و مقدار شبیه Secret اضافه می‌کند.
- Session هنگام Stream یا Deploy منقضی می‌شود.
- Browser همان Turn را پس از قطع ارتباط Retry می‌کند.
- دو Turn هم‌زمان از یک Session فرستاده می‌شوند.
- Retention Job مدتی اجرا نشده است.
- کاربر از Resource Ref مربوط به Session دیگری استفاده می‌کند.
- سؤال خارج Scope است ولی Ask می‌تواند بخشی از آن را مستند پاسخ دهد.
- Core Claim نامعتبر اما چند Supporting Claim معتبر است.

## Requirements

### Functional Requirements

- **FR-001**: سیستم MUST سه Mode به نام Ask، Guide و Diagnose ارائه دهد.
- **FR-002**: Ask MUST روی تمام منابع رسمی موجود در Knowledge Snapshot قابل‌جست‌وجو باشد.
- **FR-003**: Guide و Diagnose MUST فقط Deployment، Domain/DNS/SSL و Database را به‌صورت Workflow کامل پوشش دهند.
- **FR-004**: Router MUST چند Task Family را هم‌زمان فعال کند.
- **FR-005**: Router MUST در Confidence پایین به‌جای حدس، یک Clarification کوتاه بخواهد.
- **FR-006**: Guide/Diagnose خارج Scope MUST با پیام شفاف به Ask تنزل کند.
- **FR-007**: Ask MUST از مسیر سبک بدون Planning و Project Tool Loop استفاده کند.
- **FR-008**: کاربر MUST بتواند Token شخصی Liara را برای Session موقت متصل کند.
- **FR-009**: سیستم MUST فقط Inventory متعلق به Token متصل‌شده را نمایش دهد.
- **FR-010**: Frontend MUST برای منابع شناسه موقت و بی‌معنا دریافت کند، نه شناسه قابل‌استفاده مستقیم برای Tool.
- **FR-011**: Inspector MUST وضعیت Read-only مرتبط با PaaS، Domain/DNS و Database را پشتیبانی کند.
- **FR-012**: Refresh وضعیت پروژه MUST فقط با اقدام صریح کاربر انجام شود.
- **FR-013**: مدل MUST فقط Tool Request ساختاریافته تولید کند و اجرای Tool MUST توسط Policy مستقل انجام شود.
- **FR-014**: Tool rejected/timeout MUST به Docs-only fallback منجر شود.
- **FR-015**: Retrieval MUST جست‌وجوی دقیق Error/Identifier و جست‌وجوی معنایی فارسی/انگلیسی را ترکیب کند.
- **FR-016**: هر Claim قابل‌بررسی MUST حداقل یک Citation معتبر داشته باشد.
- **FR-017**: Citation MUST عنوان، Heading، Evidence Preview، Deep Link و امکان Copy کردن لینک/Excerpt داشته باشد.
- **FR-018**: Core Claim نامعتبر MUST کل پاسخ را Unknown کند.
- **FR-019**: Supporting Claim نامعتبر MUST بدون حذف Core Answer کنار گذاشته شود.
- **FR-020**: Unknown MUST پیام شفاف، منابع صرفاً مرتبط، افزودن جزئیات و Handoff ارائه دهد.
- **FR-021**: Handoff MUST Summary قابل Copy و فاقد Secret تولید کند.
- **FR-022**: سیستم MUST پاسخ را به‌صورت Status Event و Final/Unknown Result Stream کند.
- **FR-023**: Turn submission MUST idempotent باشد.
- **FR-024**: کاربر MUST بتواند اتصال Liara را بدون از دست‌دادن Ask ناشناس قطع کند و همچنین کل Session را جداگانه خاتمه دهد؛ هر دو عملیات MUST Token را حذف کنند.
- **FR-025**: Feedback MUST فقط شامل `resolved`، Reason محدود و `handoff_requested` و بدون متن آزاد باشد؛ `resolved=true` و `handoff_requested=true` هم‌زمان نامعتبر است.
- **FR-026**: محصول MUST UI فارسی‌اول، RTL و Responsive داشته باشد.
- **FR-027**: Code، Error، URL و Identifier MUST در جهت LTR و قابل Copy نمایش داده شوند.
- **FR-028**: سیستم MUST تعارض شناخته‌شده میان منابع یا نسخه‌ها را به‌جای ادغام قطعی، شفاف نمایش دهد و Core Answer را به Conflict/Unknown تبدیل کند.
- **FR-029**: Evidence Sufficiency MUST با یک Rule و Threshold نسخه‌دار و قابل‌آزمون تعیین شود.
- **FR-030**: سیستم MUST پیش از دریافت Liara Token یک Session ناشناس بسازد تا Ask بدون اتصال پروژه کار کند؛ Connect MUST همان Session را ارتقا دهد و شکست Token نباید Ask ناشناس را حذف کند.

### Agent Requirements

- **AR-001**: Ask MUST حداکثر یک Generation Call در هر Turn استفاده کند.
- **AR-002**: Guide و Diagnose MUST حداکثر دو Generation Call در هر Turn استفاده کنند.
- **AR-003**: Agent MUST پس از رسیدن به Call Budget، Clarification، Unknown یا Turn بعد را انتخاب کند.
- **AR-004**: Intent confidence MUST از مکانیزم قابل‌تست و غیرخوداظهاری مدل به‌دست آید.
- **AR-005**: Agent MUST در نبود Evidence کافی از پاسخ قطعی خودداری کند.
- **AR-006**: Diagnose MUST فرضیه‌ها را همراه شواهد و یک Check امن بعدی ارائه کند.
- **AR-007**: Agent MUST نتیجه Refresh را با Sanitized Snapshot قبلی مقایسه کند.

### Security and Privacy Requirements

- **SR-001**: تمام Liara Toolها MUST به GET، Host و Path Templateهای Allowlist‌شده محدود باشند.
- **SR-002**: Field Sanitization MUST allowlist-first و fail-closed باشد.
- **SR-003**: Unknown API Fields MUST خودکار حذف شوند.
- **SR-004**: Liara Token MUST فقط در Backend Memory و محدوده Session نگهداری شود.
- **SR-005**: Token MUST از Log، Database، Browser persistence و Model Context حذف باشد.
- **SR-006**: Session MUST پس از ۳۰ دقیقه عدم فعالیت یا دو ساعت عمر مطلق منقضی شود.
- **SR-007**: Application Responseهای حساس MUST مانع Cache شدن شوند.
- **SR-008**: Anonymous Session creation MUST حداکثر ۲۰ درخواست در ۱۰ دقیقه، Connect MUST حداکثر ۱۰ درخواست کل و ۵ تلاش ناموفق در ۱۰ دقیقه، Turn MUST حداکثر ۲۰ درخواست در ۱۰ دقیقه و Tool MUST حداکثر ۱۰ فراخوانی در ۱۰ دقیقه داشته باشد.
- **SR-009**: Rate-limit IP key MUST موقت و غیرقابل Persistence باشد.
- **SR-010**: Telemetry MUST فقط Schema مثبت مصوب را ذخیره کند.
- **SR-011**: محتوای سؤال/پاسخ، IP، Resource identity، Token، Log و Snapshot MUST Persist نشوند.
- **SR-012**: Telemetry MUST حداکثر ۳۰ روز نگهداری شود.
- **SR-013**: Corpus MUST فقط منابع رسمی Allowlist‌شده و Merge‌شده را شامل شود.
- **SR-014**: GitHub Issues، PRها، Comments، Discussions و Forkها MUST Index نشوند.
- **SR-015**: Knowledge Snapshot rebuild MUST هیچ Runtime HTTP Endpointی نداشته باشد.
- **SR-016**: Policy MUST محدودیت احتمالی Access Log زیرساخت میزبان را مستند کند.

### Reliability and Performance Requirements

- **NFR-001**: Ask SHOULD در صدک ۹۵ حداکثر ۸ ثانیه پاسخ دهد.
- **NFR-002**: Guide current-step SHOULD در صدک ۹۵ حداکثر ۱۲ ثانیه پاسخ دهد.
- **NFR-003**: Diagnose دارای Tool SHOULD در صدک ۹۵ حداکثر ۱۵ ثانیه پاسخ دهد.
- **NFR-004**: Retrieval CPU-bound MUST خارج از Async Event Loop اجرا شود.
- **NFR-005**: External Provider outage MUST باعث Restart Loop سرویس نشود.
- **NFR-006**: Session loss پس از Restart MUST با درخواست اتصال مجدد مدیریت شود.
- **NFR-007**: Knowledge Snapshot MUST reproducible، hash-verified و version-visible باشد.
- **NFR-008**: Broken Source Anchor MUST پیش از انتشار Snapshot کشف شود.
- **NFR-009**: UI MUST با Keyboard قابل‌استفاده و Focus State قابل‌مشاهده داشته باشد.
- **NFR-010**: تمام Errorها MUST Code محدود، پیام امن و Request ID داشته باشند.

### Evaluation Requirements

- **ER-001**: سیستم MUST یک Golden Set نسخه‌دار شامل Ask، Guide، Diagnose، Unknown و Conflict cases داشته باشد.
- **ER-002**: Evaluation MUST مدل، Prompt، Snapshot و Threshold version را ثبت کند.
- **ER-003**: Citation Accuracy MUST با قضاوت Golden Set سنجیده شود، نه صرفاً Gate pass.
- **ER-004**: Time-to-resolution MUST با BM25 search baseline روی Taskهای یکسان مقایسه شود.
- **ER-005**: Confirmed Containment MUST برابر Sessionهای واجد شرایط با `resolved=true` و بدون Handoff تقسیم بر Sessionهای واجد شرایط دارای Outcome صریح باشد؛ Feedback Coverage و Conservative Lower Bound روی تمام Sessionهای واجد شرایط نیز MUST جدا گزارش شوند.
- **ER-006**: Evaluation MUST Route accuracy، Tool selection، Unknown handling، latency و cost را گزارش کند.

### Key Entities

- **Anonymous Session**: Session موقت شامل شناسه تصادفی، Expiry، Resource Refها، Agent State و حداکثر دو Sanitized Snapshot.
- **Resource Reference**: شناسه بی‌معنای Session-scoped که به یک Resource مجاز در Inventory حافظه نگاشت می‌شود.
- **Agent Turn**: ورودی کاربر، Route، Budget، Status، Result و Feedback reference؛ متن آن Persist نمی‌شود.
- **Knowledge Snapshot**: مجموعه تغییرناپذیر Chunk، Index و Manifest نسخه‌دار.
- **Knowledge Chunk**: متن پاک‌سازی‌شده رسمی همراه Source identity، Heading، Anchor، hash و trust metadata.
- **Claim**: واحد پاسخ با نقش Core یا Supporting و Citationهای خود.
- **Citation**: اتصال Claim به Chunk و Evidence Span دقیق.
- **Sanitized Project State**: DTO allowlist‌شده از Liara API بدون Field حساس.
- **Tool Request**: درخواست Typed و Untrusted مدل که Policy آن را بررسی می‌کند.
- **Turn Telemetry**: رکورد بدون محتوا برای Route، `containment_eligible`، outcome، latency، cost و evaluation aggregates.
- **Evaluation Run**: نتیجه نسخه‌دار اجرای Golden Set یا Baseline.

## Success Criteria

### Measurable Outcomes

- **SC-001**: حداقل ۹۵٪ Citation Accuracy روی Golden Set دستی.
- **SC-002**: حداقل ۹۰٪ Citation Coverage برای Claimهای قابل‌بررسی.
- **SC-003**: حداقل ۹۰٪ Correct Unknown Handling و حداکثر ۵٪ False-answer Rate.
- **SC-004**: حداقل ۶۰٪ Containment در Sessionهای واجد شرایط سه Task Family.
- **SC-005**: حداقل ۷۰٪ Task Completion برای Guide/Diagnoseهای Golden Set.
- **SC-006**: حداقل ۹۰٪ Tool Selection Accuracy.
- **SC-007**: حداقل ۳۵٪ کاهش Median Time-to-resolution نسبت به BM25 Search baseline.
- **SC-008**: Ask در `p95 <= 8s`، Guide در `p95 <= 12s` و Diagnose در `p95 <= 15s` در محیط Demo.
- **SC-009**: هیچ Field حساس یا Unknown از Contract Testهای Liara API وارد Agent Context نشود.
- **SC-010**: هیچ Endpoint نوشتنی Liara در Security Tests قابل فراخوانی نباشد.
- **SC-011**: یک جریان واقعی Browser → Backend → AvalAI → Citation Result روی Liara Deploy موفق باشد.
- **SC-012**: یک جریان واقعی Connect → Resource Select → Read-only Inspect → Diagnose روی Liara Deploy موفق باشد.
- **SC-013**: تمام Citation Linkهای Snapshot منتشرشده Anchor معتبر داشته باشند.
- **SC-014**: RTL، Responsive behavior، Keyboard navigation و Evidence display مطابق Design System بازبینی شوند.

## Assumptions

- کاربر یک Liara API Token معتبر در اختیار دارد و مسئول ابطال آن است.
- Liara API ممکن است Token صرفاً Read-only ارائه نکند؛ Read-only بودن در MVP توسط Application Policy تضمین می‌شود.
- AvalAI Key مرکزی محصول هزینه درخواست‌های MVP را پوشش می‌دهد.
- اتصال اینترنت کاربر و دسترسی Backend به AvalAI و Liara API برقرار است.
- Knowledge Snapshot برای Demo پیش از Build ساخته و در Repository قرار می‌گیرد.
- یک Instance و یک Worker برای بار مسابقه کافی است.
- Platform Access Logs ممکن است خارج از کنترل Application وجود داشته باشند.
- Thresholdهای اولیه Citation با Golden Set پیش از Demo کالیبره می‌شوند.

## Dependencies

- دسترسی به AvalAI Chat/Responses و Embeddings API.
- دسترسی به Liara PaaS، Domain/DNS و DBaaS read endpoints.
- منابع رسمی Liara و Default Branch مخازن رسمی.
- PostgreSQL مدیریت‌شده برای Telemetry محدود.
- Design System پروژه در `docs/design-system/liara-intelligence-design-system.md`.

## Out of Scope

- هرگونه Write Action روی Liara یا GitHub.
- Deploy، Restart، Scale، تغییر Env، DNS یا Database.
- User account، persistent chat history و cross-session memory.
- Free-text feedback persistence.
- Runtime crawling/index rebuilding.
- GitHub user repository inspection.
- Index کردن محتوای User-generated.
- Multi-agent architecture، Microservices، Redis و dedicated vector database.
- Automatic support-ticket creation.
- Guide/Diagnose کامل خارج از سه Task Family مصوب.
