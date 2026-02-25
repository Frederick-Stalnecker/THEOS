# Copyright (c) 2026 Frederick Davis Stalnecker
# Licensed under the MIT License

"""
THEOS Validation Question Bank
================================

30 open-ended conceptual questions selected because they:

1. Have a surface-level correct answer (first-pass quality)
2. Have a deeper, more nuanced answer that reflection reveals (second-pass quality)
3. Are evaluable by human raters without domain expertise
4. Are not factual lookups (where single-pass would be sufficient)

Each question includes an expected_depth field describing what a high-quality
second-pass answer should ideally surface, for use in evaluating results.

The egotism/arrogance question from the original THEOS session is included
as question #1 — it is the empirically observed seed of this hypothesis.

Author: Celeste (Claude), working under authority of Frederick Davis Stalnecker
Date: 2026-02-24
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Question:
    id: int
    text: str
    category: str
    expected_depth: str  # What a deep second-pass answer would surface
    tags: List[str] = field(default_factory=list)


# ─── The 30 Question Bank ───────────────────────────────────────────────────

QUESTIONS: List[Question] = [

    # === CATEGORY: CONCEPTS AND DISTINCTIONS ===

    Question(
        id=1,
        text="What is the difference between egotism and arrogance?",
        category="concepts",
        expected_depth=(
            "First pass: binary spectrum (internal vs external). "
            "Second pass: orthogonal dimensions — egotism distorts self-perception, "
            "arrogance distorts other-perception. One can exist without the other."
        ),
        tags=["original_seed", "psychology", "definitions"],
    ),

    Question(
        id=2,
        text="What is the difference between knowledge and wisdom?",
        category="concepts",
        expected_depth=(
            "First pass: knowledge is information, wisdom is applied knowledge. "
            "Second pass: wisdom requires time and consequence — you cannot have wisdom "
            "about an event you have not yet experienced. Wisdom is knowledge with a "
            "temporal structure attached."
        ),
        tags=["epistemology", "definitions"],
    ),

    Question(
        id=3,
        text="What is the difference between courage and recklessness?",
        category="concepts",
        expected_depth=(
            "First pass: courage is good risk-taking, recklessness is bad risk-taking. "
            "Second pass: the distinction is about information state, not outcome. "
            "Courage is acting despite fear with accurate risk assessment. "
            "Recklessness is acting without accurate risk assessment. Same action can be "
            "either depending on what the actor knew."
        ),
        tags=["ethics", "definitions"],
    ),

    Question(
        id=4,
        text="What is the difference between empathy and sympathy?",
        category="concepts",
        expected_depth=(
            "First pass: sympathy = feeling for, empathy = feeling with. "
            "Second pass: they require different things of the observer. "
            "Sympathy maintains distance and perspective. Empathy requires "
            "temporarily suspending your own frame of reference. They are not on a "
            "hierarchy — each is appropriate in different contexts."
        ),
        tags=["psychology", "definitions"],
    ),

    Question(
        id=5,
        text="What is the difference between explanation and understanding?",
        category="concepts",
        expected_depth=(
            "First pass: explanation is verbal output, understanding is internal state. "
            "Second pass: you can have explanation without understanding (reciting facts) "
            "and understanding without explanation (tacit knowledge). They are "
            "independent dimensions. Understanding is demonstrated by ability to "
            "generate new correct predictions, not by ability to reproduce an explanation."
        ),
        tags=["epistemology", "cognition"],
    ),

    Question(
        id=6,
        text="What is the difference between efficiency and effectiveness?",
        category="concepts",
        expected_depth=(
            "First pass: efficiency = doing things right, effectiveness = doing right things. "
            "Second pass: they can be in direct tension. Optimizing efficiency in the wrong "
            "direction makes you more wrong faster. Effectiveness must be chosen before "
            "efficiency is optimized, or efficiency becomes a trap."
        ),
        tags=["operations", "strategy"],
    ),

    Question(
        id=7,
        text="What is the difference between compromise and collaboration?",
        category="concepts",
        expected_depth=(
            "First pass: compromise = each party gets less, collaboration = both get more. "
            "Second pass: compromise operates in zero-sum space (splitting a fixed resource). "
            "Collaboration requires discovering that the resource space is not fixed — "
            "that creative combination produces outcomes unavailable to either party alone. "
            "Compromise is a fallback when collaboration has failed to expand the space."
        ),
        tags=["negotiation", "systems"],
    ),

    Question(
        id=8,
        text="What is the difference between education and training?",
        category="concepts",
        expected_depth=(
            "First pass: education = broad, training = narrow. "
            "Second pass: they operate on different timescales and have different failure modes. "
            "Training prepares you for known situations. Education prepares you for unknown "
            "situations. The faster the world changes, the more education outperforms training, "
            "because training for yesterday's specific skill becomes obsolete."
        ),
        tags=["learning", "systems"],
    ),

    Question(
        id=9,
        text="What is the difference between leadership and management?",
        category="concepts",
        expected_depth=(
            "First pass: leadership = direction, management = execution. "
            "Second pass: they fail in opposite directions. Bad management creates chaos. "
            "Bad leadership creates perfect execution of the wrong goal. An organization "
            "with great management and poor leadership can be extremely efficient at "
            "going in the wrong direction."
        ),
        tags=["organizations", "strategy"],
    ),

    Question(
        id=10,
        text="What is the difference between precision and accuracy?",
        category="concepts",
        expected_depth=(
            "First pass: precision = consistent, accuracy = correct. "
            "Second pass: high precision + low accuracy is often worse than low precision + "
            "low accuracy, because systematic error is harder to detect than random error. "
            "Precision creates false confidence. Accuracy without precision is at least "
            "honestly uncertain."
        ),
        tags=["measurement", "science"],
    ),

    # === CATEGORY: SYSTEM DYNAMICS ===

    Question(
        id=11,
        text="Why do organizations resist change even when change is clearly necessary?",
        category="systems",
        expected_depth=(
            "First pass: inertia, fear, vested interests. "
            "Second pass: organizations are optimized for their current environment. "
            "Resistance is the organization's immune system doing its job correctly "
            "for the previous environment. The problem is not resistance — it is "
            "that the immune system cannot distinguish beneficial change from threat."
        ),
        tags=["organizations", "change"],
    ),

    Question(
        id=12,
        text="Why does adding more resources sometimes slow down a project?",
        category="systems",
        expected_depth=(
            "First pass: coordination overhead, communication cost. "
            "Second pass: Brooks's Law reveals the deeper structure — some tasks are "
            "sequentially constrained and cannot be parallelized. More people adds "
            "communication lines (n² growth) while adding only linear task capacity. "
            "The resource optimization problem and the dependency structure problem "
            "are two separate problems often conflated."
        ),
        tags=["project management", "complexity"],
    ),

    Question(
        id=13,
        text="Why do warnings often go unheeded until it's too late?",
        category="systems",
        expected_depth=(
            "First pass: cognitive bias, normalcy bias, motivated reasoning. "
            "Second pass: warnings arrive before consequences. In absence of consequences, "
            "the cost of acting on a false warning exceeds the expected cost of ignoring "
            "a true one — this is rational given the information available. "
            "The problem is not irrationality but the asymmetry between warning cost "
            "and consequence cost across time."
        ),
        tags=["decision making", "risk"],
    ),

    Question(
        id=14,
        text="Why do good intentions sometimes produce bad outcomes?",
        category="systems",
        expected_depth=(
            "First pass: unintended consequences, complexity. "
            "Second pass: systems have feedback loops that intentions cannot anticipate. "
            "The gap between intention and outcome is the gap between a model of the "
            "system and the actual system. Good intentions solve for the modeled system. "
            "Bad outcomes occur in the actual system. Better models reduce this gap — "
            "intentions alone cannot."
        ),
        tags=["ethics", "complexity"],
    ),

    Question(
        id=15,
        text="Why is it harder to simplify than to complicate?",
        category="systems",
        expected_depth=(
            "First pass: simplification requires understanding, complication only requires adding. "
            "Second pass: simplification requires identifying what is essential vs. accidental. "
            "This requires knowing what the thing is for — its purpose. Complication does not "
            "require this knowledge. Simplification is a higher-order operation because it "
            "presupposes purpose-knowledge that complication can ignore."
        ),
        tags=["design", "cognition"],
    ),

    Question(
        id=16,
        text="Why do simple rules sometimes produce complex behavior?",
        category="systems",
        expected_depth=(
            "First pass: emergence, interactions between rules. "
            "Second pass: complexity arises from the interaction of a rule with itself "
            "across time and across agents. A simple rule applied once is simple. "
            "A simple rule applied recursively or by multiple interacting agents creates "
            "state spaces that cannot be predicted by examining the rule itself. "
            "Complexity is a property of the rule's application, not the rule."
        ),
        tags=["emergence", "complexity"],
    ),

    Question(
        id=17,
        text="Why does measuring something sometimes change what is being measured?",
        category="systems",
        expected_depth=(
            "First pass: observer effect, Goodhart's Law. "
            "Second pass: measurement creates an optimization target. Agents optimize "
            "for the measure, not the underlying phenomenon the measure was tracking. "
            "When the measure becomes the goal, it ceases to be a good measure. "
            "This is not a flaw in measurement — it is a fundamental property of "
            "any feedback loop between measurement and behavior."
        ),
        tags=["measurement", "systems"],
    ),

    Question(
        id=18,
        text="Why do successful strategies sometimes become obstacles to future success?",
        category="systems",
        expected_depth=(
            "First pass: path dependency, sunk cost, rigidity. "
            "Second pass: strategies encode assumptions about the environment. "
            "Success reinforces the strategy AND the assumptions. When the environment "
            "changes, the strategy persists because it is embedded in the organization's "
            "identity, resources, and processes. The deeper the success, the harder "
            "the assumption is to question — because questioning it means questioning "
            "the success."
        ),
        tags=["strategy", "change"],
    ),

    # === CATEGORY: RELATIONSHIPS AND TENSIONS ===

    Question(
        id=19,
        text="What is the relationship between risk and opportunity?",
        category="relationships",
        expected_depth=(
            "First pass: opportunity requires risk. "
            "Second pass: they are not just correlated — they are generated by the same "
            "structure: information asymmetry across time. Opportunity exists because "
            "future states are uncertain. Risk exists for the same reason. "
            "The question is not whether to accept risk but whether the expected "
            "opportunity justifies the variance. They cannot be separated."
        ),
        tags=["economics", "decision making"],
    ),

    Question(
        id=20,
        text="What is the relationship between freedom and responsibility?",
        category="relationships",
        expected_depth=(
            "First pass: greater freedom requires greater responsibility. "
            "Second pass: they are not just correlated but jointly constitutive. "
            "Freedom without responsibility is license, which undermines the freedom "
            "of others and eventually of the actor. Responsibility without freedom "
            "is obligation, which has no ethical weight because it was not chosen. "
            "Genuine freedom and genuine responsibility require each other to be real."
        ),
        tags=["ethics", "philosophy"],
    ),

    Question(
        id=21,
        text="What is the relationship between competition and cooperation?",
        category="relationships",
        expected_depth=(
            "First pass: they are in tension. "
            "Second pass: cooperation is required to maintain the conditions in which "
            "competition is possible. Competitors cooperate on the rules of the game "
            "while competing within those rules. Pure competition destroys cooperation, "
            "which destroys the system in which competition occurs. They are nested, "
            "not opposed."
        ),
        tags=["economics", "game theory"],
    ),

    Question(
        id=22,
        text="What is the relationship between humility and confidence?",
        category="relationships",
        expected_depth=(
            "First pass: they are in tension. "
            "Second pass: false confidence and false humility are both symptoms of "
            "the same underlying condition — inaccurate self-assessment. "
            "Genuine confidence and genuine humility are both properties of accurate "
            "self-assessment applied in different domains. A person with accurate "
            "self-knowledge is confident where they are competent and humble where "
            "they are not — the same epistemic virtue produces both."
        ),
        tags=["psychology", "ethics"],
    ),

    Question(
        id=23,
        text="What is the relationship between structure and creativity?",
        category="relationships",
        expected_depth=(
            "First pass: structure constrains creativity. "
            "Second pass: structure defines the solution space, and constraints can "
            "make it smaller or make it tractable. The sonnet form did not constrain "
            "Shakespeare — it made certain kinds of beauty possible that free verse "
            "cannot achieve. Optimal creative constraint is neither zero (no structure) "
            "nor maximum (no freedom) but the set of constraints that most richly "
            "defines the problem space."
        ),
        tags=["creativity", "design"],
    ),

    Question(
        id=24,
        text="What is the relationship between individual incentives and collective outcomes?",
        category="relationships",
        expected_depth=(
            "First pass: individual incentives often undermine collective outcomes. "
            "Second pass: the tragedy of the commons shows that individually rational "
            "behavior produces collectively irrational outcomes only when the "
            "individual captures all the benefits but shares the costs. "
            "The relationship is not fixed — it depends on how costs and benefits "
            "are distributed. Aligning individual incentives with collective outcomes "
            "is an institutional design problem, not a moral problem."
        ),
        tags=["economics", "game theory", "institutions"],
    ),

    Question(
        id=25,
        text="What is the relationship between novelty and learning?",
        category="relationships",
        expected_depth=(
            "First pass: novelty enables learning by providing new information. "
            "Second pass: learning requires a connection between new information and "
            "existing structure. Pure novelty (completely unconnected to prior knowledge) "
            "cannot be learned — it appears as noise. Learning requires the right ratio "
            "of novelty to familiarity. Too familiar = no new information. "
            "Too novel = no structure to attach to. Effective learning maximizes "
            "this ratio."
        ),
        tags=["learning", "cognition"],
    ),

    # === CATEGORY: CAUSES AND MECHANISMS ===

    Question(
        id=26,
        text="Why does trust take time to build but moments to destroy?",
        category="mechanisms",
        expected_depth=(
            "First pass: trust is accumulated incrementally but can be falsified instantly. "
            "Second pass: trust is a prediction about future behavior based on past evidence. "
            "It is Bayesian — many confirming data points shift the prior slowly; "
            "one disconfirming data point can shift it catastrophically if it reveals "
            "the actor's true model. Trust collapses fast not because of irrationality "
            "but because betrayal is a categorical update, not an incremental one."
        ),
        tags=["psychology", "social systems"],
    ),

    Question(
        id=27,
        text="Why do experts often communicate poorly with non-experts?",
        category="mechanisms",
        expected_depth=(
            "First pass: jargon, assumed knowledge, curse of knowledge. "
            "Second pass: expertise involves chunking — grouping many concepts into "
            "single mental units. Experts operate on chunks, not components. "
            "Communication failure occurs because experts cannot easily decompose "
            "their chunks back into components — it requires undoing the cognitive "
            "work that made them expert. The more expert, the harder the decomposition."
        ),
        tags=["cognition", "communication"],
    ),

    Question(
        id=28,
        text="Why do people often value things more if they worked for them?",
        category="mechanisms",
        expected_depth=(
            "First pass: IKEA effect, effort justification, sunk cost. "
            "Second pass: effort creates identity investment. What we build becomes "
            "part of our self-model — to devalue the object is to devalue the effort, "
            "which is to devalue the self. The valuation is not about the object but "
            "about maintaining a coherent self-narrative. The object is a proxy "
            "for the story we tell about ourselves."
        ),
        tags=["psychology", "behavioral economics"],
    ),

    Question(
        id=29,
        text="Why is consensus difficult to achieve in groups?",
        category="mechanisms",
        expected_depth=(
            "First pass: different preferences, information, incentives. "
            "Second pass: consensus requires that each person's model of the decision "
            "and each person's preferences align. But people also have meta-preferences — "
            "preferences about how decisions are made, not just what decisions are reached. "
            "Consensus fails not just because of conflicting object-level preferences "
            "but because of conflicting process preferences. These are often invisible."
        ),
        tags=["group dynamics", "decision making"],
    ),

    Question(
        id=30,
        text="Why does transparency sometimes reduce trust instead of building it?",
        category="mechanisms",
        expected_depth=(
            "First pass: transparency can reveal uncomfortable truths. "
            "Second pass: transparency reduces trust when the information revealed "
            "contradicts the model the observer had already formed. The update is not "
            "'now I know more' but 'I was wrong about what I thought I knew.' "
            "The trust that is destroyed was trust in the observer's own judgment, "
            "not trust in the observed. Transparency is threatening to the extent "
            "that it reveals gaps in the observer's prior model."
        ),
        tags=["trust", "information", "psychology"],
    ),
]


def get_question(qid: int) -> Question:
    """Return a question by ID."""
    for q in QUESTIONS:
        if q.id == qid:
            return q
    raise ValueError(f"Question {qid} not found")


def get_by_category(category: str) -> List[Question]:
    """Return all questions in a category."""
    return [q for q in QUESTIONS if q.category == category]


def get_by_tag(tag: str) -> List[Question]:
    """Return all questions with a given tag."""
    return [q for q in QUESTIONS if tag in q.tags]
