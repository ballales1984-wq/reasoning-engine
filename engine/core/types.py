from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Tuple

@dataclass
class Entity:
    """Un'entità estratta dal testo."""
    name: str
    entity_type: str  # number, concept, operator
    value: Any = None
    position: Tuple[int, int] = (0, 0)

@dataclass
class Relation:
    """Una relazione tra entità."""
    subject: str
    relation_type: str
    object: str
    confidence: float = 1.0

@dataclass
class ParsedQuery:
    """Output del parser NLP."""
    raw: str
    intent: str = "general"
    entities: List[str] = field(default_factory=list)
    relations: List[Tuple[str, str, str]] = field(default_factory=list)
    numbers: List[float] = field(default_factory=list)
    operators: List[str] = field(default_factory=list)
    confidence: float = 0.5
    language: str = "it"
    operation: str = "unknown"

@dataclass
class DeductionStep:
    """Un singolo passo di deduzione."""
    rule_type: str
    premise1: str
    premise2: str
    conclusion: str
    confidence: float = 1.0

@dataclass
class DeductionResult:
    """Risultato di una deduzione."""
    found: bool
    conclusion: str = ""
    chain: List[DeductionStep] = field(default_factory=list)
    confidence: float = 0.0
    steps_count: int = 0

@dataclass
class Pattern:
    """Un pattern induttivo."""
    description: str
    attribute: str
    value: Any
    frequency: int
    total_examples: int
    confidence: float = 0.0

@dataclass
class InductionResult:
    """Risultato di un'induzione."""
    found: bool
    patterns: List[Pattern] = field(default_factory=list)
    rules_created: List[Dict] = field(default_factory=list)
    explanation: str = ""

@dataclass
class Analogy:
    """Un'analogia tra due concetti."""
    source: str
    target: str
    shared_relations: List[str] = field(default_factory=list)
    shared_properties: List[str] = field(default_factory=list)
    structural_similarity: float = 0.0
    explanation: str = ""

@dataclass
class AnalogyResult:
    """Risultato di una ricerca di analogie."""
    found: bool
    analogies: List[Analogy] = field(default_factory=list)
    best_analogy: Optional[Analogy] = None
    explanation: str = ""

@dataclass
class ReasoningStep:
    """Un passo nella pipeline di ragionamento."""
    type: str  # lookup, deduction, induction, analogy, llm
    description: str
    input: Any = None
    output: Any = None
    confidence: float = 1.0

@dataclass
class ReasoningResult:
    """Risultato finale del ragionamento."""
    answer: Any
    confidence: float = 0.0
    reasoning_type: str = "unknown"
    steps: List[ReasoningStep] = field(default_factory=list)
    explanation: str = ""
    verified: bool = False
    knowledge_used: List[str] = field(default_factory=list)
    rules_used: List[str] = field(default_factory=list)
    llm_used: bool = False
    sources: List[str] = field(default_factory=list)
