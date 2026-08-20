# Liara Intelligence Design System (LIDS)

نسخه: 1.0 — Discovery baseline  
تاریخ: ۲۰ اوت ۲۰۲۶  
وضعیت: Canonical design specification for MVP  
زبان و جهت پایه: فارسی، راست‌به‌چپ  
دامنه: محصول مبتنی بر LLM برای استفاده هدف‌محور از مستندات Liara

---

## 0. راهنمای استفاده کم‌هزینه در Implementation

این فایل مرجع کامل است، اما برای هر Task لازم نیست تمام آن وارد Context شود. مسیر خواندن زیر الزامی است:

| Task | بخش‌هایی که باید خوانده شوند |
|---|---|
| تنظیم Theme و CSS foundation | 5، 6، 7، 11، 22 |
| ساخت App shell و Responsive layout | 8، 9، 15، 17 |
| ساخت Primitive component | 5 تا 7، Component مربوط در 12، سپس 17 و 18 |
| ساخت Chat/LLM interaction | 13.1 تا 13.4، 14، 16، 20 |
| ساخت Goal workflow | 4، 13.5، 13.6، 13.13، 13.14، 14 |
| ساخت Source/Evidence UI | 13.7 تا 13.9، 18، 20 |
| ساخت Troubleshooting | 13.10 تا 13.15، 16، 19 |
| ساخت Mobile UI | 8.4، 8.5، 12.11، 17، 18 |
| Accessibility review | 17، 18 و Checklist بخش 28 |
| Security review | 13.12، 13.15، 19 و Checklist بخش 28 |
| تحویل نهایی MVP | 25، 27، 28، 29 |

### Snapshot تصمیم‌های تثبیت‌شده

```text
Direction: Technical Intelligence Workspace
Default theme: Dark
Base background: #181818
Brand gradient: #87FCC4 → #28C1F5 at 92deg
Font: Yekan Bakh
Body typography: 15px / 28px
Code typography: 13px / 22px monospace
Spacing base: 4px
Control radius: 8px
Card radius: 12px
Dialog radius: 16px
Desktop layout: 248px nav + 560–840px main + 320px evidence
Tablet: 72px nav rail + evidence drawer
Mobile: single column + navigation drawer + evidence bottom sheet
Accessibility target: WCAG 2.2 AA
Primary interaction: Goal → Clarify → Plan → Validate → Recover/Complete
Visual signature: Liara Signal
Confidence display: qualitative answerability labels; never arbitrary percentages
Source behavior: claim-level citation + Evidence Rail
Security behavior: secret detection and redaction before send/export
```

### قانون تغییر

مقادیر Snapshot و Tokenهای بخش ۵ تا ۷ قفل‌شده‌اند. اگر در Implementation نیاز به تغییر وجود داشت، ابتدا همین سند Version شود؛ مقدار جدید نباید فقط در Code اضافه شود. هر Component جدید نیز باید State، Responsive behavior، RTL behavior، Accessibility و Error behavior صریح داشته باشد.

---

## 1. هدف سند

این سند مرجع نهایی طراحی بصری و رفتاری MVP است. در مرحله Implementation، هر تصمیم مربوط به رنگ، تایپوگرافی، فاصله، Layout، Responsive behavior، State، Accessibility یا رفتار کامپوننت‌ها باید از این سند گرفته شود.

این سند عمداً مستقل از React، Vue، CSS framework و Component library نوشته شده است. انتخاب ابزار پیاده‌سازی نباید قراردادهای این سند را تغییر دهد.

### اهداف

- حفظ هویت بصری Liara بدون کپی سطحی Marketing website.
- ایجاد تجربه‌ای حرفه‌ای و قابل اعتماد برای پاسخ فنی، Code و Troubleshooting.
- آشکار کردن رفتار Agentic در UI، نه فقط در متن پاسخ.
- بیشینه‌کردن امتیاز UI/UX، Quality، Agentic و Security در Challenge.
- حذف تصمیم‌های تکراری در مرحله Implementation.
- پشتیبانی کامل از فارسی، RTL، Codeهای LTR و محتوای ترکیبی.

### خارج از دامنه

- انتخاب React یا Vue.
- انتخاب State management یا CSS framework.
- طراحی معماری Backend و LLM.
- انتخاب مدل یا Retrieval stack.
- تعریف Logo جدید برای Liara.
- اجرای Action روی منابع کاربر.

---

## 2. منابع Audit و منشأ تصمیم‌ها

Design System از این منابع رسمی استخراج شده است:

1. وب‌سایت اصلی Liara: <https://liara.ir/>
2. مستندات Liara: <https://docs.liara.ir/>
3. صفحه محصول AI: <https://liara.ir/products/ai/>
4. مخزن رسمی Docs: <https://github.com/liara-cloud/docs>

### یافته‌های قطعی Audit

- فونت اصلی رابط فارسی `Yekan Bakh` است.
- رنگ پایه صفحات Marketing و AI، خاکستری بسیار تیره نزدیک `#181818` است.
- Accent اصلی از گرادیان Mint به Cyan تشکیل شده است:
  - Mint: `#87FCC4`
  - Cyan: `#28C1F5`
- Marketing website از Glow، radial gradient، خطوط شبکه‌ای و سطوح شفاف استفاده می‌کند.
- Docs از UI آرام‌تر، Borderهای کم‌رنگ، Radius حدود ۸ پیکسل و ساختار محتوامحور استفاده می‌کند.
- Docs دارای Light/Dark mode و Semantic alertهای Info، Success، Warning و Error است.
- Docs برای متن اصلی از اندازه ۱۵ پیکسل و line-height نزدیک ۳۰ پیکسل استفاده می‌کند.
- Heading scale مشاهده‌شده در Docs شامل ۳۲، ۲۴، ۲۰، ۱۶، ۱۴ و ۱۲ پیکسل است.
- Breakpointهای پرتکرار در سایت‌ها شامل ۴۲۵، ۷۶۸، ۸۲۰، ۱۰۰۰، ۱۱۰۰ و ۱۴۴۰ پیکسل هستند.

### محدودیت Audit

Browser تعاملی محیط در زمان Audit در دسترس نبود. مقادیر این سند با بررسی HTML، CSS، Source code رسمی Docs و ساختار محتوای صفحات استخراج شده‌اند. در نتیجه، مقادیر Tokenها دقیق‌اند؛ اما Animation timingهایی که در Source صریح نبوده‌اند به‌صورت تصمیم محصولی در این سند تثبیت شده‌اند.

---

## 3. نام و شخصیت سیستم

نام سیستم:

> Liara Intelligence Design System — LIDS

شخصیت محصول باید این ویژگی‌ها را منتقل کند:

- فنی، نه خشک
- هوشمند، نه جادویی
- مطمئن، نه مطلق‌گو
- مدرن، نه نمایشی و شلوغ
- صمیمی، نه غیررسمی
- شفاف، نه Black box
- سریع، نه عجول

### اصول طراحی

#### 3.1 Evidence first

منبع، شواهد و وضعیت اعتبار پاسخ بخشی از خود پاسخ‌اند. Citation نباید فقط در انتهای Conversation مخفی شود.

#### 3.2 Goal over chat

UI باید Goal، Plan، Current step و Result را نمایش دهد. Conversation صرفاً کانال ورود و تعامل است.

#### 3.3 Calm agentic

Agentic behavior با State، Progress و Evidence دیده می‌شود؛ نه با انیمیشن‌های مداوم و عبارت‌های مبهم مانند «در حال فکر عمیق».

#### 3.4 Persian first

Layout از ابتدا RTL طراحی می‌شود. Code، URL، CLI command، Log و Identifier همیشه LTR باقی می‌مانند.

#### 3.5 Progressive disclosure

پاسخ اصلی و Next action در سطح اول نمایش داده می‌شوند. Evidence، reasoning summary، metadata و جزئیات تشخیصی در Disclosureهای سطح دوم قرار می‌گیرند.

#### 3.6 Brand restraint

گرادیان برند فقط برای CTA اصلی، Active agent state، Focus و نقاط کلیدی استفاده می‌شود. استفاده سراسری از Glow ممنوع است.

---

## 4. امضای بصری: Liara Signal

`Liara Signal` یک خط یا مسیر باریک با گرادیان Mint به Cyan است که Stateهای یک Task را به هم متصل می‌کند:

```text
Goal → Clarification → Plan → Active step → Validation → Result
```

### حالات Signal

| State | Appearance | Motion |
|---|---|---|
| Idle | Border خنثی | بدون حرکت |
| Retrieving | گرادیان ۴۰٪ opacity | حرکت خطی آرام |
| Planning | گرادیان کامل | Pulse یک‌باره |
| Waiting for user | Mint ثابت | بدون حرکت؛ نشان سؤال |
| Active step | نقطه نورانی کوچک | حرکت بسیار محدود |
| Validating | Cyan ثابت | Sweep کوتاه |
| Success | Success green | Fade-in |
| Partial | Warning + gradient branch | بدون Loop |
| Failed | Danger red | بدون لرزش |
| Handoff | خط خنثی به Support card | Fade |

### قوانین

- ضخامت پایه: `2px`.
- در Mobile: ضخامت `2px` و بدون Glow خارجی.
- Glow حداکثر `8px` blur و opacity حداکثر ۲۰٪.
- Animation loop فقط در State فعال مجاز است.
- در `prefers-reduced-motion` تمام حرکت‌ها با تغییر رنگ ثابت جایگزین شوند.
- Signal نباید تنها راه تشخیص State باشد؛ Label و Icon نیز الزامی است.

---

## 5. Color System

### 5.1 Brand palette

| Token | Value | کاربرد |
|---|---|---|
| `brand-mint` | `#87FCC4` | نقطه شروع گرادیان و highlight روی Dark |
| `brand-cyan` | `#28C1F5` | نقطه پایان گرادیان و interactive accent |
| `brand-mint-strong` | `#4DD6A0` | Success-like brand accent |
| `brand-mint-text-light` | `#087A65` | متن Accent روی Light background |
| `brand-cyan-text-light` | `#087EAA` | Link/Accent روی Light background |
| `brand-gradient` | `linear-gradient(92deg, #87FCC4 0%, #28C1F5 98.77%)` | CTA و Signal |
| `brand-gradient-soft` | `linear-gradient(92deg, #87FCC414 0%, #28C1F514 98.77%)` | Highlight surface |

### 5.2 Dark theme — حالت پیش‌فرض Demo

| Token | Value |
|---|---|
| `bg-canvas` | `#181818` |
| `bg-subtle` | `#1B1C1D` |
| `surface-1` | `#1E1F21` |
| `surface-2` | `#242628` |
| `surface-3` | `#2B2D2F` |
| `surface-inverse` | `#F7F8F8` |
| `text-primary` | `#F4F6F5` |
| `text-secondary` | `#A0ACB7` |
| `text-muted` | `#747C78` |
| `text-disabled` | `#59605D` |
| `border-subtle` | `#FFFFFF0D` |
| `border-default` | `#FFFFFF14` |
| `border-strong` | `#FFFFFF24` |
| `overlay` | `#00000099` |
| `focus-ring` | `#87FCC4` |
| `code-bg` | `#151617` |
| `code-border` | `#FFFFFF12` |

### 5.3 Light theme

| Token | Value |
|---|---|
| `bg-canvas` | `#F7F8F8` |
| `bg-subtle` | `#F1F3F2` |
| `surface-1` | `#FFFFFF` |
| `surface-2` | `#F5F6F5` |
| `surface-3` | `#E8EBE9` |
| `surface-inverse` | `#181818` |
| `text-primary` | `#181818` |
| `text-secondary` | `#65706B` |
| `text-muted` | `#89918D` |
| `text-disabled` | `#ADB3B0` |
| `border-subtle` | `#0000000A` |
| `border-default` | `#00000014` |
| `border-strong` | `#00000024` |
| `overlay` | `#00000070` |
| `focus-ring` | `#087A65` |
| `code-bg` | `#F4F5F4` |
| `code-border` | `#00000012` |

### 5.4 Semantic colors

| Role | Solid | Soft background | Dark text/icon | Light text/icon |
|---|---|---|---|---|
| Info | `#2563EB` | `#3B82F622` | `#93C5FD` | `#1D4ED8` |
| Success | `#16A34A` | `#16A34A22` | `#86EFAC` | `#15803D` |
| Warning | `#FF9800` | `#FF980022` | `#FCD34D` | `#B45309` |
| Danger | `#DC2626` | `#DC262622` | `#FCA5A5` | `#B91C1C` |
| Unknown | `#7C6FE8` | `#7C6FE81F` | `#C4B5FD` | `#5B4CC4` |

### 5.5 Color usage rules

- `brand-mint` روی White برای متن Body استفاده نشود.
- متن معمولی باید حداقل contrast برابر `4.5:1` داشته باشد.
- متن بزرگ حداقل `3:1`.
- Focus indicator حداقل `3:1` نسبت به سطح مجاور.
- Danger، Warning و Success همیشه Icon و Label متنی داشته باشند.
- Brand gradient برای متن Body ممنوع است.
- Gradient text فقط در Empty-state title، Product badge یا Demo headline مجاز است.
- Surfaceها با Border تفکیک شوند؛ Shadow نقش فرعی دارد.

### 5.6 Canonical CSS variable contract

نام‌های زیر قرارداد اجباری Implementation هستند، حتی اگر ابزار نهایی CSS-in-JS باشد:

```css
:root {
  --lids-brand-mint: #87fcc4;
  --lids-brand-cyan: #28c1f5;
  --lids-brand-gradient: linear-gradient(92deg, #87fcc4 0%, #28c1f5 98.77%);

  --lids-bg-canvas: #f7f8f8;
  --lids-bg-subtle: #f1f3f2;
  --lids-surface-1: #ffffff;
  --lids-surface-2: #f5f6f5;
  --lids-surface-3: #e8ebe9;
  --lids-text-primary: #181818;
  --lids-text-secondary: #65706b;
  --lids-text-muted: #89918d;
  --lids-border-subtle: #0000000a;
  --lids-border-default: #00000014;
  --lids-border-strong: #00000024;
  --lids-focus-ring: #087a65;
}

[data-theme="dark"] {
  --lids-bg-canvas: #181818;
  --lids-bg-subtle: #1b1c1d;
  --lids-surface-1: #1e1f21;
  --lids-surface-2: #242628;
  --lids-surface-3: #2b2d2f;
  --lids-text-primary: #f4f6f5;
  --lids-text-secondary: #a0acb7;
  --lids-text-muted: #747c78;
  --lids-border-subtle: #ffffff0d;
  --lids-border-default: #ffffff14;
  --lids-border-strong: #ffffff24;
  --lids-focus-ring: #87fcc4;
}
```

---

## 6. Typography

### 6.1 Font families

| Role | Font stack |
|---|---|
| Persian UI | `"Yekan Bakh", system-ui, sans-serif` |
| Latin UI | `"Yekan Bakh", Inter, system-ui, sans-serif` |
| Code/CLI/Log | `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace` |

فونت Yekan Bakh باید با `font-display: swap` و وزن‌های محدود ۴۰۰، ۵۰۰/۶۰۰، ۷۰۰ و ۸۰۰ بارگذاری شود. اگر فایل وزن ۵۰۰ موجود نبود، وزن ۶۰۰ جایگزین شود.

### 6.2 Type scale

| Token | Size | Line height | Weight | کاربرد |
|---|---:|---:|---:|---|
| `display` | 40 | 56 | 800 | Empty state و Hero محدود |
| `heading-1` | 32 | 44 | 700 | عنوان صفحه |
| `heading-2` | 24 | 36 | 700 | بخش اصلی |
| `heading-3` | 20 | 32 | 600 | Subsection |
| `heading-4` | 18 | 28 | 600 | Card title |
| `body-lg` | 16 | 30 | 400 | پاسخ‌های خواندنی |
| `body` | 15 | 28 | 400 | متن پیش‌فرض |
| `ui` | 14 | 22 | 500 | Button، Input، Navigation |
| `metadata` | 12 | 18 | 500 | Time، Source metadata، Label |
| `micro` | 11 | 16 | 600 | Badge محدود |
| `code` | 13 | 22 | 400 | Code و Log |

### 6.3 Typography rules

- طول خط پاسخ در Desktop بین ۶۰ تا ۸۰ کاراکتر لاتین یا عرض `720px` باشد.
- Paragraph فارسی line-height کمتر از `1.75` نداشته باشد.
- Headingها حداکثر سه سطح در یک View استفاده شوند.
- متن Button از ۱۴ پیکسل کوچک‌تر نباشد.
- Bold کامل برای Paragraph ممنوع است.
- اعداد Metric و Token usage با `font-variant-numeric: tabular-nums` نمایش داده شوند.
- URL، command و identifier با `dir="ltr"` و `unicode-bidi: isolate` نمایش داده شوند.

---

## 7. Spacing, Size and Shape

### 7.1 Spacing scale

| Token | Value |
|---|---:|
| `space-0` | 0 |
| `space-1` | 4px |
| `space-2` | 8px |
| `space-3` | 12px |
| `space-4` | 16px |
| `space-5` | 20px |
| `space-6` | 24px |
| `space-8` | 32px |
| `space-10` | 40px |
| `space-12` | 48px |
| `space-16` | 64px |

### 7.2 Radius

| Token | Value | کاربرد |
|---|---:|---|
| `radius-xs` | 4px | Inline code، tiny badge |
| `radius-sm` | 6px | Compact control |
| `radius-md` | 8px | Button، Input، Code block |
| `radius-lg` | 12px | Card، Composer |
| `radius-xl` | 16px | Dialog، large panel |
| `radius-pill` | 999px | Chip، Status badge |

### 7.3 Borders

- Border پیش‌فرض: `1px solid var(--lids-border-default)`.
- Selected card: Border strong + inner brand line، نه افزایش Shadow.
- Divider: Border subtle.
- Focus: `2px` ring با `2px` offset.
- Error input: Danger border + message؛ بدون Shake animation.

### 7.4 Shadows

| Token | Dark | Light |
|---|---|---|
| `shadow-sm` | `0 2px 8px #00000030` | `0 2px 8px #0000000D` |
| `shadow-md` | `0 12px 32px #0000004A` | `0 12px 32px #00000014` |
| `shadow-focus-brand` | `0 0 0 4px #87FCC426` | `0 0 0 4px #087A6520` |

Shadow بزرگ فقط برای Modal، Command palette و Composer شناور مجاز است.

### 7.5 Target sizes

- حداقل Touch target: `44×44px`.
- Compact desktop icon button: حداقل `36×36px`، با hit-area چهل‌وچهار پیکسلی.
- Input استاندارد: ارتفاع `44px`.
- Button استاندارد: ارتفاع `40px`.
- Button بزرگ/CTA: ارتفاع `48px`.

---

## 8. Grid and Responsive Layout

### 8.1 Breakpoints

| Name | Range |
|---|---|
| `mobile` | 0–639px |
| `tablet` | 640–1023px |
| `desktop` | 1024–1439px |
| `wide` | 1440px و بیشتر |

Breakpointهای میانی سایت رسمی به چهار گروه بالا نرمال شده‌اند تا Implementation ساده و قابل پیش‌بینی بماند.

### 8.2 App shell — Desktop

```text
┌──────────────┬──────────────────────────────┬─────────────────┐
│ Navigation   │ Main task / conversation     │ Evidence rail   │
│ 248px        │ min 560px / max 840px        │ 320px           │
└──────────────┴──────────────────────────────┴─────────────────┘
```

- Navigation: `248px` ثابت؛ قابل Collapse به `72px`.
- Main content: `minmax(560px, 840px)`.
- Evidence rail: `320px`؛ در عرض کمتر از ۱۲۸۰ پیکسل به Drawer تبدیل شود.
- Gap ستون‌ها: `16px`.
- App max-width ندارد؛ Main reading column max-width دارد.

### 8.3 Tablet

- Sidebar به Icon rail با عرض `72px` تبدیل شود.
- Evidence rail به Drawer یا Bottom sheet تبدیل شود.
- Main content تمام عرض باقی‌مانده را بگیرد.
- Composer در پایین View ثابت باشد، ولی روی محتوا Overlay نشود.

### 8.4 Mobile

- یک ستون.
- Top app bar: ارتفاع `56px`.
- Navigation: Full-height drawer از سمت راست.
- Evidence: Bottom sheet با Snap pointهای ۴۰٪ و ۹۰٪.
- Plan: Accordion عمودی.
- Composer: Sticky bottom، در حالت بازشدن Keyboard به viewport واکنش دهد.
- Horizontal scrolling فقط داخل Code/Table مجاز است.
- CTAهای هم‌اهمیت عمودی شوند؛ Primary بالاتر از Secondary.

### 8.5 Safe areas

در Mobile از `env(safe-area-inset-*)` برای App bar، Composer و Bottom sheet استفاده شود.

---

## 9. Navigation and Information Architecture UI

### 9.1 Primary navigation

ترتیب پیشنهادی:

1. گفت‌وگوی جدید
2. Taskهای اخیر
3. تاریخچه
4. منابع و مستندات
5. Feedback/گزارش مشکل
6. تنظیمات

### 9.2 Navigation item

- Icon: ۲۰px.
- Label: ۱۴px/۲۲، وزن ۵۰۰.
- ارتفاع: ۴۰px.
- Radius: ۸px.
- Active: `surface-3` + یک خط ۲px گرادیان در سمت راست.
- Hover: `surface-2`.
- Badge count حداکثر دو رقم؛ بیشتر از ۹۹ با `99+`.

### 9.3 Top context bar

شامل موارد زیر است:

- عنوان Goal یا Conversation
- Service chip
- Framework chip
- Environment chip در صورت وجود
- وضعیت Session
- Theme toggle
- Overflow actions

Context chipها قابل ویرایش‌اند، اما ویرایش آن‌ها باید تأثیر روی پاسخ‌های بعدی را به کاربر اعلام کند.

---

## 10. Iconography and Imagery

### 10.1 Icons

- سبک پایه: Outline، ضخامت ۱.۵ تا ۲ پیکسل.
- مجموعه پیشنهادی سبک: GitHub Octicons/Go icons، هم‌راستا با Docs فعلی.
- اندازه‌های مجاز: ۱۶، ۱۸، ۲۰ و ۲۴ پیکسل.
- Filled icon فقط برای Status critical یا Selected navigation.
- Icon بدون Label فقط وقتی Tooltip و معنای شناخته‌شده دارد.
- Iconهای RTL-sensitive مانند Arrow و Send باید Mirror شوند؛ Play، Code و External-link Mirror نشوند.

### 10.2 Illustration

- از Illustration سه‌بعدی عمومی AI، Robot head و Brain icon استفاده نشود.
- تصاویر تزئینی بر اساس Cloud topology، terminal، document nodes و Liara Signal باشند.
- Grid و Glow سایت AI فقط در Empty state و Onboarding قابل استفاده است.
- Decorative imagery نباید پشت متن Body قرار گیرد.

### 10.3 Logo

- Logo رسمی Liara بدون تغییر نسبت، رنگ یا افکت استفاده شود.
- فضای امن پیرامون Logo حداقل برابر ارتفاع نشانه داخلی آن باشد.
- Gradient روی خود Logo اعمال نشود.

---

## 11. Motion System

### 11.1 Durations

| Token | Value | کاربرد |
|---|---:|---|
| `motion-instant` | 80ms | Press feedback |
| `motion-fast` | 160ms | Hover، focus، tooltip |
| `motion-base` | 240ms | Panel، accordion |
| `motion-slow` | 320ms | Task state transition |
| `motion-progress` | 1200ms | Retrieval signal loop |

### 11.2 Easing

- Standard: `cubic-bezier(0.2, 0, 0, 1)`.
- Enter: `cubic-bezier(0, 0, 0.2, 1)`.
- Exit: `cubic-bezier(0.4, 0, 1, 1)`.

### 11.3 Motion rules

- Layout shift ناشی از Streaming ممنوع است؛ فضای پاسخ باید پایدار بماند.
- Streaming cursor حداکثر هر ۶۰۰ms blink کند.
- Skeleton بعد از ۳۰۰ms تأخیر نمایش داده شود تا Flicker ایجاد نشود.
- Spinner برای فرآیندهای نامشخص؛ Progress step برای فرآیندهای چندمرحله‌ای.
- Animation celebratory در محصول فنی استفاده نشود.
- `prefers-reduced-motion` تمام transform و loopها را حذف می‌کند.

---

## 12. Core Primitive Components

### 12.1 Button

Variants:

| Variant | کاربرد | ظاهر |
|---|---|---|
| Primary | یک Action اصلی در هر ناحیه | Brand gradient، متن `#111` |
| Secondary | Action جایگزین | Surface-3 + Border |
| Ghost | Toolbar/navigation | Transparent، Hover surface |
| Link | Navigation درون متن | Cyan/Mint accessible text |
| Danger | Action مخرب | Danger solid/soft |

States الزامی: default، hover، pressed، focus-visible، loading، disabled.

قواعد:

- Button loading عرض خود را حفظ کند.
- Primary button در هر Card حداکثر یکی باشد.
- Disabled state Tooltip دلیل غیرفعال بودن را در صورت نامشخص بودن ارائه دهد.
- Icon در RTL سمت راست Label قرار گیرد، مگر Icon جهت حرکت به جلو.

### 12.2 Icon button

- اندازه استاندارد ۴۰px.
- Tooltip پس از ۵۰۰ms.
- Accessible name الزامی.
- Toggle state با `aria-pressed`.

### 12.3 Input

- Label همیشه خارج از Input باقی بماند؛ Placeholder جای Label نیست.
- Border default، Focus ring برند، Error border semantic.
- Helper text زیر Input.
- Password/secret input دارای Reveal کنترل‌شده و Warning باشد.
- Persian input راست‌چین؛ URL/Token/Code input چپ‌چین.

### 12.4 Textarea

- حداقل ارتفاع ۹۶px.
- Auto-grow تا ۲۴۰px؛ سپس Scroll داخلی.
- Character counter فقط در محدودیت واقعی.
- Resize handle در Mobile مخفی و در Desktop مجاز.

### 12.5 Select/Combobox

- Search برای بیش از ۷ گزینه.
- Selected item دارای Check icon.
- Keyboard navigation کامل.
- گزینه‌های Service دارای Icon رسمی یا generic service icon.

### 12.6 Checkbox/Switch/Radio

- Checkbox برای انتخاب مستقل.
- Radio برای گزینه‌های mutually exclusive.
- Switch فقط برای تغییر فوری Setting؛ نه Submit form.
- Label کل hit-area را فعال کند.

### 12.7 Chip

انواع: Context، Filter، Status، Source، Removable.

- ارتفاع: ۲۸ یا ۳۲px.
- Radius: Pill.
- Context chip تغییرپذیر باید Chevron یا Edit icon داشته باشد.
- Source chip شامل favicon/icon، عنوان کوتاه و شماره Citation است.

### 12.8 Card

- Padding: ۱۶px؛ Large card: ۲۴px.
- Radius: ۱۲px.
- Border default.
- Hover فقط برای Card قابل کلیک.
- Card غیرقابل کلیک cursor پیش‌فرض داشته باشد.
- Nested card بیش از یک سطح ممنوع است.

### 12.9 Tooltip

- حداکثر عرض ۲۴۰px.
- Delay: ۵۰۰ms؛ برای Validation error بدون Delay.
- محتوای ضروری فقط در Tooltip قرار نگیرد.

### 12.10 Modal/Dialog

- برای تصمیم blocking یا Sensitive action.
- Width: ۴۸۰px استاندارد، ۶۴۰px برای محتوای پیچیده.
- Escape و Close button فعال، مگر هنگام commit اتمیک بسیار کوتاه.
- Focus trap و بازگشت Focus الزامی.

### 12.11 Drawer/Bottom sheet

- Evidence و Context details در Tablet/Mobile.
- Drag handle در Mobile.
- Close gesture نباید باعث از دست رفتن Input ذخیره‌نشده شود.

### 12.12 Tabs

- Tab فعال: text primary + Border-bottom دوپیکسلی.
- Horizontal scroll در Mobile.
- Tabs برای تغییر View هم‌سطح؛ Accordion برای مراحل ترتیبی.

### 12.13 Table

- Header با surface-subtle.
- Row hover بسیار ملایم.
- حداقل ارتفاع Cell: ۴۸px.
- Sticky header برای بیش از ۸ Row.
- در Mobile ابتدا Columnهای مهم حفظ، سپس Horizontal scroll.
- Table به Cardهای متفاوت تبدیل نشود مگر داده ذاتاً Card-like باشد.

### 12.14 Alert

Variants: Info، Success، Warning، Danger، Unknown.

- Icon ۱۸px.
- Padding ۱۲px.
- Radius ۸px.
- Title اختیاری، Body الزامی.
- Alert critical دارای Action مشخص.

### 12.15 Toast

- فقط برای نتیجه Action کوتاه.
- حداکثر سه Toast هم‌زمان.
- مدت نمایش معمولی ۵ ثانیه؛ Error تا اقدام کاربر باقی بماند.
- اطلاعات تشخیصی مهم در Toast تنها نمایش داده نشود.

### 12.16 Skeleton/Spinner/Progress

- Skeleton برای Layout شناخته‌شده.
- Spinner برای انتظار کمتر از ۱۰ ثانیه و فرآیند نامشخص.
- Agent step status برای عملیات چندمرحله‌ای.
- متن وضعیت بعد از ۲ ثانیه نمایش داده شود.

---

## 13. LLM and Agentic Components

### 13.1 Prompt Composer

اجزا:

- Auto-growing textarea
- Attachment/paste affordance در صورت وجود Scope
- Send/Stop button
- Scope indicator: «پاسخ بر اساس منابع رسمی Liara»
- Context shortcut
- Secret warning هنگام تشخیص Token/Password

States:

- Empty
- Typing
- Ready
- Sending
- Streaming with Stop
- Disabled/offline
- Secret detected
- Too long

قواعد:

- Enter ارسال می‌کند؛ `Shift+Enter` خط جدید.
- در Mobile، Enter خط جدید و Send button ارسال کند تا ارسال تصادفی کاهش یابد.
- Stop باید Stream را متوقف کند ولی متن دریافت‌شده را نگه دارد.
- Secret تشخیص‌داده‌شده قبل از ارسال Mask و Confirmation دریافت کند.

### 13.2 User Message

- Surface متفاوت ولی بدون Bubble اغراق‌شده.
- عرض حداکثر ۸۵٪ Main column.
- Timestamp در حالت Hover/Focus یا Details.
- Edit/Retry برای آخرین پیام کاربر.
- Code و Log در Block مستقل LTR.

### 13.3 Agent Answer

ساختار اجباری:

1. Direct answer یا Current conclusion
2. مراحل عملیاتی
3. Validation/Expected result
4. Next best action
5. Sources summary

Header شامل:

- Agent/brand mark کوچک
- Status label
- Last verified indicator در صورت وجود

Footer شامل:

- Useful/Not useful
- Copy
- Retry
- Report unsupported claim

### 13.4 Clarification Card

- یک سؤال در هر Card.
- دلیل سؤال به‌صورت کوتاه: «این مورد روش استقرار را تغییر می‌دهد».
- Quick choices حداکثر ۴ گزینه.
- گزینه «نمی‌دانم» در صورت قابل قبول بودن.
- پاسخ قبلی قابل ویرایش.
- Liara Signal روی این مرحله متوقف می‌شود.

### 13.5 Goal Card

Fields:

- Goal statement
- Service
- Framework/runtime
- Deployment method
- Environment
- Current state

قواعد:

- Fieldهای Unknown آشکار باشند.
- Edit کردن Goal نیازمند Confirmation نیست؛ تغییر عمده باید Plan را invalid کند و پیام روشن نمایش دهد.
- Goal card در Desktop collapsible و در Mobile summary chip باشد.

### 13.6 Plan/Task Stepper

هر Step شامل:

- شماره یا Status icon
- عنوان Action-oriented
- توضیح یک‌خطی
- Required input/evidence
- Source count
- Result state

States:

- Pending
- Active
- Waiting for user
- Validating
- Complete
- Skipped with reason
- Failed
- Blocked

قواعد:

- فقط یک Step Active باشد.
- Completed steps Collapse شوند ولی قابل بازشدن باقی بمانند.
- Skip بدون Reason ممنوع.
- تغییر Plan با یک پیام Diff کوتاه نمایش داده شود.

### 13.7 Source Citation

دو سطح دارد:

#### Inline citation

- شماره یا Label کوچک کنار Claim.
- Focus/hover Preview عنوان، Section و Evidence snippet.
- Citation تنها به Page home متصل نشود؛ Deep link ترجیح دارد.

#### Source card

Fields:

- عنوان صفحه
- Source type: Docs/API/CLI/GitHub/Status
- URL
- Section
- Last verified/freshness state
- Evidence excerpt کوتاه
- Used in claims count

Freshness states:

- Current
- Date unknown
- Potentially outdated
- Conflicting

### 13.8 Evidence Rail

Evidence Rail یکی از مهم‌ترین عوامل امتیاز Quality است.

Sections:

1. Sources used
2. Evidence for active step
3. Context assumptions
4. Conflicts/unknowns

رفتار:

- انتخاب Citation، Source card مرتبط را Highlight کند.
- انتخاب Source، Claimهای مصرف‌کننده آن را Highlight کند.
- Rail در Desktop ثابت و در Tablet/Mobile Drawer است.
- Evidence excerpt حداکثر چند خط کوتاه باشد؛ از کپی طولانی مستندات جلوگیری شود.

### 13.9 Confidence/Answerability Indicator

Confidence عددی مانند ۸۷٪ نمایش داده نشود، مگر Calibration واقعی وجود داشته باشد.

Labelهای مجاز:

- Supported by official sources
- Partially supported
- More information required
- Conflicting sources
- Not found in official sources

هر Label باید دلیل کوتاه و Action بعدی داشته باشد.

### 13.10 Diagnostic Hypothesis Card

Fields:

- Hypothesis title
- Why it is possible
- Supporting evidence
- Evidence against
- Safe differentiating test
- Risk level
- Status: possible/eliminated/confirmed

قواعد:

- Hypothesis به‌عنوان Fact نمایش داده نشود.
- حداکثر سه Hypothesis اول باز باشند.
- تست کم‌ریسک در اولویت قرار گیرد.
- توصیه مخرب بدون Warning و Confirmation ممنوع.

### 13.11 Code Block

Header:

- Language/format
- Optional filename
- Copy button
- Wrap toggle برای Log، نه Code

Body:

- LTR قطعی
- Font monospace ۱۳/۲۲
- Line numbers فقط برای بلوک بیش از ۶ خط یا ارجاع خطی
- Horizontal scroll
- Highlight خطوط تغییرکرده

Placeholderها:

- Placeholder باید با شکل واضح مانند `<APP_NAME>` نمایش داده شود.
- مقدار Secret واقعی در Example ممنوع.
- Copy در صورت وجود Placeholder پیام «مقادیر مشخص‌شده را جایگزین کنید» نشان دهد.

### 13.12 Log/Error Block

- متن خام از Interpretation جدا باشد.
- Timestamp، level و service در صورت وجود قابل فیلتر باشند.
- Error line اصلی Highlight شود.
- Secret redaction با Label `[REDACTED]`.
- Copy redacted و Copy original فقط در صورت مجوز و Warning.
- جهت LTR.

### 13.13 Validation Checkpoint

اجزا:

- Expected result
- How to verify
- User choices: «موفق شد»، «خطا دارم»، «مطمئن نیستم»
- Optional paste result

اگر موفق شد، Step کامل می‌شود. اگر خطا رخ دهد، Plan وارد Recovery branch می‌شود.

### 13.14 Next Best Action

- دقیقاً یک Action پیشنهادی اصلی.
- حداکثر دو Alternative.
- دلیل کوتاه.
- Risk/effort indicator در صورت نیاز.
- Action نباید صرفاً «مطالعه بیشتر» باشد، مگر واقعاً آخرین گزینه باشد.

### 13.15 Support Handoff Card

Sections:

- Goal
- Service/environment
- Error summary
- Redacted evidence
- Steps tried and results
- Sources consulted
- Eliminated hypotheses
- Remaining questions

Actions:

- Copy summary
- Download/Export summary در صورت وجود Scope
- Open support entry point

قبل از Copy/Export، Secret scan اجرا و نتیجه به کاربر نمایش داده شود.

### 13.16 Feedback Component

- Useful / Not useful در سطح پاسخ.
- Reasonهای Not useful: incorrect، outdated، incomplete، unclear، source mismatch، other.
- Comment اختیاری.
- Feedback نباید جریان Task را قطع کند.

---

## 14. Agent State Model in UI

| State | User-facing label | Visual behavior | Allowed actions |
|---|---|---|---|
| Idle | آماده | Composer active | ارسال |
| Understanding | در حال بررسی درخواست | Signal شروع می‌شود | توقف |
| Clarifying | اطلاعات بیشتری لازم است | Clarification card | پاسخ/ویرایش Goal |
| Retrieving | در حال بررسی منابع رسمی | Source placeholders | توقف |
| Planning | در حال ساخت مسیر حل | Plan skeleton | توقف |
| Guiding | مرحله جاری | Active step | ثبت نتیجه |
| Validating | در حال بررسی نتیجه | Validation sweep | توقف |
| Recovering | مسیر جایگزین | Branch در Signal | ادامه/Handoff |
| Complete | هدف تکمیل شد | Success state | Task جدید/خلاصه |
| Partial | بخشی از هدف حل شد | Warning state | اطلاعات بیشتر/Handoff |
| Blocked | امکان ادامه مطمئن نیست | Unknown state | Handoff/بازگشت |
| Failed | عملیات پاسخ‌گویی ناموفق بود | Error state | Retry/Search fallback |
| Offline | سرویس هوشمند در دسترس نیست | Neutral state | Docs search |

### State copy rules

- «در حال فکر کردن…» به‌تنهایی ممنوع است.
- Label باید نوع کار را بگوید: «در حال بررسی مستندات Node.js».
- زمان تخمینی ساختگی نمایش داده نشود.
- بعد از ۱۰ ثانیه، توضیح وضعیت و امکان توقف نمایش داده شود.

---

## 15. Page and Screen Patterns

### 15.1 Landing/Empty workspace

اجزا:

- Logo + Product name
- Headline کوتاه: کمک برای رسیدن از سؤال به نتیجه
- Composer مرکزی
- سه Task starter واقعی:
  - استقرار یک برنامه
  - اتصال دامنه یا دیتابیس
  - بررسی یک خطا
- Scope statement
- Recent taskها در صورت وجود

تزئین مجاز: Grid بسیار کم‌رنگ + Liara Signal؛ بدون Hero illustration سنگین.

### 15.2 Simple answer

- Answer مستقیم
- Inline citations
- Related action
- Sources collapsed
- بدون Plan panel غیرضروری

### 15.3 Goal workflow

- Goal card
- Plan stepper
- Active step content
- Validation checkpoint
- Evidence rail
- Composer برای Follow-up

### 15.4 Troubleshooting workspace

- Incident summary
- Raw evidence
- Ranked hypotheses
- Safe test
- Recovery history
- Support handoff

### 15.5 Search fallback

- Query
- Filter by Product/Framework/Source type
- Result title + snippet + breadcrumbs
- پیشنهاد تبدیل Query به Goal
- Zero-result guidance

### 15.6 History

- Group by Today/Previous 7 days/Older.
- Search by Goal و Service.
- Status و last activity.
- Delete با Confirmation.
- Secret-containing content در Preview نمایش داده نشود.

---

## 16. Empty, Loading, Error and Edge States

### 16.1 Empty states

هر Empty state باید شامل این سه مورد باشد:

1. چه چیزی خالی است.
2. چرا یا چه ارزشی دارد.
3. Action بعدی.

### 16.2 No source found

Copy canonical:

> پاسخ قابل اتکایی در منابع رسمی Liara پیدا نشد.

سپس:

- Query interpreted
- Filters used
- اطلاعات تکمیلی موردنیاز
- Search manually
- Support handoff

### 16.3 Conflicting sources

- هر دو Source نمایش داده شود.
- تفاوت مشخص شود.
- Source authority و freshness نمایش داده شود.
- Action پرریسک متوقف شود.

### 16.4 Rate limit

- علت ساده
- زمان یا شرط Retry فقط اگر واقعی است
- حفظ Draft
- Link به Docs/Search fallback

### 16.5 Network/offline

- پاسخ در حال تایپ از بین نرود.
- Retry و Copy draft.
- آخرین پاسخ‌های Cache شده با Label مشخص.

### 16.6 Long conversation

- Context summary قابل مشاهده.
- امکان شروع Task جدید با Carry selected context.
- هشدار قبل از حذف Context قدیمی.

---

## 17. RTL and Bidirectional Content

### قوانین پایه

- Root document: `dir="rtl"`, `lang="fa"`.
- Code، URL، Email، CLI و Log: `dir="ltr"`.
- Identifier inline: `unicode-bidi: isolate`.
- Iconهای Forward/Back متناسب با RTL Mirror شوند.
- Sidebar در سمت راست قرار گیرد.
- Evidence rail در Desktop سمت چپ باشد تا Main reading flow فارسی حفظ شود.
- Numbered steps از راست آغاز شوند.
- Copy button در Code block سمت چپ Header قرار گیرد.
- جدول دارای داده فنی می‌تواند Header فارسی RTL و Cell فنی LTR داشته باشد.
- Punctuation اطراف Inline code با isolate کنترل شود.

### Persian copy

- از نیم‌فاصله صحیح استفاده شود.
- فعل Action در Button کوتاه باشد: «ادامه»، «بررسی خطا»، «کپی».
- اصطلاحات فنی شناخته‌شده می‌توانند انگلیسی بمانند، اما اولین بار توضیح فارسی داده شود.
- متن ترکیبی نباید با قرار دادن دستی کاراکترهای جهت‌دهی نامرئی اصلاح شود؛ از semantic direction استفاده شود.

---

## 18. Accessibility

### الزامات سطح پایه

- هدف: WCAG 2.2 AA.
- تمام Interactionها با Keyboard قابل انجام باشند.
- Focus indicator هیچ‌گاه حذف نشود.
- ترتیب Focus مطابق ترتیب بصری RTL باشد.
- Skip link برای رفتن به Main content.
- Heading hierarchy صحیح.
- Landmarkهای `header`, `nav`, `main`, `aside` و `footer`.
- Live region برای Agent status، بدون اعلام هر Token استریم‌شده.
- Error message با Input مرتبط شود.
- Color تنها حامل معنی نباشد.
- Tooltip با Focus نیز فعال شود.
- Dialog دارای focus trap و accessible title.
- Bottom sheet برای Screen reader به‌عنوان Dialog/Region معرفی شود.
- Drag تنها روش تغییر ترتیب یا اندازه نباشد.

### Streaming accessibility

- کل پاسخ در هر Token به Screen reader اعلام نشود.
- شروع و پایان تولید پاسخ اعلام شود.
- Paragraph کامل‌شده یا پاسخ نهایی قابل خواندن باشد.
- Stop button Label روشن داشته باشد.

### Reduced motion

- تمام Loopها غیرفعال.
- Smooth scrolling غیرفعال.
- State transition با color/icon/label حفظ شود.

---

## 19. Security and Trust UX

### 19.1 Secret detection

موارد هدف:

- API token
- Password
- Database URI
- Private key
- Authorization header
- Cookie/session value

رفتار:

1. تشخیص قبل از ارسال.
2. Highlight بخش حساس.
3. گزینه Mask and send به‌عنوان Primary.
4. ارسال بدون Mask فقط با Warning صریح، اگر Policy اجازه دهد.
5. Secret در History preview و Analytics ثبت نشود.

### 19.2 Trust labels

Labelهای مجاز:

- منبع رسمی Liara
- منبع رسمی GitHub Liara
- اطلاعات ارائه‌شده توسط کاربر
- استنباط سیستم
- تأییدنشده
- احتمالاً قدیمی

### 19.3 Risk labels

| Level | معنی | UI |
|---|---|---|
| Safe | Read-only/check | Neutral/brand |
| Caution | تغییر قابل بازگشت | Warning |
| High risk | احتمال downtime/data impact | Danger + Confirmation |
| Destructive | حذف یا overwrite | Danger dialog + typed confirmation در آینده |

### 19.4 Prompt injection UX

اگر محتوای Paste‌شده یا Source شامل دستور مشکوک باشد:

- محتوا به‌عنوان Data نمایش داده شود.
- Banner کوتاه «دستور موجود در این محتوا اجرا یا دنبال نشد».
- جزئیات در Security disclosure.

### 19.5 Privacy

- Memory بلندمدت پیش‌فرض خاموش.
- Retention policy در Settings قابل مشاهده.
- Delete conversation واقعی و قابل تأیید.
- Export قبل از دانلود Secret scan شود.

---

## 20. Content Design and Voice

### Voice

- مستقیم
- دقیق
- آرام
- مسئولانه
- متناسب با سطح فنی کاربر

### قواعد پاسخ

- ابتدا نتیجه، سپس توضیح.
- هر مرحله با فعل آغاز شود.
- از قطعیت بدون Evidence اجتناب شود.
- «احتمالاً» همراه با دلیل و Test باشد.
- Error خام نقل شود، اما Interpretation جدا بماند.
- پاراگراف‌های طولانی به Step یا Bullet تبدیل شوند.
- حداکثر یک سؤال Clarification در هر نوبت، مگر پاسخ‌ها مستقل و بسیار کوتاه باشند.

### Canonical phrases

| Situation | Copy |
|---|---|
| Insufficient evidence | «برای پاسخ مطمئن، یک اطلاعات دیگر لازم است.» |
| No official answer | «این مورد در منابع رسمی Liara پیدا نشد.» |
| Conflict | «دو منبع رسمی درباره این مورد اطلاعات متفاوتی دارند.» |
| Safe next action | «کم‌ریسک‌ترین بررسی بعدی این است:» |
| Partial success | «بخشی از مسئله مشخص شد، اما برای نتیجه نهایی هنوز اطلاعات کافی نداریم.» |
| Handoff | «برای ادامه مطمئن، بهتر است این خلاصه را برای پشتیبانی ارسال کنید.» |

---

## 21. Component Naming Contract

نام‌های زیر برای Design و Implementation یکسان استفاده شوند:

```text
AppShell
PrimaryNavigation
ContextBar
Workspace
EvidenceRail
PromptComposer
UserMessage
AgentAnswer
GoalCard
ClarificationCard
TaskPlan
TaskStep
ValidationCheckpoint
SourceCitation
SourceCard
AnswerabilityBadge
DiagnosticHypothesis
CodeBlock
LogBlock
NextBestAction
SupportHandoff
FeedbackControl
StatusBadge
Alert
Dialog
Drawer
BottomSheet
CommandPalette
```

از نام‌های عمومی و مبهم مانند `Box2`, `Wrapper`, `AIThing` و `ResponseWidget` استفاده نشود.

---

## 22. Z-index Contract

| Layer | Value |
|---|---:|
| Base content | 0 |
| Sticky local header | 10 |
| App navigation/top bar | 20 |
| Composer | 30 |
| Drawer/Bottom sheet | 40 |
| Overlay | 50 |
| Modal | 60 |
| Command palette | 70 |
| Toast | 80 |
| Tooltip | 90 |

مقدار خارج از این Scale بدون ثبت در Design System استفاده نشود.

---

## 23. Performance-aware Design Rules

- Hero video در App workspace استفاده نشود.
- Decorative backgroundها CSS-based و سبک باشند.
- Font subset فارسی و Latin در صورت امکان.
- بیش از دو Font family بارگذاری نشود.
- Skeleton DOM ساده باشد.
- Evidence Rail با Virtualization فقط در صورت طول زیاد؛ MVP نباید زودهنگام پیچیده شود.
- تصاویر Documentation lazy-load شوند.
- Streaming response نباید باعث Reflow مکرر Sidebar/Evidence شود.
- Syntax highlighting فقط برای Blockهای قابل مشاهده انجام شود.

---

## 24. Analytics and UX Measurement Hooks

نام Eventها مستقل از ابزار Analytics است:

```text
prompt_submitted
clarification_answered
context_edited
plan_created
task_step_started
task_step_completed
task_step_failed
validation_submitted
source_opened
citation_previewed
answer_copied
answer_feedback_submitted
secret_warning_triggered
secret_redacted
support_handoff_created
support_handoff_copied
fallback_search_used
task_completed
task_abandoned
```

قواعد:

- Prompt، Log و Secret raw در Event payload ثبت نشوند.
- IDهای Session pseudonymous باشند.
- Event naming در Implementation تغییر نکند مگر با Version migration.

---

## 25. Rubric Mapping

### Quality / 80

- Evidence Rail
- Inline citations
- Answerability labels
- Freshness/conflict states
- Validation checkpoints
- Fact/Hypothesis separation

### UI/UX / 55

- RTL-first responsive workspace
- Progressive disclosure
- Code/Log/Source components
- Stable streaming layout
- Dark/Light themes
- Accessibility AA

### Agentic & Personalization / 50

- Goal Card
- Clarification Card
- Visible Task Plan
- Liara Signal state model
- Recovery branch
- Next Best Action
- Session context

### Security/Stability / 50

- Secret detection/redaction
- Risk labels
- Safe failure states
- Offline/Search fallback
- Prompt injection notice
- Accessible error handling

### Liara Deployment / 40

- هویت بصری منطبق با Liara
- Performance-aware assets
- Responsive behavior
- Product/Service context patterns

### Cost / 25

- Simple answer mode بدون Plan غیرضروری
- Progressive disclosure
- Context summary
- Stable cached/fallback states
- نمایش UI متناسب با task complexity

---

## 26. Do / Don’t

### Do

- از `#181818` و سطوح نزدیک برای Shell تیره استفاده کن.
- گرادیان Mint→Cyan را به نقاط کلیدی محدود کن.
- Source را کنار Claim نمایش بده.
- State سیستم را با Label دقیق توضیح بده.
- Code و Log را LTR نگه دار.
- Goal و Current step را همیشه قابل تشخیص نگه دار.
- Unknown را صادقانه و قابل اقدام نمایش بده.
- Main answer را از Diagnostic detail جدا کن.

### Don’t

- UI را شبیه ChatGPT clone نساز.
- برای هر پیام Bubble رنگی ایجاد نکن.
- از Robot/Brain/Sparkle به‌عنوان هویت اصلی استفاده نکن.
- همه‌چیز را Gradient یا Glow نکن.
- Confidence درصدی غیرکالیبره نمایش نده.
- Citationها را فقط انتهای پاسخ قرار نده.
- Agent state را با Spinner بی‌توضیح نمایش نده.
- Secret را در Example، History preview یا Analytics نشان نده.
- در Mobile سه ستون را کوچک نکن؛ Layout را به یک ستون تبدیل کن.
- از رنگ به‌تنهایی برای Success/Error استفاده نکن.

---

## 27. MVP Component Priority

### MUST

- AppShell
- PrimaryNavigation
- ContextBar
- PromptComposer
- UserMessage
- AgentAnswer
- ClarificationCard
- GoalCard
- TaskPlan/TaskStep
- SourceCitation/SourceCard
- EvidenceRail
- CodeBlock/LogBlock
- ValidationCheckpoint
- NextBestAction
- Alert/StatusBadge
- Loading/Error/Empty states
- Responsive mobile layout
- Keyboard/focus behavior
- Secret detection warning UI

### SHOULD

- DiagnosticHypothesis
- SupportHandoff
- FeedbackControl
- Search fallback
- Theme toggle
- History
- Context editing

### COULD

- CommandPalette
- Export handoff
- Advanced source filters
- Read-only service state cards

### خارج از MVP

- Autonomous action execution
- Long-term personalized memory
- Multi-agent visualization
- Collaborative workspace
- Voice interface
- Custom user dashboards

---

## 28. Implementation Acceptance Checklist

### Foundations

- [ ] تمام رنگ‌ها از Semantic token استفاده می‌کنند؛ Hex پراکنده وجود ندارد.
- [ ] Yekan Bakh با font-display swap بارگذاری می‌شود.
- [ ] Type scale و spacing scale رعایت شده‌اند.
- [ ] Light و Dark tokenها بدون تغییر Component کار می‌کنند.
- [ ] Focus ring قابل مشاهده است.

### Layout

- [ ] Desktop سه‌ناحیه‌ای طبق قرارداد است.
- [ ] Evidence در Tablet به Drawer تبدیل می‌شود.
- [ ] Mobile یک ستون واقعی دارد.
- [ ] Composer روی محتوا Overlay نمی‌شود.
- [ ] Code/Table تنها نقاط Scroll افقی‌اند.

### RTL

- [ ] Root RTL و Persian lang است.
- [ ] Code، URL و Log LTR هستند.
- [ ] Arrowهای جهت‌دار درست Mirror می‌شوند.
- [ ] ترتیب Focus با UI RTL هماهنگ است.
- [ ] محتوای ترکیبی بدون شکست Punctuation نمایش داده می‌شود.

### Agentic UX

- [ ] Goal قابل مشاهده است.
- [ ] Agent state Label دقیق دارد.
- [ ] فقط یک Plan step فعال است.
- [ ] Validation نتیجه Step را تغییر می‌دهد.
- [ ] Recovery branch در UI قابل فهم است.
- [ ] Next Best Action دقیقاً یک Primary دارد.

### Quality

- [ ] Claimهای فنی Citation دارند.
- [ ] Source card نوع و freshness را نشان می‌دهد.
- [ ] Unsupported answer state وجود دارد.
- [ ] Conflict state وجود دارد.
- [ ] Confidence عددی ساختگی نمایش داده نمی‌شود.

### Security

- [ ] Secret warning قبل از ارسال فعال می‌شود.
- [ ] Copy/Export نسخه Redacted دارد.
- [ ] Risky action Label و Confirmation دارد.
- [ ] Prompt injection content به‌عنوان Data نمایش داده می‌شود.
- [ ] Raw prompt/log در Analytics ثبت نمی‌شود.

### Accessibility

- [ ] Keyboard-only flow کامل است.
- [ ] Focus trap Dialog تست شده است.
- [ ] Screen reader status برای شروع/پایان پاسخ فعال است.
- [ ] Contrast AA تأیید شده است.
- [ ] Reduced motion تست شده است.
- [ ] Touch targetها حداقل ۴۴px هستند.

### Resilience

- [ ] Offline state Draft را حفظ می‌کند.
- [ ] Rate limit state Action مشخص دارد.
- [ ] Stop streaming کار می‌کند.
- [ ] Retry محتوای قبلی را حذف نمی‌کند.
- [ ] Search fallback بدون LLM قابل استفاده است.

---

## 29. Definition of Done برای Design Implementation

Design System زمانی به‌درستی پیاده‌سازی شده است که:

1. تمام MUST componentها در Dark و Light قابل نمایش باشند.
2. هر Component تمام Stateهای تعریف‌شده را داشته باشد.
3. Desktop، Tablet و Mobile بدون Horizontal page overflow کار کنند.
4. یک Flow کامل `Goal → Clarify → Plan → Validate → Complete` قابل نمایش باشد.
5. یک Flow کامل `Error → Hypothesis → Safe test → Recovery/Handoff` قابل نمایش باشد.
6. Citation و Evidence interaction دوطرفه کار کند.
7. Secret warning و Redaction قابل Demo باشد.
8. Keyboard، Screen reader status، Contrast و Reduced motion بررسی شده باشند.
9. هیچ تصمیم بصری جدیدی خارج از Tokenها به‌صورت ad hoc وارد نشده باشد.
10. Product همچنان به‌وضوح متعلق به Liara باشد، ولی شبیه کپی صفحه Marketing یا ChatGPT نباشد.

---

## 30. تصمیم نهایی Design Direction

Direction نهایی این سند:

> یک Technical Intelligence Workspace با Shell تیره، خوانایی Docs، گرادیان کنترل‌شده Liara، Evidence-first interaction و Agent state شفاف.

این Direction برای MVP تثبیت شده است. تغییر آن فقط در صورت مشاهده مشکل جدی در User testing، Accessibility testing یا محدودیت اجرایی مستند مجاز است.
