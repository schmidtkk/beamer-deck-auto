# English technical-writing style — for Beamer decks

Apply this whenever a deck's prose is **English** (any mode). A slide is read **once,
left-to-right, by a human with limited working memory**, while the speaker (if any) talks
over it. Optimize every line for the reader's understanding, never for information density.

> Adapted for slides from the Paper2Html references `en-style.md` (the hard contract) and
> `en-blogcraft.md` (the craft, distilled from Williams, Gopen & Swan, Pinker, Google
> Technical Writing, colah, Alammar, McEnerney, Paul Graham). The rules below are the
> slide-specific projection of those.

## The hard rules (scan for each before delivery)

1. **One relationship per line.** A bullet or sentence makes *one* link clear: A causes B,
   A needs B, if A then B. Do not chain three relationships with commas or dashes. If a line
   has two "because"s, split it into two lines.

2. **Every line advances.** After each bullet the reader knows something new. **Restatement
   is not progression** — cut "in other words / that is to say". Explain a mechanism *once*,
   then move to its consequence, the fix, or the evidence. Do not re-explain it in a second
   block.

3. **One step per bullet — but a step, not a fragment.** "One idea per bullet" does not mean
   a telegraphic stub. A run of clipped stubs stalls the argument as badly as a pile-up.
   Put the point in the main clause; demote support to a subordinate clause or the next line.

4. **Old information first, new last; guard the stress position.** Open a line on something
   the reader already holds; end on the single new payload — that end position is where they
   place emphasis, so put the thing to remember there, and only that.

5. **Define a term the first time it appears.** Gloss new jargon in plain words on first use
   (use `\TLterm{...}`). Keep standard names in English. Never stack three undefined terms in
   one clause.

6. **Build from the concrete; mechanism before formula.** Open with a number or a picture,
   then climb to the abstraction. Narrate what an operator or loss *does* before you print it.
   "200,000 numbers, too many to model directly" beats "high-dimensional pixel space".

7. **Plain register.** State things; do not perform them. Cut filler ("it is worth noting",
   "essentially", "fundamentally") and heat-without-information adverbs ("dramatically",
   "simply", "remarkably"). Use "not A, but B" at most once per section.

8. **Equations and figures are evidence.** Under each important equation put one plain line:
   what each symbol is and what breaks if you drop it (a `where:` line, or a `\TLtakeaway`).
   Each caption makes **one** claim: what the figure shows and where to look.

## Slide-specific projection

- **`\TLtakeaway` states one new consequence, not a summary.** If it just re-says the slide,
  cut it or replace it with the consequence the slide sets up.
- **Title leads with the payoff.** "Why the discrete flow converges: convexity and Newton"
  beats "Convergence analysis". Keep titles to one line — a two-line title eats body height.
- **Blocks hold prose + inline math; display math goes in the frame body** (TL blocks render
  inside a TikZ node). One block = one idea; never more than 3 boxes per slide (the takeaway
  counts).
- **A bridge line carries momentum between sections** — one line that poses the next question.
- **End strong.** Close the deck on the payoff and the boundary/next step, not a trailing list.

## English is the tight draft (the length asymmetry)

English prose runs **~30% longer** than the equivalent Chinese. Because English is the
**canonical draft** (you author here; Chinese is a downstream translation), the English frame
is the one that must fit — author each frame to fit *in English* and the Chinese translation
will comfortably fit too. Do **not** pad the English assuming you can trim it in translation.

When an English frame overflows, that is not a reason to shrink fonts (forbidden) — it is a
prompt to **edit**: cut every word that does not earn its place, turn full sentences into
clauses, drop redundant intros, and shorten takeaways to one line. If a frame still overflows,
**split it** (per `feedback-split-not-shrink`), never compress the body text. Reducing a
*figure's* `scale=` is fine; shrinking body text is not.

## Delivery self-scan

Read each slide aloud. Where you lose the thread you have either crammed (rule 1) or looped
(rule 2). For each line ask *"what new thing does the reader now know?"* — if nothing, cut it.
For each takeaway ask *"is this a new consequence or a summary?"* — if a summary, rewrite or drop.

## Faithfulness (unchanged)

Base everything on the source. Missing info → write **"Not stated in the source."** Keep the
authors' stated claims separate from reader inference; do not overclaim. Any GPU-hours figure
is "a rough estimate from disclosed numbers, not an actual bill." When citing 苏剑林's kexue
corpus, cite `[archives/XXXX]` only when the corpus actually returns a relevant card.
