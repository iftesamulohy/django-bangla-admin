# Changelog

## 0.2.0

### Added
- **Settings-driven charts & KPIs.** Declare `charts` and `stat_cards` in
  `BANGLA_ADMIN` with `model`, `group_by` (incl. relation `__` traversal and
  date `trunc` buckets), `aggregate` (count/sum/avg/min/max), `field`,
  `filters`, `limit`, `kind`, and `size` — the ORM query runs for you, no
  Python required. Field `choices` are humanized to their display labels;
  Decimal sums are coerced to numbers.
- `?chart=<id>` mode on the chart-data endpoint that resolves declarative
  charts against the ORM.

## 0.1.0

- Initial release: drop-in themed `BanglaAdminSite`, config-driven design
  system, dark/light themes, HTMX SPA navigation with shell-stripping
  middleware, Bangla ⇄ English (cookie + `LocaleMiddleware`), dict labels,
  Bangla numerals, dashboard with stat cards + line/doughnut/bar charts +
  activity feed, themed change_list/change_form/login, vendored
  HTMX/Alpine/Chart.js + self-hosted fonts, demo `/example` project.
