# Passive-Study Mode

Use `passive-study` when the deck itself must teach comprehensively. The target learner may be a strong researcher but may lack field priors, background vocabulary, or local notation.

## Learning Philosophy

The deck is a generous teacher. It shields the learner from avoidable frustration by explaining background before it becomes a blocker, while still preserving rigor and intellectual taste.

> **English decks:** also load [../writing/en-technical-style.md](../writing/en-technical-style.md) —
> one relationship per line, define-on-first-use, mechanism before formula, equations as
> evidence, takeaway = one new consequence. English runs longer than Chinese; edit tighter,
> then split (never shrink).
>
> **Rigorous / theorem decks:** load [../writing/rigor-and-citations.md](../writing/rigor-and-citations.md) —
> prove the special case the deck uses in full; cite deep theorems with a verified link
> (never a hand-wavy sketch). For figures that are easy to mis-draw, source an openly-licensed
> one ([../images/external-figures-licensing.md](../images/external-figures-licensing.md)) instead of shipping a wrong TikZ.

## Authoring Rules

- Make the material self-contained: define prerequisites, notation, and domain conventions before relying on them.
- Start each concept with why it matters, then give the formal object, then give a worked example.
- Add background context when a cross-disciplinary learner would otherwise need to stop and search.
- Use complete sentences where needed; passive-study decks are readable without a speaker.
- Include common pitfalls and beginner misconceptions, but keep the tone matter-of-fact.
- Provide exercises with hints and backup solutions, but do not make exercises the main delivery mechanism.

## Acceptance Gates

- Every definition has a motivation and a worked example within two slides.
- Every major theorem or algorithm has prerequisite reminders and a concrete example.
- The deck has a glossary or notation summary when more than ten symbols or specialized terms appear.
- The learner can reconstruct the local background without opening external references.
