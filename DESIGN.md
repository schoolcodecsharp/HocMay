---
name: California Housing Lab
description: A modern geographic survey notebook for evidence-first machine learning.
colors:
  survey-ink: "#173f4a"
  survey-ink-deep: "#0f3038"
  signal-terracotta: "#bb583b"
  signal-terracotta-deep: "#8e3e29"
  field-paper: "#f4f0e7"
  field-paper-deep: "#e9e2d5"
  body-ink: "#17272b"
  secondary-ink: "#53666a"
  survey-line: "#c9c1b3"
  focus-amber: "#f0a33b"
  error-red: "#9d3027"
typography:
  display:
    fontFamily: "Be Vietnam Pro, Segoe UI, Arial, sans-serif"
    fontSize: "clamp(2.5rem, 5vw, 4.5rem)"
    fontWeight: 600
    lineHeight: 1.18
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Be Vietnam Pro, Segoe UI, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "Be Vietnam Pro, Segoe UI, Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.65
  section:
    fontSize: "clamp(1.5rem, 3vw, 2.25rem)"
    fontWeight: 600
    lineHeight: 1.25
  page:
    fontSize: "clamp(2.25rem, 4.5vw, 4rem)"
  lead:
    fontSize: "1.125rem"
  functional-heading:
    fontSize: "1.25rem"
  value:
    fontSize: "1.5rem"
  metric:
    fontSize: "3rem"
rounded:
  control: "10px"
  surface: "14px"
spacing:
  xs: "8px"
  sm: "16px"
  md: "32px"
  lg: "64px"
components:
  button-primary:
    backgroundColor: "{colors.signal-terracotta}"
    textColor: "#ffffff"
    rounded: "{rounded.control}"
    padding: "0.72rem 1.2rem"
    height: "48px"
  input:
    backgroundColor: "#fffdf7"
    textColor: "{colors.body-ink}"
    rounded: "{rounded.control}"
    padding: "0.78rem 0.9rem"
---

# Design System California Housing Lab

## Overview

**Creative North Star: "The Geographic Survey Notebook"**

The interface feels like a contemporary field record used to inspect census geography: warm paper, precise survey ink, sparse coordinate lines and a single terracotta signal. It is academic and operational rather than commercial; charts and model evidence carry more visual weight than decorative imagery.

**Key Characteristics:**

- Warm paper surfaces with deep blue-green ink.
- Vietnamese-capable, locally hosted typography with clear weight and scale contrasts.
- Coordinate grids appear only where measurement or geography is meaningful.
- Terracotta marks actions, warnings and observed points.

## Colors

Deep survey ink supplies structure, field paper keeps long reading comfortable, and terracotta is deliberately scarce.

**The Signal Color Rule.** Terracotta identifies primary action, warning or selected evidence; it is not general decoration.

## Typography

**Display and Body Font:** Be Vietnam Pro, self-hosted; Segoe UI and Arial fallbacks.

The user's font revision (2026-09-30) replaces the serif/system mix with one consistent Vietnamese family while retaining the survey palette and layout. Research headings use 600, controls 600, emphasis 700, body 400. Body is 16px/1.65; supporting copy is at least 14px. Compact headings use 1.25 leading for stacked Vietnamese accents. Narrative copy stays near 65–72 characters; evidence tables remain wide. Inputs, metrics and tables use tabular numerals.

**The Evidence Label Rule.** Multiword Vietnamese labels retain normal casing and spacing; weight establishes hierarchy. Three original TTF files (about 410KB total) and their OFL license ship in `app/static/fonts`, with `font-display: swap` and only Regular preloaded. No external font service is needed at runtime.

## Layout

The desktop container is capped at 1180px. Major pages use asymmetric two-column compositions; dense evidence may use balanced two-column galleries. At 850px, side-by-side work becomes a single reading column and navigation collapses. At 560px, form fields, figures and metric ledgers become one column.

Visible 40px coordinate grids belong only on map, research-heading or measurement surfaces. Ordinary content remains plain field paper.

## Elevation & Depth

The system is flat by default. A soft offset shadow (`0 14px 34px rgba(23, 39, 43, 0.12)`) is reserved for interactive result surfaces and figure sheets that sit above the paper.

**The Flat Evidence Rule.** Tables, ledgers and warning bands use tonal contrast and rules; they do not float.

## Shapes

Controls use restrained 10px corners. Raised result and figure surfaces use 14px corners. Tables and ledgers remain rectilinear so numerical alignment stays primary.

## Components

### Buttons

Primary buttons use signal terracotta, white text, 10px corners and a minimum 48px height. Hover deepens the signal color; keyboard focus uses a 3px amber outline.

### Cards and Containers

Cards are not the page scaffold. Only prediction results, figures and true empty states receive raised surfaces; repeated narrative content uses open layout, ledgers or rules.

### Inputs and Fields

Inputs sit on near-white paper with a visible neutral stroke and tabular numerals. Invalid values receive an error-red stroke and a written recovery message. No invalid value is silently clipped or replaced.

### Navigation

The navigation uses the deepest survey ink. Active state is a thin inset amber rule on desktop and a left rule on mobile. The mobile menu keeps standard rectangular controls and at least 48px targets.

## Do's and Don'ts

### Do:

- **Do** keep dataset year and census block group scope close to predictions.
- **Do** use charts and generated artifacts as the strongest visual evidence.
- **Do** preserve keyboard focus, error, disabled, loading and empty states.

### Don't:

- **Don't** borrow real-estate marketplace photography, pricing badges or sales language.
- **Don't** use terracotta as background decoration unrelated to state or meaning.
- **Don't** put the coordinate grid behind ordinary long-form content.
- **Don't** turn every section into a rounded card.
