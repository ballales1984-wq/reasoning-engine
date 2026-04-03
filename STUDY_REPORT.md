# Studio del Piano di Ricerca e Sviluppo

## Riepilogo del Sistema

Il ReasoningEngine è un motore di ragionamento artificiale che ragiona come un essere umano:
fa domande, elimina ipotesi, aggiorna probabilità e arriva a una sola conclusione.

---

## Architettura a 3 Livelli

### Livello 1 — Ragionamento (Core Cognitivo)
- **Question-Based Reasoner** (9 file, ~300 righe)
- Deduzione, induzione, analogia
- Information gain, probabilità, spiegazione

### Livello 2 — Conoscenza (Knowledge Layer)
- **Knowledge Graph** (graph.py, 239 righe) — nodi, proprietà, relazioni
- **Memoria vettoriale** (vector_store.py) — embedding semantici
- **LLM** (ollama.py, bridge.py) — conoscenza linguistica
- **Web browsing** (browsing_tool.py) — conoscenza esterna

### Livello 3 — Agenti (Orchestrazione)
- **Researcher** — raccoglie informazioni
- **Analyst** — ragiona
- **Critic** — verifica
- **Manager** — orchestra

---

## Come il Sistema Ottiene le Caratteristiche

### Fonte 1 — Knowledge Graph (strutturato)
```python
graph.get("gatto").channels["local"]
→ {"description": "...", "category": "animale"}
```
**Affidabilità:** Massima (dati verificati)

### Fonte 2 — LLM (estrazione automatica)
Quando il grafo non ha info, il LLM genera proprietà:
- "Quali caratteristiche distinguono un lupo da cane/gatto/volpe?"
- Il sistema normalizza e inserisce nel grafo

### Fonte 3 — Web + Memoria Vettoriale
Il Researcher cerca sul web → embedding → memoria vettoriale → aggiorna il grafo

---

## Errori Logici e Casi Limite Identificati

| Problema | Causa | Soluzione Proposta |
|----------|-------|-------------------|
| Risposte sbagliate | Utente erra | Probabilità morbide, non azzeramento |
| Risposte "non so" | Ambiguità | Risposta "unknown", mantiene ipotesi |
| Probabilità a zero | Update aggressivo | Moltiplicare per 0.1 invece di azzerare |
| Stop prematura | Nessuna feature区分 | Soglia confidenza (0.95), avvisa se indeciso |
| Entropia nulla | Priors azzerati | Controllo stato inconsistente |
| Più ipotesi finali | Caratteristiche insufficienti | "Servono altre info" invece di fingere certezza |

---

## Dimensione del Programma

| Componente | Righe stimat | Note |
|-----------|-------------|------|
| Question-Based Reasoner | ~300 | 9 file |
| Knowledge Graph | 239 | graph.py |
| Vector Store | ~150 | embedding |
| Reasoning (deduttivo, induttivo, analogico) | ~800 | pipeline, rules, verifier |
| Agenti (researcher, analyst, critic, manager) | ~600 | orchestrazione |
| LLM + Tools | ~500 | ollama, web, math, etc |
| **TOTALE** | **~2.600** | Sistema completo |

**Dimensione su disco:** ~2-4 MB (inclusi test, HTML, log)

---

## Punti Critici da Rafforzare

1. **Gestione incertezza** — Risposte "forse", probabilità morbide
2. **Normalizzazione LLM** — Da linguaggio naturale a booleani/valori
3. **Coerenza KG** — Validazione per evitare proprietà duplicate

---

## Flusso Completo: Knowledge Graph → LLM → Web → Reasoner

```
1. Utente chiede: "Che animale è?"
2. Researcher → cerca nel Knowledge Graph
3. Se manca info → LLM estrae caratteristiche
4. Se LLM insufficiente → Web browsing
5. Vector Store salva in memoria
6. Knowledge Graph si aggiorna
7. Question-Based Reasoner:
   - genera domande (Information Gain)
   - fa domande all'utente
   - elimina ipotesi incompatibili
   - aggiorna probabilità
   - arriva a conclusione
8. Explainer mostra il ragionamento
```

---

## Conclusione

Il piano è **valido, scalabile e futuristico**.

Il sistema è un'architettura da laboratorio di ricerca:
- ✅ Cognitivo completo
- ✅ Auto-apprendente
- ✅ Multi-canale (KG + LLM + Web)
- ✅ Estendibile
- ✅ Spiegabile

**Il Question-Based Reasoner è il cuore logico.**
**Il Knowledge Graph è la memoria strutturata.**
**Il Web + Vector Store è la conoscenza esterna.**
**Gli agenti sono il sistema esecutivo.**

---

*Studio generato il 2026-04-03*
