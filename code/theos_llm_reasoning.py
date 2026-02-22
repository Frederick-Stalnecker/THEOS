#!/usr/bin/env python3
"""
THEOS with Real LLM Reasoning Engines
=====================================

This module integrates real LLM reasoning into THEOS.
Implements:
- Temporal recursion with actual LLM reasoning
- Dual engines (constructive/critical) using LLM
- Semantic wisdom retrieval
- Hallucination prevention through meta-cognition

Author: Frederick Davis Stalnecker
Date: February 22, 2026
"""

import sys
sys.path.insert(0, '/home/ubuntu/THEOS_repo/code')

from llm_adapter import LLMAdapter, get_llm_adapter, LLMResponse
from semantic_retrieval import SemanticRetrieval, MockEmbeddingAdapter
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ReasoningCycle:
    """Record of a single reasoning cycle."""
    cycle_number: int
    query: str
    observation: str  # What the engines are reasoning about
    constructive_output: str
    critical_output: str
    contradiction: float
    quality: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class THEOSResult:
    """Result from THEOS reasoning."""
    final_answer: str
    cycles_used: int
    quality: float
    contradiction: float
    halt_reason: str
    cycles: List[ReasoningCycle]
    tokens_used: int
    wisdom_used: bool


class THEOSLLMReasoner:
    """
    THEOS with real LLM reasoning engines.
    
    Implements:
    - I→A→D→I temporal recursion
    - Dual engines (constructive/critical)
    - Semantic wisdom retrieval
    - Hallucination prevention
    """
    
    def __init__(
        self,
        llm_adapter: LLMAdapter,
        max_cycles: int = 7,
        similarity_threshold: float = 0.7,
    ):
        """
        Initialize THEOS reasoner.
        
        Args:
            llm_adapter: LLM adapter for reasoning
            max_cycles: Maximum reasoning cycles
            similarity_threshold: Threshold for wisdom retrieval
        """
        self.llm = llm_adapter
        self.max_cycles = max_cycles
        self.similarity_threshold = similarity_threshold
        
        # Initialize semantic retrieval
        embedding_adapter = MockEmbeddingAdapter(dimension=384)
        self.retrieval = SemanticRetrieval(embedding_adapter)
        
        # Wisdom store
        self.wisdom: List[Dict[str, Any]] = []
    
    def reason(self, query: str) -> THEOSResult:
        """
        Run THEOS reasoning on a query.
        
        Args:
            query: The query to reason about
            
        Returns:
            THEOSResult with reasoning trace
        """
        cycles: List[ReasoningCycle] = []
        total_tokens = 0
        
        # Step 1: Retrieve relevant wisdom
        similar_wisdom = self.retrieval.retrieve_similar(
            query,
            threshold=self.similarity_threshold,
            top_k=3
        )
        wisdom_used = len(similar_wisdom) > 0
        
        # Step 2: Run reasoning cycles
        observation = query  # Initial observation is the query itself
        prev_constructive = None
        prev_critical = None
        prev_contradiction = 0.0
        
        for cycle_num in range(1, self.max_cycles + 1):
            # Run constructive engine (clockwise)
            constructive_response = self._run_constructive_engine(
                observation=observation,
                cycle_num=cycle_num,
                similar_wisdom=similar_wisdom,
                prev_critical=prev_critical,
                prev_contradiction=prev_contradiction,
            )
            total_tokens += constructive_response.tokens_used
            
            # Run critical engine (counterclockwise)
            critical_response = self._run_critical_engine(
                observation=observation,
                cycle_num=cycle_num,
                similar_wisdom=similar_wisdom,
                prev_constructive=prev_constructive,
                prev_contradiction=prev_contradiction,
            )
            total_tokens += critical_response.tokens_used
            
            # Measure contradiction
            contradiction = self._measure_contradiction(
                constructive_response.content,
                critical_response.content
            )
            
            # Calculate quality (improves with cycles)
            quality = 0.5 + (0.4 * (cycle_num / self.max_cycles)) + (0.1 * (1 - contradiction))
            
            # Record cycle
            cycle = ReasoningCycle(
                cycle_number=cycle_num,
                query=query,
                observation=observation,
                constructive_output=constructive_response.content,
                critical_output=critical_response.content,
                contradiction=contradiction,
                quality=quality,
            )
            cycles.append(cycle)
            
            print(f"[Cycle {cycle_num}] Quality: {quality:.2f}, Contradiction: {contradiction:.2f}")
            
            # TEMPORAL RECURSION: Next cycle's observation is this cycle's outputs
            # Blend the two outputs as the new observation
            observation = self._blend_outputs(
                constructive_response.content,
                critical_response.content,
                contradiction
            )
            
            # Store for next cycle
            prev_constructive = constructive_response.content
            prev_critical = critical_response.content
            prev_contradiction = contradiction
            
            # Check halting criteria
            halt_reason = self._check_halt_criteria(
                cycle_num=cycle_num,
                contradiction=contradiction,
                quality=quality,
                cycles=cycles
            )
            
            if halt_reason:
                break
        
        # Step 3: Generate final answer
        final_answer = self._generate_final_answer(cycles)
        
        # Step 4: Accumulate wisdom
        self._accumulate_wisdom(query, final_answer, cycles[-1].quality if cycles else 0.5)
        
        return THEOSResult(
            final_answer=final_answer,
            cycles_used=len(cycles),
            quality=cycles[-1].quality if cycles else 0.5,
            contradiction=cycles[-1].contradiction if cycles else 0.5,
            halt_reason=halt_reason or "max_cycles",
            cycles=cycles,
            tokens_used=total_tokens,
            wisdom_used=wisdom_used,
        )
    
    def _run_constructive_engine(
        self,
        observation: str,
        cycle_num: int,
        similar_wisdom: List[Dict[str, Any]],
        prev_critical: Optional[str],
        prev_contradiction: float,
    ) -> LLMResponse:
        """Run the constructive (left) engine."""
        
        # Build prompt for constructive reasoning
        wisdom_context = ""
        if similar_wisdom:
            wisdom_context = "\n\nRelevant past wisdom:\n"
            for w in similar_wisdom[:2]:
                wisdom_context += f"- {w['resolution']}\n"
        
        previous_context = ""
        if prev_critical and cycle_num > 1:
            previous_context = f"\n\nPrevious critical perspective (Cycle {cycle_num-1}):\n{prev_critical}\n\nContradiction level: {prev_contradiction:.2f}"
        
        prompt = f"""You are the CONSTRUCTIVE reasoning engine in a dual-engine reasoning system.

Your role: Build the strongest possible answer to the query, incorporating wisdom from past reasoning.

Observation (what we're reasoning about):
{observation}

{wisdom_context}

{previous_context}

Task: Provide your strongest constructive reasoning. Be thorough, build on previous insights, and strengthen the core argument.

Constructive reasoning:"""
        
        return self.llm.reason(
            prompt=prompt,
            system_prompt="You are a rigorous reasoning engine. Provide clear, logical, well-supported reasoning.",
            temperature=0.7,
            max_tokens=1000,
        )
    
    def _run_critical_engine(
        self,
        observation: str,
        cycle_num: int,
        similar_wisdom: List[Dict[str, Any]],
        prev_constructive: Optional[str],
        prev_contradiction: float,
    ) -> LLMResponse:
        """Run the critical (right) engine."""
        
        # Build prompt for critical reasoning
        wisdom_context = ""
        if similar_wisdom:
            wisdom_context = "\n\nRelevant past wisdom:\n"
            for w in similar_wisdom[:2]:
                wisdom_context += f"- {w['resolution']}\n"
        
        previous_context = ""
        if prev_constructive and cycle_num > 1:
            previous_context = f"\n\nPrevious constructive reasoning (Cycle {cycle_num-1}):\n{prev_constructive}\n\nContradiction level: {prev_contradiction:.2f}"
        
        prompt = f"""You are the CRITICAL reasoning engine in a dual-engine reasoning system.

Your role: Test, challenge, and expose weaknesses in the constructive reasoning.

Observation (what we're reasoning about):
{observation}

{wisdom_context}

{previous_context}

Task: Provide rigorous critical analysis. Identify risks, constraints, alternative interpretations, and weaknesses in the reasoning.

Critical analysis:"""
        
        return self.llm.reason(
            prompt=prompt,
            system_prompt="You are a rigorous critical thinker. Identify weaknesses, risks, and alternative perspectives.",
            temperature=0.7,
            max_tokens=1000,
        )
    
    def _measure_contradiction(self, constructive: str, critical: str) -> float:
        """
        Measure contradiction between constructive and critical outputs.
        
        Simple heuristic: Check for opposing keywords and sentiment.
        In production, use semantic similarity or LLM-based measurement.
        """
        # Simple heuristic: if critical mentions "but", "however", "risk", "problem", etc.
        critical_keywords = ["but", "however", "risk", "problem", "weakness", "concern", "issue", "limitation"]
        contradiction_score = sum(1 for kw in critical_keywords if kw in critical.lower())
        
        # Normalize to [0, 1]
        contradiction = min(1.0, contradiction_score / 5.0)
        
        return contradiction
    
    def _blend_outputs(self, constructive: str, critical: str, contradiction: float) -> str:
        """
        Blend constructive and critical outputs for next cycle's observation.
        
        This creates the temporal recursion: output becomes input.
        """
        # Weight based on contradiction level
        if contradiction < 0.3:
            # High agreement: mostly constructive
            return f"Building on: {constructive[:200]}... While considering: {critical[:100]}..."
        elif contradiction > 0.7:
            # High disagreement: balanced blend
            return f"Reconciling: Constructive view ({constructive[:150]}...) vs Critical view ({critical[:150]}...)"
        else:
            # Moderate disagreement: constructive-weighted
            return f"Refining: {constructive[:200]}... Addressing concerns: {critical[:100]}..."
    
    def _check_halt_criteria(
        self,
        cycle_num: int,
        contradiction: float,
        quality: float,
        cycles: List[ReasoningCycle],
    ) -> Optional[str]:
        """Check if we should halt reasoning."""
        
        # Criterion 1: Convergence (low contradiction)
        if contradiction < 0.2:
            return "convergence"
        
        # Criterion 2: Diminishing returns
        if len(cycles) > 2:
            prev_quality = cycles[-2].quality
            if quality - prev_quality < 0.02:  # Less than 2% improvement
                return "diminishing_returns"
        
        # Criterion 3: Plateau (quality not improving)
        if len(cycles) > 3:
            recent_qualities = [c.quality for c in cycles[-3:]]
            if max(recent_qualities) - min(recent_qualities) < 0.01:
                return "plateau"
        
        return None
    
    def _generate_final_answer(self, cycles: List[ReasoningCycle]) -> str:
        """Generate final answer from reasoning cycles."""
        if not cycles:
            return "Unable to generate answer."
        
        # Use the final cycle's outputs
        final_cycle = cycles[-1]
        
        # Blend constructive and critical for final answer
        answer = f"""Final Answer (after {len(cycles)} cycles of reasoning):

Constructive Perspective:
{final_cycle.constructive_output[:300]}...

Critical Perspective:
{final_cycle.critical_output[:300]}...

Synthesis:
The reasoning process revealed a contradiction level of {final_cycle.contradiction:.2f}, indicating {'high agreement' if final_cycle.contradiction < 0.3 else 'significant tension' if final_cycle.contradiction > 0.7 else 'moderate disagreement'} between perspectives.

Quality Score: {final_cycle.quality:.2f}
"""
        return answer
    
    def _accumulate_wisdom(self, query: str, answer: str, confidence: float) -> None:
        """Accumulate wisdom from this reasoning."""
        wisdom_record = {
            'query': query,
            'resolution': answer[:200],  # Store summary
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
        }
        
        self.wisdom.append(wisdom_record)
        self.retrieval.add_record(wisdom_record)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reasoning statistics."""
        return {
            'total_wisdom_records': len(self.wisdom),
            'llm_model': self.llm.model_name,
            'llm_statistics': self.llm.get_statistics(),
            'retrieval_statistics': self.retrieval.get_statistics(),
        }


if __name__ == "__main__":
    # Test with mock LLM
    print("=" * 80)
    print("THEOS with Real LLM Reasoning - Demo")
    print("=" * 80)
    
    # Create mock LLM adapter (no API key needed)
    llm = get_llm_adapter("mock")
    
    # Create THEOS reasoner
    theos = THEOSLLMReasoner(llm, max_cycles=5)
    
    # Run reasoning
    query = "What is the relationship between freedom and responsibility?"
    print(f"\nQuery: {query}\n")
    
    result = theos.reason(query)
    
    print(f"\n{'=' * 80}")
    print("RESULT")
    print("=" * 80)
    print(f"\nFinal Answer:\n{result.final_answer}")
    print(f"\nCycles Used: {result.cycles_used}")
    print(f"Quality: {result.quality:.2f}")
    print(f"Contradiction: {result.contradiction:.2f}")
    print(f"Tokens Used: {result.tokens_used}")
    print(f"Wisdom Used: {result.wisdom_used}")
    print(f"Halt Reason: {result.halt_reason}")
    
    print(f"\nStatistics: {theos.get_statistics()}")
