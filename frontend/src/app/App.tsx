import { useEffect, useState } from "react";
import {
  GoBook,
  GoCheckCircleFill,
  GoCommentDiscussion,
  GoHistory,
  GoLock,
  GoPlus,
  GoSearch,
  GoShieldCheck,
  GoWorkflow,
} from "react-icons/go";
import {
  SiAngular,
  SiDjango,
  SiDocker,
  SiDotnet,
  SiFlask,
  SiGo,
  SiHtml5,
  SiLaravel,
  SiNextdotjs,
  SiNodedotjs,
  SiPhp,
  SiPython,
  SiReact,
  SiVuedotjs,
} from "react-icons/si";
import type { IconType } from "react-icons";

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
  type PlatformId,
  type ServiceSummary,
} from "../api/client";

import type { TerminalResult } from "../api/events";

type Mode = "agent" | "ticket";

type Topic =
  | "paas"
  | "cdn"
  | "ssl"
  | "dns"
  | "other";

type LoadState =
  | "idle"
  | "loading"
  | "ready"
  | "empty"
  | "error";

const topics: Array<{ id: Topic; label: string }> = [
  { id: "paas", label: "PaaS" },
  { id: "cdn", label: "CDN" },
  { id: "ssl", label: "SSL" },
  { id: "dns", label: "DNS" },
  { id: "other", label: "سایر" },
];

const platformIcons: Record<PlatformId, IconType> = {
  angular: SiAngular,
  django: SiDjango,
  docker: SiDocker,
  dotnet: SiDotnet,
  flask: SiFlask,
  go: SiGo,
  laravel: SiLaravel,
  nextjs: SiNextdotjs,
  nodejs: SiNodedotjs,
  php: SiPhp,
  python: SiPython,
  react: SiReact,
  static: SiHtml5,
  vue: SiVuedotjs,
};

export function App() {
  const [mode, setMode] = useState<Mode>("agent");

  const [topic, setTopic] = useState<Topic | null>(null);

  const [sessionReady, setSessionReady] = useState(false);
  const [csrfToken, setCsrfToken] = useState("");

  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [platform, setPlatform] =
    useState<Platform["id"] | "">("");

  const [platformQuery, setPlatformQuery] = useState("");

  const [apps, setApps] = useState<AppSummary[]>([]);
  const [selectedApp, setSelectedApp] =
    useState<AppSummary | null>(null);

  const [services, setServices] =
    useState<ServiceSummary[]>([]);
  const [selectedService, setSelectedService] =
    useState<ServiceSummary | null>(null);

  const [platformState, setPlatformState] =
    useState<LoadState>("idle");

  const [appState, setAppState] =
    useState<LoadState>("idle");

  const [serviceState, setServiceState] =
    useState<LoadState>("idle");

  const [problem, setProblem] = useState("");

  const [turnState, setTurnState] =
    useState<LoadState>("idle");

  const [result, setResult] =
    useState<TerminalResult | null>(null);

  const [ticketTopic, setTicketTopic] =
    useState<Topic>("other");

  const [ticketSubject, setTicketSubject] =
    useState("");

  const [ticketDescription, setTicketDescription] =
    useState("");

  const [handoffSummary, setHandoffSummary] =
    useState("");

  const [ticketState, setTicketState] =
    useState<LoadState>("idle");

  const [ticketRef, setTicketRef] =
    useState("");

  /*
   * Create secure session
   */
  useEffect(() => {
    void createSession()
      .then((token) => {
        setCsrfToken(token);
        setSessionReady(true);
      })
      .catch(() => {
        setSessionReady(false);
      });
  }, []);

  /*
   * Load PaaS platforms
   */
  useEffect(() => {
    if (
      topic !== "paas" ||
      !sessionReady ||
      platformState !== "idle"
    ) {
      return;
    }

    setPlatformState("loading");

    void listPlatforms()
      .then((items) => {
        setPlatforms(items);
        setPlatformState(
          items.length ? "ready" : "empty",
        );
      })
      .catch(() => {
        setPlatformState("error");
      });
  }, [platformState, sessionReady, topic]);

  /*
   * Select topic
   */
  const chooseTopic = (nextTopic: Topic) => {
    setTopic(nextTopic);

    setPlatform("");
    setPlatformQuery("");

    setApps([]);
    setSelectedApp(null);

    setServices([]);
    setSelectedService(null);

    setAppState("idle");
    setServiceState("idle");

    setResult(null);
    setTurnState("idle");
  };

  /*
   * Start a new conversation
   */
  const startNewConversation = () => {
    setMode("agent");

    setTopic(null);

    setPlatform("");
    setPlatformQuery("");

    setApps([]);
    setSelectedApp(null);

    setServices([]);
    setSelectedService(null);

    setAppState("idle");
    setServiceState("idle");

    setProblem("");

    setResult(null);
    setTurnState("idle");
  };

  /*
   * Select platform
   */
  const choosePlatform = async (
    nextPlatform: Platform["id"] | "",
  ) => {
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

      setAppState(
        items.length ? "ready" : "empty",
      );
    } catch {
      setAppState("error");
    }
  };

  /*
   * Select app
   */
  const chooseApp = async (app: AppSummary) => {
    setSelectedApp(app);

    setServices([]);
    setSelectedService(null);

    setServiceState("loading");

    try {
      const items = await listServices(app.ref);

      setServices(items);

      setServiceState(
        items.length ? "ready" : "empty",
      );
    } catch {
      setServiceState("error");
    }
  };

  /*
   * Run AI agent
   */
  const runAgent = async () => {
    if (
      !topic ||
      !csrfToken ||
      !problem.trim()
    ) {
      return;
    }

    setTurnState("loading");
    setResult(null);

    try {
      const terminal = await submitTurn(
        topic,
        problem.trim(),
        csrfToken,
        selectedService?.ref,
      );

      setResult(terminal);
      setTurnState("ready");
    } catch {
      setTurnState("error");
    }
  };

  /*
   * Submit support ticket
   */
  const sendTicket = async () => {
    if (!csrfToken) {
      return;
    }

    setTicketState("loading");

    try {
      const response = await submitTicket(
        {
          topic: ticketTopic,
          subject: ticketSubject.trim(),
          description: ticketDescription.trim(),
          handoffSummary:
            handoffSummary || undefined,
        },
        csrfToken,
      );

      setTicketRef(response.ticket_ref);
      setTicketState("ready");
    } catch {
      setTicketState("error");
    }
  };

  /*
   * Handoff agent result to ticket
   */
  const handoffToTicket = () => {
    if (!result) {
      return;
    }

    const summary = result.claims
      .map((claim) => claim.text)
      .join("\n")
      .slice(0, 1500);

    setTicketTopic(topic ?? "other");

    setTicketSubject(
      "ادامه بررسی توسط تیم پشتیبانی",
    );

    setTicketDescription(
      "پاسخ دستیار مسئله را به‌طور کامل حل نکرد؛ لطفاً بررسی را ادامه دهید.",
    );

    setHandoffSummary(summary);

    setMode("ticket");
  };

  const normalizedPlatformQuery =
    platformQuery
      .trim()
      .toLocaleLowerCase("fa");

  const filteredPlatforms =
    platforms.filter((item) =>
      `${item.label} ${item.id}`
        .toLocaleLowerCase("fa")
        .includes(normalizedPlatformQuery),
    );

  return (
    <div
      className="app-shell"
      dir="rtl"
      lang="fa"
    >
      <a
        className="skip-link"
        href="#main-content"
      >
        رفتن به محتوای اصلی
      </a>

      {/* =========================
          SIDEBAR
         ========================= */}

      <nav
        className="side-panel navigation"
        aria-label="ناوبری اصلی"
      >
        <div className="brand">
          <span
            className="brand-mark"
            aria-hidden="true"
          >
            <GoWorkflow />
          </span>

          <span className="brand-copy">
            <strong>Liara</strong>
            <small>Navigator</small>
          </span>
        </div>

        <div className="nav-group">
          <p className="nav-group-label">
            فضای کار
          </p>

          <button
            className="nav-item active"
            onClick={startNewConversation}
          >
            <GoPlus aria-hidden="true" />

            <span className="nav-label">
              گفت‌وگوی جدید
            </span>

            <span
              className="nav-shortcut"
              aria-hidden="true"
            >
              +
            </span>
          </button>

          <button
            className="nav-item"
            disabled
            title="در نسخه بعدی فعال می‌شود"
          >
            <GoHistory aria-hidden="true" />

            <span className="nav-label">
              تاریخچه
            </span>

            <span className="nav-badge">
              به‌زودی
            </span>
          </button>

          <a
            className="nav-item"
            href="https://docs.liara.ir/"
            target="_blank"
            rel="noreferrer"
          >
            <GoBook aria-hidden="true" />

            <span className="nav-label">
              مستندات لیارا
            </span>
          </a>
        </div>

        <div className="nav-trust">
          <GoShieldCheck aria-hidden="true" />

          <span className="nav-label">
            <strong>حریم خصوصی فعال</strong>
            <small>بدون ذخیره لاگ خام</small>
          </span>
        </div>
      </nav>

      {/* =========================
          MAIN
         ========================= */}

      <main
        id="main-content"
        className="workspace"
      >
        <div className="mobile-appbar">
          <span
            className="brand-mark"
            aria-hidden="true"
          >
            <GoWorkflow />
          </span>

          <strong>Liara Navigator</strong>

          <button
            className="icon-button"
            onClick={startNewConversation}
            aria-label="گفت‌وگوی جدید"
          >
            <GoPlus />
          </button>
        </div>

        {/* Header */}

        <header className="workspace-header">
          <div className="context-bar">
            <span className="context-chip">
              <GoLock aria-hidden="true" />
              نشست امن
            </span>

            <span
              className={`session-state ${
                sessionReady
                  ? "online"
                  : "connecting"
              }`}
            >
              <span aria-hidden="true" />

              {sessionReady
                ? "آماده پاسخ‌گویی"
                : "در حال اتصال"}
            </span>
          </div>

          <p className="eyebrow">
            دستیار فنی لیارا
          </p>

          <h1>
            مسئله را انتخاب کن؛ با شواهد حلش می‌کنیم.
          </h1>

          <p className="lede">
            برای پاسخ سریع از دستیار هوشمند کمک بگیر
            یا مسئله را مستقیم برای تیم پشتیبانی
            ثبت کن.
          </p>
        </header>

        {/* Mode picker */}

        <section
          className="mode-picker"
          aria-labelledby="support-path-label"
        >
          <p
            id="support-path-label"
            className="field-label"
          >
            مسیر دریافت کمک
          </p>

          <div
            className="mode-tabs"
            role="tablist"
            aria-label="نوع درخواست"
          >
            <button
              aria-label="دستیار هوشمند"
              role="tab"
              aria-selected={
                mode === "agent"
              }
              className="mode-tab"
              onClick={() =>
                setMode("agent")
              }
            >
              <span
                className="mode-icon"
                aria-hidden="true"
              >
                <GoWorkflow />
              </span>

              <span>
                <strong>
                  دستیار هوشمند
                </strong>

                <small>
                  بررسی مرحله‌ای با منابع رسمی
                </small>
              </span>

              {mode === "agent" && (
                <GoCheckCircleFill
                  className="selected-check"
                  aria-hidden="true"
                />
              )}
            </button>

            <button
              aria-label="تیکت پشتیبانی"
              role="tab"
              aria-selected={
                mode === "ticket"
              }
              className="mode-tab"
              onClick={() =>
                setMode("ticket")
              }
            >
              <span
                className="mode-icon"
                aria-hidden="true"
              >
                <GoCommentDiscussion />
              </span>

              <span>
                <strong>
                  تیکت پشتیبانی
                </strong>

                <small>
                  ارجاع مستقیم برای بررسی انسانی
                </small>
              </span>

              {mode === "ticket" && (
                <GoCheckCircleFill
                  className="selected-check"
                  aria-hidden="true"
                />
              )}
            </button>
          </div>
        </section>

        {/* =========================
            TICKET MODE
           ========================= */}

        {mode === "ticket" ? (
          <section className="workflow">
            <div className="section-heading">
              <span className="step-kicker">
                تیکت پشتیبانی
              </span>

              <h2 className="section-title">
                جزئیات مسئله را ثبت کنید
              </h2>

              <p>
                اطلاعات ضروری را بنویسید؛ متن شما
                در صورت خطا حفظ می‌شود.
              </p>
            </div>

            {ticketState === "ready" ? (
              <div
                className="ticket-success"
                role="status"
              >
                <strong>
                  تیکت آزمایشی ثبت شد.
                </strong>

                <span dir="ltr">
                  {ticketRef}
                </span>

                <p>
                  در MVP این ثبت mock است و به
                  سامانه واقعی پشتیبانی ارسال نشده
                  است.
                </p>
              </div>
            ) : (
              <form
                className="ticket-form"
                onSubmit={(event) => {
                  event.preventDefault();
                  void sendTicket();
                }}
              >
                <div className="field">
                  <label htmlFor="ticket-topic">
                    موضوع
                  </label>

                  <select
                    id="ticket-topic"
                    value={ticketTopic}
                    onChange={(event) =>
                      setTicketTopic(
                        event.target.value as Topic,
                      )
                    }
                  >
                    {topics.map((item) => (
                      <option
                        key={item.id}
                        value={item.id}
                      >
                        {item.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="field">
                  <label htmlFor="ticket-subject">
                    عنوان تیکت
                  </label>

                  <input
                    id="ticket-subject"
                    value={ticketSubject}
                    minLength={10}
                    maxLength={120}
                    required
                    onChange={(event) =>
                      setTicketSubject(
                        event.target.value,
                      )
                    }
                  />
                </div>

                <div className="field">
                  <label htmlFor="ticket-description">
                    شرح مسئله
                  </label>

                  <textarea
                    id="ticket-description"
                    value={ticketDescription}
                    minLength={20}
                    maxLength={2000}
                    required
                    onChange={(event) =>
                      setTicketDescription(
                        event.target.value,
                      )
                    }
                  />
                </div>

                {handoffSummary && (
                  <div className="handoff-preview">
                    <strong>
                      خلاصه امن دستیار
                    </strong>

                    <p>
                      {handoffSummary}
                    </p>
                  </div>
                )}

                <p className="privacy-note">
                  Token، password، connection string
                  و لاگ خام را در تیکت وارد نکنید.
                </p>

                {ticketState === "error" && (
                  <p
                    className="status error"
                    role="alert"
                  >
                    ثبت تیکت ناموفق بود؛ متن شما
                    حفظ شده است.
                  </p>
                )}

                <button
                  className="primary"
                  disabled={
                    ticketState === "loading"
                  }
                >
                  {ticketState === "loading"
                    ? "در حال ثبت…"
                    : "ثبت تیکت آزمایشی"}
                </button>
              </form>
            )}
          </section>
        ) : (
          /* =========================
             AGENT MODE
             ========================= */

          <section className="workflow">
            <div className="section-heading">
              <span className="step-kicker">
                مرحله ۱ از ۳
              </span>

              <h2 className="section-title">
                مشکل مربوط به کدام بخش است؟
              </h2>

              <p>
                موضوع را مشخص کنید تا فقط اطلاعات
                مرتبط وارد فرآیند بررسی شود.
              </p>
            </div>

            {/* Topic */}

            <fieldset
              className="topic-grid"
              aria-label="موضوع مشکل"
            >
              {topics.map((item) => (
                <label
                  className="topic-option"
                  key={item.id}
                >
                  <input
                    type="radio"
                    name="topic"
                    value={item.id}
                    checked={
                      topic === item.id
                    }
                    onChange={() =>
                      chooseTopic(item.id)
                    }
                  />

                  <span>
                    {item.label}
                  </span>
                </label>
              ))}
            </fieldset>

            {/* PaaS selectors */}

            {topic === "paas" ? (
              <div className="selector-stack">
                <div className="optional-context-note">
                  <GoShieldCheck aria-hidden="true" />

                  <div>
                    <strong>
                      انتخاب سرویس اختیاری است
                    </strong>

                    <p>
                      بدون سرویس، پاسخ از مستندات
                      رسمی ارائه می‌شود؛ با انتخاب
                      سرویس، لاگ‌های پاک‌سازی‌شده
                      نیز به بررسی کمک می‌کنند.
                    </p>
                  </div>

                  <a href="#problem">
                    ادامه بدون سرویس
                  </a>
                </div>

                {/* Platforms */}

                <div className="platform-picker">
                  <div className="picker-heading">
                    <div>
                      <span className="step-kicker">
                        مرحله ۲ از ۳
                      </span>

                      <h3>
                        پلتفرم برنامه را انتخاب کنید
                      </h3>
                    </div>

                    <span className="result-count">
                      {platforms.length || 14}{" "}
                      پلتفرم رسمی
                    </span>
                  </div>

                  {platformState ===
                  "loading" ? (
                    <p
                      className="status"
                      role="status"
                    >
                      در حال دریافت پلتفرم‌ها…
                    </p>
                  ) : (
                    <>
                      <label className="search-control">
                        <GoSearch aria-hidden="true" />

                        <span className="sr-only">
                          جست‌وجوی پلتفرم
                        </span>

                        <input
                          type="search"
                          value={platformQuery}
                          onChange={(event) =>
                            setPlatformQuery(
                              event.target.value,
                            )
                          }
                          placeholder="جست‌وجو میان Django، Node.js، Docker و…"
                        />
                      </label>

                      <fieldset
                        className="platform-grid"
                        aria-label="نوع پلتفرم"
                      >
                        {filteredPlatforms.map(
                          (item) => (
                            <label
                              className={`platform-option ${
                                platform === item.id
                                  ? "selected"
                                  : ""
                              }`}
                              key={item.id}
                            >
                              <input
                                aria-label={
                                  item.label
                                }
                                type="radio"
                                name="platform"
                                value={item.id}
                                checked={
                                  platform ===
                                  item.id
                                }
                                onChange={() =>
                                  void choosePlatform(
                                    item.id,
                                  )
                                }
                              />

                              <span
                                className="platform-logo"
                                aria-hidden="true"
                              >
                                <PlatformLogo
                                  platform={
                                    item.id
                                  }
                                />
                              </span>

                              <span
                                className="platform-name"
                                dir="ltr"
                              >
                                {item.label}
                              </span>

                              {platform ===
                                item.id && (
                                <GoCheckCircleFill
                                  className="platform-check"
                                  aria-hidden="true"
                                />
                              )}
                            </label>
                          ),
                        )}
                      </fieldset>

                      {!filteredPlatforms.length && (
                        <div className="empty-state">
                          <strong>
                            پلتفرمی پیدا نشد.
                          </strong>

                          <p>
                            عبارت جست‌وجو را تغییر
                            دهید.
                          </p>

                          <button
                            className="retry"
                            onClick={() =>
                              setPlatformQuery("")
                            }
                          >
                            پاک‌کردن جست‌وجو
                          </button>
                        </div>
                      )}
                    </>
                  )}

                  {platformState === "error" && (
                    <button
                      className="retry"
                      onClick={() =>
                        setPlatformState("idle")
                      }
                    >
                      تلاش دوباره
                    </button>
                  )}
                </div>

                {/* Apps */}

                {appState !== "idle" && (
                  <ResourceState
                    state={appState}
                    loading="در حال دریافت برنامه‌ها…"
                    empty="برنامه‌ای برای این پلتفرم وجود ندارد."
                    onRetry={() =>
                      void choosePlatform(platform)
                    }
                  />
                )}

                {apps.length > 0 && (
                  <div className="resource-section">
                    <div className="picker-heading">
                      <div>
                        <span className="step-kicker">
                          مرحله ۳ از ۳
                        </span>

                        <h3>
                          برنامه و سرویس درگیر را
                          انتخاب کنید
                        </h3>
                      </div>
                    </div>

                    <p className="field-label">
                      برنامه‌های شما روی{" "}
                      {
                        platforms.find(
                          (item) =>
                            item.id === platform,
                        )?.label
                      }
                    </p>

                    <div className="resource-grid">
                      {apps.map((app) => (
                        <button
                          key={app.ref}
                          className={`resource-card ${
                            selectedApp?.ref ===
                            app.ref
                              ? "selected"
                              : ""
                          }`}
                          onClick={() =>
                            void chooseApp(app)
                          }
                        >
                          <strong>
                            {app.name}
                          </strong>

                          <span className="resource-meta">
                            {app.platform} ·{" "}
                            {app.status}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Services */}

                {serviceState !== "idle" && (
                  <ResourceState
                    state={serviceState}
                    loading="در حال دریافت سرویس‌ها…"
                    empty="سرویسی برای این برنامه وجود ندارد."
                    onRetry={
                      selectedApp
                        ? () =>
                            void chooseApp(
                              selectedApp,
                            )
                        : undefined
                    }
                  />
                )}

                {services.length > 0 && (
                  <div className="resource-section service-section">
                    <p className="field-label">
                      انتخاب سرویس
                    </p>

                    <div className="resource-grid">
                      {services.map(
                        (service) => (
                          <button
                            key={service.ref}
                            className={`resource-card ${
                              selectedService?.ref ===
                              service.ref
                                ? "selected"
                                : ""
                            }`}
                            onClick={() =>
                              setSelectedService(
                                service,
                              )
                            }
                          >
                            <strong>
                              {service.name}
                            </strong>

                            <span className="resource-meta">
                              {service.kind} ·{" "}
                              {service.status}
                            </span>
                          </button>
                        ),
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : topic ? (
              <p className="status">
                این موضوع با مستندات رسمی لیارا
                بررسی می‌شود.
              </p>
            ) : null}

            {/* =========================
                MESSAGE COMPOSER
               ========================= */}

            <form
              className="composer"
              onSubmit={(event) => {
                event.preventDefault();
                void runAgent();
              }}
            >
              {selectedService && (
                <p className="selection-note">
                  سرویس انتخاب‌شده:{" "}
                  {selectedService.name}
                </p>
              )}

              {selectedService && (
                <p className="log-use-note">
                  با هر بررسی، حداکثر ۱۰۰ خط آخر
                  لاگ تازه دریافت، پاک‌سازی و فقط
                  برای همین پاسخ استفاده می‌شود.
                </p>
              )}

              <div className="composer-heading">
                <label htmlFor="problem">
                  شرح مسئله
                </label>

                <span>
                  پاسخ بر اساس منابع رسمی Liara
                </span>
              </div>

              <textarea
                id="problem"
                value={problem}
                onChange={(event) =>
                  setProblem(event.target.value)
                }
                placeholder="خطا، رفتار مشاهده‌شده و نتیجه‌ای که انتظار داشتید را بنویسید."
              />

              <button
                className="primary"
                disabled={
                  !topic ||
                  !problem.trim() ||
                  turnState === "loading"
                }
              >
                {turnState === "loading"
                  ? "در حال بررسی…"
                  : "شروع بررسی"}
              </button>

              <div aria-live="polite">
                {turnState === "error" && (
                  <p className="status error">
                    ارتباط با دستیار ناموفق بود؛
                    متن شما حفظ شده است.
                  </p>
                )}
              </div>
            </form>

            {/* =========================
                AGENT RESULT
               ========================= */}

            {result && (
              <section
                className={`agent-result ${result.status}`}
                aria-label="پاسخ دستیار"
              >
                <h2 className="section-title">
                  {result.status === "answer"
                    ? "پاسخ مستند"
                    : result.status ===
                        "clarification"
                      ? "جزئیات بیشتری لازم است"
                      : "پاسخ قطعی پیدا نشد"}
                </h2>

                {result.message && (
                  <p>{result.message}</p>
                )}

                {result.claims.map(
                  (claim, index) => (
                    <article
                      className="claim"
                      key={`${claim.chunk_id}-${index}-${claim.text}`}
                    >
                      <p>{claim.text}</p>

                      <div className="claim-source">
                        <span className="source-label">
                          منبع رسمی Liara
                        </span>

                        <span
                          className="source-id"
                          dir="ltr"
                        >
                          {claim.chunk_id}
                        </span>
                      </div>

                      {claim.evidence && (
                        <blockquote>
                          {claim.evidence}
                        </blockquote>
                      )}
                    </article>
                  ),
                )}

                {result.status === "answer" &&
                  result.claims.length > 0 && (
                    <button
                      className="retry"
                      onClick={
                        handoffToTicket
                      }
                    >
                      ادامه با تیکت پشتیبانی
                    </button>
                  )}
              </section>
            )}
          </section>
        )}
      </main>

      {/* =========================
          EVIDENCE PANEL
         ========================= */}

      <aside
        className="side-panel evidence-panel"
        aria-label="منابع پاسخ"
      >
        <h2 className="evidence-title">
          زمینه و منابع
        </h2>

        {result?.claims.length ? (
          result.claims.map(
            (claim, index) => (
              <div
                className="source-link"
                key={`${claim.chunk_id}-${index}`}
              >
                <span>
                  [{index + 1}] منبع رسمی Liara
                </span>

                <span
                  className="source-id"
                  dir="ltr"
                >
                  {claim.chunk_id}
                </span>
              </div>
            ),
          )
        ) : (
          <p className="evidence-copy">
            Citationها و شواهد پاسخ در این بخش
            نمایش داده می‌شوند.
          </p>
        )}

        <p className="privacy-note">
          لاگ فقط برای سرویس انتخاب‌شده و به‌شکل
          محدود دریافت می‌شود؛ داده خام ذخیره
          نخواهد شد.
        </p>
      </aside>
    </div>
  );
}

/*
 * Platform logo
 */
function PlatformLogo({
  platform,
}: {
  platform: PlatformId;
}) {
  const Logo = platformIcons[platform];

  return (
    <Logo
      focusable="false"
      aria-hidden="true"
    />
  );
}

/*
 * Generic resource loading state
 */
function ResourceState({
  state,
  loading,
  empty,
  onRetry,
}: {
  state: LoadState;
  loading: string;
  empty: string;
  onRetry?: () => void;
}) {
  if (state === "loading") {
    return (
      <p
        className="status"
        role="status"
      >
        {loading}
      </p>
    );
  }

  if (state === "empty") {
    return (
      <p className="status">
        {empty}
      </p>
    );
  }

  if (state === "error") {
    return (
      <div>
        <p
          className="status error"
          role="alert"
        >
          دریافت اطلاعات ناموفق بود؛ دوباره
          تلاش کنید.
        </p>

        {onRetry && (
          <button
            className="retry"
            onClick={onRetry}
          >
            تلاش دوباره
          </button>
        )}
      </div>
    );
  }

  return null;
}
