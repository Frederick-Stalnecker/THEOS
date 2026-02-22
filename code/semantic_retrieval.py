#!/usr/bin/env python3
"""
Semantic Retrieval - Embedding-Based Wisdom Matching
=====================================================

This module provides semantic similarity matching for wisdom retrieval.
Uses embeddings to find conceptually similar past queries and resolutions.

Supports:
- OpenAI embeddings
- Sentence transformers
- Custom embedding functions

Author: Frederick Davis Stalnecker
Date: February 22, 2026
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import json
import math


@dataclass
class EmbeddingVector:
    """Embedding vector for a piece of text."""
    text: str
    vector: List[float]
    
    def __post_init__(self):
        """Validate vector."""
        if len(self.vector) == 0:
            raise ValueError("Embedding vector cannot be empty")
    
    @property
    def dimension(self) -> int:
        """Get vector dimension."""
        return len(self.vector)


class EmbeddingAdapter(ABC):
    """
    Abstract base class for embedding providers.
    
    Implementations should override:
    - _embed: Generate embedding for text
    """
    
    def __init__(self, model_name: str):
        """Initialize embedding adapter."""
        self.model_name = model_name
        self.cache: Dict[str, List[float]] = {}
    
    def embed(self, text: str) -> EmbeddingVector:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            EmbeddingVector with embedding
        """
        # Check cache
        if text in self.cache:
            vector = self.cache[text]
            return EmbeddingVector(text=text, vector=vector)
        
        # Generate embedding
        vector = self._embed(text)
        
        # Cache it
        self.cache[text] = vector
        
        return EmbeddingVector(text=text, vector=vector)
    
    @abstractmethod
    def _embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        pass


class MockEmbeddingAdapter(EmbeddingAdapter):
    """
    Mock embedding adapter for testing.
    
    Generates deterministic embeddings based on text hash.
    """
    
    def __init__(self, dimension: int = 384):
        """Initialize mock adapter."""
        super().__init__(model_name="mock-embedding")
        self.dimension = dimension
    
    def _embed(self, text: str) -> List[float]:
        """Generate deterministic embedding."""
        # Use hash to generate deterministic but varied embeddings
        hash_val = hash(text)
        
        # Generate vector based on hash
        vector = []
        for i in range(self.dimension):
            # Mix hash with index to get varied values
            val = math.sin((hash_val + i * 12345) / 10000.0)
            vector.append(val)
        
        # Normalize
        magnitude = math.sqrt(sum(v**2 for v in vector))
        vector = [v / magnitude for v in vector]
        
        return vector


class SemanticRetrieval:
    """
    Semantic similarity-based retrieval system.
    
    Finds similar wisdom records based on semantic embeddings.
    """
    
    def __init__(self, embedding_adapter: EmbeddingAdapter):
        """
        Initialize semantic retrieval.
        
        Args:
            embedding_adapter: Adapter for generating embeddings
        """
        self.embedding_adapter = embedding_adapter
        self.wisdom_records: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []
    
    def add_record(self, record: Dict[str, Any]) -> None:
        """
        Add a wisdom record.
        
        Args:
            record: Wisdom record with 'query', 'resolution', 'confidence', etc.
        """
        # Store record
        self.wisdom_records.append(record)
        
        # Generate embedding for query
        query_text = record.get('query', '')
        embedding = self.embedding_adapter.embed(query_text)
        self.embeddings.append(embedding.vector)
    
    def retrieve_similar(
        self,
        query: str,
        threshold: float = 0.7,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar wisdom records.
        
        Args:
            query: Query to find similar records for
            threshold: Minimum similarity score (0-1)
            top_k: Maximum number of results
            
        Returns:
            List of similar records with similarity scores
        """
        if not self.wisdom_records:
            return []
        
        # Generate embedding for query
        query_embedding = self.embedding_adapter.embed(query)
        
        # Compute similarities
        similarities: List[Tuple[int, float]] = []
        for i, record_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(
                query_embedding.vector,
                record_embedding
            )
            
            if similarity >= threshold:
                similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k records with scores
        results = []
        for idx, similarity in similarities[:top_k]:
            record = self.wisdom_records[idx].copy()
            record['similarity_score'] = similarity
            results.append(record)
        
        return results
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score in [0, 1]
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")
        
        # Dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Magnitudes
        mag1 = math.sqrt(sum(a**2 for a in vec1))
        mag2 = math.sqrt(sum(b**2 for b in vec2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = dot_product / (mag1 * mag2)
        
        # Normalize to [0, 1]
        return (similarity + 1) / 2
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get retrieval statistics."""
        return {
            'total_records': len(self.wisdom_records),
            'embedding_model': self.embedding_adapter.model_name,
            'embedding_dimension': len(self.embeddings[0]) if self.embeddings else 0,
            'cache_size': len(self.embedding_adapter.cache),
        }


if __name__ == "__main__":
    # Test semantic retrieval
    print("Testing Semantic Retrieval...")
    
    # Create mock embedding adapter
    embedding = MockEmbeddingAdapter(dimension=384)
    
    # Create retrieval system
    retrieval = SemanticRetrieval(embedding)
    
    # Add some wisdom records
    records = [
        {
            'query': 'What is the relationship between freedom and responsibility?',
            'resolution': 'Freedom and responsibility are interdependent. Greater freedom requires greater responsibility.',
            'confidence': 0.85,
        },
        {
            'query': 'How should AI systems handle ethical dilemmas?',
            'resolution': 'AI systems should use multi-perspective reasoning to identify ethical trade-offs.',
            'confidence': 0.80,
        },
        {
            'query': 'What makes a good decision?',
            'resolution': 'Good decisions balance multiple values, consider long-term consequences, and remain open to revision.',
            'confidence': 0.82,
        },
    ]
    
    for record in records:
        retrieval.add_record(record)
    
    # Test retrieval
    test_query = 'What is the connection between liberty and accountability?'
    
    print(f"\nQuery: {test_query}")
    print(f"\nSimilar wisdom records:")
    
    similar = retrieval.retrieve_similar(test_query, threshold=0.5, top_k=3)
    
    for i, record in enumerate(similar, 1):
        print(f"\n  {i}. Similarity: {record['similarity_score']:.2f}")
        print(f"     Query: {record['query']}")
        print(f"     Resolution: {record['resolution']}")
        print(f"     Confidence: {record['confidence']:.2f}")
    
    print(f"\nStatistics: {retrieval.get_statistics()}")
