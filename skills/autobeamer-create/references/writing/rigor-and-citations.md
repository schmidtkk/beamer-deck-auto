# Rigor & citations — for theorem-bearing decks

Load this whenever the deck states theorems or claims a "rigorous / theorem-proof" level. A
reader who actually checks will reject a compressed one-line "sketch" dressed up as a proof, and
will not trust an asserted theorem with no source. The rule is simple: **prove it, or link it —
and verify the link.**

## Proofs-or-cite (no third option)

Every non-trivial result is in exactly one of two states:

1. **Proven in-deck.** Show the derivation step by step to a boxed result — the level a reader
   can follow without faith. Prefer to **fully prove the special case the deck actually uses**,
   even when the general theorem is only cited. (Example: cite Theorema Egregium in general, but
   *derive* `K = -e^{-2u}Δu` in isothermal coordinates in full, because that identity is the one
   the rest of the deck runs on.)
2. **Cited with a working link.** If the full proof is genuinely a chapter (uniformization,
   Ricci-flow convergence, Korn–Lichtenstein, discrete Hodge, Chow–Luo convexity), state the
   theorem cleanly and put a clickable citation next to it:
   ```latex
   \href{https://en.wikipedia.org/wiki/Theorema_Egregium}{Theorema Egregium} ; do Carmo \S4-3
   ```
   Label it honestly — "Full proof (cited, not sketched)" — so the reader knows it is a pointer,
   not a proof. Give a canonical source (textbook section or paper) **and** an open link
   (Wikipedia / arXiv / DOI) so the claim is checkable for free.

What is **not** acceptable: a hand-wavy "Sketch: A ⟹ B ⟹ done" with no derivation and no link.
That reads as hand-waving and is the fastest way to lose a rigorous reader.

## Verify every link before shipping

Fabricated or dead links destroy trust faster than a missing one. Check each URL returns 200
(proxy required for egress):

```bash
for u in <url1> <url2> ...; do
  echo "$(curl -q --proxy http://127.0.0.1:8888 -sL -o /dev/null -w '%{http_code}' --max-time 25 "$u")  $u"
done
```

Any non-200 → fix or drop the link. The References slides carry real URLs; standard Wikipedia
article titles (`Uniformization_theorem`, `Ricci_flow`, `Gaussian_curvature`, `Hodge_theory`,
`Isothermal_coordinates`, `Quasiconformal_mapping`, `Circle_packing_theorem`, `Angular_defect`,
`Gauss–Bonnet_theorem`) are stable, but **still verify** — do not assume.

## Faithfulness

Base every claim on the source or a real derivation. Missing info → "Not stated in the source."
Keep stated results separate from inference; never overclaim. When citing 苏剑林's kexue corpus,
cite `[archives/XXXX]` only when the corpus actually returns a relevant card.
