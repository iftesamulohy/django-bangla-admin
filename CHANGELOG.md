# Changelog

## 0.3.0

### Added
- **Collapsible tree-view sidebar.** Apps are now parent nodes whose models
  are nested, animated children (auto mode builds the tree from the registry;
  manual menus gain a `children` key). The group holding the active page
  auto-expands, and a collapsed rail reveals children as a hover flyout.
- **Per-row Edit + Delete buttons** on every changelist row (permission-checked
  via a new `ba_result_list` tag and `change_list.html` override).
- New icons: `chevron-right`, `chevron-down`, `folder`, `square-pen`,
  `trash-2`, `log-in`, `plus`, `lock`. New `default_app_icon` setting.

### Changed
- **Design refresh.** Modernized tokens (radius/shadow tiers, focus ring),
  gradient brand mark + primary buttons, blurred sticky topbar, card hover
  lift, thin themed scrollbars, refined nav active state, and polished
  breadcrumbs / page headings.
- **Changelist edit links** are now highlighted in the primary color.
- **Login page redesign** — gradient backdrop, input icons, and a gradient
  Log in button with icon.

## 0.2.1

### Fixed
- Logout button now submits a CSRF-protected POST request instead of a GET
  link, fixing logout on Django 5.0+ where the admin `logout` view rejects GET.

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
