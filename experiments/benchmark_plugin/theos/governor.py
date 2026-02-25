"""
THEOS Plugin - Governor Module
Convergence detection and cycle control for triadic reasoning

Author: Frederick Davis Stalnecker & Manus AI
License: MIT
Version: 1.0.0
"""

import logging
import math
from typing import Tuple
from .core import THEOSConfig


logger = logging.getLogger(__name__)


class Governor:
    """
    Governor system for managing triadic reasoning cycles.
    
    Responsibilities:
    - Detect convergence between constructive and deconstructive vortices
    - Score reasoning paths for quality assessment
    - Control cycle continuation based on convergence and quality
    """
    
    def __init__(self, config: THEOSConfig):
        """
        Initialize Governor with configuration.
        
        Args:
            config: THEOS configuration object
        """
        self.config = config
        self.cycle_count = 0
        self.convergence_history = []
        self.score_history = []
        logger.debug(f"Governor initialized with threshold={config.convergence_threshold}")
    
    def check_convergence(self, constructive_output: str, deconstructive_output: str) -> Tuple[bool, float]:
        """
        Check if constructive and deconstructive vortices have converged.
        
        Uses cosine similarity between outputs to detect alignment.
        
        Args:
            constructive_output: Output from constructive vortex
            deconstructive_output: Output from deconstructive vortex
        
        Returns:
            Tuple of (converged: bool, similarity_score: float)
        """
        # Simple word-based similarity (can be enhanced with embeddings)
        similarity = self._calculate_similarity(constructive_output, deconstructive_output)
        
        # Convergence occurs when similarity exceeds threshold
        converged = similarity >= (1.0 - self.config.convergence_threshold)
        
        self.convergence_history.append(similarity)
        
        logger.debug(f"Convergence check: similarity={similarity:.4f}, converged={converged}")
        
        return converged, similarity
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using word overlap.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        # Tokenize into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def score_path(self, constructive_output: str, deconstructive_output: str) -> float:
        """
        Score the quality of the reasoning path.
        
        Considers:
        - Length and complexity of outputs
        - Balance between constructive and deconstructive reasoning
        - Convergence trend
        
        Args:
            constructive_output: Output from constructive vortex
            deconstructive_output: Output from deconstructive vortex
        
        Returns:
            Quality score between 0 and 1
        """
        # Length score (prefer substantial outputs)
        len_c = len(constructive_output.split())
        len_d = len(deconstructive_output.split())
        avg_len = (len_c + len_d) / 2
        length_score = min(avg_len / 50, 1.0)  # Normalize to 50 words
        
        # Balance score (prefer similar lengths)
        if len_c > 0 and len_d > 0:
            balance_score = min(len_c, len_d) / max(len_c, len_d)
        else:
            balance_score = 0.0
        
        # Convergence score (from latest check)
        convergence_score = self.convergence_history[-1] if self.convergence_history else 0.0
        
        # Weighted combination
        score = (
            0.3 * length_score +
            0.3 * balance_score +
            0.4 * convergence_score
        )
        
        self.score_history.append(score)
        
        logger.debug(f"Path score: {score:.4f} (length={length_score:.2f}, balance={balance_score:.2f}, conv={convergence_score:.2f})")
        
        return score
    
    def should_continue(self, cycle: int, converged: bool) -> bool:
        """
        Determine if reasoning should continue for another cycle.
        
        Args:
            cycle: Current cycle number (1-indexed)
            converged: Whether convergence has been detected
        
        Returns:
            True if should continue, False if should stop
        """
        # Always do minimum cycles
        if cycle < self.config.min_cycles:
            logger.debug(f"Continue: cycle {cycle} < min_cycles {self.config.min_cycles}")
            return True
        
        # Stop if converged
        if converged:
            logger.debug(f"Stop: converged at cycle {cycle}")
            return False
        
        # Stop if reached max cycles
        if cycle >= self.config.max_cycles:
            logger.debug(f"Stop: reached max_cycles {self.config.max_cycles}")
            return False
        
        # Continue otherwise
        logger.debug(f"Continue: cycle {cycle}, not converged")
        return True
    
    def reset(self):
        """Reset governor state for new generation."""
        self.cycle_count = 0
        self.convergence_history = []
        self.score_history = []
        logger.debug("Governor state reset")
    
    def get_stats(self) -> dict:
        """
        Get governor statistics.
        
        Returns:
            Dictionary with convergence and score history
        """
        return {
            'cycle_count': self.cycle_count,
            'convergence_history': self.convergence_history,
            'score_history': self.score_history,
            'avg_convergence': sum(self.convergence_history) / len(self.convergence_history) if self.convergence_history else 0.0,
            'avg_score': sum(self.score_history) / len(self.score_history) if self.score_history else 0.0,
        }
