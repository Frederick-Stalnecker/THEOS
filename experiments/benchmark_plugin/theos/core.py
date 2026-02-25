"""
THEOS Plugin - Core Data Structures
Configuration, response objects, and cached state management

Author: Frederick Davis Stalnecker & Manus AI
License: MIT
Version: 1.0.0
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


@dataclass
class THEOSConfig:
    """Configuration for THEOS reasoning system."""
    
    max_cycles: int = 5
    min_cycles: int = 2
    convergence_threshold: float = 0.1
    max_tokens: int = 50
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    enable_cache: bool = True
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.max_cycles < self.min_cycles:
            raise ValueError(f"max_cycles ({self.max_cycles}) must be >= min_cycles ({self.min_cycles})")
        if not 0 <= self.convergence_threshold <= 1:
            raise ValueError(f"convergence_threshold must be between 0 and 1, got {self.convergence_threshold}")
        if self.max_tokens < 1:
            raise ValueError(f"max_tokens must be positive, got {self.max_tokens}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'THEOSConfig':
        """Create config from dictionary."""
        return cls(**data)
    
    def save(self, filepath: str):
        """
        Save configuration to file.
        
        Args:
            filepath: Path to save config (JSON or YAML based on extension)
        """
        data = self.to_dict()
        
        if filepath.endswith('.json'):
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        elif filepath.endswith('.yaml') or filepath.endswith('.yml'):
            try:
                import yaml
                with open(filepath, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
            except ImportError:
                raise ImportError("PyYAML is required for YAML config saving. Install with: pip install pyyaml")
        else:
            raise ValueError(f"Unsupported file extension. Use .json or .yaml")
        
        logger.info(f"Configuration saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'THEOSConfig':
        """
        Load configuration from file.
        
        Args:
            filepath: Path to load config from
        
        Returns:
            THEOSConfig instance
        """
        if filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
        elif filepath.endswith('.yaml') or filepath.endswith('.yml'):
            try:
                import yaml
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)
            except ImportError:
                raise ImportError("PyYAML is required for YAML config loading. Install with: pip install pyyaml")
        else:
            raise ValueError(f"Unsupported file extension. Use .json or .yaml")
        
        logger.info(f"Configuration loaded from {filepath}")
        return cls.from_dict(data)


@dataclass
class THEOSResponse:
    """Response object containing generated text and metadata."""
    
    text: str
    cycles: int
    converged: bool
    constructive_states: List[str] = field(default_factory=list)
    deconstructive_states: List[str] = field(default_factory=list)
    governor_scores: List[float] = field(default_factory=list)
    cached: bool = False
    tokens_used: int = 0
    time_elapsed: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'THEOSResponse':
        """Create response from dictionary."""
        return cls(**data)


@dataclass
class CachedState:
    """Cached reasoning state for wisdom reuse."""
    
    key: str
    constructive_state: str
    deconstructive_state: str
    synthesis: str
    cycles: int
    score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    
    def is_expired(self, ttl: int) -> bool:
        """
        Check if cached state has expired.
        
        Args:
            ttl: Time-to-live in seconds
        
        Returns:
            True if expired, False otherwise
        """
        created_at = datetime.fromisoformat(self.timestamp)
        age = datetime.now() - created_at
        return age > timedelta(seconds=ttl)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cached state to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CachedState':
        """Create cached state from dictionary."""
        return cls(**data)
