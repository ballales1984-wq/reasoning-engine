# ReasoningEngine — Architettura Completa

## Filosofia
L'engine ragiona, l'LLM fornisce conoscenza. Non il contrario.
L'engine è il cervello, l'LLM è l'enciclopedia.

---

## Architettura a Layer

```
┌─────────────────────────────────────────────────┐
│              USER INTERFACE                      │
│         (API / CLI / Chat / Web)                 │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│           LAYER 1: NLP PARSER                    │
│                                                  │
│  Input grezzo → Intent + Entities + Relations    │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Tokenizer│  │ Intent   │  │ Entity        │  │
│  │          │→ │ Classifier│→ │ Extractor     │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
└──────────────────────┬──────────────────────────┘
                       │ ParsedQuery
                       ▼
┌─────────────────────────────────────────────────┐
│         LAYER 2: REASONING CORE                  │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │         Pipeline Executor                 │   │
│  │                                           │   │
│  │  1. Knowledge Lookup                      │   │
│  │  2. Deductive Reasoning (se regole)       │   │
│  │  3. Inductive Reasoning (se esempi)       │   │
│  │  4. Analogical Reasoning (se similitudini)│   │
│  │  5. LLM Fallback (se non sa)              │   │
│  │  6. Verification                          │   │
│  │  7. Explanation Generation                │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌────────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ Deductive  │ │Inductive │ │ Analogical   │  │
│  │ Reasoner   │ │Reasoner  │ │ Reasoner     │  │
│  └────────────┘ └──────────┘ └──────────────┘  │
│                                                  │
│  ┌────────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ Knowledge  │ │ Rule     │ │ Learner      │  │
│  │ Graph      │ │ Engine   │ │              │  │
│  └────────────┘ └──────────┘ └──────────────┘  │
│                                                  │
│  ┌────────────┐ ┌──────────┐                    │
│  │ Verifier   │ │Explainer │                    │
│  └────────────┘ └──────────┘                    │
└──────────────────────┬──────────────────────────┘
                       │ ReasoningResult
                       ▼
┌─────────────────────────────────────────────────┐
│          LAYER 3: LLM BRIDGE                     │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │  LLMClient (Astrazione provider)         │   │
│  │  - OpenAI / Anthropic / Local / etc.     │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │  LLM Roles:                              │   │
│  │  1. Knowledge Provider (fatti nuovi)     │   │
│  │  2. Fallback Solver (quando engine non sa)│  │
│  │  3. Natural Language Generator            │   │
│  │  4. Pattern Suggester (suggerisce regole) │  │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │  LLM→Engine Bridge:                      │   │
│  │  Risposte LLM vengono VERIFICATE         │   │
│  │  dall'engine prima di accettarle.        │   │
│  │  Se l'LLM sbaglia, l'engine lo sa.       │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## Layer 1: NLP Parser

### Responsabilità
Trasformare input testuale in struttura dati comprensibile all'engine.

### Componenti

#### 1a. Tokenizer
- Splide il testo in token significativi
- Gestisce italiano (contrazioni, articoli, preposizioni)
- Normalizza (lowercase, rimuove accenti opzionali)

#### 1b. Intent Classifier
Classifica l'intento dell'utente:

| Intent | Esempi | Descrizione |
|--------|--------|-------------|
| `calculate` | "quanto fa 2+3?", "calcola il 20% di 100" | Operazione matematica |
| `define` | "cosa è un atomo?", "cos'è la gravità" | Definizione/concetto |
| `compare` | "qual è più grande, 5 o 7?", "differenza tra X e Y" | Confronto |
| `explain` | "perché il cielo è blu?", "come funziona X" | Spiegazione causale |
| `learn` | "il gatto è un mammifero", "6 = 5+1" | Insegnamento nuovo fatto |
| `verify` | "è vero che 2+2=4?", "conferma che X è Y" | Verifica di un fatto |
| `relate` | "cosa c'è in comune tra X e Y?" | Trova relazioni |
| `general` | fallback | Domanda generica |

#### 1c. Entity Extractor
Estrae entità dal testo:

- **Numeri:** interi, decimali, parole ("tre" → 3)
- **Concetti:** nomi propri, termini tecnici
- **Relazioni:** "è", "ha", "può", "contiene", "causa"
- **Quantificatori:** "tutti", "alcuni", "nessuno", "almeno"
- **Operatori logici:** "e", "o", "non", "se...allora"

### Output: `ParsedQuery`
```python
@dataclass
class ParsedQuery:
    raw: str                    # Input originale
    intent: str                 # Intent classificato
    entities: list[Entity]      # Entità estratte
    relations: list[Relation]   # Relazioni trovate
    numbers: list[float]        # Numeri estratti
    operators: list[str]        # Operatori logici/matematici
    confidence: float           # Confidenza del parsing
    language: str               # Lingua rilevata
```

---

## Layer 2: Reasoning Core

### 2a. Pipeline Executor
Il cuore del motore. Esegue la pipeline di ragionamento:

```
Input (ParsedQuery)
    │
    ▼
[1] Knowledge Lookup ──→ Trova concetti noti nel grafo
    │
    ▼
[2] Deductive Reasoning ──→ Applica regole logiche (se → allora)
    │
    ▼
[3] Inductive Reasoning ──→ Generalizza da esempi noti
    │
    ▼
[4] Analogical Reasoning ──→ Trova analogie con concetti simili
    │
    ▼
[5] LLM Fallback ──→ Se ancora non sa, chiede all'LLM
    │                    (con verifica!)
    ▼
[6] Verification ──→ Verifica coerenza del risultato
    │
    ▼
[7] Explanation ──→ Genera spiegazione del ragionamento
    │
    ▼
Output (ReasoningResult)
```

### 2b. Deductive Reasoner (NUOVO)
Ragiona dal generale al particolare.

**Formato regole deduttive:**
```python
# Tutti gli X sono Y → Se Z è X, allora Z è Y
Premessa 1: "Tutti i mammiferi sono animali"
Premessa 2: "Il gatto è un mammifero"
Conclusione: "Il gatto è un animale"
```

**Come funziona:**
1. Le regole sono nel Knowledge Graph come relazioni `è_un`, `sono`, `implica`
2. Il Deductive Reasoner catena le regole (forward chaining)
3. Può fare backward chaining (parte dalla conclusione e cerca premesse)

**Esempio di regola nel KG:**
```python
kg.add("mammifero", category="biologia")
kg.add("animale", category="biologia")
kg.add("gatto", category="biologia")
kg.connect("mammifero", "è_un_tipo_di", "animale")
kg.connect("gatto", "è_un_tipo_di", "mammifero")
# Il Deductive Reasoner deduce: gatto → animale
```

### 2c. Inductive Reasoner (NUOVO)
Ragiona dal particolare al generale.

**Come funziona:**
1. Riceve una lista di esempi
2. Trova il pattern comune
3. Crea una regola generale

**Esempio:**
```
Esempi: "il cane ha 4 zampe", "il gatto ha 4 zampe", "il cavallo ha 4 zampe"
Induzione: "I mammiferi terrestri tipicamente hanno 4 zampe"
```

**Implementazione:**
- Analisi di similarità tra esempi
- Estrazione di attributi comuni
- Generalizzazione con livello di confidenza

### 2d. Analogical Reasoner (NUOVO)
Trova somiglianze tra concetti diversi.

**Come funziona:**
1. Confronta la struttura di due concetti
2. Trova mapping tra le loro relazioni
3. Trasferisce proprietà da un concetto all'altro

**Esempio:**
```
Concetto A: "il sistema solare" (sole + pianeti in orbita)
Concetto B: "l'atomo" (nucleo + elettroni in orbita)
Analogia: "Un atomo è come un sistema solare in miniatura"
```

### 2e. Question-Based Reasoner (NUOVO)
Ragiona facendo domande, eliminando ipotesi, arrivando a una conclusione.

**Come funziona:**
1. Genera domande utili (che distinguono le ipotesi)
2. Seleziona la migliore (**Information Gain** = entropia)
3. Chiede la risposta (utente / LLM / sensori)
4. Aggiorna ipotesi + probabilità
5. Continua finché non ci sono più domande utili
6. Restituisce conclusione + trace completo

**Componenti:**
```
engine/question_based/
 ├── hypothesis_space.py    # Gestione ipotesi + probabilità
 ├── question_generator.py # Genera domande utili
 ├── information_gain.py  # Seleziona (entropia)
 ├── probability_updater.py # Aggiorna Bayes-like
 ├── question_reasoner.py  # Ciclo completo
 └── explainer.py          # Trace log
```

**Esempio "Indovina l'animale":**
```
Ipotesi: cane, gatto, volpe, coniglio
Domanda: "È domestico?" → risposta: sì
Ipotesi rimanenti: cane, gatto, coniglio

Domanda: "Ha la coda lunga?" → risposta: sì
Ipotesi rimanenti: gatto, coniglio

Domanda: "Fa 'miao'?" → risposta: no
Ipotesi rimanenti: cane

Conclusione: cane (100%)
```

**Perché è rivoluzionario:**
- Non indovina, indaga
- Non allucina, esclude
- Arriva a una sola conclusione
- Spiega il percorso logico
- Funziona come un detective umano

### 2f. Knowledge Graph (esteso)
Il grafo esistente + nuovi tipi di relazione:

| Relazione | Esempio | Uso |
|-----------|---------|-----|
| `è_un` | gatto → mammifero | Tassonomia |
| `ha_propietà` | acqua → liquido | Attributi |
| `causa` | pioggia → bagnato | Causalità |
| `è_parte_di` | ruota → macchina | Composizione |
| `è_simile_a` | gatto ↔ tigre | Analogia |
| `si_oppone_a` | caldo ↔ freddo | Opposizione |
| `implica` | piove → strada_bagnata | Logica |
| `è_un_esempio_di` | Roma → capitale | Istanza |
| `ha_attributo` | gatto → peloso | Proprietà |
| `può` | uccello → volare | Capacità |
| `non_può` | pesce → volare | Limitazione |
| `è_necessario_per` | ossigeno → respirare | Prerequisito |

### 2f. Rule Engine (esteso)
Oltre le regole matematiche, aggiunge regole logiche:

```python
# Regola logica: Modus Ponens
# Se A implica B, e A è vero, allora B è vero

# Regola logica: Sillogismo
# Se tutti gli A sono B, e tutti i B sono C, allora tutti gli A sono C

# Regola logica: Modus Tollens
# Se A implica B, e B è falso, allora A è falso

# Regola di default
# Se X normalmente è Y, e non ci sono evidenze contrarie, X è Y
```

---

## Layer 3: LLM Bridge

### Principio fondamentale
**L'LLM è un tool dell'engine, non il contrario.**

L'engine controlla quando e come chiamare l'LLM.
Le risposte dell'LLM vengono verificate prima di essere accettate.

### 3a. LLMClient (Astrazione)
```python
class LLMClient:
    """Astrazione per qualsiasi provider LLM."""
    
    def __init__(self, provider="openai", model="gpt-4", api_key=None):
        ...
    
    def ask(self, prompt: str, context: dict = None) -> str:
        """Manda un prompt e riceve una risposta."""
        ...
    
    def extract_facts(self, text: str) -> list[dict]:
        """Estrae fatti strutturati da testo libero."""
        ...
    
    def suggest_rules(self, examples: list[str]) -> list[dict]:
        """Suggerisce regole basandosi su esempi."""
        ...
```

### 3b. Ruoli dell'LLM

| Ruolo | Quando | Come |
|-------|--------|------|
| **Knowledge Provider** | L'engine non conosce un concetto | Chiede "cos'è X?" → estrae fatti → aggiunge al KG |
| **Fallback Solver** | Nessuna regola applicabile | Chiede di risolvere → verifica il risultato |
| **NL Generator** | Output finale | Converte ragionamento in linguaggio naturale |
| **Pattern Suggester** | Inductive reasoning | Suggerisce regole da esempi |

### 3c. LLM→Engine Bridge (Verifica)
**Questo è il pezzo chiave.**

```
LLM dice: "La capitale della Francia è Parigi"
    │
    ▼
Engine verifica:
  1. "Parigi" è nel KG come capitale? → Se sì, conferma
  2. "Francia" ha relazione "ha_capitale" → Se sì, verifica
  3. Se non sa → marca come "non verificato" con confidenza ridotta
```

**Principio:** L'engine non accetta ciecamente le risposte dell'LLM.
Se l'LLM sbaglia (e sbaglia), l'engine deve poterlo rilevare.

---

## ReasoningResult (Output)

```python
@dataclass
class ReasoningResult:
    answer: any                          # La risposta
    confidence: float                    # 0-1
    reasoning_type: str                  # deductive/inductive/analogical/llm
    steps: list[ReasoningStep]           # Passaggi del ragionamento
    explanation: str                     # Spiegazione in linguaggio naturale
    verified: bool                       # Verificato?
    knowledge_used: list[str]            # Concetti usati
    rules_used: list[str]                # Regole usate
    llm_used: bool                       # Ha usato l'LLM?
    sources: list[str]                   # Da dove viene la conoscenza

@dataclass
class ReasoningStep:
    type: str                            # lookup/deduction/induction/etc.
    description: str                     # Cosa ha fatto
    input: any                           # Input del passo
    output: any                          # Output del passo
    confidence: float                    # Confidenza del passo
```

---

## Flussi di Esempio

### Flusso 1: Domanda matematica (già funziona)
```
"quanto fa 15 + 27?"
→ NLP Parser: intent=calculate, numbers=[15,27], op=addition
→ Pipeline: Rule Engine → addition(15,27) = 42
→ Verifier: 42-27=15 ✓
→ Explainer: "15 + 27 = 42"
→ Result: 42, confidence=1.0, llm_used=false
```

### Flusso 2: Ragionamento deduttivo (NUOVO)
```
"il gatto è un animale?"
→ NLP Parser: intent=verify, entities=[gatto, animale], relation=è_un
→ Pipeline:
  [1] KG Lookup: gatto → è_un_tipo_di → mammifero
  [2] Deductive: mammifero → è_un_tipo_di → animale
  [3] Catena: gatto → mammifero → animale
→ Verifier: catena valida ✓
→ Explainer: "Il gatto è un mammifero, e tutti i mammiferi sono animali. Quindi sì, il gatto è un animale."
→ Result: Sì, confidence=0.95, llm_used=false
```

### Flusso 3: Apprendimento + Induzione (NUOVO)
```
User: "il cane ha 4 zampe, il gatto ha 4 zampe, il cavallo ha 4 zampe"
→ NLP Parser: intent=learn (multipli esempi)
→ Inductive Reasoner:
  - Analizza esempi
  - Pattern comune: "4 zampe" + tutti sono "mammiferi terrestri"
  - Regola: "I mammiferi terrestri hanno 4 zampe" (confidenza: 0.8)
→ KG Update: aggiunge regola indotta
→ Explainer: "Ho notato un pattern: questi mammiferi terrestri hanno tutti 4 zampe."
```

### Flusso 4: LLM Fallback (NUOVO)
```
"qual è la velocità della luce?"
→ NLP Parser: intent=define, entities=[velocità della luce]
→ Pipeline:
  [1] KG Lookup: "velocità della luce" → non trovato
  [2] Deductive: nessuna regola applicabile
  [3] Inductive: nessun esempio disponibile
  [4] Analogical: nessuna analogia trovata
  [5] LLM Bridge: chiede all'LLM
      LLM risponde: "299,792,458 m/s"
      Engine verifica: valore numerico? unità coerente? range sensato?
      → Verificato come "fisicamente plausibile"
  [6] KG Update: aggiunge "velocità della luce" = "299792458 m/s"
→ Result: 299792458 m/s, confidence=0.9, llm_used=true, verified=true
```

### Flusso 5: Analogia (NUOVO)
``"come funziona il cuore?"
→ NLP Parser: intent=explain, entities=[cuore]
→ Pipeline:
  [1] KG Lookup: cuore → ha_propietà → pompa, muscolo
  [2] Analogical: cuore ↔ pompa dell'acqua
      - Entrambi: spingono liquido attraverso tubi
      - Entrambi: hanno un ritmo ciclico
      - Entrambi: si rompono se non lubrificati
→ Explainer: "Il cuore è come una pompa: spinge il sangue attraverso i vasi sanguigni, in modo ciclico, per portare ossigeno e nutrienti a tutto il corpo."
→ Result: ..., reasoning_type=analogical
```

---

## Implementazione — Ordine Suggerito

### Fase 1: Architettura (OGGI)
- [x] Questo documento
- [ ] Struttura directory nuovi moduli
- [ ] Dataclass e interfacce

### Fase 2: NLP Parser
- [ ] Tokenizer italiano
- [ ] Intent Classifier (regole + pattern matching)
- [ ] Entity Extractor
- [ ] ParsedQuery dataclass

### Fase 3: Reasoning Core
- [ ] Deductive Reasoner
- [ ] Inductive Reasoner
- [ ] Analogical Reasoner
- [x] Question-Based Reasoner (✅ implementato!)
- [ ] Pipeline Executor (orchestratore)
- [ ] Estensione Knowledge Graph (nuovi tipi di relazione)
- [ ] Estensione Rule Engine (regole logiche)

### Fase 4: LLM Bridge
- [ ] LLMClient (astrazione provider)
- [ ] Ruoli LLM (provider, fallback, generator, suggester)
- [ ] LLM→Engine Bridge (verifica risposte)

### Fase 5: Integrazione & Test
- [ ] ReasoningEngine aggiornato con pipeline completa
- [ ] Test di tutti i flussi
- [ ] Demo interattiva

### Fase 6: Persistenza
- [ ] Salva/carica Knowledge Graph (JSON/SQLite)
- [ ] Salva/carica regole
- [ ] Salva/carica cronologia apprendimento

---

## Tecnologie

- **Linguaggio:** Python (già usato)
- **LLM:** OpenAI API (gpt-4o-mini per iniziare, economico)
- **Persistenza:** JSON files → SQLite se serve
- **NLP:** Spacy (italiano) o rule-based per iniziare
- **Test:** pytest

## Note Architetturali

1. **No LLM-first.** L'engine ragiona PRIMA, l'LLM è fallback.
2. **Verifica sempre.** Ogni risposta (engine o LLM) viene verificata.
3. **Spiega sempre.** Ogni risposta ha un reasoning trace.
4. **Impara sempre.** Ogni interazione può insegnare qualcosa.
5. **Confidenza onesta.** Se non sai, dillo. Mai inventare.
