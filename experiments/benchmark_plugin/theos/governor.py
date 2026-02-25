"""
THEOS Plugin - Governor Module
Convergence detection and cycle control for triadic reasoning

Author: Frederick Davis Stalnecker & Manus AI
License: MIT
Version: 1.0.0

Similarity metric change (2026-02-25, Celeste):
- Previous: Jaccard word overlap (intersection / union of word sets)
- Replaced with: TF-IDF cosine similarity (no external dependencies)
- Reason: Jaccard measures lexical overlap only. Two texts sharing stop words
  ("the", "is", "a") score high even when semantically divergent. Two texts
  with different vocabulary but the same meaning score near zero (false negative).
  TF-IDF cosine weights words by frequency and inverse document frequency,
  making function words nearly invisible. This is not true semantic similarity
  (which requires embeddings) but it is substantially more accurate than Jaccard.
- Note: For production use with capable models, replace with cosine similarity
  over sentence embeddings using code/semantic_retrieval.py.
"""

import logging
import math
from collections import Counter
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
    
    # English stop words to filter from similarity calculation.
    # These words carry no semantic content and inflate Jaccard scores.
    _STOP_WORDS = frozenset({
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "that", "this", "these", "those",
        "it", "its", "i", "you", "he", "she", "we", "they", "not", "no",
        "as", "if", "then", "than", "so", "can", "all", "also", "more",
        "such", "any", "when", "which", "what", "how", "who", "there",
        "their", "they", "our", "your", "my", "his", "her", "into", "about",
    })

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using TF-IDF cosine similarity.

        Replaces the prior Jaccard word-overlap implementation. Jaccard treats
        word presence as binary and counts stop words equally with content words,
        producing false positives (texts sharing only function words score high)
        and false negatives (same meaning, different vocabulary scores low).

        This implementation:
        1. Tokenizes both texts into lower-cased words
        2. Filters common English stop words
        3. Computes term frequency (TF) for each word in each text
        4. Computes inverse document frequency (IDF) across the two-document corpus
        5. Returns the cosine similarity of the two TF-IDF vectors

        This is still lexical similarity (not semantic). For true semantic
        similarity, use sentence embeddings (see code/semantic_retrieval.py).

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0

        def tokenize(text: str):
            words = text.lower().split()
            return [w.strip(".,;:!?\"'()[]{}") for w in words
                    if w.strip(".,;:!?\"'()[]{}") and
                    w.strip(".,;:!?\"'()[]{}") not in self._STOP_WORDS]

        tokens1 = tokenize(text1)
        tokens2 = tokenize(text2)

        if not tokens1 or not tokens2:
            return 0.0

        # Term frequency (normalized by document length)
        tf1 = Counter(tokens1)
        tf2 = Counter(tokens2)
        doc_len1 = len(tokens1)
        doc_len2 = len(tokens2)

        # Vocabulary union
        vocab = set(tf1.keys()) | set(tf2.keys())
        if not vocab:
            return 0.0

        # IDF: log((N + 1) / (df + 1)) + 1 (smoothed), N=2 documents
        n_docs = 2

        def idf(term: str) -> float:
            df = int(term in tf1) + int(term in tf2)
            return math.log((n_docs + 1) / (df + 1)) + 1.0

        # Build TF-IDF vectors
        vec1 = {t: (tf1.get(t, 0) / doc_len1) * idf(t) for t in vocab}
        vec2 = {t: (tf2.get(t, 0) / doc_len2) * idf(t) for t in vocab}

        # Cosine similarity
        dot = sum(vec1[t] * vec2[t] for t in vocab)
        mag1 = math.sqrt(sum(v * v for v in vec1.values()))
        mag2 = math.sqrt(sum(v * v for v in vec2.values()))

        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0

        return dot / (mag1 * mag2)
    
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
