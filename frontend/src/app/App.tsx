import { useEffect, useState } from "react";

import "../styles/global.css";
import {
  createSession,
  listApps,
  listPlatforms,
  listServices,
  submitTicket,
  submitTurn,
  type AppSummary,
  type Platform,
  type ServiceSummary,
} from "../api/client";
import type { TerminalResult } from "../api/events";


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
  const [csrfToken, setCsrfToken] = useState("");
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [platform, setPlatform] = useState<Platform["id"] | "">("");
  const [apps, setApps] = useState<AppSummary[]>([]);
  const [selectedApp, setSelectedApp] = useState<AppSummary | null>(null);
  const [services, setServices] = useState<ServiceSummary[]>([]);
  const [selectedService, setSelectedService] = useState<ServiceSummary | null>(null);
  const [platformState, setPlatformState] = useState<LoadState>("idle");
  const [appState, setAppState] = useState<LoadState>("idle");
  const [serviceState, setServiceState] = useState<LoadState>("idle");
  const [problem, setProblem] = useState("");
  const [turnState, setTurnState] = useState<LoadState>("idle");
  const [result, setResult] = useState<TerminalResult | null>(null);
  const [ticketTopic, setTicketTopic] = useState<Topic>("other");
  const [ticketSubject, setTicketSubject] = useState("");
  const [ticketDescription, setTicketDescription] = useState("");
  const [handoffSummary, setHandoffSummary] = useState("");
  const [ticketState, setTicketState] = useState<LoadState>("idle");
  const [ticketRef, setTicketRef] = useState("");

  useEffect(() => {
    void createSession()
      .then((token) => {
        setCsrfToken(token);
        setSessionReady(true);
      })
      .catch(() => setSessionReady(false));
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
    setResult(null);
    setTurnState("idle");
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

  const runAgent = async () => {
    if (!topic || !csrfToken || !problem.trim()) return;
    setTurnState("loading");
    setResult(null);
    try {
      const terminal = await submitTurn(topic, problem.trim(), csrfToken, selectedService?.ref);
      setResult(terminal);
      setTurnState("ready");
    } catch {
      setTurnState("error");
    }
  };

  const sendTicket = async () => {
    if (!csrfToken) return;
    setTicketState("loading");
    try {
      const response = await submitTicket({
        topic: ticketTopic,
        subject: ticketSubject.trim(),
        description: ticketDescription.trim(),
        handoffSummary: handoffSummary || undefined,
      }, csrfToken);
      setTicketRef(response.ticket_ref);
      setTicketState("ready");
    } catch {
      setTicketState("error");
    }
  };

  const handoffToTicket = () => {
    if (!result) return;
    const summary = result.claims.map((claim) => claim.text).join("\n").slice(0, 1500);
    setTicketTopic(topic ?? "other");
    setTicketSubject("ادامه بررسی توسط تیم پشتیبانی");
    setTicketDescription("پاسخ دستیار مسئله را به‌طور کامل حل نکرد؛ لطفاً بررسی را ادامه دهید.");
    setHandoffSummary(summary);
    setMode("ticket");
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
            {ticketState === "ready" ? (
              <div className="ticket-success" role="status">
                <strong>تیکت آزمایشی ثبت شد.</strong>
                <span dir="ltr">{ticketRef}</span>
                <p>در MVP این ثبت mock است و به سامانه واقعی پشتیبانی ارسال نشده است.</p>
              </div>
            ) : (
              <form className="ticket-form" onSubmit={(event) => { event.preventDefault(); void sendTicket(); }}>
                <div className="field">
                  <label htmlFor="ticket-topic">موضوع</label>
                  <select id="ticket-topic" value={ticketTopic} onChange={(event) => setTicketTopic(event.target.value as Topic)}>
                    {topics.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="ticket-subject">عنوان تیکت</label>
                  <input id="ticket-subject" value={ticketSubject} minLength={10} maxLength={120} required onChange={(event) => setTicketSubject(event.target.value)} />
                </div>
                <div className="field">
                  <label htmlFor="ticket-description">شرح مسئله</label>
                  <textarea id="ticket-description" value={ticketDescription} minLength={20} maxLength={2000} required onChange={(event) => setTicketDescription(event.target.value)} />
                </div>
                {handoffSummary && <div className="handoff-preview"><strong>خلاصه امن دستیار</strong><p>{handoffSummary}</p></div>}
                <p className="privacy-note">Token، password، connection string و لاگ خام را در تیکت وارد نکنید.</p>
                {ticketState === "error" && <p className="status error" role="alert">ثبت تیکت ناموفق بود؛ متن شما حفظ شده است.</p>}
                <button className="primary" disabled={ticketState === "loading"}>{ticketState === "loading" ? "در حال ثبت…" : "ثبت تیکت آزمایشی"}</button>
              </form>
            )}
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

            <form className="composer" onSubmit={(event) => { event.preventDefault(); void runAgent(); }}>
              {selectedService && <p className="selection-note">سرویس انتخاب‌شده: {selectedService.name}</p>}
              {selectedService && <p className="log-use-note">با هر بررسی، حداکثر ۱۰۰ خط آخر لاگ تازه دریافت، پاک‌سازی و فقط برای همین پاسخ استفاده می‌شود.</p>}
              <label htmlFor="problem">شرح مسئله</label>
              <textarea id="problem" value={problem} onChange={(event) => setProblem(event.target.value)} disabled={topic === "paas" && !selectedService} placeholder="خطا، رفتار مشاهده‌شده و نتیجه‌ای که انتظار داشتید را بنویسید." />
              <button className="primary" disabled={!topic || !problem.trim() || turnState === "loading" || (topic === "paas" && !selectedService)}>{turnState === "loading" ? "در حال بررسی…" : "شروع بررسی"}</button>
              <div aria-live="polite">
                {turnState === "error" && <p className="status error">ارتباط با دستیار ناموفق بود؛ متن شما حفظ شده است.</p>}
              </div>
            </form>

            {result && (
              <section className={`agent-result ${result.status}`} aria-label="پاسخ دستیار">
                <h2 className="section-title">{result.status === "answer" ? "پاسخ مستند" : result.status === "clarification" ? "جزئیات بیشتری لازم است" : "پاسخ قطعی پیدا نشد"}</h2>
                {result.message && <p>{result.message}</p>}
                {result.claims.map((claim) => (
                  <article className="claim" key={`${claim.citation.chunk_id}-${claim.text}`}>
                    <p>{claim.text}</p>
                    <a href={claim.citation.url} target="_blank" rel="noreferrer">[{claim.citation.title} — {claim.citation.heading}]</a>
                    <blockquote>{claim.citation.evidence}</blockquote>
                  </article>
                ))}
                <button className="retry" onClick={handoffToTicket}>ادامه با تیکت پشتیبانی</button>
              </section>
            )}
          </section>
        )}
      </main>

      <aside className="side-panel evidence-panel" aria-label="منابع پاسخ">
        <h2 className="evidence-title">زمینه و منابع</h2>
        {result?.claims.length ? result.claims.map((claim, index) => (
          <a className="source-link" href={claim.citation.url} target="_blank" rel="noreferrer" key={claim.citation.chunk_id}>[{index + 1}] {claim.citation.title}</a>
        )) : <p className="evidence-copy">Citationها و شواهد پاسخ در این بخش نمایش داده می‌شوند.</p>}
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
