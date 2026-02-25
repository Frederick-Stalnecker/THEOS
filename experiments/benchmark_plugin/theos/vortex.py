"""
THEOS Plugin - Vortex Processors
Triadic reasoning through constructive and deconstructive vortices

Author: Frederick Davis Stalnecker & Manus AI
License: MIT
Version: 1.0.0
"""

import logging
from typing import Tuple
from .core import THEOSConfig


logger = logging.getLogger(__name__)


class TriadicReasoner:
    """
    Implements triadic reasoning: Inductive → Abductive → Deductive
    
    This is the core philosophical engine that processes information through
    three distinct reasoning modes to build comprehensive understanding.
    """
    
    def __init__(self, config: THEOSConfig):
        """
        Initialize TriadicReasoner.
        
        Args:
            config: THEOS configuration
        """
        self.config = config
        logger.debug("TriadicReasoner initialized")
    
    def reason(self, model, tokenizer, context: str) -> str:
        """
        Execute full triadic reasoning cycle.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            context: Input context/prompt
        
        Returns:
            Synthesized reasoning output
        """
        # Step 1: Inductive reasoning (observe patterns)
        inductive_output = self._inductive_step(model, tokenizer, context)
        
        # Step 2: Abductive reasoning (form hypotheses)
        abductive_output = self._abductive_step(model, tokenizer, context, inductive_output)
        
        # Step 3: Deductive reasoning (draw conclusions)
        deductive_output = self._deductive_step(model, tokenizer, context, abductive_output)
        
        return deductive_output
    
    def _inductive_step(self, model, tokenizer, context: str) -> str:
        """
        Inductive reasoning: Observe patterns and generalize.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            context: Input context
        
        Returns:
            Inductive reasoning output
        """
        inductive_prompt = f"""Context: {context}

Inductive Analysis (observe patterns and generalize):
"""
        
        output = self._generate(model, tokenizer, inductive_prompt)
        return output.strip()
    
    def _abductive_step(self, model, tokenizer, context: str, inductive_output: str) -> str:
        """
        Abductive reasoning: Form best explanatory hypotheses.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            context: Input context
            inductive_output: Output from inductive step
        
        Returns:
            Abductive reasoning output
        """
        abductive_prompt = f"""Context: {context}

Patterns observed: {inductive_output}

Abductive Analysis (form explanatory hypotheses):
"""
        
        output = self._generate(model, tokenizer, abductive_prompt)
        return output.strip()
    
    def _deductive_step(self, model, tokenizer, context: str, abductive_output: str) -> str:
        """
        Deductive reasoning: Draw logical conclusions.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            context: Input context
            abductive_output: Output from abductive step
        
        Returns:
            Deductive reasoning output
        """
        deductive_prompt = f"""Context: {context}

Hypotheses formed: {abductive_output}

Deductive Analysis (draw logical conclusions):
"""
        
        output = self._generate(model, tokenizer, deductive_prompt)
        return output.strip()
    
    def _generate(self, model, tokenizer, prompt: str) -> str:
        """
        Generate text using the language model.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            prompt: Input prompt
        
        Returns:
            Generated text
        """
        # Get model's max position embeddings (default 1024 for GPT-2)
        if hasattr(model, 'config'):
            max_model_length = getattr(model.config, 'n_positions', 1024)
        else:
            max_model_length = 1024  # Default for mock models
        
        # Leave room for generation (max_new_tokens)
        max_input_length = max_model_length - self.config.max_tokens
        
        # Tokenize with proper truncation
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_input_length)
        
        # Move to same device as model
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # Generate
        outputs = model.generate(
            **inputs,
            max_new_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        # Decode
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove prompt from output
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return generated_text


class ConstructiveVortex:
    """
    Constructive vortex: Builds understanding through triadic reasoning.
    
    This represents the "thesis" phase - constructing meaning and understanding
    through systematic reasoning.
    """
    
    def __init__(self, config: THEOSConfig):
        """
        Initialize ConstructiveVortex.
        
        Args:
            config: THEOS configuration
        """
        self.config = config
        self.reasoner = TriadicReasoner(config)
        logger.debug("ConstructiveVortex initialized")
    
    def process(self, model, tokenizer, prompt: str, previous_state: str = "") -> str:
        """
        Process input through constructive reasoning.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            prompt: Input prompt
            previous_state: Previous cycle's state (for refinement)
        
        Returns:
            Constructive reasoning output
        """
        # Build context
        if previous_state:
            context = f"{prompt}\n\nPrevious understanding: {previous_state}\n\nRefined constructive analysis:"
        else:
            context = prompt
        
        # Apply triadic reasoning
        output = self.reasoner.reason(model, tokenizer, context)
        
        logger.debug(f"ConstructiveVortex output: {output[:100]}...")
        return output


class DeconstructiveVortex:
    """
    Deconstructive vortex: Challenges and refines through critical analysis.
    
    This represents the "antithesis" phase - questioning assumptions and
    identifying weaknesses in the constructive understanding.
    """
    
    def __init__(self, config: THEOSConfig):
        """
        Initialize DeconstructiveVortex.
        
        Args:
            config: THEOS configuration
        """
        self.config = config
        self.reasoner = TriadicReasoner(config)
        logger.debug("DeconstructiveVortex initialized")
    
    def process(self, model, tokenizer, prompt: str, constructive_output: str, previous_state: str = "") -> str:
        """
        Process input through deconstructive reasoning.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            prompt: Original prompt
            constructive_output: Output from constructive vortex
            previous_state: Previous cycle's state (for refinement)
        
        Returns:
            Deconstructive reasoning output
        """
        # Build critical context
        if previous_state:
            context = f"""Original question: {prompt}

Constructive analysis: {constructive_output}

Previous critique: {previous_state}

Refined critical analysis (challenge assumptions, identify weaknesses):"""
        else:
            context = f"""Original question: {prompt}

Constructive analysis: {constructive_output}

Critical analysis (challenge assumptions, identify weaknesses):"""
        
        # Apply triadic reasoning with critical lens
        output = self.reasoner.reason(model, tokenizer, context)
        
        logger.debug(f"DeconstructiveVortex output: {output[:100]}...")
        return output


class VortexPair:
    """
    Manages the dual-vortex system: Constructive and Deconstructive.
    
    This is the synthesis engine that combines thesis (constructive) and
    antithesis (deconstructive) into a refined, balanced understanding.
    """
    
    def __init__(self, config: THEOSConfig):
        """
        Initialize VortexPair.
        
        Args:
            config: THEOS configuration
        """
        self.config = config
        self.constructive = ConstructiveVortex(config)
        self.deconstructive = DeconstructiveVortex(config)
        logger.debug("VortexPair initialized")
    
    def cycle(
        self,
        model,
        tokenizer,
        prompt: str,
        previous_constructive: str = "",
        previous_deconstructive: str = ""
    ) -> Tuple[str, str]:
        """
        Execute one reasoning cycle through both vortices.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            prompt: Input prompt
            previous_constructive: Previous constructive state
            previous_deconstructive: Previous deconstructive state
        
        Returns:
            Tuple of (constructive_output, deconstructive_output)
        """
        # Constructive phase (thesis)
        constructive_output = self.constructive.process(
            model, tokenizer, prompt, previous_constructive
        )
        
        # Deconstructive phase (antithesis)
        deconstructive_output = self.deconstructive.process(
            model, tokenizer, prompt, constructive_output, previous_deconstructive
        )
        
        return constructive_output, deconstructive_output
    
    def synthesize(self, model, tokenizer, prompt: str, constructive: str, deconstructive: str) -> str:
        """
        Synthesize constructive and deconstructive outputs.
        
        This is the final synthesis phase that combines thesis and antithesis
        into a balanced, refined answer.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            prompt: Original prompt
            constructive: Constructive vortex output
            deconstructive: Deconstructive vortex output
        
        Returns:
            Synthesized output
        """
        synthesis_prompt = f"""Original question: {prompt}

Constructive perspective (thesis): {constructive}

Critical perspective (antithesis): {deconstructive}

Balanced synthesis (integrate both perspectives):"""
        
        # Get model's max position embeddings
        if hasattr(model, 'config'):
            max_model_length = getattr(model.config, 'n_positions', 1024)
        else:
            max_model_length = 1024
        
        max_input_length = max_model_length - self.config.max_tokens
        
        # Tokenize
        inputs = tokenizer(synthesis_prompt, return_tensors="pt", truncation=True, max_length=max_input_length)
        
        # Move to device
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # Generate synthesis
        outputs = model.generate(
            **inputs,
            max_new_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        # Decode
        synthesis = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove prompt
        if synthesis.startswith(synthesis_prompt):
            synthesis = synthesis[len(synthesis_prompt):].strip()
        
        logger.debug(f"Synthesis output: {synthesis[:100]}...")
        return synthesis
