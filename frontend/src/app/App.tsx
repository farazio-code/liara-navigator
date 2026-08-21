import { useEffect, useState } from "react";

import "../styles/global.css";
import {
  createSession,
  listApps,
  listPlatforms,
  listServices,
  type AppSummary,
  type Platform,
  type ServiceSummary,
} from "../api/client";


type Mode = "agent" | "ticket";
type Topic = "paas" | "cdn" | "ssl" | "dns" | "other";
type LoadState = "idle" | "loading" | "ready" | "empty" | "error";


const topics: Array<{ id: Topic; label: string }> = [
  { id: "paas", label: "PaaS" },
  { id: "cdn", label: "CDN" },
  { id: "ssl", label: "SSL" },
  { id: "dns", label: "DNS" },
  { id: "other", label: "سایر" },
];


export function App() {
  const [mode, setMode] = useState<Mode>("agent");
  const [topic, setTopic] = useState<Topic | null>(null);
  const [sessionReady, setSessionReady] = useState(false);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [platform, setPlatform] = useState<Platform["id"] | "">("");
  const [apps, setApps] = useState<AppSummary[]>([]);
  const [selectedApp, setSelectedApp] = useState<AppSummary | null>(null);
  const [services, setServices] = useState<ServiceSummary[]>([]);
  const [selectedService, setSelectedService] = useState<ServiceSummary | null>(null);
  const [platformState, setPlatformState] = useState<LoadState>("idle");
  const [appState, setAppState] = useState<LoadState>("idle");
  const [serviceState, setServiceState] = useState<LoadState>("idle");

  useEffect(() => {
    void createSession().then(() => setSessionReady(true)).catch(() => setSessionReady(false));
  }, []);

  useEffect(() => {
    if (topic !== "paas" || !sessionReady || platformState !== "idle") return;
    setPlatformState("loading");
    void listPlatforms()
      .then((items) => {
        setPlatforms(items);
        setPlatformState(items.length ? "ready" : "empty");
      })
      .catch(() => setPlatformState("error"));
  }, [platformState, sessionReady, topic]);

  const chooseTopic = (nextTopic: Topic) => {
    setTopic(nextTopic);
    setPlatform("");
    setApps([]);
    setSelectedApp(null);
    setServices([]);
    setSelectedService(null);
    setAppState("idle");
    setServiceState("idle");
  };

  const choosePlatform = async (nextPlatform: Platform["id"] | "") => {
    setPlatform(nextPlatform);
    setApps([]);
    setSelectedApp(null);
    setServices([]);
    setSelectedService(null);
    setServiceState("idle");
    if (!nextPlatform) {
      setAppState("idle");
      return;
    }
    setAppState("loading");
    try {
      const items = await listApps(nextPlatform);
      setApps(items);
      setAppState(items.length ? "ready" : "empty");
    } catch {
      setAppState("error");
    }
  };

  const chooseApp = async (app: AppSummary) => {
    setSelectedApp(app);
    setServices([]);
    setSelectedService(null);
    setServiceState("loading");
    try {
      const items = await listServices(app.ref);
      setServices(items);
      setServiceState(items.length ? "ready" : "empty");
    } catch {
      setServiceState("error");
    }
  };

  return (
    <div className="app-shell" dir="rtl" lang="fa">
      <a className="skip-link" href="#main-content">رفتن به محتوای اصلی</a>
      <nav className="side-panel navigation" aria-label="ناوبری اصلی">
        <div className="brand"><span className="brand-mark">●</span> <span className="brand-text">Liara Navigator</span></div>
        <div className="nav-list">
          <div className="nav-item active">گفت‌وگوی جدید</div>
          <div className="nav-item">تاریخچه</div>
          <div className="nav-item">مستندات</div>
        </div>
      </nav>

      <main id="main-content" className="workspace">
        <header>
          <p className="eyebrow">دستیار فنی لیارا</p>
          <h1>از سؤال تا پاسخ قابل‌استناد</h1>
          <p className="lede">مسیر مناسب را انتخاب کنید؛ جزئیات فنی فقط در صورت نیاز دریافت می‌شوند.</p>
        </header>

        <div className="mode-tabs" role="tablist" aria-label="نوع درخواست">
          <button role="tab" aria-selected={mode === "agent"} className="mode-tab" onClick={() => setMode("agent")}>دستیار هوشمند</button>
          <button role="tab" aria-selected={mode === "ticket"} className="mode-tab" onClick={() => setMode("ticket")}>تیکت پشتیبانی</button>
        </div>

        {mode === "ticket" ? (
          <section className="workflow">
            <h2 className="section-title">ارسال تیکت برای تیم پشتیبانی</h2>
            <p className="status">در Slice پنجم، فرم امن تیکت در این بخش فعال می‌شود.</p>
          </section>
        ) : (
          <section className="workflow">
            <h2 className="section-title">موضوع مشکل چیست؟</h2>
            <fieldset className="topic-grid" aria-label="موضوع مشکل">
              {topics.map((item) => (
                <label className="topic-option" key={item.id}>
                  <input type="radio" name="topic" value={item.id} checked={topic === item.id} onChange={() => chooseTopic(item.id)} />
                  <span>{item.label}</span>
                </label>
              ))}
            </fieldset>

            {topic === "paas" ? (
              <div className="selector-stack">
                <div className="field">
                  <label htmlFor="platform">نوع پلتفرم</label>
                  <select id="platform" value={platform} disabled={platformState === "loading"} onChange={(event) => void choosePlatform(event.target.value as Platform["id"] | "")}>
                    <option value="">انتخاب کنید</option>
                    {platforms.map((item) => <option value={item.id} key={item.id}>{item.label}</option>)}
                  </select>
                  {platformState === "loading" && <p className="status" role="status">در حال دریافت پلتفرم‌ها…</p>}
                  {platformState === "error" && <button className="retry" onClick={() => setPlatformState("idle")}>تلاش دوباره</button>}
                </div>

                {appState !== "idle" && (
                  <ResourceState
                    state={appState}
                    loading="در حال دریافت برنامه‌ها…"
                    empty="برنامه‌ای برای این پلتفرم وجود ندارد."
                    onRetry={() => void choosePlatform(platform)}
                  />
                )}
                {apps.length > 0 && (
                  <div>
                    <p className="field-label">انتخاب برنامه</p>
                    <div className="resource-grid">
                      {apps.map((app) => (
                        <button key={app.ref} className={`resource-card ${selectedApp?.ref === app.ref ? "selected" : ""}`} onClick={() => void chooseApp(app)}>
                          <strong>{app.name}</strong><span className="resource-meta">{app.platform} · {app.status}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {serviceState !== "idle" && (
                  <ResourceState
                    state={serviceState}
                    loading="در حال دریافت سرویس‌ها…"
                    empty="سرویسی برای این برنامه وجود ندارد."
                    onRetry={selectedApp ? () => void chooseApp(selectedApp) : undefined}
                  />
                )}
                {services.length > 0 && (
                  <div>
                    <p className="field-label">انتخاب سرویس</p>
                    <div className="resource-grid">
                      {services.map((service) => (
                        <button key={service.ref} className={`resource-card ${selectedService?.ref === service.ref ? "selected" : ""}`} onClick={() => setSelectedService(service)}>
                          <strong>{service.name}</strong><span className="resource-meta">{service.kind} · {service.status}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : topic ? <p className="status">این موضوع با مستندات رسمی لیارا بررسی می‌شود.</p> : null}

            <div className="composer">
              {selectedService && <p className="selection-note">سرویس انتخاب‌شده: {selectedService.name}</p>}
              <label htmlFor="problem">شرح مسئله</label>
              <textarea id="problem" disabled={topic === "paas" && !selectedService} placeholder="خطا، رفتار مشاهده‌شده و نتیجه‌ای که انتظار داشتید را بنویسید." />
              <button className="primary" disabled={!topic || (topic === "paas" && !selectedService)}>شروع بررسی</button>
            </div>
          </section>
        )}
      </main>

      <aside className="side-panel evidence-panel" aria-label="منابع پاسخ">
        <h2 className="evidence-title">زمینه و منابع</h2>
        <p className="evidence-copy">Citationها و شواهد پاسخ در این بخش نمایش داده می‌شوند.</p>
        <p className="privacy-note">لاگ فقط برای سرویس انتخاب‌شده و به‌شکل محدود دریافت می‌شود؛ داده خام ذخیره نخواهد شد.</p>
      </aside>
    </div>
  );
}


function ResourceState({ state, loading, empty, onRetry }: {
  state: LoadState;
  loading: string;
  empty: string;
  onRetry?: () => void;
}) {
  if (state === "loading") return <p className="status" role="status">{loading}</p>;
  if (state === "empty") return <p className="status">{empty}</p>;
  if (state === "error") return (
    <div>
      <p className="status error" role="alert">دریافت اطلاعات ناموفق بود؛ دوباره تلاش کنید.</p>
      {onRetry && <button className="retry" onClick={onRetry}>تلاش دوباره</button>}
    </div>
  );
  return null;
}
