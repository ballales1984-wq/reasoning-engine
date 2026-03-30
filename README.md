# ReasoningEngine — AI che ragiona come un umano

Un engine di ragionamento che agisce come filtro sopra LLM esistenti.

## Architettura

```
Utente → [ReasoningEngine] → LLM (opzionale) → [ReasoningEngine] → Risposta verificata
```

## Componenti

1. **KnowledgeGraph** — concetti collegati tra loro
2. **RuleEngine** — regole logiche esplicite
3. **Learner** — impara nuovi concetti da esempi minimi
4. **Verifier** — verifica coerenza delle risposte

## Come funziona

```python
from engine import ReasoningEngine

engine = ReasoningEngine()

# Insegna un concetto
engine.learn("6", examples=["🍎🍎🍎🍎🍎🍎", "sei cose", "5+1"])

# Insegna una regola
engine.learn_rule("addition", lambda a, b: a + b, description="somma due numeri")

# Ragiona su un problema
result = engine.reason("Quanto fa 6 + 9?")
# → Passo 1: So che 6 è una quantità
# → Passo 2: So che 9 è una quantità  
# → Passo 3: Applico la regola di addizione
# → Risultato: 15 ✅
```
