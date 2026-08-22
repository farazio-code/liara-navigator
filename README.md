# Liara Navigator

یک دستیار مستندات هدف‌محور و مبتنی بر LLM برای یافتن پاسخ‌های مستند، راهنمایی مرحله‌ای و بررسی Read-only وضعیت پروژه‌های Liara.

## وضعیت پروژه

MVP وب، API، گردش گفت‌وگوی مستند، مسیر PaaS و Ticket پیاده‌سازی شده‌اند. پاسخ واقعی مدل در
محیط development/production از API سازگار با OpenAI در AvalAI دریافت می‌شود.

## اجرای محلی

فایل `.env.example` را با نام `.env.local` کپی کنید و فقط مقادیر Secret را محلی وارد کنید؛ این
فایل در Git ثبت نمی‌شود. سپس:

```bash
docker compose -f compose.local.yaml up -d
npm --prefix frontend run build
backend/.venv/bin/uvicorn app.main:app --app-dir backend --reload
```

آدرس برنامه `http://127.0.0.1:8000` است.

## به‌روزرسانی snapshot مستندات

فرمان زیر مخزن رسمی مستندات را خودکار clone می‌کند، MDXها را پاک‌سازی و chunk می‌کند، citation
URL می‌سازد و snapshot نسخه‌دار و hash‌شده را در پروژه قرار می‌دهد:

```bash
backend/.venv/bin/python scripts/build_docs_snapshot.py
```

بعد از ساخت نسخه جدید، مقدار `KNOWLEDGE_SNAPSHOT_VERSION` چاپ‌شده توسط فرمان را در محیط استقرار
قرار دهید. snapshot فعلی `liara-docs-dbb7430b1abc` است.

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
