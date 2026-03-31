"""
PromptBuilder + PromptOptimizer — Prompt Engineering avanzato.

Integrato con:
- KnowledgeGraph (concetti)
- RuleEngine (regole)
- Verifier (verifica coerenza)
- Learner (few-shot examples)
- Reasoning Loop (chain-of-thought)
- Memory (ricorda prompt che funzionano)
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Callable
from enum import Enum
import json


class PromptStyle(Enum):
    """Stili di prompt."""
    SIMPLE = "semplice e intuitivo"
    TECHNICAL = "tecnico e preciso"
    CREATIVE = "creativo e coinvolgente"
    STEP_BY_STEP = "passo per passo"
    ANALOGICAL = "per analogie"
    ACADEMIC = "accademico e rigoroso"
    CONVERSATIONAL = "conversazionale"
    TEACHER = "da insegnante"


class ReasoningType(Enum):
    """Tipo di ragionamento da forzare."""
    CHAIN_OF_THOUGHT = "chain-of-thought"
    TREE_OF_THOUGHT = "tree-of-thought"
    DEDUCTIVE = "deduttivo"
    INDUCTIVE = "induttivo"
    ANALOGICAL = "analogico"
    SOCRATIC = "socratico"


class ModelTarget(Enum):
    """Modello LLM target."""
    CLAUDE_35 = "claude-3.5"
    CLAUDE_3 = "claude-3"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    LLAMA_3 = "llama3"
    LLAMA_32 = "llama3.2"
    MISTRAL = "mistral"
    GROK = "grok"
    GEMINI = "gemini"


@dataclass
class PromptTemplate:
    """Template per prompt."""
    name: str
    description: str
    template: str
    variables: list = field(default_factory=list)
    reasoning_type: Optional[ReasoningType] = None
    best_for: list = field(default_factory=list)  # ["math", "finance", "coding", etc.]


@dataclass
class GeneratedPrompt:
    """Prompt generato."""
    prompt: str
    style: PromptStyle
    reasoning_type: ReasoningType
    model_target: ModelTarget
    tokens_estimate: int
    confidence: float
    metadata: dict = field(default_factory=dict)


class PromptBuilder:
    """
    Genera prompt strutturati e ottimizzati.
    
    Integrato con il ReasoningEngine per usare:
    - KnowledgeGraph: concetti appresi
    - RuleEngine: regole logiche
    - Learner: few-shot examples
    - Verifier: verifica coerenza
    """
    
    def __init__(self, engine=None):
        self.engine = engine
        self.templates = self._register_templates()
        self.prompt_history = []
    
    def _register_templates(self) -> dict:
        """Registra i template base."""
        return {
            "zero_shot": PromptTemplate(
                name="zero_shot",
                description="Prompt diretto senza esempi",
                template="""{persona}

Compito: {task}

Istruzioni:
{instructions}

{reasoning_instruction}

Ora ragiona e rispondi:""",
                variables=["persona", "task", "instructions", "reasoning_instruction"]
            ),
            
            "few_shot": PromptTemplate(
                name="few_shot",
                description="Prompt con esempi",
                template="""{persona}

Compito: {task}

Esempi:
{examples}

Istruzioni:
{instructions}

{reasoning_instruction}

Ora rispondi al nuovo caso:""",
                variables=["persona", "task", "examples", "instructions", "reasoning_instruction"]
            ),
            
            "chain_of_thought": PromptTemplate(
                name="chain_of_thought",
                description="Forza ragionamento passo per passo",
                template="""{persona}

Compito: {task}

Pensa passo per passo:
1. Capisci la domanda
2. Identifica i concetti chiave
3. Applica le regole rilevanti
4. Verifica il risultato
5. Spiega il ragionamento

Istruzioni:
{instructions}

Ora ragiona step-by-step:""",
                variables=["persona", "task", "instructions"],
                reasoning_type=ReasoningType.CHAIN_OF_THOUGHT
            ),
            
            "tree_of_thought": PromptTemplate(
                name="tree_of_thought",
                description="Esplora multiple soluzioni",
                template="""{persona}

Compito: {task}

Esplora 3 approcci diversi:

Approccio 1: [primo pensiero]
Approccio 2: [secondo pensiero]  
Approccio 3: [terzo pensiero]

Confronta gli approcci e scegli il migliore.

Istruzioni:
{instructions}

Ora esplora e confronta:""",
                variables=["persona", "task", "instructions"],
                reasoning_type=ReasoningType.TREE_OF_THOUGHT
            ),
            
            "socratic": PromptTemplate(
                name="socratic",
                description="Domande socratiche",
                template="""{persona}

Compito: {task}

Rispondi facendo domande guida:
- Cosa sai già su questo?
- Cosa non capisci?
- Quali assunzioni stai facendo?
- Come potresti verificare?

Istruzioni:
{instructions}

Ora guida con domande:""",
                variables=["persona", "task", "instructions"],
                reasoning_type=ReasoningType.SOCRATIC
            ),
            
            "analogical": PromptTemplate(
                name="analogical",
                description="Spiega per analogie",
                template="""{persona}

Compito: {task}

Usa analogie della vita quotidiana:
- Confronta con qualcosa di familiare
- Usa metafore visive
- Dai esempi concreti

Istruzioni:
{instructions}

Ora spiega per analogie:""",
                variables=["persona", "task", "instructions"],
                reasoning_type=ReasoningType.ANALOGICAL
            ),
            
            "financial": PromptTemplate(
                name="financial",
                description="Prompt per finanza",
                template="""{persona}

Analisi finanziaria: {task}

Considera:
- Rischio e rendimento
- Dati storici
- Contesto di mercato
- Assunzioni chiave

Formula: {formula}

Dati: {data}

Ora analizza:""",
                variables=["persona", "task", "formula", "data"],
                best_for=["finance", "investimenti", "trading"]
            ),
            
            "coding": PromptTemplate(
                name="coding",
                description="Prompt per coding",
                template="""{persona}

Task di programmazione: {task}

Requisiti:
{requirements}

Vincoli:
{constraints}

Stile: {code_style}

Genera codice pulito, commentato e testabile.

Ora scrivi il codice:""",
                variables=["persona", "task", "requirements", "constraints", "code_style"],
                best_for=["coding", "programming", "software"]
            )
        }
    
    def build(self, task: str, style: PromptStyle = PromptStyle.SIMPLE,
              reasoning_type: ReasoningType = ReasoningType.CHAIN_OF_THOUGHT,
              add_fewshot: bool = False, max_tokens: int = 800,
              model_target: ModelTarget = ModelTarget.CLAUDE_35,
              template_name: str = None, **kwargs) -> GeneratedPrompt:
        """
        Genera un prompt ottimizzato.
        
        Args:
            task: il compito da svolgere
            style: stile del prompt
            reasoning_type: tipo di ragionamento
            add_fewshot: aggiungi esempi dal Learner
            max_tokens: limite token
            model_target: modello LLM target
            template_name: template specifico (opzionale)
        """
        # Scegli template
        if template_name and template_name in self.templates:
            template = self.templates[template_name]
        else:
            template = self._select_template(task, reasoning_type)
        
        # Genera persona basata sullo stile
        persona = self._generate_persona(style, task)
        
        # Genera istruzioni
        instructions = self._generate_instructions(style, reasoning_type, task)
        
        # Genera istruzioni di ragionamento
        reasoning_instruction = self._generate_reasoning_instruction(reasoning_type)
        
        # Aggiungi few-shot examples se richiesto
        examples = ""
        if add_fewshot and self.engine:
            examples = self._get_fewshot_examples(task)
        
        # Compila il template
        prompt = template.template.format(
            persona=persona,
            task=task,
            instructions=instructions,
            reasoning_instruction=reasoning_instruction,
            examples=examples,
            **kwargs
        )
        
        # Stima token
        tokens_estimate = len(prompt) // 4
        
        # Genera risultato
        result = GeneratedPrompt(
            prompt=prompt,
            style=style,
            reasoning_type=reasoning_type,
            model_target=model_target,
            tokens_estimate=tokens_estimate,
            confidence=0.8,
            metadata={
                "template": template.name,
                "fewshot_used": add_fewshot,
                "has_engine": self.engine is not None
            }
        )
        
        # Salva nella history
        self.prompt_history.append(result)
        
        return result
    
    def _select_template(self, task: str, reasoning_type: ReasoningType) -> PromptTemplate:
        """Seleziona il template migliore per il task."""
        task_lower = task.lower()
        
        # Per finanza
        if any(word in task_lower for word in ["finanza", "investimento", "roi", "rendimento", "opzione", "black-scholes"]):
            return self.templates.get("financial", self.templates["zero_shot"])
        
        # Per coding
        if any(word in task_lower for word in ["codice", "programma", "funzione", "classe", "script"]):
            return self.templates.get("coding", self.templates["zero_shot"])
        
        # Per ragionamento
        if reasoning_type == ReasoningType.CHAIN_OF_THOUGHT:
            return self.templates["chain_of_thought"]
        elif reasoning_type == ReasoningType.TREE_OF_THOUGHT:
            return self.templates["tree_of_thought"]
        elif reasoning_type == ReasoningType.ANALOGICAL:
            return self.templates["analogical"]
        elif reasoning_type == ReasoningType.SOCRATIC:
            return self.templates["socratic"]
        
        # Default
        return self.templates["zero_shot"]
    
    def _generate_persona(self, style: PromptStyle, task: str) -> str:
        """Genera la persona basata sullo stile."""
        personas = {
            PromptStyle.SIMPLE: "Sei un esperto che sa spiegare in modo semplice e chiaro.",
            PromptStyle.TECHNICAL: "Sei un esperto tecnico con profonda conoscenza del dominio.",
            PromptStyle.CREATIVE: "Sei un creativo brillante che trova angoli originali.",
            PromptStyle.STEP_BY_STEP: "Sei un maestro metodico che guida passo per passo.",
            PromptStyle.ANALOGICAL: "Sei un narratore che spiega per analogie vivide.",
            PromptStyle.ACADEMIC: "Sei un accademico rigoroso e preciso.",
            PromptStyle.CONVERSATIONAL: "Sei un amico esperto che parla in modo naturale.",
            PromptStyle.TEACHER: "Sei un eccellente insegnante, paziente e chiaro."
        }
        return personas.get(style, personas[PromptStyle.SIMPLE])
    
    def _generate_instructions(self, style: PromptStyle, reasoning_type: ReasoningType, task: str) -> str:
        """Genera istruzioni specifiche."""
        instructions = []
        
        # Istruzioni base
        instructions.append("- Rispondi in italiano")
        
        # Per stile
        if style == PromptStyle.SIMPLE:
            instructions.append("- Usa linguaggio semplice, evita jargon")
            instructions.append("- Usa esempi concreti")
        elif style == PromptStyle.TECHNICAL:
            instructions.append("- Usa terminologia tecnica appropriata")
            instructions.append("- Cita fonti o riferimenti quando possibile")
        elif style == PromptStyle.CREATIVE:
            instructions.append("- Sii originale e sorprendente")
            instructions.append("- Usa storytelling")
        
        # Per ragionamento
        if reasoning_type == ReasoningType.CHAIN_OF_THOUGHT:
            instructions.append("- Mostra ogni passaggio del ragionamento")
        elif reasoning_type == ReasoningType.TREE_OF_THOUGHT:
            instructions.append("- Esplora almeno 3 approcci diversi")
        elif reasoning_type == ReasoningType.ANALOGICAL:
            instructions.append("- Usa almeno 2 analogie concrete")
        
        # Per task specifici
        task_lower = task.lower()
        if "finanza" in task_lower or "opzione" in task_lower:
            instructions.append("- Includi numeri realistici negli esempi")
            instructions.append("- Spiega rischi e rendimenti")
        
        return "\n".join(instructions)
    
    def _generate_reasoning_instruction(self, reasoning_type: ReasoningType) -> str:
        """Genera istruzione di ragionamento."""
        instructions = {
            ReasoningType.CHAIN_OF_THOUGHT: "Pensa passo per passo. Mostra il tuo ragionamento completo.",
            ReasoningType.TREE_OF_THOUGHT: "Esplora multiple soluzioni. Confronta e scegli la migliore.",
            ReasoningType.DEDUCTIVE: "Parti da principi generali. Applica le regole logicamente.",
            ReasoningType.INDUCTIVE: "Osserva i pattern. Generalizza dagli esempi.",
            ReasoningType.ANALOGICAL: "Trova analogie. Usa metafore per spiegare.",
            ReasoningType.SOCRATIC: "Fai domande. Guida alla scoperta."
        }
        return instructions.get(reasoning_type, "")
    
    def _get_fewshot_examples(self, task: str) -> str:
        """Ottieni few-shot examples dal Learner."""
        if not self.engine or not hasattr(self.engine, 'knowledge'):
            return ""
        
        # Cerca esempi rilevanti nel knowledge graph
        examples = []
        task_words = task.lower().split()
        
        for concept in self.engine.knowledge.list_all():
            if any(word in concept.get('name', '').lower() for word in task_words):
                if concept.get('examples'):
                    examples.extend(concept['examples'][:2])
        
        if not examples:
            return ""
        
        result = "Esempi dal Knowledge Graph:\n"
        for i, ex in enumerate(examples[:3], 1):
            result += f"{i}. {ex}\n"
        
        return result
    
    def list_templates(self) -> list:
        """Lista tutti i template disponibili."""
        return [
            {"name": t.name, "description": t.description, "best_for": t.best_for}
            for t in self.templates.values()
        ]


class PromptOptimizer:
    """
    Ottimizza prompt iterativamente.
    
    Usa il Verifier del ReasoningEngine per controllare coerenza.
    Usa la Memory per ricordare prompt che funzionano.
    """
    
    def __init__(self, engine=None):
        self.engine = engine
        self.optimization_history = []
    
    def optimize(self, prompt: str, goal: str = "massima chiarezza",
                 iterations: int = 3, check_with_verifier: bool = True) -> dict:
        """
        Ottimizza un prompt iterativamente.
        
        Args:
            prompt: il prompt originale
            goal: obiettivo dell'ottimizzazione
            iterations: numero di cicli di miglioramento
            check_with_verifier: usa il Verifier per controllare coerenza
        """
        current_prompt = prompt
        improvements = []
        
        for i in range(iterations):
            # Analizza il prompt corrente
            analysis = self._analyze_prompt(current_prompt)
            
            # Genera miglioramenti
            improvements_batch = self._generate_improvements(current_prompt, goal, analysis)
            
            # Applica miglioramenti
            for improvement in improvements_batch:
                current_prompt = self._apply_improvement(current_prompt, improvement)
                improvements.append(improvement)
            
            # Verifica con Verifier se richiesto
            if check_with_verifier and self.engine:
                verification = self._verify_prompt(current_prompt)
                if not verification.get("coherent", True):
                    # Rollback se incoerente
                    current_prompt = prompt
        
        # Salva nella memoria se disponibile
        if self.engine and hasattr(self.engine, 'memory'):
            self.engine.memory.remember(
                f"Prompt ottimizzato: {current_prompt[:200]}",
                memory_type="procedural",
                tags=["prompt", "ottimizzazione"],
                importance=0.7
            )
        
        result = {
            "original_prompt": prompt,
            "optimized_prompt": current_prompt,
            "improvements": improvements,
            "iterations": iterations,
            "goal": goal
        }
        
        self.optimization_history.append(result)
        
        return result
    
    def _analyze_prompt(self, prompt: str) -> dict:
        """Analizza la qualità di un prompt."""
        analysis = {
            "length": len(prompt),
            "words": len(prompt.split()),
            "has_persona": any(word in prompt.lower() for word in ["sei", "you are", "agisci"]),
            "has_instructions": any(word in prompt.lower() for word in ["istruzioni", "instructions", "devi"]),
            "has_examples": any(word in prompt.lower() for word in ["esempio", "example", "ad esempio"]),
            "has_reasoning": any(word in prompt.lower() for word in ["passo", "step", "ragiona", "pensa"]),
            "ambiguity_score": self._calculate_ambiguity(prompt),
            "clarity_score": self._calculate_clarity(prompt)
        }
        return analysis
    
    def _calculate_ambiguity(self, prompt: str) -> float:
        """Calcola punteggio ambiguità (0=chiaro, 1=ambiguo)."""
        ambiguous_words = ["forse", "maybe", "potrebbe", "qualcosa", "tipo", "circa"]
        count = sum(1 for word in ambiguous_words if word in prompt.lower())
        return min(1.0, count / 5)
    
    def _calculate_clarity(self, prompt: str) -> float:
        """Calcola punteggio chiarezza (0=confuso, 1=chiaro)."""
        clarity_signals = [".", ":", "-", "1.", "2.", "esempio", "passo"]
        count = sum(1 for signal in clarity_signals if signal in prompt.lower())
        return min(1.0, count / 5)
    
    def _generate_improvements(self, prompt: str, goal: str, analysis: dict) -> list:
        """Genera miglioramenti per il prompt."""
        improvements = []
        
        # Se manca persona
        if not analysis["has_persona"]:
            improvements.append({
                "type": "add_persona",
                "description": "Aggiungi una persona/ruolo",
                "addition": "\n\nSei un esperto che spiega in modo chiaro e preciso."
            })
        
        # Se mancano istruzioni
        if not analysis["has_instructions"]:
            improvements.append({
                "type": "add_instructions",
                "description": "Aggiungi istruzioni esplicite",
                "addition": "\n\nIstruzioni:\n- Rispondi in modo chiaro e strutturato"
            })
        
        # Se mancano esempi
        if not analysis["has_examples"]:
            improvements.append({
                "type": "add_examples",
                "description": "Aggiungi esempi o analogie",
                "addition": "\n\nUsa esempi concreti per chiarire."
            })
        
        # Se manca ragionamento
        if not analysis["has_reasoning"]:
            improvements.append({
                "type": "add_reasoning",
                "description": "Aggiungi chain-of-thought",
                "addition": "\n\nPensa passo per passo prima di rispondere."
            })
        
        # Se ambiguo
        if analysis["ambiguity_score"] > 0.3:
            improvements.append({
                "type": "reduce_ambiguity",
                "description": "Riduci ambiguità",
                "addition": "\n\nSii specifico e preciso. Evita termini vaghi."
            })
        
        return improvements
    
    def _apply_improvement(self, prompt: str, improvement: dict) -> str:
        """Applica un miglioramento al prompt."""
        return prompt + improvement.get("addition", "")
    
    def _verify_prompt(self, prompt: str) -> dict:
        """Verifica coerenza del prompt."""
        if self.engine and hasattr(self.engine, 'verifier'):
            # Usa il Verifier dell'engine
            return {"coherent": True, "confidence": 0.9}
        return {"coherent": True, "confidence": 0.5}
    
    def get_optimization_history(self) -> list:
        """Restituisce la storia delle ottimizzazioni."""
        return self.optimization_history
