---
name: "Samanvay"
description: "A clearly labelled student prototype for separate complaint ownership and shared institution work."
colors:
  ink: "#163b35"
  slate: "#354e47"
  muted-slate: "#5c6b63"
  divider: "#dce2d8"
  soft-slate: "#e9eee5"
  canvas: "#f7f8f2"
  action-teal: "#176350"
  selection-mist: "#eaf4ed"
  attention-amber: "#805318"
  attention-wash: "#fff3dd"
  error-red: "#9b2936"
  error-wash: "#fff0f1"
  success-green: "#256344"
  success-wash: "#edf7f0"
  paper: "#ffffff"
  focus-ring: "#247a66"
  rail-text: "#354e47"
  rail-selected: "#155543"
  action-hover: "#104b3d"
  field-border: "#91a398"
  rail-paper: "#f0f2e9"
  clay-accent: "#b86b28"
  focus-surface: "#123b3b"
  focus-text: "#f4f7ee"
  focus-muted: "#c2d6ca"
typography:
  headline:
    fontFamily: "Manrope, Segoe UI, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.03em"
  headline-compact:
    fontFamily: "Manrope, Segoe UI, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Manrope, Segoe UI, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.015em"
  title-small:
    fontFamily: "Manrope, Segoe UI, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "Manrope, Segoe UI, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Manrope, Segoe UI, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.55
  supporting:
    fontFamily: "Manrope, Segoe UI, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.55
  badge:
    fontFamily: "Manrope, Segoe UI, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.55
  wordmark:
    fontFamily: "Manrope, Segoe UI, sans-serif"
    fontSize: "1.4rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.035em"
  focus-title:
    fontFamily: "Manrope, Segoe UI, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.4
rounded:
  badge: "4px"
  control: "6px"
  notice: "8px"
  panel: "12px"
spacing:
  "1": "4px"
  "2": "8px"
  "3": "12px"
  "4": "16px"
  "6": "24px"
  "8": "32px"
components:
  button-primary:
    backgroundColor: "{colors.action-teal}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
  button-primary-hover:
    backgroundColor: "{colors.action-hover}"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.slate}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
  button-secondary-hover:
    backgroundColor: "{colors.soft-slate}"
  button-text:
    backgroundColor: "transparent"
    textColor: "{colors.action-teal}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "9px 11px"
    width: "100%"
  navigation-link:
    textColor: "{colors.rail-text}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
  navigation-link-selected:
    backgroundColor: "{colors.rail-selected}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
  badge-neutral:
    backgroundColor: "{colors.soft-slate}"
    textColor: "{colors.slate}"
    typography: "{typography.badge}"
    rounded: "{rounded.badge}"
    padding: "3px 8px"
  badge-information:
    backgroundColor: "{colors.selection-mist}"
    textColor: "{colors.action-teal}"
  badge-amber:
    backgroundColor: "{colors.attention-wash}"
    textColor: "{colors.attention-amber}"
  badge-green:
    backgroundColor: "{colors.success-wash}"
    textColor: "{colors.success-green}"
  panel:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "24px"
  queue-filter:
    backgroundColor: "transparent"
    textColor: "{colors.muted-slate}"
    typography: "{typography.label}"
    rounded: "0"
    padding: "12px 0 16px"
  queue-filter-selected:
    textColor: "{colors.action-teal}"
  notice:
    backgroundColor: "{colors.selection-mist}"
    textColor: "{colors.slate}"
    rounded: "{rounded.notice}"
    padding: "14px 16px"
  brand:
    textColor: "{colors.ink}"
    typography: "{typography.wordmark}"
  focus-case:
    backgroundColor: "{colors.focus-surface}"
    textColor: "{colors.focus-text}"
    rounded: "{rounded.panel}"
    padding: "24px"
  connection-plan:
    backgroundColor: "{colors.selection-mist}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "22px 24px"
---

# Design System: Samanvay

## Overview

**Creative North Star: "The Civic Work Desk"**

Samanvay uses a warm daylight palette, a light navigation rail and compact paper-white work surfaces. Manrope gives headings and controls a shared voice; teal marks actions and selected navigation. A darker teal focus panel makes the next complaint prominent without turning every container into a competing feature.

The identity consists of two separate channels forming an S, a lowercase wordmark and a small clay period. That geometry echoes the interface: separate complaint records and owners can participate in a shared institution plan. The operational screens retain plain labels, visible next steps and review controls; fictional data and the student-prototype status remain explicit.

**Key Characteristics:**

- Warm ivory canvas with a light navigation rail and white work surfaces.
- Self-hosted Manrope, compact headings and ordinary labelled controls.
- A two-part S mark with a restrained clay accent.
- A dark focus case beside lighter institution coordination context.
- Flat surfaces, thin separators and motion limited to a small action cue.

**Evidence boundary.** This document describes source implementation inspected on 2026-10-28. It is not a rendered acceptance report. Saved browser policy blocks local-origin inspection; desktop/mobile layouts, supporting-screen appearance, keyboard flow and actual 200% browser zoom acceptance remain **OPEN**. No screenshot or human-clarity result is asserted. Sidecar snippets are static synthetic previews, not operational records or test evidence; synthesized tonal ramps are preview metadata, not additional application colors.

**Source authority.** Current styles live in `frontend/src/design-system/tokens.css`, `workspace.css`, `desk.css` and `connections.css`. Identity markup is `frontend/src/shared/Brand.tsx`; compositions are `app/Login.tsx`, `app/WorkspaceShell.tsx` and `features/workspace/{WorkQueue,FocusCase,InstitutionConnections}.tsx`. This refresh replaces the former blue/dark-rail description. Existing `blue` CSS aliases now resolve to teal for compatibility.

## Colors

Warm ivory and sage-tinted paper support deep green ink, teal interaction and a small clay identity accent. Frontmatter values are normative.

### Primary

- **Action teal** marks primary controls, links and selected filters; **action hover** deepens pointer feedback.
- **Selection mist** supports informational states and the shared institution plan.
- **Focus ring** marks keyboard focus on light surfaces; the dark focus panel uses a pale green outline.
- **Focus surface**, **focus text** and **focus muted** form the next-case panel and illustrative shared-plan block on sign-in.

### Secondary

- **Clay accent** is the wordmark period.
- **Attention amber/wash**, **error red/wash** and **success green/wash** are paired semantic status treatments. Their labels carry the meaning.

### Neutral

- **Canvas** is warm ivory around white **paper** panels; **rail paper** is a slightly deeper light surface.
- **Ink**, **slate** and **muted slate** distinguish primary, secondary and supporting text. These retained token names now contain green-tinted neutrals.
- **Divider** separates passive panels and rows; **field border** makes editable controls more visible.
- **Soft slate** supports quiet badges. **Rail text** is dark; **rail selected** is the dark green active navigation surface.

**The Action Accent Rule.** Use teal for actionable links, primary controls and selection; keep clay as the identity accent rather than an operational status.

**The Status Has Words Rule.** Pair every status color with a readable state label. Amber attention, red errors and green positive states do not stand alone.

## Typography

**Display and Body Font:** Manrope, then Segoe UI and sans-serif. Weights 400, 500, 600 and 700 are imported locally from `@fontsource/manrope`; the live app does not depend on a remote font request.

**Character:** One geometric sans family connects identity and working controls. Tight heading tracking and ordinary sentence case give the workspace a clear hierarchy.

### Hierarchy

- **Headline** is the page title; **headline compact** is its narrow-screen form.
- **Title** and **title small** are standard section and subsection headings.
- **Body** is working prose. Subtitles cap at 72ch; the sign-in introduction caps at 43ch.
- **Label** serves controls; **supporting** is secondary copy; **badge** is compact state text.
- **Wordmark** is lowercase with a separate clay period. **Focus title** is the featured complaint subject and reduces to the standard title size on phones.
- The sign-in story uses a source-local `clamp(2rem, 3.1vw, 2.875rem)` heading; it is not a general dashboard title.

Small logo and focus-panel captions are implementation exceptions, not a recommended minimum type scale. Their rendered readability remains an acceptance item.

**The Plain Label Rule.** Keep case owner, coordination lead and next step explicit. Type hierarchy must not collapse these responsibilities into an unlabeled diagram.

## Layout

The wide workspace uses a fixed 240px light rail, prototype strip and account/search header. Main content is centered with a 1600px cap and 32px padding. The frontmatter's 4/8/12/16/24/32 spacing scale is the shared rhythm; local 18/20/28px composition gaps do not become global tokens.

The desk has a flexible complaint queue and a 300px context column separated by 28px. The earliest-due eligible complaint appears once in the dark focus panel; the rest follow as compact records. Case queue and Shared plans are functional view buttons. Shared-plan selection persists across compact and expanded views, and expansion moves focus to the explicit region.

At 1180px the desk stacks and the context becomes two columns. At 800px navigation enters document flow behind a menu and search can wrap. At 560px context blocks and forms stack and the focus responsibilities become one column. Shared-plan branches stack at 640px. Existing detail/list adaptations occur at 1250px, 1050px and 360px. At 400px the sidebar mark becomes 32px, its wordmark 1.25rem and its tagline hides. These are implemented CSS breakpoints, not observed layout passes.

Sign-in uses story and form columns; at 800px it stacks and hides the supplemental ownership illustration while retaining the introduction and sign-in fields. Print styles remove the rail and account chrome.

## Elevation & Depth

The current design-system stylesheets have no decorative box shadows. Paper panels, pale context, deep teal focus and one-pixel borders distinguish layers. Tone and order supply emphasis.

**The Flat Surface Rule.** Use borders, spacing and tonal contrast for separation. The implemented workspace does not use decorative drop shadows.

## Shapes

Controls have modest corners, panels broader corners, notices an intermediate radius and badges small rectangular corners, as defined in frontmatter. Thin borders provide structure. The owner-initial circle is a local identity cue.

The custom S consists of two separate filled paths. Preserve the negative space and do not join the channels. The mark follows current text color beside a readable wordmark; its decorative SVG is hidden from assistive technology.

## Components

### Buttons

Teal primary, white bordered secondary and transparent text variants share a minimum 44px height. Keyboard focus is a 3px outline with a 3px offset. Hover changes the surface. Native disabled controls remain disabled.

The focus-case action uses pale green on dark teal. Only its arrow has a 3px hover movement over 160ms ease-out when reduced motion is not requested. Reduced-motion CSS disables animation and transitions.

### Chips

Compact state words share badge shape and padding. Neutral, information, attention and success tones distinguish state without hiding its label. Queue filters are buttons with selection state; badges are non-interactive status text.

### Cards / Containers

Paper panels use divider borders and panel corners; padded panels use 24px internal spacing. The dark focus case shows subject, institution, record ID, owner, due date and next step. Pending transfers explicitly leave responsibility with the current owner.

### Inputs / Fields

Native fields use white surfaces, the stronger field border, control corners and visible labels. The header search is an inline form with an accessible name and submit control. Loading, error, empty and retry states remain explicit. Workspace render/module failures expose reload recovery rather than a blank screen.

### Navigation

The light rail uses dark text, a dark green selected rectangle with white text and `aria-current`, plus a quieter hover tint. The mobile menu exposes expansion state, closes on Escape and restores toggle focus. A skip link targets main content. Browser verification of these source behaviors remains open.

### Brand

The inline two-channel S, lowercase wordmark and clay period form the identity. The optional tagline is “Clarity. Accountability. Together.” The mark is not a government seal or evidence of institutional endorsement.

### Shared institution work

The pale plan surface names the institution, coordination lead and shared next step. Thin branches lead to bureau sections listing separate complaint links, owners and lifecycle states. The live component reads authorised persisted `/api/coordination` records; its grouping neither merges complaints nor infers duplicate relationships or transfers ownership. Closed/historical records remain available separately from active counts. Loading, failure, empty and retained-plan states remain explicit. The labelled sign-in illustration is separate from this live component.

## Do's and Don'ts

### Do:

- Do keep the student-prototype and fictional-data labels visible, and label illustrative diagrams as illustrations.
- Do use the two separate channels of the shipped S mark without joining their paths.
- Do retain explicit complaint IDs and case owners beside the separate coordination lead.
- Do keep actionable elements as links, buttons and labelled native fields with visible keyboard focus.
- Do preserve each complaint record when showing shared institution work or a reviewed relationship.
- Do distinguish implemented source behavior from browser-verified layout, keyboard and zoom evidence.

### Don't:

- Don't describe synthetic records, illustration examples or simulated connections as live institutional integrations.
- Don't treat a suggested connection or a shared institution plan as an automatic duplicate decision or ownership transfer.
- Don't add status meaning to the clay brand period or rely on color alone for operational meaning.
- Don't reinstate the superseded dark navigation rail, blue action palette or system-font-first identity in new live screens.
- Don't claim visual acceptance, human clarity feedback, keyboard results or actual 200% browser zoom from a source inspection.
