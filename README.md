# Liara Navigator

یک دستیار مستندات هدف‌محور و مبتنی بر LLM برای یافتن پاسخ‌های مستند، راهنمایی مرحله‌ای و بررسی Read-only وضعیت پروژه‌های Liara.

## وضعیت پروژه

مرحله Discovery، معماری، Design System و Spec Kit تکمیل شده است. پیاده‌سازی MVP هنوز آغاز نشده است.

## مسیرهای اصلی

- [`specs/001-liara-navigator/spec.md`](specs/001-liara-navigator/spec.md): Feature Specification
- [`specs/001-liara-navigator/plan.md`](specs/001-liara-navigator/plan.md): Implementation Plan
- [`specs/001-liara-navigator/tasks.md`](specs/001-liara-navigator/tasks.md): فهرست Taskهای اجرایی
- [`docs/design-system/liara-intelligence-design-system.md`](docs/design-system/liara-intelligence-design-system.md): Design System مرجع
- [`design-system-preview/index.html`](design-system-preview/index.html): پیش‌نمایش تعاملی Design System
- [`specs/001-liara-navigator/contracts/openapi.yaml`](specs/001-liara-navigator/contracts/openapi.yaml): قرارداد OpenAPI

## مشاهده پیش‌نمایش Design System

```bash
cd design-system-preview
python3 -m http.server 4173
```

سپس `http://127.0.0.1:4173` را باز کنید.

## سیاست Commit

- هر Feature یا تغییر مستقل در Commit جداگانه ثبت می‌شود.
- پیش از Commit، تست‌ها و کنترل‌های مرتبط اجرا می‌شوند.
- Secret، Token، فایل `.env`، Virtual environment و خروجی Build وارد Git نمی‌شوند.
- پیام Commitها از قالب‌هایی مانند `feat:`, `fix:`, `test:`, `docs:` و `chore:` استفاده می‌کنند.
