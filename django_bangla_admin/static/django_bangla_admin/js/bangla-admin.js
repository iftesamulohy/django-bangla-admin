/* django-bangla-admin — shell behavior: theme, language, sidebar, HTMX wiring.
 * No framework dependency beyond HTMX (+ optional Alpine for niceties).
 * Vanilla so it works even if Alpine fails to load. */
(function () {
  "use strict";

  var THEME_KEY = "ba-theme";
  var COLLAPSE_KEY = "ba-sidebar-collapsed";
  var root = document.documentElement;

  /* ---- Theme ----------------------------------------------------------- */
  function applyTheme(theme) {
    root.setAttribute("data-ba-theme", theme);
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) {}
    document.cookie = "ba_theme=" + theme + ";path=/;max-age=31536000;samesite=Lax";
    document.dispatchEvent(new CustomEvent("ba:theme-changed", { detail: { theme: theme } }));
  }
  function toggleTheme() {
    var cur = root.getAttribute("data-ba-theme") === "light" ? "light" : "dark";
    applyTheme(cur === "light" ? "dark" : "light");
  }
  // Honor stored preference early (server already set initial from cookie).
  try {
    var stored = localStorage.getItem(THEME_KEY);
    if (stored && stored !== root.getAttribute("data-ba-theme")) {
      root.setAttribute("data-ba-theme", stored);
    }
  } catch (e) {}

  /* ---- Sidebar collapse / mobile drawer -------------------------------- */
  function shell() { return document.querySelector(".ba-shell"); }
  function toggleCollapse() {
    var s = shell(); if (!s) return;
    s.classList.toggle("is-collapsed");
    try { localStorage.setItem(COLLAPSE_KEY, s.classList.contains("is-collapsed") ? "1" : "0"); } catch (e) {}
  }
  function toggleDrawer() {
    var s = shell(); if (s) s.classList.toggle("is-drawer-open");
  }
  function closeDrawer() {
    var s = shell(); if (s) s.classList.remove("is-drawer-open");
  }
  try {
    if (localStorage.getItem(COLLAPSE_KEY) === "1") {
      document.addEventListener("DOMContentLoaded", function () {
        var s = shell(); if (s) s.classList.add("is-collapsed");
      });
    }
  } catch (e) {}

  /* ---- Active nav state on SPA swap ------------------------------------ */
  function syncActiveNav(url) {
    var path = url || window.location.pathname;
    document.querySelectorAll("a.ba-nav-item").forEach(function (a) {
      var href = a.getAttribute("href");
      if (!href || href === "#") return;
      var active = href === "/" ? path === "/" : path.indexOf(href) === 0;
      a.classList.toggle("active", active);
      // Expand the parent tree group that owns the active child link.
      if (active && a.classList.contains("ba-nav-child")) {
        var group = a.closest("[data-ba-tree]");
        if (group) group.classList.add("is-open");
      }
    });
  }

  /* ---- Sidebar tree (collapsible app -> model groups) ------------------ */
  function toggleTree(btn) {
    var group = btn.closest("[data-ba-tree]");
    if (!group) return;
    var open = group.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  }
  // Reflect server-rendered open state onto aria-expanded at load.
  function syncTreeAria() {
    document.querySelectorAll("[data-ba-tree]").forEach(function (g) {
      var btn = g.querySelector(".ba-nav-parent");
      if (btn) btn.setAttribute("aria-expanded", g.classList.contains("is-open") ? "true" : "false");
    });
  }

  /* ---- Global click delegation ----------------------------------------- */
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-ba-action]");
    if (!t) return;
    var action = t.getAttribute("data-ba-action");
    if (action === "toggle-theme") { e.preventDefault(); toggleTheme(); }
    else if (action === "toggle-collapse") { e.preventDefault(); toggleCollapse(); }
    else if (action === "toggle-drawer") { e.preventDefault(); toggleDrawer(); }
    else if (action === "close-drawer") { e.preventDefault(); closeDrawer(); }
    else if (action === "toggle-tree") { e.preventDefault(); toggleTree(t); }
  });

  /* ---- ⌘K / Ctrl-K focuses search -------------------------------------- */
  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      var input = document.querySelector(".ba-search input");
      if (input) { e.preventDefault(); input.focus(); }
    }
  });

  /* ---- HTMX integration ------------------------------------------------ */
  document.addEventListener("DOMContentLoaded", function () {
    if (window.htmx) {
      // Send theme + drawer behavior signals if needed later; close drawer on nav.
      document.body.addEventListener("htmx:afterSwap", function (evt) {
        closeDrawer();
        var cur = evt.detail && evt.detail.xhr && evt.detail.xhr.getResponseHeader
          ? evt.detail.xhr.getResponseHeader("HX-Current-URL") : null;
        syncActiveNav(cur);
        if (window.BaCharts) window.BaCharts.initAll();
      });
    }
    syncActiveNav();
    syncTreeAria();
    if (window.BaCharts) window.BaCharts.initAll();
  });

  // Re-color charts when the theme flips.
  document.addEventListener("ba:theme-changed", function () {
    if (window.BaCharts) window.BaCharts.recolorAll();
  });

  window.BanglaAdmin = {
    toggleTheme: toggleTheme,
    applyTheme: applyTheme,
    toggleCollapse: toggleCollapse,
    toggleDrawer: toggleDrawer,
    syncActiveNav: syncActiveNav,
  };
})();
