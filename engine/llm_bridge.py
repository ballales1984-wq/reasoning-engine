"""
LLM Bridge — L'LLM come tool dell'engine, non viceversa.

Ruoli:
1. Knowledge Provider — quando l'engine non conosce un concetto
2. Fallback Solver — quando nessuna regola si applica
3. Natural Language Generator — output in linguaggio naturale
4. Pattern Suggester — suggerisce regole da esempi

Principio: l'engine controlla, l'LLM esegue.
Le risposte dell'LLM vengono VERIFICATE prima di essere accettate.
"""

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    """Risposta strutturata dall'LLM."""
    raw: str                           # Risposta grezza
    facts: list = field(default_factory=list)      # Fatti estratti
    confidence: float = 0.0            # Confidenza assegnata
    verified: bool = False             # Verificato dall'engine?
    source: str = "llm"               # Fonte della conoscenza


@dataclass
class ExtractedFact:
    """Un fatto estratto dalla risposta dell'LLM."""
    subject: str
    relation: str
    value: str
    confidence: float = 0.8
    verifiable: bool = True


class LLMClient:
    """
    Client astratto per qualsiasi provider LLM.
    Supporta OpenAI, Anthropic, o qualsiasi API compatibile.
    """

    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini",
                 api_key: str = None, base_url: str = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url or self._default_base_url()
        self._client = None

    def _default_base_url(self) -> str:
        urls = {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
            "ollama": "http://localhost:11434/v1",
        }
        return urls.get(self.provider, "https://api.openai.com/v1")

    def _get_client(self):
        """Lazy init del client HTTP."""
        if self._client is None:
            import urllib.request
            self._client = urllib.request
        return self._client

    def ask(self, prompt: str, system: str = None, max_tokens: int = 500) -> str:
        """
        Manda un prompt all'LLM e ritorna la risposta testuale.
        """
        import urllib.request
        import urllib.error

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3,  # Bassa temperatura per risposte fattuali
        }

        data = json.dumps(payload).encode("utf-8")
        url = f"{self.base_url}/chat/completions"

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else str(e)
            return f"ERRORE LLM: {e.code} - {error_body}"
        except Exception as e:
            return f"ERRORE LLM: {str(e)}"

    def is_configured(self) -> bool:
        """Verifica se il client è configurato."""
        return self.api_key is not None and len(self.api_key) > 10


class LLMBridge:
    """
    Ponte tra ReasoningEngine e LLM.
    L'engine chiama il bridge, il bridge chiama l'LLM,
    e verifica le risposte prima di restituirle.
    """

    def __init__(self, llm_client: LLMClient, knowledge_graph, verifier=None):
        self.llm = llm_client
        self.knowledge = knowledge_graph
        self.verifier = verifier
        self.history = []  # Log delle chiamate

    def is_available(self) -> bool:
        """Verifica se l'LLM è disponibile."""
        return self.llm.is_configured()

    # ============================================================
    # RUOLO 1: Knowledge Provider
    # ============================================================

    def provide_knowledge(self, concept: str) -> LLMResponse:
        """
        Chiede all'LLM informazioni su un concetto sconosciuto.
        Estrae fatti strutturati e li verifica.
        """
        if not self.is_available():
            return LLMResponse(raw="LLM non configurato", confidence=0.0)

        prompt = f"""Rispondi SOLO con fatti verificabili su "{concept}".
Formato JSON:
{{"descrizione": "...", "categoria": "...", "proprietà": ["...", "..."], "esempi": ["...", "..."], "relazioni": [["soggetto", "relazione", "oggetto"], ...]}}

Rispondi SOLO con il JSON, nient'altro."""

        system = "Sei un knowledge base. Rispondi con fatti oggettivi in formato JSON. Mai inventare."

        raw = self.llm.ask(prompt, system=system, max_tokens=300)
        response = LLMResponse(raw=raw, source="llm")

        # Parsa JSON
        facts = self._parse_knowledge_response(concept, raw)
        response.facts = facts

        # Verifica fatti
        if self.verifier:
            for fact in facts:
                fact.confidence = self._verify_fact(fact)
                if fact.confidence < 0.5:
                    fact.verifiable = False

        response.confidence = sum(f.confidence for f in facts) / max(len(facts), 1)
        response.verified = all(f.verifiable for f in facts) if facts else False

        self.history.append({
            "action": "provide_knowledge",
            "concept": concept,
            "facts_count": len(facts),
            "confidence": response.confidence
        })

        return response

    # ============================================================
    # RUOLO 2: Fallback Solver
    # ============================================================

    def fallback_solve(self, question: str, context: dict = None) -> LLMResponse:
        """
        Chiede all'LLM di risolvere un problema che l'engine non sa risolvere.
        La risposta viene verificata.
        """
        if not self.is_available():
            return LLMResponse(raw="LLM non configurato", confidence=0.0)

        # Costruisci contesto
        ctx_text = ""
        if context:
            if context.get("known_concepts"):
                ctx_text += f"Concetti noti: {', '.join(context['known_concepts'])}\n"
            if context.get("steps"):
                ctx_text += f"Passi già tentati: {'; '.join(context['steps'])}\n"

        prompt = f"""Risolvi questo problema e spiega il ragionamento step by step.
{ctx_text}
Domanda: {question}

Rispondi in formato JSON:
{{"risposta": "...", "spiegazione": "...", "passaggi": ["...", "..."], "confidenza": 0.0-1.0}}

Rispondi SOLO con il JSON."""

        system = """Sei un risolutore di problemi. Spiega ogni passaggio.
Se non sei sicuro, metti confidenza bassa. Mai inventare numeri."""

        raw = self.llm.ask(prompt, system=system, max_tokens=500)
        response = LLMResponse(raw=raw, source="llm")

        # Parsa risposta
        result = self._parse_solve_response(raw)
        if result:
            response.facts = [ExtractedFact(
                subject=question,
                relation="risposta",
                value=str(result.get("risposta", "")),
                confidence=result.get("confidenza", 0.5)
            )]
            response.confidence = result.get("confidenza", 0.5)

        self.history.append({
            "action": "fallback_solve",
            "question": question,
            "confidence": response.confidence
        })

        return response

    # ============================================================
    # RUOLO 3: NL Generator
    # ============================================================

    def generate_explanation(self, reasoning_steps: list[str],
                             answer: Any, question: str) -> str:
        """
        Converte il ragionamento dell'engine in linguaggio naturale.
        """
        if not self.is_available():
            # Fallback senza LLM
            return self._generate_simple_explanation(reasoning_steps, answer)

        steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(reasoning_steps))

        prompt = f"""Converti questi passaggi di ragionamento in una spiegazione chiara e naturale in italiano.

Domanda: {question}
Risposta: {answer}

Passaggi del ragionamento:
{steps_text}

Scrivi una spiegazione concisa e chiara, come se la spiegassi a un amico."""

        system = "Sei un comunicatore scientifico. Spiega in modo semplice e diretto."

        return self.llm.ask(prompt, system=system, max_tokens=300)

    # ============================================================
    # RUOLO 4: Pattern Suggester
    # ============================================================

    def suggest_rules(self, examples: list[str]) -> LLMResponse:
        """
        Analizza esempi e suggerisce regole/pattern.
        """
        if not self.is_available():
            return LLMResponse(raw="LLM non configurato", confidence=0.0)

        examples_text = "\n".join(f"- {e}" for e in examples)

        prompt = f"""Analizza questi esempi e trova il pattern comune.
Genera una regola generale.

Esempi:
{examples_text}

Rispondi in formato JSON:
{{"regola": "...", "categoria": "...", "confidenza": 0.0-1.0, "spiegazione": "..."}}

Rispondi SOLO con il JSON."""

        system = "Sei un analista di pattern. Trova regole generali da esempi specifici."

        raw = self.llm.ask(prompt, system=system, max_tokens=300)
        response = LLMResponse(raw=raw, source="llm")

        result = self._parse_json_response(raw)
        if result:
            response.confidence = result.get("confidenza", 0.5)
            response.facts = [ExtractedFact(
                subject="pattern",
                relation="regola",
                value=result.get("regola", ""),
                confidence=response.confidence
            )]

        return response

    # ============================================================
    # HELPERS
    # ============================================================

    def _parse_knowledge_response(self, concept: str, raw: str) -> list[ExtractedFact]:
        """Estrae fatti dalla risposta JSON dell'LLM."""
        data = self._parse_json_response(raw)
        if not data:
            return []

        facts = []

        # Descrizione
        if "descrizione" in data:
            facts.append(ExtractedFact(
                subject=concept, relation="descrizione",
                value=data["descrizione"], confidence=0.9
            ))

        # Categoria
        if "categoria" in data:
            facts.append(ExtractedFact(
                subject=concept, relation="categoria",
                value=data["categoria"], confidence=0.85
            ))

        # Proprietà
        for prop in data.get("proprietà", data.get("proprieta", [])):
            facts.append(ExtractedFact(
                subject=concept, relation="ha_propietà",
                value=prop, confidence=0.8
            ))

        # Esempi
        for ex in data.get("esempi", []):
            facts.append(ExtractedFact(
                subject=concept, relation="ha_esempio",
                value=ex, confidence=0.85
            ))

        # Relazioni
        for rel in data.get("relazioni", []):
            if isinstance(rel, list) and len(rel) == 3:
                facts.append(ExtractedFact(
                    subject=rel[0], relation=rel[1],
                    value=rel[2], confidence=0.7
                ))

        return facts

    def _parse_solve_response(self, raw: str) -> dict:
        """Parsa la risposta JSON del solver."""
        return self._parse_json_response(raw)

    def _parse_json_response(self, raw: str) -> dict:
        """Estrae JSON da una risposta dell'LLM (gestisce markdown wrapping)."""
        text = raw.strip()

        # Rimuovi code blocks markdown
        if text.startswith("```"):
            lines = text.split("\n")
            # Trova prima { e ultima }
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith("{"):
                    in_json = True
                if in_json:
                    json_lines.append(line)
                if in_json and line.strip().endswith("}"):
                    break
            text = "\n".join(json_lines)

        # Trova il JSON
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass

        return {}

    def _verify_fact(self, fact: ExtractedFact) -> float:
        """Verifica un fatto contro il knowledge graph esistente."""
        # Se il concetto esiste già e ha info contraddittorie
        existing = self.knowledge.get(fact.subject)
        if existing and fact.relation == "descrizione":
            if existing.description and existing.description != fact.value:
                # Contraddizione — bassa confidenza
                return 0.4

        # Verifica di coerenza base
        if not fact.value or len(fact.value) < 2:
            return 0.3

        return 0.8  # Default: accettato ma non verificato internamente

    def _generate_simple_explanation(self, steps: list[str], answer: Any) -> str:
        """Genera spiegazione senza LLM."""
        text = "🧠 Ragionamento:\n\n"
        for i, step in enumerate(steps, 1):
            text += f"{i}. {step}\n"
        text += f"\n✅ Risposta: {answer}"
        return text

    def get_history(self) -> list[dict]:
        """Restituisce lo storico delle chiamate LLM."""
        return self.history
