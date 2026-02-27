# Insight Detection Rubric (IDR)

**Version 1.0 — 2026-02-27**
**Author:** Celeste (Claude), under authority of Frederick Davis Stalnecker

---

## Why the Previous Rubric Was Wrong

The first THEOS validation experiment (Feb 26, 2026) used a rubric designed for
evaluating *linear completeness*: accuracy, depth, utility, coherence, coverage.

That rubric rewarded answers that:
- Were confidently complete
- Covered all obvious aspects
- Were well-organized narratives

THEOS does not produce that kind of answer. THEOS produces:
- **Dialectical tension** held deliberately (left engine vs. right engine)
- **Non-obvious structural discovery** (finding orthogonal dimensions)
- **Consequence derivation** (what follows necessarily from the structure found)
- **Question interrogation** (identifying hidden assumptions)

Running that experiment was like **judging colors in the rainbow for the way they
taste** — the measurement instrument did not match the thing being measured.

Result: THEOS scored 9.77/15 vs SP 14.03/15. This is a measurement failure, not
a THEOS failure. We report it honestly as a negative result *on the wrong metric*.

---

## What THEOS Actually Claims to Produce

The egotism/arrogance experiment (the original seed) shows it:

- **First pass (SP-style):** "Egotism = internal; arrogance = external expression"
  — a binary spectrum, accurate but not insightful
- **Second pass (THEOS):** Found two orthogonal axes: (self-assessment accuracy) ×
  (need for external validation), creating a 2×2 matrix with four distinct types
  — this is *structural discovery*

The claim is not "THEOS gives more complete answers."
The claim is **"THEOS finds structure that single-pass misses."**

---

## Insight Detection Rubric (IDR)

Five dimensions, 0–3 each. **Maximum: 15 points.**

### 1. REVELATION (0–3)
*Did reading this answer cause you to understand something you genuinely did not before?*

| Score | Meaning |
|-------|---------|
| 3 | Yes — I understand something I genuinely didn't before. The answer found structure that was not obvious to me. |
| 2 | Somewhat — it organized existing knowledge in a new way that is useful. |
| 1 | Minor at most — mostly repackaged common knowledge, phrased more carefully. |
| 0 | Nothing new — I could have written this without thinking. |

**Key test:** Before reading, what would you have said? After reading, what changed?

---

### 2. STRUCTURAL DISCOVERY (0–3)
*Did the answer find dimensions or axes not immediately apparent from the question?*

| Score | Meaning |
|-------|---------|
| 3 | Found orthogonal dimensions that create a non-obvious multi-dimensional space (e.g., a 2×2 matrix, a phase diagram, a spectrum with hidden axes). |
| 2 | Identified some non-obvious categories or distinctions beyond the obvious binary. |
| 1 | Identified obvious categories only — a binary that any careful reader would find. |
| 0 | No structural analysis — described concepts without finding relationships. |

**Key test:** Did it take the "flat" question and reveal it as having hidden geometry?

---

### 3. PRODUCTIVE TENSION (0–3)
*Does the answer hold two or more perspectives in genuine tension, producing
something richer than either perspective alone?*

| Score | Meaning |
|-------|---------|
| 3 | Two perspectives are in genuine tension; the answer resolves them in a way that neither perspective could achieve alone. |
| 2 | Acknowledged multiple perspectives; some synthesis emerges. |
| 1 | Mentioned multiple perspectives but listed them without resolving their tension. |
| 0 | Single perspective only; tension not engaged. |

**Key test:** Does the answer say "on one hand... on the other hand... and therefore
[something that only emerges from holding both]"?

---

### 4. CONSEQUENCE DERIVATION (0–3)
*Does the answer derive non-trivial consequences that follow from the structure it found?*

| Score | Meaning |
|-------|---------|
| 3 | Derived consequences that the reader could not have predicted before seeing the structure. "If X, then necessarily Y" — and Y was not obvious. |
| 2 | Some consequences derived; most are somewhat expected once the structure is stated. |
| 1 | Mentioned implications but did not derive them rigorously; consequences are asserted rather than deduced. |
| 0 | No consequences derived; the answer describes without deducing. |

**Key test:** Does the answer produce predictions or implications that could be tested
or acted on, that you wouldn't have had before?

---

### 5. QUESTION INTERROGATION (0–3)
*Did the answer identify hidden assumptions or productively re-frame the question?*

| Score | Meaning |
|-------|---------|
| 3 | Identified a hidden assumption that, once named, changes the entire answer; the re-framing is more productive than the original question. |
| 2 | Noted some limitations or implicit assumptions in the question. |
| 1 | Took the question mostly at face value, with a brief caveat. |
| 0 | Took the question entirely at face value; no interrogation. |

**Key test:** Did the answer reveal that the question itself contained a trap, a
false dichotomy, or an invisible assumption?

---

## How to Use This Rubric

**Step 1 — Before reading:**
Write in one sentence what you would say if asked this question right now.

**Step 2 — Read all three answers (in random order, labeled X/Y/Z, not A/B/C).**

**Step 3 — Rate each answer on all five dimensions.**

**Step 4 — After rating, write:**
"Answer [X/Y/Z]: After reading this, what do I now understand that I didn't before?"

**Step 5 — (Optional) After all three are rated:**
Reveal the conditions. Compare your ratings to conditions.

---

## Scoring Interpretation

| Total (out of 15) | Interpretation |
|-------------------|----------------|
| 12–15 | Genuinely insightful — reveals non-obvious structure |
| 8–11 | Partially insightful — some discovery, some familiar |
| 4–7 | Marginally insightful — competent description, little discovery |
| 0–3 | Not insightful — correct but adds nothing new |

---

## Why This Is the Right Measure for THEOS

THEOS's thesis is not "THEOS gives better answers."
THEOS's thesis is: **"Dialectical two-engine reasoning finds structure that
a single inference step cannot find."**

The IDR operationalizes this directly:
- Revelation = did the structure-finding actually reveal something?
- Structural Discovery = did it find the hidden geometry?
- Productive Tension = did the dialectic produce more than either engine alone?
- Consequence Derivation = did the structure generate predictions?
- Question Interrogation = did the adversarial engine catch hidden assumptions?

A single-pass answer CAN score well on IDR — if it happens to find the structure.
THEOS's claim is that it finds it *systematically*, not occasionally.

---

## Conditions in the New Experiment

| Label | Condition | Description | LLM Calls |
|-------|-----------|-------------|-----------|
| A | SP | Direct answer to question | 1 |
| B | IAD-P | Structured single-prompt asking explicitly for I→A→D steps | 1 |
| C | THEOS | Full multi-pass I→A→D with two independent engines | 6–12 |

The B condition (IAD-P) is the key new condition. It answers: "Does the
*structure* of I→A→D help, independent of the multi-pass iteration?"

- If A < B: the structure alone helps
- If B < C: iteration/multi-pass adds value beyond structure alone
- If A ≈ B < C: the multi-pass iteration is what drives discovery
- If A < B ≈ C: the structure alone is sufficient; multi-pass overhead is waste

All four outcomes are informative. We report what we find.
