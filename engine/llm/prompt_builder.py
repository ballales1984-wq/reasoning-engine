"""
PromptBuilder — Assembla il prompt dinamicamente, come Claude Code.

In Claude Code, il system prompt non è un singolo testo.
È un ARRAY di segmenti assemblati dinamicamente:
- identità e safety framing
- behavioral instructions
- tool descriptions
- environment info
- memory content
- session-specific guidance

Noi facciamo lo stesso per il ReasoningEngine.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PromptSegment:
    """Un segmento del prompt."""
    name: str
    content: str
    priority: int = 0          # Priorità (più alto = più importante)
    always_include: bool = False  # Sempre incluso?
    max_tokens: int = 0        # Limite token (0 = nessun limite)


class PromptBuilder:
    """
    Assembla il prompt per il ragionamento.
    
    Come Claude Code, non usa un prompt statico.
    Assembla dinamicamente in base al contesto.
    """
    
    def __init__(self):
        self.segments = []
        self._register_default_segments()
    
    def _register_default_segments(self):
        """Registra i segmenti di default."""
        
        # Identità
        self.add_segment(PromptSegment(
            name="identity",
            content="""Sei un ReasoningEngine — un AI che ragiona come un umano.
Non applichi pattern statistici — costruisci comprensione step-by-step.
Ogni risposta deve essere VERIFICATA e SPIEGATA.""",
            priority=100,
            always_include=True
        ))
        
        # Behavioral rules
        self.add_segment(PromptSegment(
            name="behavior",
            content="""Regole di comportamento:
1. Ragiona passo per passo
2. Verifica ogni risultato
3. Spiega il tuo ragionamento
4. Se non sai, dillo (non inventare)
5. Impara dagli errori""",
            priority=90,
            always_include=True
        ))
        
        # Tool descriptions
        self.add_segment(PromptSegment(
            name="tools",
            content="""Tool disponibili:
- knowledge_lookup: cerca concetti nel knowledge graph
- apply_rule: applica una regola logica
- math_solve: risolvi problemi matematici
- verify: verifica un risultato
- deduce: fai deduzioni logiche
- induce: trova pattern da esempi
- find_analogy: trova analogie
- recall_memory: richiama dalla memoria
- store_memory: salva in memoria
- llm_query: chiedi all'LLM (fallback)""",
            priority=80,
            always_include=True
        ))
        
        # Reasoning strategy
        self.add_segment(PromptSegment(
            name="strategy",
            content="""Strategia di ragionamento:
1. Analizza la domanda (cosa chiede?)
2. Cerca nella memoria (già visto?)
3. Cerca nel knowledge graph (conosco il concetto?)
4. Applica regole (posso dedurre?)
5. Cerca analogie (è simile a qualcosa?)
6. Verifica (ha senso?)
7. Spiega (perché è giusto?)""",
            priority=70,
            always_include=True
        ))
    
    def add_segment(self, segment: PromptSegment):
        """Aggiunge un segmento al prompt."""
        self.segments.append(segment)
    
    def remove_segment(self, name: str):
        """Rimuove un segmento per nome."""
        self.segments = [s for s in self.segments if s.name != name]
    
    def build(self, context: dict = None, question: str = None) -> str:
        """
        Assembla il prompt finale.
        
        Come Claude Code:
        1. Filtra i segmenti rilevanti
        2. Ordina per priorità
        3. Concatena
        4. Applica limiti
        """
        context = context or {}
        
        # Filtra segmenti
        included = []
        
        for segment in self.segments:
            if segment.always_include:
                included.append(segment)
            else:
                # Includi solo se rilevante al contesto
                if self._is_relevant(segment, context, question):
                    included.append(segment)
        
        # Ordina per priorità (più alto prima)
        included.sort(key=lambda s: s.priority, reverse=True)
        
        # Assembla
        parts = []
        for segment in included:
            content = segment.content
            
            # Applica limite token se specificato
            if segment.max_tokens > 0:
                words = content.split()
                if len(words) > segment.max_tokens:
                    content = " ".join(words[:segment.max_tokens]) + "..."
            
            parts.append(f"[{segment.name}]\n{content}")
        
        return "\n\n".join(parts)
    
    def _is_relevant(self, segment: PromptSegment, context: dict, question: str) -> bool:
        """Determina se un segmento è rilevante al contesto."""
        
        # Controlla se le parole chiave del segmento sono nel contesto
        segment_lower = segment.content.lower()
        question_lower = (question or "").lower()
        
        # Match semplice
        for word in question_lower.split():
            if len(word) > 3 and word in segment_lower:
                return True
        
        return False
    
    def build_with_memory(self, memory_context: dict, knowledge_context: dict = None) -> str:
        """
        Assembla il prompt con memoria e conoscenza.
        
        Come Claude Code che inietta CLAUDE.md e MEMORY.md.
        """
        # Aggiungi segmento memoria
        if memory_context:
            memory_content = "Memoria corrente:\n"
            
            if memory_context.get("focus"):
                memory_content += f"- Focus: {memory_context['focus']}\n"
            
            if memory_context.get("working_memory"):
                memory_content += "- Working memory:\n"
                for item in memory_context["working_memory"][:5]:
                    memory_content += f"  • {item}\n"
            
            self.add_segment(PromptSegment(
                name="memory",
                content=memory_content,
                priority=85,
                max_tokens=200
            ))
        
        # Aggiungi segmento conoscenza
        if knowledge_context:
            knowledge_content = "Conoscenza rilevante:\n"
            
            for concept in knowledge_context.get("concepts", [])[:5]:
                knowledge_content += f"- {concept.get('name', '')}: {concept.get('description', '')[:100]}\n"
            
            self.add_segment(PromptSegment(
                name="knowledge",
                content=knowledge_content,
                priority=75,
                max_tokens=300
            ))
        
        return self.build()
