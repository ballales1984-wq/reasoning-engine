# ReasoningEngine v2.0

**Un AI che ragiona come un umano** — NLP, ragionamento deduttivo/induttivo/analogico, multi-agent, memoria vettoriale, LLM locale.

## Funzionalita

### Ragionamento
- **Deduttivo**: "Se tutti i gatti sono mammiferi, e Z e un gatto, allora Z e un animale"
- **Induttivo**: Trova pattern comuni da esempi concreti
- **Analogico**: Trova somiglianze strutturali tra concetti

### Multi-Agent System
- **Researcher**: Raccoglie informazioni da knowledge graph, memoria vettoriale e web
- **Analyst**: Processa dati e integra ragionamento simbolico (deduzione + analogia)
- **Critic**: Verifica qualita e coerenza delle risposte
- **Manager**: Orchestra il workflow Ricerca -> Analisi -> Critica

### Memoria Vettoriale (RAG)
- Vector store locale con accelerazione JIT (Numba)
- Embedding generati via Ollama (nomic-embed-text)
- Cosine similarity ottimizzata per ricerca semantica
- Cache matriciale per performance

### Matematica
- Addizione, sottrazione, moltiplicazione, divisione
- Potenze, radici, percentuali, fattoriali
- Geometria (area cerchio, rettangolo, triangolo, volume)
- Teorema di Pitagora
- Equazioni, derivate, integrali, matrici

### Finanza
- Interesse semplice e composto
- ROI, mutuo, margine di profitto, punto di pareggio
- Dati finanziari live (yfinance)

### Web + LLM
- Deep browsing con scraping testuale (BeautifulSoup)
- LLM locale via Ollama (gemma3:1b default)
- Generazione embedding GPU-accelerata
- Fallback automatico a LLM se l'engine non sa rispondere

### NLP Parser
- Intent classification (calculate, define, compare, explain, verify, learn, identity, search, code)
- Estrazione entita, numeri, operatori, relazioni
- Supporto italiano + inglese

### 📝 Prompt Engineering
- 8 template (zero-shot, few-shot, CoT, ToT, etc.)
- 8 stili (semplice, tecnico, creativo, etc.)
- Ottimizza prompt esistenti

### 🎯 Question-Based Reasoning (Indovina-Chi)
- **Nuovo motore di ragionamento iterativo**
- Genera domande utili basate sulle differenze tra ipotesi
- Seleziona la domanda migliore usando **Information Gain** (entropia)
- Aggiorna probabilità dopo ogni risposta
- Continua fino a una sola conclusione
- Produce spiegazione completa del percorso

_funziona come un detective: non indovina, indaga_

## Come si usa

### Scarica e installa

```bash
git clone https://github.com/ballales1984-wq/reasoning-engine.git
cd reasoning-engine
pip install numpy numba httpx beautifulsoup4 yfinance
python main.py
```

### Ollama (opzionale, per LLM locale)

1. Installa Ollama: https://ollama.com
2. Avvia: `ollama serve`
3. Scarica un modello: `ollama pull gemma3:1b`
4. Scarica embedding model: `ollama pull nomic-embed-text`

## Architettura

```
engine/
  __init__.py          # ReasoningEngine - entry point principale
  core/
    types.py           # Dataclass tipizzati (Entity, ParsedQuery, ReasoningResult, ecc.)
  nlp/
    parser.py          # NLP parser con intent classification
  reasoning/
    deductive.py       # Ragionamento deduttivo (modus ponens, sillogismo)
    inductive.py       # Ragionamento induttivo (pattern discovery)
    analogical.py      # Ragionamento analogico (structural similarity)
    rules.py           # Rule engine con regole matematiche
    verifier.py        # Verifica coerenza risultati
    explainer.py       # Generazione spiegazioni
  agents/
    base.py            # Interfaccia base agenti
    manager.py         # Orchestratore multi-agent
    researcher.py      # Agente ricerca
    analyst.py         # Agente analisi
    critic.py          # Agente verifica qualita
  data/
    graph.py           # Knowledge graph multi-canale
    learner.py         # Modulo apprendimento
    vector_store.py    # Memoria vettoriale JIT-accelerata
  tools/
    math.py            # Modulo matematico avanzato
    finance_data.py    # Dati finanziari
    data_analyzer.py   # Analisi dati
    memory_tool.py     # Tool memoria semantica (RAG)
    browsing_tool.py   # Deep web browsing
  llm/
    ollama.py          # Integrazione Ollama (LLM locale + embeddings)
```

## Test

```bash
python test_v2_core.py         # Test core engine
python test_multi_agent.py     # Test multi-agent system
python test_vector_memory.py   # Test memoria vettoriale
python test_benchmark.py       # Benchmark performance
python test_deep_reasoning.py  # Test ragionamento profondo
python test_power_tools.py     # Test tool avanzati
python test_browsing.py        # Test web browsing
```

## Licenza

MIT

## Autore

Alessio Gnappo
