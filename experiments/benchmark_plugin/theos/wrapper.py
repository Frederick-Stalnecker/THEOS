"""
THEOS Plugin - Main Wrapper
User-facing API for THEOS triadic reasoning system

Author: Frederick Davis Stalnecker & Manus AI
License: MIT
Version: 1.0.0
"""

import logging
import time
from typing import Union, List
from .core import THEOSConfig, THEOSResponse, CachedState
from .cache import WisdomCache
from .governor import Governor
from .vortex import VortexPair


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class THEOSWrapper:
    """
    Main wrapper for THEOS triadic reasoning system.
    
    This is the primary user-facing API that integrates:
    - VortexPair (constructive/deconstructive reasoning)
    - Governor (convergence detection and cycle control)
    - WisdomCache (state caching and reuse)
    
    Usage:
        model = GPT2LMHeadModel.from_pretrained("gpt2")
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        theos = THEOSWrapper(model, tokenizer)
        response = theos.generate("Your question here")
    """
    
    def __init__(self, model, tokenizer, config: THEOSConfig = None, cache: WisdomCache = None):
        """
        Initialize THEOS wrapper.
        
        Args:
            model: HuggingFace language model
            tokenizer: HuggingFace tokenizer
            config: THEOS configuration (uses defaults if None)
            cache: WisdomCache instance (creates new if None)
        """
        self.model = model
        self.tokenizer = tokenizer
        self.config = config or THEOSConfig()
        
        # Initialize components
        self.vortex_pair = VortexPair(self.config)
        self.governor = Governor(self.config)
        
        # Initialize cache if enabled
        if self.config.enable_cache:
            self.cache = cache or WisdomCache()
        else:
            self.cache = None
        
        logger.info(f"THEOSWrapper initialized: max_cycles={self.config.max_cycles}, cache_enabled={self.config.enable_cache}")
    
    def generate(self, prompt: str, return_metadata: bool = True) -> Union[THEOSResponse, str]:
        """
        Generate response using triadic reasoning.
        
        Args:
            prompt: Input question/prompt
            return_metadata: If True, return THEOSResponse object; if False, return string
        
        Returns:
            THEOSResponse object (if return_metadata=True) or string (if False)
        """
        start_time = time.time()
        
        logger.info(f"Generating response for: {prompt[:50]}...")
        
        # Check cache first
        if self.cache is not None and self.config.enable_cache:
            cached_state = self.cache.get(prompt)
            if cached_state:
                logger.info("Cache hit! Returning cached response.")
                
                if return_metadata:
                    return THEOSResponse(
                        text=cached_state.synthesis,
                        cycles=cached_state.cycles,
                        converged=True,
                        constructive_states=[cached_state.constructive_state],
                        deconstructive_states=[cached_state.deconstructive_state],
                        governor_scores=[cached_state.score],
                        cached=True,
                        time_elapsed=time.time() - start_time
                    )
                else:
                    return cached_state.synthesis
        
        # Reset governor for new generation
        self.governor.reset()
        
        # Initialize state tracking
        constructive_states = []
        deconstructive_states = []
        governor_scores = []
        
        converged = False
        cycle = 0
        
        previous_constructive = ""
        previous_deconstructive = ""
        
        # Reasoning loop
        while cycle < self.config.max_cycles:
            cycle += 1
            
            # Execute vortex cycle
            constructive_output, deconstructive_output = self.vortex_pair.cycle(
                self.model,
                self.tokenizer,
                prompt,
                previous_constructive,
                previous_deconstructive
            )
            
            # Store states
            constructive_states.append(constructive_output)
            deconstructive_states.append(deconstructive_output)
            
            # Check convergence
            converged, similarity = self.governor.check_convergence(
                constructive_output,
                deconstructive_output
            )
            
            # Score path
            score = self.governor.score_path(constructive_output, deconstructive_output)
            governor_scores.append(score)
            
            # Update previous states
            previous_constructive = constructive_output
            previous_deconstructive = deconstructive_output
            
            # Check if should continue
            if not self.governor.should_continue(cycle, converged):
                break
        
        # Synthesize final output
        synthesis = self.vortex_pair.synthesize(
            self.model,
            self.tokenizer,
            prompt,
            constructive_states[-1],
            deconstructive_states[-1]
        )
        
        # Calculate final score
        final_score = governor_scores[-1] if governor_scores else 0.0
        
        logger.info(f"Generation complete: {cycle} cycles, converged={converged}, path_score={final_score:.4f}")
        
        # Cache the result if enabled
        if self.cache is not None and self.config.enable_cache:
            cached_state = CachedState(
                key=prompt,
                constructive_state=constructive_states[-1],
                deconstructive_state=deconstructive_states[-1],
                synthesis=synthesis,
                cycles=cycle,
                score=final_score
            )
            self.cache.put(cached_state)
            logger.info(f"Result cached for prompt: {prompt[:50]}...")
        
        # Build response
        time_elapsed = time.time() - start_time
        
        if return_metadata:
            return THEOSResponse(
                text=synthesis,
                cycles=cycle,
                converged=converged,
                constructive_states=constructive_states,
                deconstructive_states=deconstructive_states,
                governor_scores=governor_scores,
                cached=False,
                time_elapsed=time_elapsed
            )
        else:
            return synthesis
    
    def generate_batch(self, prompts: List[str], return_metadata: bool = True) -> List[Union[THEOSResponse, str]]:
        """
        Generate responses for multiple prompts.
        
        Args:
            prompts: List of input prompts
            return_metadata: If True, return THEOSResponse objects; if False, return strings
        
        Returns:
            List of THEOSResponse objects or strings
        """
        logger.info(f"Batch generation for {len(prompts)} prompts")
        
        results = []
        for i, prompt in enumerate(prompts, 1):
            logger.info(f"Processing batch item {i}/{len(prompts)}")
            result = self.generate(prompt, return_metadata=return_metadata)
            results.append(result)
        
        logger.info(f"Batch generation complete: {len(results)} responses")
        return results
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics, or empty dict if cache disabled
        """
        if self.cache is not None:
            return self.cache.get_stats()
        return {}
    
    def save_cache(self, filepath: str):
        """
        Save cache to file.
        
        Args:
            filepath: Path to save cache
        """
        if self.cache is not None:
            self.cache.save(filepath)
            logger.info(f"Cache saved to {filepath}")
        else:
            logger.warning("Cache is disabled, nothing to save")
    
    def load_cache(self, filepath: str):
        """
        Load cache from file.
        
        Args:
            filepath: Path to load cache from
        """
        if self.cache is not None:
            self.cache.load(filepath)
            logger.info(f"Cache loaded from {filepath}")
        else:
            logger.warning("Cache is disabled, cannot load")
    
    def clear_cache(self):
        """Clear all cached states."""
        if self.cache is not None:
            self.cache.clear()
            logger.info("Cache cleared")
        else:
            logger.warning("Cache is disabled, nothing to clear")
    
    def __repr__(self) -> str:
        """String representation of wrapper."""
        return f"THEOSWrapper(max_cycles={self.config.max_cycles}, cache_enabled={self.config.enable_cache})"
