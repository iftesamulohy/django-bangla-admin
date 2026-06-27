/* django-bangla-admin — Chart.js helpers with theme-aware palettes.
 * Charts read CSS custom properties so they recolor on theme toggle, fetch
 * JSON from staff-only endpoints, and survive HTMX SPA swaps. */
(function () {
  "use strict";

  var instances = {}; // canvasId -> { chart, kind, url, data }

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function palette() {
    var primary = cssVar("--ba-primary") || "#2DD4BF";
    return {
      primary: primary,
      text: cssVar("--ba-text") || "#E6EDF3",
      muted: cssVar("--ba-muted") || "#8B949E",
      grid: cssVar("--ba-border-soft") || "rgba(255,255,255,.06)",
      surface: cssVar("--ba-surface") || "#161B22",
      series: [
        primary,
        cssVar("--ba-info") || "#58A6FF",
        cssVar("--ba-warning") || "#D29922",
        cssVar("--ba-success") || "#3FB950",
        cssVar("--ba-danger") || "#F85149",
      ],
    };
  }

  // Bengali numerals for axis ticks when document language is Bangla.
  var BN = ["০", "১", "২", "৩", "৪", "৫", "৬", "৭", "৮", "৯"];
  function localizeNum(v) {
    if (document.documentElement.getAttribute("lang") !== "bn") return v;
    return String(v).replace(/[0-9]/g, function (d) { return BN[+d]; });
  }

  function hexToRgba(hex, a) {
    var m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!m) return hex;
    return "rgba(" + parseInt(m[1], 16) + "," + parseInt(m[2], 16) + "," + parseInt(m[3], 16) + "," + a + ")";
  }

  function buildConfig(kind, data, p) {
    var ds = (data.datasets || []).map(function (d, i) {
      var color = p.series[i % p.series.length];
      var base = { label: d.label || "", data: d.data || [] };
      if (kind === "line") {
        return Object.assign(base, {
          borderColor: color, backgroundColor: hexToRgba(color, 0.12),
          fill: true, tension: 0.38, pointRadius: 0, pointHoverRadius: 4,
          borderWidth: 2,
        });
      }
      if (kind === "bar") {
        return Object.assign(base, {
          backgroundColor: color, borderRadius: 6, maxBarThickness: 28,
        });
      }
      if (kind === "doughnut" || kind === "pie") {
        return Object.assign(base, {
          backgroundColor: p.series, borderColor: p.surface, borderWidth: 2,
        });
      }
      return Object.assign(base, { backgroundColor: color, borderColor: color });
    });

    var isRadial = kind === "doughnut" || kind === "pie";
    var scales = isRadial ? {} : {
      x: {
        grid: { color: p.grid, drawBorder: false },
        ticks: { color: p.muted, callback: function (v) { return localizeNum(this.getLabelForValue(v)); } },
      },
      y: {
        grid: { color: p.grid, drawBorder: false },
        ticks: { color: p.muted, callback: function (v) { return localizeNum(v); } },
      },
    };

    return {
      type: kind,
      data: { labels: data.labels || [], datasets: ds },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: isRadial ? "62%" : undefined,
        plugins: {
          legend: {
            display: isRadial,
            position: "bottom",
            labels: { color: p.text, usePointStyle: true, boxWidth: 8, padding: 16 },
          },
          tooltip: {
            backgroundColor: p.surface, titleColor: p.text, bodyColor: p.muted,
            borderColor: p.grid, borderWidth: 1, padding: 10,
          },
        },
        scales: scales,
      },
    };
  }

  function render(canvas, kind, data) {
    if (!window.Chart) return;
    var id = canvas.id;
    if (instances[id] && instances[id].chart) instances[id].chart.destroy();
    var cfg = buildConfig(kind, data, palette());
    instances[id] = { chart: new window.Chart(canvas, cfg), kind: kind, data: data, url: canvas.dataset.url };
  }

  function initCanvas(canvas) {
    if (!canvas || canvas.dataset.baInit === "1") {
      // Already initialized in this DOM; skip unless content was swapped.
    }
    var kind = canvas.dataset.kind || "line";
    var url = canvas.dataset.url;
    var inline = canvas.dataset.chartData;
    canvas.dataset.baInit = "1";
    if (inline) {
      try { render(canvas, kind, JSON.parse(inline)); return; } catch (e) {}
    }
    if (url) {
      fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(function (r) { return r.json(); })
        .then(function (data) { render(canvas, kind, data); })
        .catch(function () {});
    }
  }

  function initAll() {
    document.querySelectorAll("canvas[data-ba-chart]").forEach(function (c) {
      // Re-init if the canvas is fresh (post-swap canvases lose their chart).
      if (!instances[c.id] || !document.getElementById(c.id)) {
        delete c.dataset.baInit;
      }
      initCanvas(c);
    });
  }

  function recolorAll() {
    Object.keys(instances).forEach(function (id) {
      var entry = instances[id];
      var canvas = document.getElementById(id);
      if (canvas && entry) render(canvas, entry.kind, entry.data);
    });
  }

  document.addEventListener("ba:lang-changed", recolorAll);

  window.BaCharts = { initAll: initAll, recolorAll: recolorAll, render: render };
})();
