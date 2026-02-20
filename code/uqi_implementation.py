"""
Unified Query Interface (UQI) Implementation for THEOS

This module provides transparent storage layer escalation across JSON, SQLite,
and Vector Database backends. The interface is unified - applications use the
same API regardless of backend.

Date Created: February 20, 2026
Status: Patent Pending - Unified Query Interface
"""

import json
import sqlite3
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import os
from abc import ABC, abstractmethod


class StorageBackend(Enum):
    """Available storage backends"""
    JSON = "json"
    SQLITE = "sqlite"
    VECTOR_DB = "vector_db"


@dataclass
class UnifiedQuery:
    """
    Unified query specification that works across all backends.
    
    This is the key to UQI - applications always use this format,
    regardless of which backend is actually used.
    """
    domain: str              # Wisdom domain (e.g., "medical", "financial")
    query_text: str          # Natural language query
    similarity_threshold: float = 0.85  # [0, 1] minimum similarity
    max_results: int = 10    # Maximum results to return
    filters: Dict[str, Any] = None  # Optional filters
    semantic_search: bool = True  # Enable semantic similarity


@dataclass
class UnifiedResult:
    """
    Unified result format returned by all backends.
    
    Applications always receive results in this format, regardless
    of which backend executed the query.
    """
    records: List[Dict]      # Matching wisdom records
    total_count: int         # Total matches found
    backend_used: str        # Which backend executed query
    query_time_ms: float     # Execution time in milliseconds
    similarity_scores: List[float]  # Similarity score for each result
    
    def __post_init__(self):
        """Validate result structure"""
        assert len(self.records) == len(self.similarity_scores), \
            "Records and scores must have same length"
        assert self.total_count >= len(self.records), \
            "Total count must be >= returned records"


class WisdomRecord:
    """
    Standard wisdom record format used across all backends.
    
    This ensures consistency regardless of storage layer.
    """
    
    def __init__(
        self,
        domain: str,
        question: str,
        answer: str,
        confidence: float,
        cycles_needed: int,
        energy_cost: float,
        consequence: str = "neutral",
        timestamp: Optional[str] = None
    ):
        self.id = self._generate_id(question)
        self.domain = domain
        self.question = question
        self.question_hash = hashlib.sha256(question.encode()).hexdigest()
        self.answer = answer
        self.confidence = confidence
        self.cycles_needed = cycles_needed
        self.energy_cost = energy_cost
        self.consequence = consequence
        self.timestamp = timestamp or datetime.now().isoformat()
        self.tags = self._extract_tags(question)
    
    def _generate_id(self, question: str) -> str:
        """Generate unique ID from question hash"""
        return f"w_{hashlib.sha256(question.encode()).hexdigest()[:12]}"
    
    def _extract_tags(self, question: str) -> List[str]:
        """Extract tags from question"""
        # Simple tag extraction - could be more sophisticated
        words = question.lower().split()
        return [w for w in words if len(w) > 5]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'domain': self.domain,
            'question': self.question,
            'question_hash': self.question_hash,
            'answer': self.answer,
            'confidence': self.confidence,
            'cycles_needed': self.cycles_needed,
            'energy_cost': self.energy_cost,
            'consequence': self.consequence,
            'timestamp': self.timestamp,
            'tags': self.tags
        }


class BackendInterface(ABC):
    """Abstract base class for all storage backends"""
    
    @abstractmethod
    def query(self, query: UnifiedQuery) -> UnifiedResult:
        """Execute unified query on backend"""
        pass
    
    @abstractmethod
    def store(self, record: WisdomRecord) -> bool:
        """Store wisdom record"""
        pass
    
    @abstractmethod
    def count_records(self) -> int:
        """Count total records in backend"""
        pass
    
    @abstractmethod
    def export_all(self) -> List[Dict]:
        """Export all records for migration"""
        pass
    
    @abstractmethod
    def import_all(self, records: List[Dict]) -> bool:
        """Import records from another backend"""
        pass


class JSONBackend(BackendInterface):
    """
    JSON storage backend - ideal for small wisdom sets.
    
    Uses in-memory indexing for fast queries.
    """
    
    def __init__(self, filepath: str = "wisdom.json"):
        self.filepath = filepath
        self.data = self._load()
        self._index = self._build_index()
    
    def _load(self) -> Dict:
        """Load wisdom from JSON file"""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {"wisdom_records": []}
    
    def _save(self):
        """Save wisdom to JSON file"""
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _build_index(self) -> Dict:
        """Build in-memory index for fast queries"""
        index = {
            'by_domain': {},
            'by_question_hash': {},
            'by_tags': {}
        }
        
        for record in self.data.get('wisdom_records', []):
            domain = record.get('domain')
            if domain not in index['by_domain']:
                index['by_domain'][domain] = []
            index['by_domain'][domain].append(record)
            
            q_hash = record.get('question_hash')
            index['by_question_hash'][q_hash] = record
            
            for tag in record.get('tags', []):
                if tag not in index['by_tags']:
                    index['by_tags'][tag] = []
                index['by_tags'][tag].append(record)
        
        return index
    
    def query(self, query: UnifiedQuery) -> UnifiedResult:
        """Execute query on JSON backend"""
        start_time = datetime.now()
        
        # Get candidates by domain
        candidates = self._index['by_domain'].get(query.domain, [])
        
        # Filter by similarity
        results = []
        scores = []
        for record in candidates:
            similarity = self._compute_similarity(
                query.query_text,
                record['question']
            )
            if similarity >= query.similarity_threshold:
                results.append(record)
                scores.append(similarity)
        
        # Sort by similarity descending
        sorted_results = sorted(
            zip(results, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Limit results
        limited_results = sorted_results[:query.max_results]
        
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return UnifiedResult(
            records=[r[0] for r in limited_results],
            total_count=len(results),
            backend_used="JSON",
            query_time_ms=elapsed_ms,
            similarity_scores=[r[1] for r in limited_results]
        )
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        """Compute text similarity (simple implementation)"""
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def store(self, record: WisdomRecord) -> bool:
        """Store wisdom record"""
        self.data['wisdom_records'].append(record.to_dict())
        self._save()
        self._index = self._build_index()
        return True
    
    def count_records(self) -> int:
        """Count records"""
        return len(self.data.get('wisdom_records', []))
    
    def export_all(self) -> List[Dict]:
        """Export all records"""
        return self.data.get('wisdom_records', [])
    
    def import_all(self, records: List[Dict]) -> bool:
        """Import records"""
        self.data['wisdom_records'] = records
        self._save()
        self._index = self._build_index()
        return True


class SQLiteBackend(BackendInterface):
    """
    SQLite storage backend - ideal for medium wisdom sets.
    
    Provides efficient queries with indexing.
    """
    
    def __init__(self, filepath: str = "wisdom.db"):
        self.filepath = filepath
        self.conn = sqlite3.connect(filepath)
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wisdom (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                question TEXT NOT NULL,
                question_hash TEXT UNIQUE,
                answer TEXT NOT NULL,
                confidence REAL,
                cycles_needed INTEGER,
                energy_cost REAL,
                consequence TEXT,
                timestamp TEXT,
                tags TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_domain ON wisdom(domain)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_question_hash ON wisdom(question_hash)
        """)
        
        self.conn.commit()
    
    def query(self, query: UnifiedQuery) -> UnifiedResult:
        """Execute query on SQLite backend"""
        start_time = datetime.now()
        
        cursor = self.conn.cursor()
        
        # Query by domain
        sql = """
            SELECT * FROM wisdom 
            WHERE domain = ?
            ORDER BY confidence DESC
            LIMIT ?
        """
        
        cursor.execute(sql, [query.domain, query.max_results * 2])
        rows = cursor.fetchall()
        
        # Filter by similarity
        results = []
        scores = []
        for row in rows:
            record = self._row_to_dict(row)
            similarity = self._compute_similarity(
                query.query_text,
                record['question']
            )
            if similarity >= query.similarity_threshold:
                results.append(record)
                scores.append(similarity)
        
        # Sort by similarity
        sorted_results = sorted(
            zip(results, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        limited_results = sorted_results[:query.max_results]
        
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return UnifiedResult(
            records=[r[0] for r in limited_results],
            total_count=len(results),
            backend_used="SQLite",
            query_time_ms=elapsed_ms,
            similarity_scores=[r[1] for r in limited_results]
        )
    
    def _row_to_dict(self, row: Tuple) -> Dict:
        """Convert database row to dictionary"""
        return {
            'id': row[0],
            'domain': row[1],
            'question': row[2],
            'question_hash': row[3],
            'answer': row[4],
            'confidence': row[5],
            'cycles_needed': row[6],
            'energy_cost': row[7],
            'consequence': row[8],
            'timestamp': row[9],
            'tags': json.loads(row[10]) if row[10] else []
        }
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        """Compute text similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def store(self, record: WisdomRecord) -> bool:
        """Store wisdom record"""
        cursor = self.conn.cursor()
        
        record_dict = record.to_dict()
        
        cursor.execute("""
            INSERT OR REPLACE INTO wisdom 
            (id, domain, question, question_hash, answer, confidence, 
             cycles_needed, energy_cost, consequence, timestamp, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            record_dict['id'],
            record_dict['domain'],
            record_dict['question'],
            record_dict['question_hash'],
            record_dict['answer'],
            record_dict['confidence'],
            record_dict['cycles_needed'],
            record_dict['energy_cost'],
            record_dict['consequence'],
            record_dict['timestamp'],
            json.dumps(record_dict['tags'])
        ])
        
        self.conn.commit()
        return True
    
    def count_records(self) -> int:
        """Count records"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM wisdom")
        return cursor.fetchone()[0]
    
    def export_all(self) -> List[Dict]:
        """Export all records"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM wisdom")
        
        records = []
        for row in cursor.fetchall():
            records.append(self._row_to_dict(row))
        
        return records
    
    def import_all(self, records: List[Dict]) -> bool:
        """Import records"""
        cursor = self.conn.cursor()
        
        for record in records:
            cursor.execute("""
                INSERT OR REPLACE INTO wisdom 
                (id, domain, question, question_hash, answer, confidence,
                 cycles_needed, energy_cost, consequence, timestamp, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                record['id'],
                record['domain'],
                record['question'],
                record['question_hash'],
                record['answer'],
                record['confidence'],
                record['cycles_needed'],
                record['energy_cost'],
                record['consequence'],
                record['timestamp'],
                json.dumps(record['tags'])
            ])
        
        self.conn.commit()
        return True


class EscalationManager:
    """
    Manages automatic escalation between storage backends.
    
    Monitors data volume and triggers migration when thresholds exceeded.
    """
    
    # Escalation thresholds
    JSON_TO_SQLITE_THRESHOLD = 10_000
    SQLITE_TO_VECTOR_DB_THRESHOLD = 1_000_000
    
    def __init__(self, initial_backend: StorageBackend = StorageBackend.JSON):
        self.current_backend = initial_backend
        self.backend_instance = None
        self._init_backend()
    
    def _init_backend(self):
        """Initialize current backend"""
        if self.current_backend == StorageBackend.JSON:
            self.backend_instance = JSONBackend()
        elif self.current_backend == StorageBackend.SQLITE:
            self.backend_instance = SQLiteBackend()
        else:
            raise NotImplementedError("Vector DB backend not yet implemented")
    
    def check_escalation(self) -> bool:
        """Check if escalation needed"""
        record_count = self.backend_instance.count_records()
        
        if (self.current_backend == StorageBackend.JSON and 
            record_count > self.JSON_TO_SQLITE_THRESHOLD):
            self.escalate_to_sqlite()
            return True
        
        elif (self.current_backend == StorageBackend.SQLITE and 
              record_count > self.SQLITE_TO_VECTOR_DB_THRESHOLD):
            self.escalate_to_vector_db()
            return True
        
        return False
    
    def escalate_to_sqlite(self):
        """Migrate from JSON to SQLite"""
        print("Escalating from JSON to SQLite...")
        
        # Export from JSON
        json_records = self.backend_instance.export_all()
        
        # Initialize SQLite
        self.current_backend = StorageBackend.SQLITE
        self._init_backend()
        
        # Import to SQLite
        self.backend_instance.import_all(json_records)
        
        print(f"Escalation complete: {len(json_records)} records migrated")
    
    def escalate_to_vector_db(self):
        """Migrate from SQLite to Vector DB"""
        print("Escalating from SQLite to Vector DB...")
        print("(Vector DB implementation coming soon)")
        # TODO: Implement Vector DB backend
    
    def query(self, query: UnifiedQuery) -> UnifiedResult:
        """Execute query (same API regardless of backend)"""
        # Check for escalation before query
        self.check_escalation()
        
        # Execute query on current backend
        return self.backend_instance.query(query)
    
    def store(self, record: WisdomRecord) -> bool:
        """Store record (same API regardless of backend)"""
        # Check for escalation before store
        self.check_escalation()
        
        # Store on current backend
        return self.backend_instance.store(record)


class UnifiedWisdomInterface:
    """
    High-level interface for THEOS wisdom management.
    
    Provides unified API for querying and storing wisdom across
    all storage backends with automatic escalation.
    """
    
    def __init__(self):
        self.escalation_manager = EscalationManager()
    
    def query_wisdom(
        self,
        domain: str,
        question: str,
        similarity_threshold: float = 0.85,
        max_results: int = 10
    ) -> UnifiedResult:
        """
        Query accumulated wisdom using unified interface.
        
        Same API regardless of storage backend.
        """
        query = UnifiedQuery(
            domain=domain,
            query_text=question,
            similarity_threshold=similarity_threshold,
            max_results=max_results
        )
        
        return self.escalation_manager.query(query)
    
    def store_wisdom(
        self,
        domain: str,
        question: str,
        answer: str,
        confidence: float,
        cycles_needed: int,
        energy_cost: float,
        consequence: str = "neutral"
    ) -> bool:
        """
        Store wisdom using unified interface.
        
        Same API regardless of storage backend.
        """
        record = WisdomRecord(
            domain=domain,
            question=question,
            answer=answer,
            confidence=confidence,
            cycles_needed=cycles_needed,
            energy_cost=energy_cost,
            consequence=consequence
        )
        
        return self.escalation_manager.store(record)
    
    def get_backend_info(self) -> Dict:
        """Get information about current backend"""
        return {
            'backend': self.escalation_manager.current_backend.value,
            'record_count': self.escalation_manager.backend_instance.count_records(),
            'next_escalation_threshold': (
                self.escalation_manager.JSON_TO_SQLITE_THRESHOLD
                if self.escalation_manager.current_backend == StorageBackend.JSON
                else self.escalation_manager.SQLITE_TO_VECTOR_DB_THRESHOLD
            )
        }


# Example usage
if __name__ == "__main__":
    # Initialize unified wisdom interface
    wisdom = UnifiedWisdomInterface()
    
    # Store some wisdom
    wisdom.store_wisdom(
        domain="medical",
        question="How to diagnose pneumonia?",
        answer="Look for fever, cough, chest pain, and consolidation on X-ray",
        confidence=0.95,
        cycles_needed=3,
        energy_cost=0.42,
        consequence="success"
    )
    
    # Query wisdom
    results = wisdom.query_wisdom(
        domain="medical",
        question="What are symptoms of pneumonia?",
        similarity_threshold=0.85
    )
    
    print(f"Found {results.total_count} results using {results.backend_used}")
    print(f"Query time: {results.query_time_ms:.2f}ms")
    
    # Check backend info
    backend_info = wisdom.get_backend_info()
    print(f"Backend: {backend_info['backend']}")
    print(f"Records: {backend_info['record_count']}")
