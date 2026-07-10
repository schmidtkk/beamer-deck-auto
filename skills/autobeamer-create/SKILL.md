---
name: autobeamer-create
description: "Create a new XeLaTeX Beamer deck from scratch in one of three modes — passive-study, active-socratic, or academic-presentation — from papers, notes, books, or ideas."
when_to_use: |
  Use when creating a new deck from source material or an idea.
  Do NOT trigger on editing existing slides (use autobeamer-layout), build errors
  (use autobeamer-build), or review-only tasks (use autobeamer-review).
argument-hint: "create [topic-or-file] -- starts the deck creation pipeline"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "AskUserQuestion", "TaskCreate", "TaskUpdate", "TaskList", "TaskGet"]
---

# AutoBeamer Create

Create XeLaTeX Beamer decks through a mode-aware pipeline. Keep this file as the router; load only the references needed for the user's deck.

## Execution Model — leader + 3 waves

You (the create skill) act as the **team leader/orchestrator**, not the worker.
Split the pipeline into three waves and assign each to one specialized subagent,
reviewing the handoff between waves.

| Wave | Phases | Subagent | Produces |
|------|--------|----------|----------|
| 1 — Plan | 0–2 | [`autobeamer-planner`](../../agents/autobeamer-planner.md) | structure plan + validated `image_index.json` |
| 2 — Draft+Figures | 3–4 (merged) | [`autobeamer-drafter`](../../agents/autobeamer-drafter.md) | deck `.tex` + resolved image-request log |
| 3 — Polish | 5 | [`autobeamer-finisher`](../../agents/autobeamer-finisher.md) | final PDF + validation/review report |

**Between Wave 2 and Wave 3 the leader runs the anti-drift [alignment check](references/validation/alignment-check.md)** against the Wave-1 plan and the original demands; on drift, bounce back to the Drafter before polishing.

**When to use waves:** for substantial or source-document-driven decks, dispatch the three subagents (by `subagent_type` name) and pass the handoff artifacts (plan, `image_index.json` path, deck path, reports) — each subagent starts cold. For small/simple decks, run the phases inline yourself; the same gates still apply.

**Before any wave**, run the [environment doctor](references/validation/env-doctor.md): it writes `.autobeamer/env_state.json`, which determines whether figure extraction is possible and the figure-confidence ceiling for the whole run.

## Required First Steps

0. **Run the environment doctor first** — the skill needs a runtime it does not control. Probe deps and record this model's visual capability, then branch on the result during planning (see [references/validation/env-doctor.md](references/validation/env-doctor.md)):
   ```bash
   python tools/doctor.py check                                  # exit!=0 ⇒ STOP, report blockers
   python tools/doctor.py set-capability --model <your-model-id>
   ```
   If `check` reports blockers (missing `xelatex`/poppler), stop and tell the user what to install. Otherwise read `.autobeamer/env_state.json` `profile` and let it gate Phase 0 figure extraction and the image-index visual-check method.
1. Read skill memory before planning, resolved at the plugin/repo root: `memories/MEMORY_INDEX.md`, then `memories/repo/user-preferences.md`. If `memories/` is absent (e.g., a fresh public checkout that ships without it), proceed without it and rely on the in-skill defaults — do not fabricate preferences.
2. If source material is provided, inspect it before asking questions.
3. Set exactly one mode: `passive-study`, `active-socratic`, or `academic-presentation`.
4. Load the selected mode reference and [references/validation/mode-gates.md](references/validation/mode-gates.md).
5. If a PDF or source document is provided, load [references/images/source-document-first.md](references/images/source-document-first.md) and extract figures before web search.
6. **Default to English.** You reason and draft in English; confirm the **target language** in the interview. A non-English deck is produced by translating the finished English deck — see [Language Policy](#language-policy). Load [references/writing/en-technical-style.md](references/writing/en-technical-style.md) before drafting English prose.

## Mode Routing

| Mode | Use when | Load |
|------|----------|------|
| `passive-study` | The learner is entering an unfamiliar field and needs comprehensive, self-contained teaching with background support | [references/modes/passive-study.md](references/modes/passive-study.md) |
| `active-socratic` | The learner wants guided discovery through questions, thought experiments, derivations, and attempt gates | [references/modes/active-socratic.md](references/modes/active-socratic.md) |
| `academic-presentation` | The deck is for a live talk, seminar, defense, journal club, or academic sharing | [references/modes/academic-presentation.md](references/modes/academic-presentation.md) |

Compatibility aliases:
- "Mentor", "self-study", "study deck", or textbook/chapter requests map to `passive-study` unless the user asks for Socratic discovery.
- "Socratic", "active study", "reinvent", "derive with me", or "mentor me with questions" map to `active-socratic`.
- "Presentation", "talk", "seminar", "conference", "defense", or "academic sharing" map to `academic-presentation`.

Every structure plan must state the selected mode, loaded references, and mode-specific acceptance gates.

## Language Policy

**English is the default, and the language you reason and draft in.** You author best in
English, so the canonical draft — outline, prose, takeaways, figure labels — is always written
and verified in English first, following
[references/writing/en-technical-style.md](references/writing/en-technical-style.md).
**Do not think or draft directly in a non-English language;** your non-English instinct
produces calques. A non-English deck is a *governed translation* of the finished English one.

**Ask the target language in the Interview Gate (default English).** If the user wants a
non-English deck (e.g. Chinese), produce it like this — never by drafting in that language:

1. Build and fully QA the **English** deck first (compile, validate, visual-check, review).
2. Run the **TRANSLATE pass** (Phase 6): translate the verified English `.tex` into the target
   language under that language's technical-style reference. Change **only natural-language
   strings** (frame titles, prose, bullets, `\TL*` block text, TikZ labels/captions). Keep all
   math, `\TL*` macro names, and TikZ structure/coordinates byte-identical.
3. **Re-run the full Quality Gate** on the translated deck — language length changes layout.

### Chinese target — translation-pass specifics

Load and obey [references/writing/zh-technical-style.md](references/writing/zh-technical-style.md)
(译意不译词; the anti-翻译腔/calque tables — the sentence skeleton must be natural Chinese). Plus
the mechanical steps:

1. **Fonts auto-detected.** font-config (Priority 1.5) checks `.fonts/SourceHanSerifSC-Medium.otf`
   (Source Han Serif SC Medium+Bold); else system Noto Sans CJK (thinner). KpMath pairs fine — no
   math-font override needed.
2. **Localize `\TLtakeaway`.** Override its hardcoded "Key Takeaway." → "要点。":
   ```latex
   \renewcommand{\TLtakeaway}[1]{...\textbf{要点。} #1...}
   ```
3. **Translate TikZ node labels, axis annotations, captions.** Keep math in LaTeX math mode unchanged.
4. **Validator bilingual glosses.** `validate_deck.py` matches English keywords (notation / exercise /
   reference; Socratic question / attempt / hint / reflection). Keep bilingual titles — e.g.
   「符号表 (Notation)」「习题 (Exercises)」「参考文献 (References)」 — so the gates still pass.
5. **Re-check overflow.** Chinese is usually *shorter* than English, so frames that fit in English
   normally still fit — but re-run the Quality Gate; on any Overfull, split, never shrink.

## Pipeline

```
                          ┌─ WAVE 1: PLAN ──────────────────────────────────┐
Phase 0: MATERIAL ANALYSIS  -> read sources, extract figures -> image index
Phase 1: NEEDS INTERVIEW    -> ask only missing content/audience/mode questions
Phase 2: STRUCTURE PLAN     -> detailed outline + planned figures; approval gate
                          └─────────────────────────────────────────────────┘
                          ┌─ WAVE 2: DRAFT + FIGURES (merged) ──────────────┐
Phase 3+4: DRAFT+FIGURES    -> write batches; each figure-needing slide emits an
                               image request and resolves it from the index
                          └─────────────────────────────────────────────────┘
            >>> leader runs the ALIGNMENT CHECK (anti-drift) here <<<
                          ┌─ WAVE 3: POLISH ────────────────────────────────┐
Phase 5: QUALITY LOOP       -> compile, validate, visual-check, review, fix
                          └─────────────────────────────────────────────────┘
            >>> if target language ≠ English: run Phase 6, then re-run Wave 3 <<<
                          ┌─ WAVE 4: TRANSLATE (conditional) ───────────────┐
Phase 6: TRANSLATE          -> translate the verified English .tex into the target
                               language under that language's technical-style reference
                               (strings only; math/macros/TikZ unchanged); re-run Quality Gate
                          └─────────────────────────────────────────────────┘
```

Phases 3 and 4 are **one wave**: decide a slide's figure while you draft it, not in a separate pass. Do not skip phases. **Phase 6 runs only for non-English targets** and always on top of a fully verified English deck (see [Language Policy](#language-policy)). For detailed guidance, load [references/workflows/full-create-guide.md](references/workflows/full-create-guide.md).

## Material Analysis

If papers/materials are provided:
- Read the source thoroughly before interviewing the user.
- Extract contribution, method, theorem/result structure, notation, prerequisites, and slide-worthy figures.
- For PDFs, run:
  ```bash
  python tools/paper_parser.py parse paper.pdf --output slides_assets/paper.json
  python tools/paper_parser.py extract-images paper.pdf --output slides_assets/source_figures/
  ```
- Build the **image index** as the figure inventory — do not keep it ad-hoc. Seed it from the parser, attach captions/context, then visually check each image to set its `key_idea` and `confidence` (confidence is capped when no visual check is possible). See [references/images/image-index.md](references/images/image-index.md):
  ```bash
  python tools/image_index.py init --path slides_assets/image_index.json
  python tools/image_index.py import-parser slides_assets/paper.json --path slides_assets/image_index.json
  python tools/image_index.py validate --path slides_assets/image_index.json
  ```

## Interview Gate

Ask only what cannot be inferred safely:
- **Target language** (default **English**). Ask interactively (e.g. via `AskUserQuestion`). If the user picks a non-English language, note that the deck will be drafted in English and then translated (Phase 6) — see [Language Policy](#language-policy).
- Duration or target effort budget.
- Audience/learner level and prior field exposure.
- Mode confirmation when ambiguous.
- Paper-specific scope decisions derived from the source.
- Whether speaker notes are needed for `academic-presentation`.

Avoid generic questionnaires. Use the material to ask concrete choices.

**Map the audience to a reader profile.** Once the audience answer is in, resolve it to a profile via
[autobeamer-calibrate](../autobeamer-calibrate/SKILL.md) `set-profile` (P1 AI engineer · P2 undergrad ·
P3 high-school · P4 biomed · P5 humanities · P6 cross-field grad, or nearest + axis deltas). This drives a
**per-slide cognitive-load budget** instead of the flat "≤5 new symbols" cap, and the per-profile
scaffolding obligations. **Governing tenet:** for applied readers (P1/P4), proofs are *in-zone* and must be
*scaffolded* (more steps), never gated away.

## Structure Plan Gate

Before drafting, present a plan containing:
- Selected mode and loaded references.
- **Target language** and, if non-English, a note that the deck is drafted in English then translated (Phase 6).
- Section list with slide counts.
- Per-section learning objective or narrative purpose.
- Planned figures, tables, TikZ diagrams, or source images.
- New notation and prerequisite reminders.
- **Reader-profile budget card** from [autobeamer-calibrate](../autobeamer-calibrate/SKILL.md) `budget`:
  per-slide `L_max`, abstraction-jump cap `τ`, working-set `W` (recap cadence), `teaching_style` opener,
  `anchor_domain`, and the profile's scaffolding obligations. The planner plans each frame against `L_max`
  and ensures every concept is introduced before use (zero prereq debt).
- Validation gates from [references/validation/mode-gates.md](references/validation/mode-gates.md).

Ask for approval before drafting.

The Wave-2→3 **alignment check** then adds one line: every frame respects the target-profile budget
(run `autobeamer-calibrate load-audit`); added scaffolding that raises load is absorbed by **splitting**,
never shrinking.

## Drafting Rules

Shared hard rules:
- No overlays: never use `\pause`, `\onslide`, `\only`, or `\uncover`.
- Maximum 3 colored boxes per slide.
- Motivation before formalism.
- Worked example within 2 slides of every definition.
- Every slide needs at least one substantive element.
- New decks use template-lib commands such as `\TLinfoblock`, `\TLalertblock`, `\TLresultblock`, `\TLwarnblock`, and `\TLtakeaway`.

Mode-specific writing:
- `passive-study`: complete sentences, background context, examples, exercises, glossary, bibliographical notes.
- `active-socratic`: one central question/task per learning frame, staged hints, learner attempts before answers.
- `academic-presentation`: telegraphic prompts, time-aware pacing, references before Thank You, backup slides after `\appendix`.

**Language prose style** — you always draft in **English** first (see [Language Policy](#language-policy)):
- **English (the draft you write)** → [references/writing/en-technical-style.md](references/writing/en-technical-style.md):
  one relationship per line, every line advances, define-on-first-use, mechanism before formula,
  equations as evidence, plain register, payoff-first titles, takeaway = one new consequence.
- **Non-English target** → produced by the Phase 6 **translation pass** on the verified English
  deck, not by drafting in that language. For Chinese, the pass obeys
  [references/writing/zh-technical-style.md](references/writing/zh-technical-style.md)
  (译意不译词 / anti-翻译腔). Note the length flip: English runs ~30% longer than Chinese, so the
  English draft is the tight one; a translation rarely overflows, but re-run the gate and **split,
  never shrink** if it does.

## Figures And Layout (merged into drafting — Wave 2)

Figures are resolved **while drafting**, not in a separate pass. When a slide
needs a figure, log an image request and adopt from the index by key idea:
```bash
python tools/image_index.py request-add --slide "<title>" --need "<key idea>"
python tools/image_index.py query --key-idea "<key idea>"
python tools/image_index.py request-resolve --request <id> --image <imgid> --status adopted
```

Source-document-first precedence (see [references/images/image-index.md](references/images/image-index.md)):
1. Indexed source figure (matched via `query`).
2. Rendered/cropped source page region.
3. Local TikZ/pgfplots **only when you can get the geometry right** — a wrong schematic is worse than none on a rigorous deck. For things easy to mis-draw (3-D surfaces, real curvature, circle packings), prefer (4).
4. An **openly-licensed** external image (public domain / CC0 / CC BY), downloaded locally, credited on-slide, with provenance recorded. **Never embed a copyrighted paper/journal figure — cite/link it instead.** Full discipline (Commons API workflow, license table, credits ledger, height-bounded inclusion): [references/images/external-figures-licensing.md](references/images/external-figures-licensing.md).

For image-heavy slides, run `python tools/layout_optimizer.py suggest --img W:H --cards N`. Use [autobeamer-layout](../autobeamer-layout/SKILL.md) for layout and [autobeamer-tikz](../autobeamer-tikz/SKILL.md) for diagrams. Leave no image request `open`.

### Figure proposal & external figure database (search-first; draft is text-only)

The draft is **pure text**; figures are proposed, sourced, and inserted around it via
`tools/figure_search.py` (Commons/Openverse, license-filtered, dependency-free) and a per-deck
**figure DB** `assets/<deck>/figures_db.json`. Sources live in `tools/figure_sources.json`
(enable/disable; `sources --ping --disable-unreachable` drops dead ones).

1. **STATIC (Wave 1, during planning):** for each *planned* figure in the structure plan, search
   the openly-licensed sources and record candidates in the figure DB **before drafting**:
   ```bash
   python tools/figure_search.py sources --ping
   python tools/figure_search.py search --query "<key idea>" --limit 6      # Commons + Openverse
   python tools/figure_search.py db-add --db assets/<deck>/figures_db.json --status candidate ...
   ```
2. **DYNAMIC (Wave 2, while drafting text):** the draft only emits image *requests* (`<slide, need>`)
   — no figures yet. When a new need appears, search again and add fresh candidates to the same DB.
3. **INSERT (Wave 3, after the text is done):** adopt one candidate per slot, fetch it, embed,
   credit, and verify:
   ```bash
   python tools/figure_search.py fetch --url <thumb_url> --out assets/<deck>/<name>.png
   magick assets/<deck>/<name>_orig.png -trim +repage -bordercolor white -border 12 assets/<deck>/<name>.png
   python tools/figure_search.py db-add --db assets/<deck>/figures_db.json --status adopted ... --slide "<title>"
   python tools/figure_search.py db-credits --db assets/<deck>/figures_db.json --latex   # on-slide credit lines
   ```
   Bound the image by `height=` (not width), render the page, and **visually verify** it. A sourced
   figure is checked the same way TikZ is. Full discipline + the vetted source table:
   [references/images/external-figures-licensing.md](references/images/external-figures-licensing.md).

**Search first, TikZ last.** Only draw TikZ when the search genuinely fails, and then the
render + self + Codex visual double-check is mandatory (autobeamer-tikz Rule 0).

## Quality Gate

After each draft batch:
```bash
./build.sh deck-name
python tools/validate_deck.py static deck.tex --mode MODE
python tools/check_layout.py deck.tex build/deck.log --advise
```

**Between Wave 2 and Wave 3** the leader runs the [alignment check](references/validation/alignment-check.md): does the draft still match the plan and the original demands (sections, objectives, planned figures, every image request resolved, mode fidelity)? On drift, return to the Drafter before polishing.

Before delivery (Wave 3):
- Compile with XeLaTeX; confirm zero `Overfull \vbox` (split or scale a *figure*, never shrink body text).
- Run static validation and layout audit.
- Run [autobeamer-validate](../autobeamer-validate/SKILL.md) `visual-check` on the PDF, especially every frame with blocks and every embedded figure.
- Use [autobeamer-review](../autobeamer-review/SKILL.md) with the matching mode rubric.

**Role-simulation review is a HARD gate, not optional** (for any teaching/publishable deck):
- Run [autobeamer-review](../autobeamer-review/SKILL.md) `excellence` (Content Expert · Design Reviewer · Audience Advocate) **and** `devils-advocate` **and** `pedagogy`, then **fix what they find before declaring done.** Mechanical gates (compile/validate/overflow) judge *format*; only this gate judges *whether it teaches*.
- For substantial decks, run the perspectives as **parallel subagents** (a council), and include an **independent voice** (a different model via `codex:codex-rescue`). The skill's default is solo-in-one-pass; escalate to the council whenever the deck matters or the user asks.
- **Run the council on the PLAN/storyboard first, before drafting** — catching a bad spine is far cheaper than catching N bad slides. A converged council critique of the question-spine is the highest-leverage check in the whole pipeline.

**Publishable / educational-grade gate** (apply when the deck must be shippable):
- **Figures:** every non-original figure is openly licensed (PD / CC0 / CC BY), downloaded locally, credited on-slide **and** in `assets/<deck>/CREDITS.md`, and visually verified to render uncropped. No copyrighted paper/journal figures. See [references/images/external-figures-licensing.md](references/images/external-figures-licensing.md).
- **Rigor:** every theorem is proven in-deck **or** carries a working citation link — no hand-wavy sketches passed off as proofs. See [references/writing/rigor-and-citations.md](references/writing/rigor-and-citations.md).
- **Links:** every external URL returns HTTP 200 — verify by `curl --proxy http://127.0.0.1:8888 -o /dev/null -w '%{http_code}'` before shipping; never ship an unverified or fabricated link.

## Reference Index

| Need | Reference |
|------|-----------|
| Full creation workflow | [references/workflows/full-create-guide.md](references/workflows/full-create-guide.md) |
| English prose style (the draft you write) | [references/writing/en-technical-style.md](references/writing/en-technical-style.md) |
| Chinese technical style (En→Zh translate pass) | [references/writing/zh-technical-style.md](references/writing/zh-technical-style.md) |
| Rigor & citations (theorem decks: prove-or-link) | [references/writing/rigor-and-citations.md](references/writing/rigor-and-citations.md) |
| External figures — licensing & sourcing | [references/images/external-figures-licensing.md](references/images/external-figures-licensing.md) |
| Passive-study mode | [references/modes/passive-study.md](references/modes/passive-study.md) |
| Active-Socratic mode | [references/modes/active-socratic.md](references/modes/active-socratic.md) |
| Academic-presentation reference | [references/modes/academic-presentation.md](references/modes/academic-presentation.md) |
| Source-document-first images | [references/images/source-document-first.md](references/images/source-document-first.md) |
| Image index (figure adoption) | [references/images/image-index.md](references/images/image-index.md) |
| Validation mode gates | [references/validation/mode-gates.md](references/validation/mode-gates.md) |
| Environment doctor / dep gating | [references/validation/env-doctor.md](references/validation/env-doctor.md) |
| Anti-drift alignment check | [references/validation/alignment-check.md](references/validation/alignment-check.md) |
| Wave 1 — planner subagent | [agents/autobeamer-planner.md](../../agents/autobeamer-planner.md) |
| Wave 2 — drafter subagent | [agents/autobeamer-drafter.md](../../agents/autobeamer-drafter.md) |
| Wave 3 — finisher subagent | [agents/autobeamer-finisher.md](../../agents/autobeamer-finisher.md) |
| Layout optimization | [autobeamer-layout](../autobeamer-layout/SKILL.md) |
| Build/compile errors | [autobeamer-build](../autobeamer-build/SKILL.md) |
| Review/audit | [autobeamer-review](../autobeamer-review/SKILL.md) |
| Automated validation / visual-check | [autobeamer-validate](../autobeamer-validate/SKILL.md) |
| TikZ diagrams | [autobeamer-tikz](../autobeamer-tikz/SKILL.md) |
| CJK fonts / Chinese deck setup | [autobeamer-build](../autobeamer-build/SKILL.md) (CJK Fonts section) |
