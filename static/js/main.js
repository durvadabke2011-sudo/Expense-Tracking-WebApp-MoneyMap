/**
 * MoneyMap – Global JS Utilities (Firebase Edition)
 * Exposes window.MM with fetch helpers, modal control, toast, formatting, theme.
 */
(function () {
  "use strict";

  // ── Currency formatter ──────────────────────────────────────────
  const formatCurrency = (amount, currency = "INR") => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency", currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  // ── Toast notifications ─────────────────────────────────────────
  let toastContainer = null;
  function ensureToastContainer() {
    if (!toastContainer) {
      toastContainer = document.createElement("div");
      toastContainer.id = "toast-container";
      document.body.appendChild(toastContainer);
    }
  }
  function toast(message, type = "success", duration = 3500) {
    ensureToastContainer();
    const icons = { success: "✅", error: "❌", warning: "⚠️", info: "ℹ️" };
    const el = document.createElement("div");
    el.className = `toast ${type}`;
    el.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${message}</span>`;
    toastContainer.appendChild(el);
    setTimeout(() => {
      el.style.animation = "toastIn .3s ease reverse";
      setTimeout(() => el.remove(), 300);
    }, duration);
  }

  // ── Modal helpers ───────────────────────────────────────────────
  function openModal(id) {
    const el = document.getElementById(id);
    if (el) { el.classList.add("open"); document.body.style.overflow = "hidden"; }
  }
  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) { el.classList.remove("open"); document.body.style.overflow = ""; }
  }
  // Close modals on overlay click
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal-overlay")) {
      closeModal(e.target.id);
    }
  });
  // Close on Escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay.open").forEach((m) => {
        closeModal(m.id);
      });
    }
  });

  // ── Theme (Dark / Light) ────────────────────────────────────────
  const THEME_KEY = "mm_theme";

  function themeGet() {
    return localStorage.getItem(THEME_KEY) || "light";
  }

  function themeSet(theme) {
    localStorage.setItem(THEME_KEY, theme);
    if (theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  }

  // Apply saved theme immediately on every page load
  themeSet(themeGet());

  // ── Fetch wrappers ──────────────────────────────────────────────
  async function apiFetch(url, options = {}) {
    try {
      const res = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });
      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || `HTTP ${res.status}`);
      }
      const ct = res.headers.get("Content-Type") || "";
      if (ct.includes("application/json")) return await res.json();
      return null;
    } catch (err) {
      toast(err.message || "Request failed", "error");
      throw err;
    }
  }
  const get   = (url)       => apiFetch(url);
  const post  = (url, body) => apiFetch(url, { method: "POST",   body: JSON.stringify(body) });
  const put   = (url, body) => apiFetch(url, { method: "PUT",    body: JSON.stringify(body) });
  const del   = (url)       => apiFetch(url, { method: "DELETE" });
  const patch = (url, body) => apiFetch(url, { method: "PATCH",  body: JSON.stringify(body) });

  // ── Report download helpers ─────────────────────────────────────
  function downloadReport(type, month) {
    const m = month || currentMonth();
    window.location.href = `/reports/${type}?month=${m}`;
  }

  // ── Month helpers ────────────────────────────────────────────────
  function currentMonth() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  }
  function monthLabel(m) {
    if (!m) return "";
    const [y, mo] = m.split("-");
    const d = new Date(parseInt(y), parseInt(mo) - 1, 1);
    return d.toLocaleDateString("en-IN", { month: "long", year: "numeric" });
  }

  // ── Chart colour defaults (theme-aware) ─────────────────────────
  function chartDefaults() {
    const dark = document.documentElement.getAttribute("data-theme") === "dark";
    return {
      gridColor:   dark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)",
      tickColor:   dark ? "#8b90a8"                : "#64748b",
      legendColor: dark ? "#e8eaf6"                : "#0f172a",
    };
  }

  // ── Loading skeleton ─────────────────────────────────────────────
  function showSkeleton(el, lines = 3) {
    if (!el) return;
    el.innerHTML = Array.from({ length: lines }, (_, i) =>
      `<div class="skeleton mb-1" style="height:${i === 0 ? 36 : 22}px;width:${90 - i * 10}%;border-radius:6px;margin-bottom:10px;"></div>`
    ).join("");
  }

  // ── Expose MM namespace ──────────────────────────────────────────
  window.MM = {
    fmt: formatCurrency,
    toast,
    openModal,
    closeModal,
    get, post, put, del, patch,
    downloadReport,
    currentMonth,
    monthLabel,
    showSkeleton,
    theme: {
      get: themeGet,
      set: themeSet,
    },
    chartDefaults,
  };
})();