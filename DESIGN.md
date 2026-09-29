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
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "clamp(2.8rem, 6vw, 5.8rem)"
    fontWeight: 500
    lineHeight: 1.12
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Segoe UI Variable, Segoe UI, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Segoe UI Variable, Segoe UI, Arial, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 800
    letterSpacing: "0.14em"
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
- Editorial serif questions paired with familiar sans-serif controls.
- Coordinate grids appear only where measurement or geography is meaningful.
- Terracotta marks actions, warnings and observed points.

## Colors

Deep survey ink supplies structure, field paper keeps long reading comfortable, and terracotta is deliberately scarce.

**The Signal Color Rule.** Terracotta identifies primary action, warning or selected evidence; it is not general decoration.

## Typography

**Display Font:** Georgia with Times New Roman fallback  
**Body Font:** Segoe UI Variable with Segoe UI and Arial fallbacks

Large serif headings frame research questions. Sans-serif text handles controls, labels, warnings and dense model evidence. Body copy stays near 65–75 characters where practical.

**The Evidence Label Rule.** Uppercase tracked labels are reserved for datelines, metric names and short research metadata.

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
