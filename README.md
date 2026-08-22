# Liara Navigator

دستیار فارسی و مستندمحور برای پاسخ به پرسش‌های فنی Liara، راهنمایی مرحله‌ای، نمایش citation و
بررسی Read-only سرویس‌ها و logهای PaaS.

## وضعیت MVP

نسخه وب و API این قابلیت‌ها را دارد:

- انتخاب بین دستیار هوشمند و ثبت Ticket پشتیبانی
- پاسخ به موضوع‌های PaaS، CDN، SSL، DNS و سایر مستندات
- انتخاب پلتفرم، برنامه و سرویس PaaS همراه با آیکون پلتفرم
- ادامه گفت‌وگو حتی اگر کاربر برنامه یا سرویسی نداشته باشد
- ارسال log محدود و پاک‌سازی‌شده به agent در مسیر PaaS
- پاسخ مبتنی بر snapshot رسمی مستندات همراه با citation معتبر
- اتصال production به AvalAI از طریق API سازگار با OpenAI

## معماری اجرا

Frontend با React/Vite ساخته می‌شود و FastAPI همان فایل‌های buildشده و API را از یک container
ارائه می‌کند. مستندات رسمی در زمان اجرا از اینترنت خوانده نمی‌شوند؛ snapshot نسخه‌دار داخل image
قرار می‌گیرد. برای development/production از AvalAI و برای تست‌ها از provider قطعی داخلی استفاده
می‌شود.

## پیش‌نیازها

- Python 3.12 و `uv`
- Node.js 22 و npm
- Docker برای PostgreSQL محلی و بررسی image نهایی

وابستگی‌ها را از ریشه پروژه نصب کنید:

```bash
uv sync --project backend --frozen
npm ci --prefix frontend
```

## تنظیم محیط محلی

فایل نمونه را کپی کنید:

```bash
cp .env.example .env.local
```

سپس در `.env.local` حداقل این دو مقدار را قرار دهید:

- `SESSION_HMAC_SECRET`: یک مقدار تصادفی با حداقل ۳۲ کاراکتر؛ برای ساخت آن می‌توانید
  `openssl rand -hex 32` را اجرا کنید.
- `AVALAI_API_KEY`: کلید فعال AvalAI؛ این مقدار را هرگز commit نکنید.

اجرای برنامه:

```bash
docker compose -f compose.local.yaml up -d
npm --prefix frontend run build
backend/.venv/bin/uvicorn app.main:app --app-dir backend --reload
```

برنامه روی `http://127.0.0.1:8000` و health check روی
`http://127.0.0.1:8000/api/v1/health/live` در دسترس است.

## متغیرهای production

این مقادیر را در تنظیمات برنامه Liara وارد کنید:

| متغیر | مقدار پیشنهادی/توضیح |
| --- | --- |
| `APP_ENV` | `production` |
| `DATABASE_URL` | DSN دیتابیس PostgreSQL؛ در MVP هنوز persistence فعال نیست اما config آن را الزامی می‌داند |
| `SESSION_HMAC_SECRET` | خروجی جدید و محرمانه `openssl rand -hex 32` |
| `AI_BASE_URL` | `https://api.avalai.ir/v1` |
| `AVALAI_API_KEY` | کلید جدید AvalAI، فقط در Environment لیارا |
| `AI_FAST_MODEL` | `gpt-5.4-mini` |
| `AI_REASONING_MODEL` | `gpt-5.5` |
| `AI_EMBEDDING_MODEL` | `text-embedding-3-small` |
| `KNOWLEDGE_SNAPSHOT_VERSION` | `liara-docs-dbb7430b1abc` |

مقادیر threshold موجود در `.env.example` اختیاری‌اند و در صورت تنظیم‌نشدن از پیش‌فرض امن برنامه
استفاده می‌کنند. production با snapshot آزمایشی `test-fixture` اجرا نخواهد شد.

## استقرار روی Liara با GitHub

پروژه برای پلتفرم Docker آماده است و `Dockerfile` و `liara.json` در ریشه قرار دارند.

1. در کنسول Liara یک برنامه با پلتفرم Docker بسازید و پورت را `8000` انتخاب کنید.
2. از تنظیمات حساب، GitHub را متصل کنید و دسترسی repository را بدهید.
3. در صفحه «استقرار جدید»، repository را با branch `main` به برنامه متصل کنید.
4. متغیرهای بخش قبل را در «تنظیمات ← متغیرها» ثبت کنید.
5. «استقرار دستی» را اجرا کنید و build/deploy log را تا پایان بررسی کنید.
6. ابتدا `/api/v1/health/live` و سپس صفحه اصلی را باز کنید.
7. یک پرسش DNS یا SSL ارسال کنید و بازشدن citation رسمی را کنترل کنید.

راهنمای مرجع: [استقرار Docker در Liara](https://docs.liara.ir/paas/docker/quick-start) و
[تنظیم متغیرهای محیطی](https://docs.liara.ir/paas/details/envs).

## تست و کنترل کیفیت

```bash
cd backend
.venv/bin/python -m pytest -q
.venv/bin/ruff check app tests ../scripts/build_docs_snapshot.py
.venv/bin/mypy app

cd ../frontend
npm test -- --run
npm run build
```

## snapshot مستندات

فرمان زیر مخزن رسمی `liara-cloud/docs` را خودکار clone می‌کند، فایل‌های MDX را پاک‌سازی و chunk
می‌کند، topic/platform و citation URL می‌سازد و خروجی immutable و hash‌شده تولید می‌کند:

```bash
backend/.venv/bin/python scripts/build_docs_snapshot.py
```

پس از ساخت نسخه جدید باید مقدار چاپ‌شده `KNOWLEDGE_SNAPSHOT_VERSION` را در Environment و
`.env.example` قرار دهید و پوشه snapshot جدید را commit کنید. نسخه فعلی شامل ۳۱۵۵ chunk از commit
`dbb7430b1abc5bf92ccca3538f45c54bdc632fa8` مستندات رسمی است.

## محدودیت‌های آگاهانه MVP

- API برنامه‌ها، سرویس‌ها و logهای Liara فعلاً mock و فقط Read-only است.
- Ticket واقعاً برای تیم پشتیبانی ارسال نمی‌شود و mock است.
- session، rate-limit و telemetry در حافظه‌اند و با restart پاک می‌شوند.
- snapshot فقط با اجرای pipeline به‌روزرسانی می‌شود و در runtime اینترنت را crawl نمی‌کند.

این موارد برای demo/MVP مناسب‌اند؛ پیش از استفاده عملیاتی عمومی باید provider واقعی Liara، ارسال
Ticket و persistence مشترک پیاده‌سازی شوند.

## مسیرهای اصلی

- [`specs/001-liara-navigator/spec.md`](specs/001-liara-navigator/spec.md): Feature Specification
- [`specs/001-liara-navigator/plan.md`](specs/001-liara-navigator/plan.md): Implementation Plan
- [`specs/001-liara-navigator/tasks.md`](specs/001-liara-navigator/tasks.md): Taskهای اجرایی
- [`docs/design-system/liara-intelligence-design-system.md`](docs/design-system/liara-intelligence-design-system.md): Design System
- [`specs/001-liara-navigator/contracts/openapi.yaml`](specs/001-liara-navigator/contracts/openapi.yaml): قرارداد OpenAPI
- [`scripts/build_docs_snapshot.py`](scripts/build_docs_snapshot.py): pipeline ساخت snapshot

## امنیت repository

Secret، API token، فایل `.env`، virtual environment، log و خروجی build نباید وارد Git شوند. فقط
`.env.example` بدون مقدار محرمانه نگهداری می‌شود.
