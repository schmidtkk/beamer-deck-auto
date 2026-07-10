---
name: autobeamer-tikz
description: "Create or review TikZ diagrams in Beamer slides: quality standards, math-accuracy rules, sizing constraints, 6 common patterns, and an iterative review loop."
when_to_use: |
  Triggers on: "tikz", "diagram", "flowchart", "plot", "tree", "brace",
  "coordinate plot", "tikz diagram", "tikz quality", "tikz review".
  Do NOT trigger on: general slide creation (use autobeamer-create), build errors (use autobeamer-build).
argument-hint: "tikz — apply TikZ quality standards and patterns"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

# AutoBeamer TikZ — Quality Standards & Patterns

> **For creating full decks**, see [autobeamer-create](../autobeamer-create/SKILL.md).
> **For reviewing slide content**, see [autobeamer-review](../autobeamer-review/SKILL.md).
> **For layout optimization**, see [autobeamer-layout](../autobeamer-layout/SKILL.md).

---

## Quality Standards

### Rule 1: No Overlaps

Labels NEVER overlap with curves, lines, dots, or other labels.
When two labels are near the same vertical position, stagger them (one `above`, one `below`, or offset horizontally).
Minimum 0.2 units between any label and nearest graphical element.

### Rule 2: Visual Semantics

| Style | Meaning |
|-------|---------|
| Solid line | Observed / actual |
| Dashed line | Counterfactual / hypothetical |
| Filled dot | Observed data point |
| Hollow dot | Counterfactual / estimated |

Be consistent within a single diagram and across the deck.

### Rule 3: Line Weights

| Element | Weight |
|---------|--------|
| Axes | `thick` |
| Data curves | `thick` |
| Annotations | `thick` |
| Grid lines | `thin` |
| Box borders | default (or `thick` for emphasis) |

Never use `very thick` — it looks heavy on projected slides.

### Rule 4: Standard Parameters

| Parameter | Value |
|-----------|-------|
| Full-width diagram scale | `[scale=1.1]` |
| Data point radius | `4pt` |
| Label clearance from curve | ≥ 0.2 units |
| Arrow tip | `{Stealth}` (from `arrows.meta`) |

---

## Mathematical Accuracy (CRITICAL)

NEVER hardcode y-coordinates that should lie on a plotted curve. ALL coordinates for markers, dashed-line endpoints, and intersections MUST be computed via `\pgfmathsetmacro` from the SAME function used to draw the curve.

### Rule 0: Search for a real figure first — TikZ is the fallback

TikZ renders mathematical figures poorly, and a schematic that *misrepresents the math* is worse
than no figure. So the standing rule is **search first, draw last**:

- **Search the vetted openly-licensed sources first** (Wikimedia Commons, Openverse, Servier
  Medical Art for anatomy, NASA/Smithsonian, BioIcons/SciDraw, …) — full list + licenses +
  workflow in the create skill's
  [external-figures-licensing.md](../autobeamer-create/references/images/external-figures-licensing.md).
  A real, correct, openly-licensed figure (downloaded + credited) beats a hand drawing for
  **3-D surfaces, real curvature, saddles, circle packings, conformal grids, Ricci-flow
  snapshots, anatomy** — anything easy to fake and easy to get wrong.
- **Only if search truly fails**, reserve TikZ for what it does well: flowcharts, labelled
  triangles/meshes, 2-D schematics, computed function plots.

**If you do draw TikZ, the render + double visual-check is MANDATORY (no exceptions):**
1. Render the page to PNG (`pdftoppm -png -r 150 -f N -l N build/deck.pdf out`).
2. **Self visual-check** the pixels: perpendiculars actually perpendicular, markers on their
   curves (coordinates `\pgfmathsetmacro`-computed, never hardcoded), labels on the right objects,
   nothing clipped.
3. **Codex cross-check** via `codex:codex-rescue`: hand it the TikZ source (and PNG if available)
   to find geometric/math errors a second pair of eyes catches.
4. Fix and re-render until both checks pass — or go back and search harder for a real figure.

### ❌ WRONG — Hardcoded

```latex
\draw[thick] plot[domain=0.8:10] (\x, {0.3*\x + 2.7/\x});
\draw[dashed] (2, 0) -- (2, 3.2);  % BAD: 3.2 ≠ f(2)=1.95
\node at (2, 3.2) {Label};         % BAD: floats above curve
```

### ✅ CORRECT — Computed

```latex
\draw[thick] plot[domain=0.8:10] (\x, {0.3*\x + 2.7/\x});
\pgfmathsetmacro{\yTwo}{0.3*2 + 2.7/2}  % = 1.95 exactly
\draw[dashed] (2, 0) -- (2, \yTwo);
\fill (2, \yTwo) circle (2pt);
\node[above left] at (2, \yTwo) {Label};
```

### Curve Intersections

Solve algebraically first, then compute:

```latex
% Intersection of y=0.5x and y=2.5/x+0.3
% 0.5x = 2.5/x + 0.3 → x² - 0.6x - 5 = 0
\pgfmathsetmacro{\xint}{(0.6 + sqrt(20.36))/2}
\pgfmathsetmacro{\yint}{0.5*\xint}
\fill (\xint, \yint) circle (3pt);
```

---

## Sizing on Mixed-Content Slides

Beamer 16:9 at 10pt has **~70mm usable height** below the title bar.

### Estimation Procedure

1. Count text + equations above the diagram:
   - Each display equation: ~12–15mm
   - Each text line: ~5mm
   - Plus spacing (~3mm per gap)
2. Remaining height = 70mm − text height
3. TikZ bounding box height = (max y − min y) × yscale × 0.3528mm/pt
4. If diagram won't fit: reduce `yscale`, shrink coordinate ranges, or split to separate slide

### Safe Defaults

| Context | xscale | yscale |
|---------|--------|--------|
| Mixed slide (text + diagram) | 0.5–0.7 | 0.4–0.6 |
| Full-slide diagram | 0.9–1.1 | 0.9–1.1 |

---

## Edge Labels on Short Arrows

1. Estimate label text width vs. arrow length. If label > 80% of gap → increase gap or shrink font
2. Use `above=4pt` (or more) instead of bare `above` for clearance
3. For flow diagrams with N boxes: total width = N × box_width + (N−1) × gap ≤ **14cm** (16:9)
4. Always compile and visually verify — no label overlaps any box border

---

## Common Patterns

All patterns require these libraries:

```latex
\usetikzlibrary{arrows.meta, positioning, decorations.pathreplacing}
```

### 1. Flowchart (Horizontal)

```latex
\begin{tikzpicture}[
  box/.style={draw, rounded corners, minimum width=2.2cm, minimum height=0.8cm,
              font=\small, fill=positive!10},
  arr/.style={-{Stealth}, thick}
]
  \node[box] (A) {Step 1};
  \node[box, right=1.5cm of A] (B) {Step 2};
  \node[box, right=1.5cm of B] (C) {Step 3};
  \draw[arr] (A) -- node[above, font=\scriptsize] {label} (B);
  \draw[arr] (B) -- (C);
\end{tikzpicture}
```

Width constraint: N × 2.2cm + (N−1) × 1.5cm ≤ 14cm.

### 2. Timeline

```latex
\begin{tikzpicture}
  \draw[-{Stealth}, thick] (0,0) -- (12,0) node[right] {Time};
  \foreach \x/\lab in {1.5/Event A, 5/Event B, 9/Event C} {
    \draw[thick] (\x, 0.15) -- (\x, -0.15);
    \node[above=3pt, font=\small] at (\x, 0.15) {\lab};
  }
\end{tikzpicture}
```

### 3. Tree Diagram

```latex
\begin{tikzpicture}[
  level distance=1.2cm, sibling distance=2.5cm,
  every node/.style={draw, rounded corners, font=\small, minimum width=1.5cm}
]
  \node {Root}
    child { node {A} child { node {A1} } child { node {A2} } }
    child { node {B} child { node {B1} } };
\end{tikzpicture}
```

### 4. Annotated Brace

```latex
\draw[decorate, decoration={brace, amplitude=6pt, raise=2pt}]
  (start) -- (end) node[midway, above=10pt, font=\small] {annotation};
```

### 5. Coordinate Plot with Computed Intersection

```latex
\begin{tikzpicture}[scale=1.1]
  \draw[-{Stealth}, thick] (0,0) -- (6,0) node[right] {$x$};
  \draw[-{Stealth}, thick] (0,0) -- (0,4) node[above] {$y$};
  \draw[thick, positive] plot[smooth, domain=0.5:5.5] (\x, {0.5*\x});
  \draw[thick, negative, dashed] plot[smooth, domain=0.5:5.5] (\x, {2.5/\x + 0.3});
  % Intersection computed via \pgfmathsetmacro
  \pgfmathsetmacro{\xint}{(0.6 + sqrt(20.36))/2}
  \pgfmathsetmacro{\yint}{0.5*\xint}
  \fill (\xint, \yint) circle (3pt);
  \node[above right, font=\small] at (\xint, \yint) {Intersection};
\end{tikzpicture}
```

### 6. Decision Diamond

```latex
\node[diamond, draw, aspect=2, inner sep=1pt, font=\small] (D) {condition?};
\draw[arr] (D) -- node[right, font=\scriptsize] {yes} ++(0,-1.2);
\draw[arr] (D) -- node[above, font=\scriptsize] {no} ++(2.5,0);
```

Requires: `\usetikzlibrary{shapes.geometric}`.

---

## Iterative Review Loop

For complex diagrams (≥ 5 nodes or plotted curves):

```
Round 1–3:
  ┌─→ Step 1: Mentally render — trace every coordinate
  │   Step 2: Check for issues
  │     - Label overlaps
  │     - Misaligned elements
  │     - Inconsistent semantics
  │     - Hardcoded coordinates on curves
  │     - Bounding box overflow
  │   Step 3: Classify each issue — CRITICAL / MAJOR / MINOR
  │   Step 4: Fix all CRITICAL and MAJOR
  │   Step 5: Re-compile and visually verify in PDF
  └── If CRITICAL or MAJOR remain and round < 3: loop
      Otherwise: declare verdict
```

### Verdicts

| Verdict | Condition | Action |
|---------|-----------|--------|
| **APPROVED** | Zero CRITICAL, zero MAJOR | Ship it |
| **NEEDS REVISION** | CRITICAL or MAJOR remain | Fix before using |
| **REJECTED** | Fundamental structural problems | Redesign from scratch |

---

## TikZ Checklist

Before approving any TikZ diagram:

- [ ] No label–label overlaps
- [ ] No label–curve overlaps
- [ ] No edge labels overlapping adjacent nodes
- [ ] Diagram bounding box fits within remaining slide space
- [ ] ALL marked points computed via `\pgfmathsetmacro` — no hardcoded y-values on curves
- [ ] Dashed reference lines terminate exactly at the curve
- [ ] Consistent dot style (filled=observed, hollow=counterfactual)
- [ ] Consistent line style (solid=observed, dashed=counterfactual)
- [ ] Arrow annotations: FROM label TO feature (direction clear)
- [ ] Axes extend beyond all data points
- [ ] Labels legible at presentation size (min `\small`)
- [ ] Minimum spacing between labels and graphical elements (≥ 0.2 units)
- [ ] Width ≤ 14cm for 16:9 slides

---

## Cross-References

| Need | Skill |
|------|-------|
| Create new deck from scratch | [autobeamer-create](../autobeamer-create/SKILL.md) |
| Review slides for quality | [autobeamer-review](../autobeamer-review/SKILL.md) |
| Layout optimization, DGV grammar | [autobeamer-layout](../autobeamer-layout/SKILL.md) |
| Build errors, compilation | [autobeamer-build](../autobeamer-build/SKILL.md) |
| Automated validation | [autobeamer-validate](../autobeamer-validate/SKILL.md) |
