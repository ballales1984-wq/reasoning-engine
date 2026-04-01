# 🧠 ReasoningEngine v2.0

**Un AI che ragiona come un umano**

## Cosa può fare

### 📐 Matematica
- Addizione, sottrazione, moltiplicazione, divisione
- Potenze, radici, percentuali, fattoriali
- Geometria (area cerchio, rettangolo, triangolo, volume)
- Teorema di Pitagora
- Equazioni

### 💰 Finanza
- Interesse semplice e composto
- ROI (Return on Investment)
- Calcolo mutuo
- Margine di profitto
- Punto di pareggio
- Rapporto rischio/rendimento

### 🧠 Ragionamento
- **Deduttivo**: "Se tutti i gatti sono mammiferi → il gatto è un animale"
- **Induttivo**: Trova pattern da esempi
- **Analogico**: Trova somiglianze tra concetti

### 🌐 Web + Coding + LLM
- Ricerca online (DuckDuckGo)
- Esecuzione codice Python
- LLM locale (Ollama - Llama, Mistral, etc.)

### 📝 Prompt Engineering
- 8 template (zero-shot, few-shot, CoT, ToT, etc.)
- 8 stili (semplice, tecnico, creativo, etc.)
- Ottimizza prompt esistenti

## Come si usa

### Scarica e installa

```bash
# Clona il repository
git clone https://github.com/ballales1984-wq/reasoning-engine.git
cd reasoning-engine

# Installa dipendenze (nessuna richiesta!)

# Avvia
python main.py
```

### Usa l'exe (Windows)

```bash
# Compila l'exe
pip install pyinstaller
pyinstaller --onefile main.py

# L'exe sarà in dist/ReasoningEngine.exe
```

### Menu interattivo

```
╔════════════════════════════════════════╗
║        🧠 REASONING ENGINE v2.0       ║
╠════════════════════════════════════════╣
║  1. 💬 Chat con AI                    ║
║  2. 📐 Demo Matematica                ║
║  3. 💰 Demo Finanza                   ║
║  4. 🧪 Esegui Test                    ║
║  5. 🤖 Configura Ollama               ║
║  6. 🚀 Esci                           ║
╚════════════════════════════════════════╝
```

### Chat mode

```
Tu> quanto fa 15 + 27?
🧠 42.0

Tu> area cerchio raggio 5
🧠 Area cerchio (r=5.0): π × 5.0² = 78.5398

Tu> :math radice di 144
→ √144.0 = 12.0

Tu> :finance
→ Scegli: 1 (interesse composto)
→ 1000€ × (1 + 7.0%)^10 = 1967.15€
```

## Integrazione Ollama (LLM locale)

1. Installa Ollama: https://ollama.com
2. Avvia: `ollama serve`
3. Scarica un modello: `ollama pull llama3.2`
4. L'app lo rileva automaticamente!

## Architettura

34 moduli, 11.500+ righe di codice, ispirata a Claude Code:

- Reasoning Loop (come query.ts)
- Tool System (12+ tool)
- Context Manager (pressione + compaction)
- State Manager (bootstrap + reactive store)
- Memory System (4 tipi)
- Permission System
- Persistence

## Test

16/16 test passati (100%):
- 5 test matematica
- 3 test ragionamento
- 6 test finanza
- 2 test NLP

```bash
python main.py
# Scegli: 4 (Esegui Test)
```

## Licenza

MIT

## Autore

Alessio Gnappo
