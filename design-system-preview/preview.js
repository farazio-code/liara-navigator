(function (root) {
  const AGENT_STATES = [
    { key: 'idle', label: 'آماده' },
    { key: 'retrieving', label: 'در حال بررسی منابع رسمی' },
    { key: 'planning', label: 'در حال ساخت مسیر حل' },
    { key: 'guiding', label: 'مرحله جاری' },
    { key: 'validating', label: 'در حال بررسی نتیجه' },
    { key: 'complete', label: 'هدف تکمیل شد' },
  ];

  function nextTheme(theme) {
    return theme === 'dark' ? 'light' : 'dark';
  }

  function nextAgentState(current) {
    const index = AGENT_STATES.findIndex((state) => state.key === current);
    return AGENT_STATES[(index + 1 + AGENT_STATES.length) % AGENT_STATES.length];
  }

  function detectSecret(value) {
    const patterns = [
      /(?:api[_-]?key|token|password|secret)\s*[:=]\s*["']?[a-z0-9_\-.]{12,}/i,
      /\bliara_[a-z0-9]{12,}\b/i,
      /\bsk-[a-z0-9_-]{16,}\b/i,
    ];
    return patterns.some((pattern) => pattern.test(value));
  }

  function toggleSelection(activeId, selectedId) {
    return activeId === selectedId ? null : selectedId;
  }

  function initializePreview(documentRef) {
    const rootElement = documentRef.documentElement;
    const themeButton = documentRef.querySelector('[data-theme-toggle]');
    const stateButton = documentRef.querySelector('[data-state-cycle]');
    const agentStage = documentRef.querySelector('[data-agent-stage]');
    const stateLabel = documentRef.querySelector('[data-agent-label]');
    const composer = documentRef.querySelector('[data-composer]');
    const secretWarning = documentRef.querySelector('[data-secret-warning]');
    const modal = documentRef.querySelector('[data-modal]');
    const toast = documentRef.querySelector('[data-toast]');
    let activeSource = null;
    let toastTimer;

    function showToast(message) {
      if (!toast) return;
      toast.querySelector('[data-toast-message]').textContent = message;
      toast.hidden = false;
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => {
        toast.hidden = true;
      }, 4200);
    }

    function setTheme(theme) {
      rootElement.dataset.theme = theme;
      if (themeButton) {
        themeButton.setAttribute('aria-pressed', String(theme === 'light'));
        themeButton.querySelector('[data-theme-label]').textContent =
          theme === 'dark' ? 'حالت روشن' : 'حالت تاریک';
      }
    }

    themeButton?.addEventListener('click', () => {
      setTheme(nextTheme(rootElement.dataset.theme));
    });

    stateButton?.addEventListener('click', () => {
      const state = nextAgentState(agentStage.dataset.agentStage);
      agentStage.dataset.agentStage = state.key;
      stateLabel.textContent = state.label;
      agentStage.setAttribute('aria-label', `وضعیت عامل: ${state.label}`);
    });

    composer?.addEventListener('input', () => {
      const hasSecret = detectSecret(composer.value);
      composer.setAttribute('aria-invalid', String(hasSecret));
      secretWarning.hidden = !hasSecret;
    });

    documentRef.querySelectorAll('[data-citation]').forEach((citation) => {
      citation.addEventListener('click', () => {
        const selectedId = citation.dataset.citation;
        activeSource = toggleSelection(activeSource, selectedId);
        documentRef.querySelectorAll('[data-citation]').forEach((item) => {
          item.setAttribute('aria-expanded', String(item.dataset.citation === activeSource));
        });
        documentRef.querySelectorAll('[data-source]').forEach((source) => {
          source.classList.toggle('is-active', source.dataset.source === activeSource);
        });
        if (activeSource && window.matchMedia('(max-width: 1279px)').matches) {
          documentRef.querySelector('[data-evidence-rail]')?.classList.add('is-open');
        }
      });
    });

    documentRef.querySelectorAll('[data-tab]').forEach((tab) => {
      tab.addEventListener('click', () => {
        const target = tab.dataset.tab;
        documentRef.querySelectorAll('[data-tab]').forEach((item) => {
          const selected = item === tab;
          item.setAttribute('aria-selected', String(selected));
          item.tabIndex = selected ? 0 : -1;
        });
        documentRef.querySelectorAll('[data-tab-panel]').forEach((panel) => {
          panel.hidden = panel.dataset.tabPanel !== target;
        });
      });
    });

    documentRef.querySelectorAll('[data-open-modal]').forEach((button) => {
      button.addEventListener('click', () => {
        modal.hidden = false;
        modal.querySelector('[data-close-modal]')?.focus();
      });
    });

    documentRef.querySelectorAll('[data-close-modal]').forEach((button) => {
      button.addEventListener('click', () => {
        modal.hidden = true;
      });
    });

    modal?.addEventListener('click', (event) => {
      if (event.target === modal) modal.hidden = true;
    });

    documentRef.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && modal && !modal.hidden) modal.hidden = true;
    });

    documentRef.querySelectorAll('[data-show-toast]').forEach((button) => {
      button.addEventListener('click', () => showToast('تنظیمات با موفقیت ذخیره شد.'));
    });

    documentRef.querySelectorAll('[data-copy-code]').forEach((button) => {
      button.addEventListener('click', async () => {
        const code = button.closest('.code-block').querySelector('code').textContent;
        try {
          await navigator.clipboard.writeText(code);
          showToast('کد در کلیپ‌بورد کپی شد.');
        } catch {
          showToast('امکان کپی خودکار وجود ندارد.');
        }
      });
    });

    documentRef.querySelector('[data-evidence-close]')?.addEventListener('click', () => {
      documentRef.querySelector('[data-evidence-rail]')?.classList.remove('is-open');
    });

    setTheme(rootElement.dataset.theme || 'dark');
  }

  const api = { nextTheme, nextAgentState, detectSecret, toggleSelection };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => initializePreview(document));
  }
  root.LiaraPreview = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
