# Analisi Logica del ReasoningEngine v2.0

## Panoramica del Sistema

Il ReasoningEngine è un sistema multi-agent per il ragionamento automatizzato. Ecco l'architettura:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ReasoningEngine (main)                       │
│  ┌──────────────┬──────────────┬─────────────┬────────────────┐ │
│  │ Fast-Path    │ Multi-Agent  │ Question    │ Fallback       │ │
│  │ (greeting,  │ Pipeline     │ Based       │ (web, LLM)     │ │
│  │  datetime,  │ (Manager)    │ Reasoner    │                │ │
│  │  compare,   │              │             │                │ │
│  │  lookup)    │              │             │                │ │
│  └──────────────┴──────────────┴─────────────┴────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Knowledge     │    │ Tools         │    │ Reasoning     │
│ Graph         │    │ (web, math,   │    │ (deductive,   │
│               │    │  memory,      │    │  inductive,   │
│ (memory store)│    │  datetime)   │    │  analogical)  │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Flusso di Elaborazione (metodo `reason()`)

### 1. Parsing Iniziale
```python
parsed_dict = self._parse_question(question)  # NLP parsing
route_mode = self._classify_route_mode(question, parsed)
```
- Estrae intent, entità, numeri, operatori
- Classifica la query (deterministic_fact, date_time, open_world, reasoning_required)

### 2. Fast-Path (Sistema 1 - Risposte Rapide)
Ordine di elaborazione:

| Ordine | Tipo | Esempi | Comportamento |
|--------|------|--------|---------------|
| 1 | Saluti | "ciao", "come stai" | Risposta diretta |
| 2 | Commenti | "grazie", "ok" | Risposta casuale |
| 3 | Capacità | "chi sei?", "cosa puoi fare" | Identity lookup |
| 4 | Math | "2+2", "calcola area" | MathModule |
| 5 | DateTime | "che giorno è?", "che ora è" | DateTimeTool |
| 6 | **Confronti** | "chi è più vecchio tra X e Y" | **Web search** |
| 7 | Logica/Deduzione | "Se tutti gli X sono Y..." | DeductiveReasoner |
| 8 | Lookup | "capitale di Italia" | Knowledge Graph |

### 3. Slow-Path (Sistema 2 - Multi-Agent)
Se i fast-path falliscono:
```
Manager orchestrate():
  ├─ Researcher (cerca info da KG, web, memory)
  ├─ Analyst (sintetizza e genera risposta)
  └─ Critic (verifica qualità, pertinence, grounding)
       │
       └─ Se rejected → retry (max 2 iterazioni)
```

### 4. Fallback
Se la risposta dell'agente è debole:
```
if weak_answer and route_mode == "open_world" and pertinence < 0.15:
    → Web fallback (DuckDuckGo)

if use_llm and self.llm.is_available() and confidence < 0.30:
    → LLM fallback (Gemma via Ollama)
```

## Componenti Chiave

### 1. Knowledge Graph (`data/graph.py`)
- Memorizza entità, relazioni, esempi
- Cerca per nome, similarità semantica
- Persistenza JSON

### 2. Agent Pipeline
- **Researcher**: cerca informazioni da KG, web, vector memory
- **Analyst**: sintetizza i dati in una risposta coerente
- **Critic**: verifica pertinenza (keyword overlap), grounding (evidenze), lunghezza

### 3. Strumenti
| Tool | Funzione |
|------|----------|
| WebTool | Ricerca DuckDuckGo, parsing HTML |
| MemoryTool | Vector store + embeddings (sentence-transformers, Ollama) |
| MathModule | Calcoli matematici |
| DateTimeTool | Data/ora locale |
| BrowsingTool | Web scraping profondo |

### 4. Reasoning Modules
- **Deductive**: sillogismi, logica formale
- **Inductive**: generalizzazione da esempi
- **Analogical**: ragionamento per analogia

### 5. Question-Based Reasoner (opzionale)
- HypothesisSpace con prior probabilities
- Information Gain per selezionare domande
- Aggiornamento Bayesian delle probabilità

## Problemi Identificati

### Problema 1: Confronti non funzionano
**Sintomo**: "chi è più vecchio tra albano e mick jagger?" → restituisce info sui Rolling Stones

**Causa**: Il fast-path confronti usa `search_and_summarize()` che prende SOLO il primo risultato DuckDuckGo. Se la query contiene "Mick Jagger", restituisce info su di lui invece di confrontare.

**Codice problema** (`web.py:185-186`):
```python
first_result = result["results"][0]
summary = first_result.get("content", "")[:400]
```

**Soluzione**: Modificare la query di ricerca per i confronti:
- Invece di: "chi è più vecchio tra albano e mick jagger"
- Usare: "confronto età albano vs mick jagger" o estrarre le entità e cercare entrambe

### Problema 2: Critic blocks too many answers (RISOLTO)
**Problema**: Threshold troppo alto (0.30) bloccava risposte buone
**Soluzione**: Ridotto a 0.15 (già applicato)

### Problema 3: Output mostra dati interni (RISOLTO)
**Problema**: Risposta mostra steps, explanation, verified
**Soluzione**: Pulito output in app.py (già applicato)

### Problema 4: Ollama non attivo senza API key (RISOLTO)
**Soluzione**: Modificato `bridge.py` per restituire True per Ollama (già applicato)

## Schema delle Classi Principali

```
ReasoningEngine
├── knowledge: KnowledgeGraph
├── rules: RuleEngine
├── learner: Learner
├── verifier: Verifier
├── explainer: Explainer
├── math: MathModule
├── finance_data: FinancialDataTool
├── data_analyzer: DataAnalysisTool
├── memory: MemoryTool
├── browser: BrowsingTool
├── web: WebTool
├── datetime: DateTimeTool
├── agents: AgentManager
│   ├── researcher: ResearcherAgent
│   ├── analyst: AnalystAgent
│   └── critic: CriticAgent
├── deductive: DeductiveReasoner
├── inductive: InductiveReasoner
├── analogical: AnalogicalReasoner
└── llm: LLMBridge
```

## Flusso Dati Completo

```
User Question
      │
      ▼
┌─────────────┐
│ Parse (NLP)│ → intent, entities, numbers
└─────────────┘
      │
      ▼
┌─────────────┐
│ Classify   │ → route_mode (fast-path vs slow-path)
│ Route      │
└─────────────┘
      │
      ├─→ Fast-Path: greeting, math, datetime, compare, lookup
      │
      └─→ Slow-Path: Multi-Agent Pipeline
                    │
                    ▼
            ┌───────────────┐
            │   Researcher │
            │ (search KG,  │
            │  web, memory)│
            └───────────────┘
                    │
                    ▼
            ┌───────────────┐
            │    Analyst   │
            │ (synthesize) │
            └───────────────┘
                    │
                    ▼
            ┌───────────────┐
            │    Critic    │
            │ (verify)     │
            └───────────────┘
                    │
         ┌───────────┴───────────┐
         ▼                       ▼
    APPROVED               REJECTED
    (return answer)        (retry or fallback)
```

## Metriche di Configurazione

| Parametro | Valore | Descrizione |
|-----------|--------|-------------|
| WEB_FALLBACK_MIN_PERTINENCE | 0.15 | Minima pertinenza per web fallback |
| LLM_FALLBACK_MIN_CONFIDENCE | 0.30 | Minima confidenza per LLM fallback |
| MAX_WEB_FALLBACKS | 2 | Max retry web |
| MAX_ITERATIONS (Manager) | 2 | Max iterazioni agenti |
| PERTINENCE_THRESHOLD (Critic) | 0.15 | Soglia pertinenza |
| GROUNDING_THRESHOLD (Critic) | 0.10 | Soglia grounding |

## Prossimi Miglioramenti Proposti

1. **Migliorare confronti**: usare query strutturate per confronti diretti
2. **Integrare Question-Based Reasoner**: attivare per query ambigue
3. **Aggiungere caching**: memorizzare risposte recenti
4. **Migliorare parsing italiano**: supportare più pattern linguistici
5. **Aggiungere multi-lingua**: supporto completo EN/IT
