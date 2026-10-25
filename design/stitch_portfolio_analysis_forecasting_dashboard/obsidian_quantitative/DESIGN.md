---
name: Obsidian Quantitative
colors:
  surface: '#0f131c'
  surface-dim: '#0f131c'
  surface-bright: '#353943'
  surface-container-lowest: '#0a0e17'
  surface-container-low: '#181b25'
  surface-container: '#1c1f29'
  surface-container-high: '#262a34'
  surface-container-highest: '#31353f'
  on-surface: '#dfe2ef'
  on-surface-variant: '#bcc9cd'
  inverse-surface: '#dfe2ef'
  inverse-on-surface: '#2c303a'
  outline: '#869397'
  outline-variant: '#3d494c'
  surface-tint: '#4cd7f6'
  primary: '#4cd7f6'
  on-primary: '#003640'
  primary-container: '#06b6d4'
  on-primary-container: '#00424f'
  inverse-primary: '#00687a'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb2b7'
  on-tertiary: '#67001b'
  tertiary-container: '#ff7f8b'
  on-tertiary-container: '#7d0023'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#acedff'
  primary-fixed-dim: '#4cd7f6'
  on-primary-fixed: '#001f26'
  on-primary-fixed-variant: '#004e5c'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdadb'
  tertiary-fixed-dim: '#ffb2b7'
  on-tertiary-fixed: '#40000d'
  on-tertiary-fixed-variant: '#92002a'
  background: '#0f131c'
  on-background: '#dfe2ef'
  surface-variant: '#31353f'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.025em
  display-lg-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  stat-lg:
    fontFamily: JetBrains Mono
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.02em
  stat-md:
    fontFamily: JetBrains Mono
    fontSize: 16px
    fontWeight: '500'
    lineHeight: 22px
    letterSpacing: -0.01em
  stat-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.06em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-mobile: 0.75rem
  margin: 1.5rem
  margin-mobile: 1rem
  space-2xs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-base: 1rem
  space-lg: 1.25rem
  space-xl: 1.5rem
  space-2xl: 2rem
  space-3xl: 3rem
---

## Brand & Style

This design system delivers a high-precision, technical-grade aesthetic designed for data-intensive portfolio analytics and algorithmic forecasting. Engineered to project institutional credibility, quantitative mastery, and forward-looking momentum, it serves discerning active investors and wealth managers who expect dense, frictionless telemetry.

The aesthetic fuses **Tactile Technical Minimalism** with **Subtle Luminescent Depth**. Rather than treating dark mode as inverted white space, the canvas is approached as an illuminated digital terminal: dense, structured, hyper-readable, and deliberate. Depth is articulated via layered slate-obsidian planes, micro-borders, and targeted spectral glows (teal for predictive models, emerald for positive alpha) rather than heavy drop shadows. High contrast is balanced by nuanced secondary and tertiary type hierarchy, preventing visual exhaustion during sustained market sessions.

## Colors

The palette balances clinical precision with luminous visual cues:

- **Canvas & Surface Tiering**:
  - `Canvas Default`: `#090D16` (Deep Obsidian, the structural floor)
  - `Canvas Subdued`: `#0B132B` (Recessed wells, inactive tabs, track backgrounds)
  - `Surface Tier 1`: `#0F172A` (Standard cards, modules, navigation bars)
  - `Surface Tier 2`: `#131E36` (Elevated cards, active rows, dialogs)
  - `Surface Tier 3`: `#1E293B` (Floating menus, tooltips, segmented control thumbs)
- **Functional Semantics**:
  - `Primary / Predictive`: `#06B6D4` (Electric Cyan) and `#38BDF8` (Sky) denote AI models, stochastic cones, future projections, and active interactive elements.
  - `Secondary / Alpha`: `#10B981` (Vibrant Emerald) communicates positive return, profit, inflow, and structural strength.
  - `Tertiary / Risk`: `#F43F5E` (Coral Red) signals drawdowns, volatility breach, stop-losses, and warnings.
  - `Warning / Delta`: `#F59E0B` (Amber) for pending settlements or neutral exposure shifts.
- **Data & Neutral Scale**:
  - `Text Primary`: `#F8FAFC` (100% white-adjacent clarity)
  - `Text Secondary`: `#94A3B8` (Institutional slate for metrics labels and meta)
  - `Text Tertiary`: `#64748B` (Inactive states, micro-annotations)
  - `Border Subtle`: `rgba(148, 163, 184, 0.12)`
  - `Border Focus / Accent`: `rgba(6, 182, 212, 0.45)`

## Typography

The typography engine is constructed around two distinct disciplines: editorial human clarity via `Inter` and disciplined numeric alignment via `JetBrains Mono`.

- **Numerical Uniformity**: All monetary figures, percentage returns, basis points, Sharpe ratios, and timestamps MUST employ `font-variant-numeric: tabular-nums` or the dedicated `stat-*` font family (`JetBrains Mono`). This guarantees zero horizontal jitter across real-time price updates and chart scrubs.
- **Visual Weight**: Section headers and macro-indicators utilize tight tracking (`-0.02em` to `-0.025em`) to emphasize institutional weight. Micro-labels, asset classes, and metric descriptors employ `label-caps` in uppercase styling with positive letter-spacing (`0.06em`) to ensure legibility against deep obsidian surfaces.

## Layout & Spacing

The layout philosophy prioritizes high data density and modular scanning, tailored primarily for a high-performance native mobile experience with adaptive expansion for tablet viewports.

- **Grid Architecture**: Mobile viewports utilize an asymmetric fluid grid with `margin-mobile` (16px) margins and `gutter-mobile` (12px) internal gaps, maximizing horizontal telemetry. Tablet screens expand to a 6- or 8-column layout with 24px outer margins.
- **Rhythmic Densities**: 
  - Micro-metric groupings and inline delta indicators use `space-xs` (4px) to `space-sm` (8px).
  - Component internal padding uses `space-md` (12px) for compact data lists and `space-lg` (20px) for primary hero cards.
  - Section-to-section flow maintains a disciplined `space-xl` (24px) to `space-2xl` (32px) breath to demarcate analytics suites (e.g., Monte Carlo simulations vs. Sector Allocation).

## Elevation & Depth

Visual hierarchy does not rely on diffused drop shadows, which muddy dark interfaces. Depth is communicated via **Tonal Layering**, **Crisp Inner Luster**, and **Spectral Luminescence**:

- **Tonal Stepping**: Background begins at `#090D16`. Content containers sit on `#0F172A`. Focused modules or floating widgets occupy `#131E36`. Overlays and popovers inhabit `#1E293B`.
- **Low-Contrast Micro-Borders**: Every surface container is outlined with a 1px border using `rgba(148, 163, 184, 0.10)` to define perimeter geometry against deep backgrounds. For interactive or high-conviction cards, use an illuminated boundary: `linear-gradient(180deg, rgba(6, 182, 212, 0.3) 0%, rgba(148, 163, 184, 0.05) 100%)`.
- **Predictive Glows & Ambient Radiance**: Glowing effects are strictly functional, reserved for dynamic indicators:
  - Cyan model trajectories use a subtle drop shadow (`box-shadow: 0 0 16px rgba(6, 182, 212, 0.35)`).
  - Outperforming assets emit an emerald aura (`0 0 12px rgba(16, 185, 129, 0.25)`).
  - Critical drawdown breaches invoke an urgent coral beacon (`0 0 12px rgba(244, 63, 94, 0.3)`).
- **Backdrop Filters**: Modals, sheets, and the persistent bottom navigation invoke `backdrop-filter: blur(20px)` over `rgba(9, 13, 22, 0.82)`, keeping background data trends contextually visible.

## Shapes

The shape hierarchy is engineered for a balanced, modern, high-precision environment. It uses refined radii that feel sculpted rather than aggressive or childlike:

- **Default Modules & Cards**: Styled with `rounded` (8px) for internal nested items and `rounded-lg` (16px) for primary layout cards.
- **Pill Badges & Toggles**: Pill styling (`rounded-full` / 9999px) is reserved exclusively for numerical chips, delta status badges, category filters, and slider thumbs, creating clear semantic differentiation between containers (structural rectangles) and data tags (smooth capsules).
- **Inputs & Control Tracks**: Use 8px radii to match nested visual rhythm within 16px outer cards.

## Components

### Buttons
- **Primary (Action / Forecast Trigger)**: Deep cyan solid background (`#06B6D4`) with `#090D16` bold typography, height 48px, radius 12px. Interactive state adds a subtle radial bloom (`0 0 20px rgba(6, 182, 212, 0.4)`).
- **Secondary (Tertiary Actions)**: Background `#131E36`, 1px border `rgba(148, 163, 184, 0.15)`, text `#F8FAFC`.
- **Ghost / Utility**: Borderless, text `#94A3B8`, hover/pressed state reveals `rgba(255, 255, 255, 0.05)` fill.

### Crisp Pill Badges
- Continuous status badges (e.g., `+18.4% Alpha`, `Low Risk`, `VaR 95%`): Height 24px, padding 2px 10px, fully rounded (9999px).
- Positive state: Background `rgba(16, 185, 129, 0.12)`, border `1px solid rgba(16, 185, 129, 0.3)`, text `#10B981` (in `stat-sm`).
- Negative state: Background `rgba(244, 63, 94, 0.12)`, border `1px solid rgba(244, 63, 94, 0.3)`, text `#F43F5E`.
- Predictive state: Background `rgba(6, 182, 212, 0.12)`, border `1px solid rgba(6, 182, 212, 0.3)`, text `#38BDF8`.

### Glowing Gradient Charts & Micro-Sparklines
- **Area Fills**: Gradients transition from `rgba(6, 182, 212, 0.28)` at the upper line to `rgba(6, 182, 212, 0.0)` at baseline. Positive returns transition from emerald (`rgba(16, 185, 129, 0.25)`).
- **Stroke**: Crisp 2px vector path with an ambient duplicate stroke at blur 4px to emulate an illuminated monitor trace.
- **Sparklines**: Ultra-compact (height 28px, width 64px), no grid axes, isolated glow stroke, terminal node represented by a 3px solid indicator dot.

### Segmented Control Toggles
- Recessed base on `#0B132B`, 1px border `rgba(148, 163, 184, 0.10)`, padding 3px, height 36px, radius 10px.
- Selected state: Elevated `#1E293B` thumb with 1px border `rgba(148, 163, 184, 0.2)`, text `#F8FAFC`, subtle drop-shadow `0 2px 6px rgba(0, 0, 0, 0.3)`. Unselected text `#64748B`.

### Slider Controls (Scenario & Stress Testing)
- **Track**: 4px height, background `#1E293B`. Active progress track uses `#06B6D4` or dynamic multi-stop gradient (emerald-to-coral for risk thresholds).
- **Thumb**: 20px circle, `#F8FAFC` solid core surrounded by a 2px `#06B6D4` border and focused glow ring (`0 0 10px rgba(6, 182, 212, 0.5)`). Shows real-time numeric tooltip directly above during scrub.

### Financial Telemetry Cards
- Surface `#0F172A` with 1px `rgba(148, 163, 184, 0.12)` border and 16px corner radius.
- Standard layout: Top row contains metric descriptor (`label-caps`) paired with status pill badge; center features high-impact monetary value (`stat-lg`); bottom houses inline micro-sparkline or comparison delta against baseline benchmarks.

### Lists & Row Items
- Padded at 14px vertical, separated by hairline borders (`rgba(148, 163, 184, 0.06)`). Left side anchors asset icon, ticker, and allocation weight; right side aligns tabular current value and localized percentage return.