import re
import os
import html as html_lib
from .core.types import (
    Entity,
    ParsedQuery,
    DeductionResult,
    InductionResult,
    AnalogyResult,
    ReasoningStep,
    ReasoningResult,
    SourceMetadata,
)
from .nlp.parser import parse
from .reasoning.deductive import DeductiveReasoner
from .reasoning.inductive import InductiveReasoner
from .reasoning.analogical import AnalogicalReasoner
from .reasoning.rules import RuleEngine
from .reasoning.verifier import Verifier
from .reasoning.explainer import Explainer
from .data.graph import KnowledgeGraph
from .data.learner import Learner
from .tools.math import MathModule
from .tools.finance_data import FinancialDataTool
from .tools.data_analyzer import DataAnalysisTool
from .tools.memory_tool import MemoryTool
from .tools.browsing_tool import BrowsingTool
from .tools.web import WebTool
from .tools.datetime import DateTimeTool
from .agents.manager import AgentManager
from .llm.bridge import LLMBridge, LLMClient

try:
    from .question_based.question_reasoner import QuestionReasoner, ReasoningStatus

    QUESTION_BASED_AVAILABLE = True
except ImportError:
    QUESTION_BASED_AVAILABLE = False
    QuestionReasoner = None
    ReasoningStatus = None


class ReasoningEngine:
    """
    Il cervello principale. Coordina tutti i componenti e il team di agenti Multi-Agent.
    """

    WEB_FALLBACK_MIN_PERTINENCE = 0.30
    LLM_FALLBACK_MIN_CONFIDENCE = 0.50
    MAX_WEB_FALLBACKS = 2

    def __init__(
        self,
        llm_api_key: str = None,
        llm_model: str = "gpt-4o-mini",
        llm_provider: str = None,
    ):
        self.knowledge = KnowledgeGraph()
        self.knowledge.load()  # Carica conoscenze salvate
        self.rules = RuleEngine()
        self.learner = Learner(self.knowledge)
        self.verifier = Verifier(self.rules)
        self.explainer = Explainer()
        self.math = MathModule(self.knowledge, self.rules)
        self.finance_data = FinancialDataTool(self)
        self.data_analyzer = DataAnalysisTool(self)
        self.memory = MemoryTool(self)  # Long-term semantic memory
        self.browser = BrowsingTool(self)  # Deep web browsing
        self.web = WebTool()  # Web search fallback
        self.datetime = DateTimeTool()  # Date/ora locale
        self.agents = AgentManager(self)  # Multi-Agent Team
        self.deductive = DeductiveReasoner(self.knowledge, self.rules)
        self.inductive = InductiveReasoner(self.knowledge, self.rules)
        self.analogical = AnalogicalReasoner(self.knowledge)

        # LLM Bridge (auto-detect provider/model, supporto Groq/OpenAI)
        resolved_key = (
            llm_api_key or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        )
        resolved_provider = LLMClient.detect_provider(
            resolved_key, explicit_provider=llm_provider
        )
        resolved_model = llm_model
        if llm_model == "gpt-4o-mini" and resolved_provider == "groq":
            # Modello Groq veloce e stabile come default.
            resolved_model = "llama-3.1-8b-instant"

        llm_client = LLMClient(
            provider=resolved_provider,
            model=resolved_model,
            api_key=resolved_key,
        )
        self.llm = LLMBridge(llm_client, self.knowledge, self.verifier)

        # Question-Based Reasoner per query ambigue
        if QUESTION_BASED_AVAILABLE:
            self.question_reasoner = QuestionReasoner(
                domain="general",
                confidence_threshold=0.90,
                ambiguity_threshold=0.20,
            )
        else:
            self.question_reasoner = None

        # Contesto conversazione
        self.conversation_history = []

        # Auto-identità
        self.knowledge.add(
            "self_identity",
            description="Sono ReasoningEngine v2.0, un AI che ragiona come un umano. "
            "Combino NLP, ragionamento deduttivo/induttivo/analogico, "
            "matematica avanzata, ricerca web e esecuzione codice.",
            category="system",
            channel="system",
        )
        self._seed_baseline_knowledge()

    def _seed_baseline_knowledge(self):
        """Semi base per domande fattuali frequenti (deterministiche)."""
        seeds = {
            "Francia": "Parigi",
            "Italia": "Roma",
            "Germania": "Berlino",
            "Spagna": "Madrid",
            "Giappone": "Tokyo",
        }
        for country, capital in seeds.items():
            c = self.knowledge.add(
                country,
                description=f"{country} è uno Stato europeo.",
                category="geografia",
                channel="system",
            )
            c.add_relation("capitale", capital, channel="system")

    def learn(
        self,
        concept: str,
        examples: list[str],
        description: str = None,
        category: str = "general",
        channel: str = "user",
        trust_score: float = None,
    ):
        """Insegna un concetto all'engine specificando il canale."""
        c = self.learner.add_concept(
            concept, examples, description, category, channel, trust_score
        )
        self.knowledge.save()
        return f"Ho imparato: {concept} [Canale: {channel}]"

    def _state_path(self, name: str = "default", directory: str = None) -> str:
        """Costruisce il percorso del file di stato."""
        filename = name if str(name).endswith(".json") else f"{name}.json"
        if directory:
            return os.path.join(directory, filename)
        return os.path.join(os.path.dirname(__file__), "..", "data", filename)

    def save(self, name: str = "default", directory: str = None) -> str:
        """Salva la conoscenza su disco e ritorna il path usato."""
        if name == "default" and directory is None:
            self.knowledge.save()
            return os.path.join(
                os.path.dirname(__file__), "..", "data", "knowledge.json"
            )
        path = self._state_path(name, directory)
        self.knowledge.save(path)
        return path

    def load(self, name: str = "default", directory: str = None) -> bool:
        """Carica conoscenza da disco; ritorna True se il file esiste."""
        if name == "default" and directory is None:
            self.knowledge.load()
            return True
        path = self._state_path(name, directory)
        if not os.path.exists(path):
            return False
        self.knowledge.load(path)
        return True

    def learn_rule(
        self,
        name: str,
        func,
        description: str = "",
        inputs: list[str] = None,
        output_type: str = "any",
    ):
        """Insegna una regola all'engine."""
        self.rules.add_rule(name, func, description, inputs, output_type)
        return f"Regola aggiunta: {name}"

    def reason(
        self, question: str, use_llm: bool = False, channel: str = "user_interaction"
    ) -> ReasoningResult:
        """
        Ragiona su una domanda tramite collaborazione Multi-Agent.
        """
        # 1. NLP Parsing Iniziale (per intent e canali veloci)
        parsed_dict = self._parse_question(question)
        parsed = parsed_dict["_parsed"]
        route_mode = self._classify_route_mode(question, parsed)
        parsed_dict["route_mode"] = route_mode

        # 2. Fast-Path: Saluti brevi (evita risposte "sporche" dal KG)
        normalized = re.sub(r"[^\w\s]", "", question.lower()).strip()
        greeting_tokens = set(normalized.split())
        greeting_words = {
            "ciao",
            "salve",
            "hey",
            "hello",
            "hi",
            "buongiorno",
            "buonasera",
            "buonanotte",
            "come",
            "stai",
            "va",
        }
        # Saluti semplici o con "come stai"
        is_greeting = (
            normalized
            and len(greeting_tokens) <= 4
            and (
                greeting_tokens.issubset(greeting_words)
                or ("ciao" in greeting_tokens and len(greeting_tokens) <= 3)
            )
        )
        if is_greeting:
            return ReasoningResult(
                answer="Ciao! Ci sono, come stai?",
                confidence=1.0,
                reasoning_type="greeting",
                steps=[
                    ReasoningStep(
                        type="greeting",
                        description="Gestione diretta del saluto",
                        input=question,
                        output="saluto_riconosciuto",
                        channel="system",
                    )
                ],
                explanation="Risposta rapida di saluto.",
                verified=True,
            )

        # 2b. Fast-Path: Commenti casuali e frasi non-domanda
        casual_patterns = [
            r"^(io\s+)?(sto\s+)?bene$",
            r"^tutto\s+bene$",
            r"^sto\s+bene$",
            r"^grazie$",
            r"^perfetto$",
            r"^ok$",
            r"^va bene$",
            r"^mah$",
            r"^boh$",
            r"^si$",
            r"^no$",
            r"^figo$",
            r"^wow$",
            r"^cool$",
            r"^nice$",
            r"\bgrazie\b",
            r"\bperfetto\b",
            r"\bokk\b",
            r"che\s+(bel|forte|veloce|bell|interessant|figo|fortun|strano)",
            r"come\s+vuoi",
        ]
        for pattern in casual_patterns:
            if re.search(pattern, normalized):
                casual_responses = {
                    "che bel": "Grazie! Dimmi cosa vuoi sapere.",
                    "che veloce": "Grazie! Sono ottimizzato per rispondere velocemente.",
                    "che forte": "Grazie! Puoi chiedermi quello che vuoi.",
                    "io bene": "Ottimo, felice di sentirlo! Dimmi pure su cosa vuoi lavorare.",
                    "sto bene": "Ottimo, felice di sentirlo! Dimmi pure su cosa vuoi lavorare.",
                    "tutto bene": "Grande! Se vuoi possiamo continuare con i test o migliorare l'app.",
                    "bene": "Ottimo! Dimmi pure come vuoi procedere.",
                    "grazie": "Prego! Sono qui per aiutarti.",
                    "perfetto": "Perfetto! Cosa vuoi fare?",
                    "ok": "Ok! Dimmi pure.",
                    "va bene": "Va bene! Chiedimi quello che vuoi.",
                    "si": "Ottimo! Cosa vuoi sapere?",
                    "no": "Ok, come preferisci. Chiedimi pure.",
                    "figo": "Grazie! Vuoi provare qualcosa di specifico?",
                    "wow": "Grazie! Sono qui per aiutarti.",
                }
                for key, resp in casual_responses.items():
                    if key in normalized:
                        return ReasoningResult(
                            answer=resp,
                            confidence=1.0,
                            reasoning_type="casual",
                            steps=[
                                ReasoningStep(
                                    type="casual",
                                    description="Gestione frase casuale",
                                    input=question,
                                    output="risposta_casuale",
                                    channel="system",
                                )
                            ],
                            explanation="Risposta a commento casuale.",
                            verified=True,
                        )

        # 3. Fast-Path: Richiesta capacità/identità (generale, non frase-per-frase)
        if self._is_capability_question(question, normalized, parsed):
            identity = self.knowledge.get("self_identity")
            if identity:
                best = identity.get_best_info()
                return ReasoningResult(
                    answer=best["description"],
                    confidence=1.0,
                    reasoning_type="identity",
                    steps=[
                        ReasoningStep(
                            type="identity",
                            description="Risposta diretta su identità e capacità",
                            input=question,
                            output=best,
                            channel="system",
                        )
                    ],
                    explanation="Accesso diretto alle capacità di sistema.",
                    verified=True,
                )

        # 4. Fast-Path: Calcolo matematico diretto (prima del multi-agent)
        math_ops = {
            "addition",
            "subtraction",
            "multiplication",
            "division",
            "power",
            "sqrt",
            "percentage",
            "factorial",
            "area_circle",
            "perimeter_circle",
            "area_rectangle",
            "area_triangle",
            "pythagoras",
            "volume_cube",
            "volume_sphere",
            "equation",
        }
        if parsed.intent == "calculate" or parsed.operation in math_ops:
            math_res = self.math.solve(question)
            if math_res.get("answer") is not None:
                return ReasoningResult(
                    answer=math_res.get("answer"),
                    confidence=1.0,
                    reasoning_type="math",
                    steps=[
                        ReasoningStep(
                            type="math",
                            description="Risoluzione diretta tramite MathModule",
                            input=question,
                            output=math_res,
                            channel="math_module",
                        )
                    ],
                    explanation=math_res.get("explanation", ""),
                    verified=True,
                )

        # 4b. Fast-Path: data/ora (evita ricerca web per domande temporali semplici)
        if self._is_datetime_question(normalized):
            now_data = self.datetime.now()
            if re.search(
                r"\b(che\s+giorno|giorno\s+e|giorno\s+è|what\s+day)\b", normalized
            ):
                answer = f"Oggi è {now_data['day_it']}."
            elif re.search(
                r"\b(che\s+data|data\s+di\s+oggi|today'?s\s+date)\b", normalized
            ):
                answer = f"Oggi è {self.datetime.today()}."
            elif re.search(r"\b(che\s+ora|ora\s+attuale|what\s+time)\b", normalized):
                answer = f"Sono le {self.datetime.time()}."
            else:
                answer = f"Oggi è {self.datetime.today()}."
            return ReasoningResult(
                answer=answer,
                confidence=1.0,
                reasoning_type="datetime",
                steps=[
                    ReasoningStep(
                        type="datetime",
                        description="Risposta diretta tramite DateTimeTool",
                        input=question,
                        output=now_data,
                        channel="datetime_tool",
                    )
                ],
                explanation="Risposta temporale locale senza ricerca web.",
                verified=True,
            )

        # 4b. Fast-Path: lookup fattuale (es. capitali) dal Knowledge Graph
        if "capitale" in normalized:
            country_name = self._extract_country_name_for_capital(question)
            if country_name:
                concept = self.knowledge.get(country_name)
                if concept:
                    rels = getattr(concept, "relations", {}) or {}
                    for rel_name, targets in rels.items():
                        if "capitale" in rel_name.lower() and targets:
                            target = (
                                targets[0][0]
                                if isinstance(targets[0], tuple)
                                else targets[0]
                            )
                            return ReasoningResult(
                                answer=f"La capitale del {concept.name} è {target}.",
                                confidence=1.0,
                                reasoning_type="lookup",
                                steps=[
                                    ReasoningStep(
                                        type="lookup",
                                        description="Recupero diretto dal Knowledge Graph",
                                        input=question,
                                        output={
                                            "entity": concept.name,
                                            "relation": rel_name,
                                            "value": target,
                                        },
                                        channel="knowledge_graph",
                                    )
                                ],
                                explanation="Risposta fattuale recuperata dal grafo di conoscenza.",
                                verified=True,
                            )
            for ent in parsed.entities:
                concept = self.knowledge.get(ent.name)
                if not concept:
                    continue
                rels = getattr(concept, "relations", {}) or {}
                for rel_name, targets in rels.items():
                    if "capitale" in rel_name.lower() and targets:
                        target = (
                            targets[0][0]
                            if isinstance(targets[0], tuple)
                            else targets[0]
                        )
                        return ReasoningResult(
                            answer=f"La capitale della {concept.name} è {target}.",
                            confidence=1.0,
                            reasoning_type="lookup",
                            steps=[
                                ReasoningStep(
                                    type="lookup",
                                    description="Recupero diretto dal Knowledge Graph",
                                    input=question,
                                    output={
                                        "entity": concept.name,
                                        "relation": rel_name,
                                        "value": target,
                                    },
                                    channel="knowledge_graph",
                                )
                            ],
                            explanation="Risposta fattuale recuperata dal grafo di conoscenza.",
                            verified=True,
                        )

        # 5. Fast-Path: Identity Handling (Sistema 1)
        if parsed.intent == "identity":
            identity = self.knowledge.get("self_identity")
            if identity:
                best = identity.get_best_info()
                return ReasoningResult(
                    answer=best["description"],
                    confidence=1.0,
                    reasoning_type="identity",
                    steps=[
                        ReasoningStep(
                            type="identity",
                            description="Identificazione rapida",
                            output=best,
                            channel="system",
                        )
                    ],
                    explanation="Accesso diretto all'identità di sistema.",
                )

        # 6. Slow-Path: Multi-Agent Orchestration (Sistema 2)
        # Il manager coordina Researcher -> Analyst -> Critic
        agent_res = self.agents.orchestrate(question, parsed_dict)

        # 7. Verifica Finale Coerenza (rinforzata oltre il Critic)
        verified = agent_res.get("status") == "approved"
        agent_steps = agent_res.get("steps", [])

        # 8. Salva nel contesto conversazione
        self.conversation_history.append(
            {
                "question": question,
                "answer": str(agent_res["answer"])
                if agent_res.get("answer") is not None
                else None,
                "confidence": agent_res.get("confidence", 0),
                "channel": channel,
            }
        )

        # 9. Generazione Spiegazione Finale
        final_explanation = self.explainer.generate(
            [s.description for s in agent_steps], {"answer": agent_res["answer"]}
        )
        if agent_res.get("feedback"):
            final_explanation += f"\n[Critica AI: {agent_res['feedback']}]"

        # 10. Fallback to LLM if answer is missing OR too weak/generic
        answer_text = (
            str(agent_res.get("answer", "")).strip().lower()
            if agent_res.get("answer") is not None
            else ""
        )
        weak_patterns = [
            "non ho trovato informazioni dirette",
            "non ho abbastanza informazioni",
            "non posso rispondere",
            "non so",
        ]
        weak_answer = (
            agent_res.get("answer") is None
            or agent_res.get("confidence", 0.0) < 0.45
            or any(p in answer_text for p in weak_patterns)
        )

        # 10a. Web fallback rigoroso: solo per open_world con pertinenza minima
        pertinence = agent_res.get("pertinence_score", 0.0)
        grounding = agent_res.get("grounding_score", 0.0)
        can_fallback_web = (
            weak_answer
            and route_mode == "open_world"
            and pertinence < self.WEB_FALLBACK_MIN_PERTINENCE
        )

        if can_fallback_web:
            web_res = self.web.search_and_summarize(question)
            summary = self._clean_web_summary(str(web_res.get("summary", "") or ""))
            if (
                web_res.get("success")
                and summary
                and summary != "Nessun risultato trovato."
            ):
                web_confidence = min(0.72, max(grounding + 0.3, 0.5))
                return ReasoningResult(
                    answer=summary,
                    confidence=web_confidence,
                    reasoning_type="web",
                    steps=agent_steps
                    + [
                        ReasoningStep(
                            type="web",
                            description=f"Risposta via ricerca web (fallback: pertinenza={pertinence:.2f}<{self.WEB_FALLBACK_MIN_PERTINENCE})",
                            channel="web_search",
                            output={
                                "sources": web_res.get("sources", []),
                                "query": question,
                                "fallback_reason": f"low_pertinence_{pertinence:.2f}",
                            },
                        )
                    ],
                    explanation=f"Fallback web perché pertinenza insufficiente ({pertinence:.2f} < {self.WEB_FALLBACK_MIN_PERTINENCE}).",
                    verified=False,
                    sources=[SourceMetadata(channel="web", trust_score=0.5)],
                )

        # 10b. LLM fallback rigoroso: solo con confidenza agente bassa e dopo web fallito
        agent_conf = agent_res.get("confidence", 0.0)
        can_fallback_llm = (
            weak_answer
            and use_llm
            and self.llm.is_available()
            and agent_conf < self.LLM_FALLBACK_MIN_CONFIDENCE
        )

        if can_fallback_llm:
            llm_res = self.llm.fallback_solve(question)
            if llm_res.facts:
                best = max(llm_res.facts, key=lambda f: f.confidence)
                llm_answer = str(getattr(best, "value", "") or "").strip()

                if not llm_answer:
                    raw = str(getattr(llm_res, "raw", "") or "").strip()
                    if raw and not raw.lower().startswith("errore llm"):
                        llm_answer = raw

                if not llm_answer:
                    llm_answer = (
                        "Capito. Dimmi pure cosa vuoi fare e ti aiuto passo passo."
                    )

                llm_confidence = min(best.confidence, 0.65)
                return ReasoningResult(
                    answer=llm_answer,
                    confidence=llm_confidence,
                    reasoning_type="llm",
                    steps=agent_steps
                    + [
                        ReasoningStep(
                            type="llm",
                            description=f"Fallback LLM (confidenza agente: {agent_conf:.2f} < {self.LLM_FALLBACK_MIN_CONFIDENCE})",
                            channel=self.llm.llm.provider,
                            output={
                                "fallback_reason": f"low_confidence_{agent_conf:.2f}"
                            },
                        )
                    ],
                    explanation=f"Fallback LLM perché confidenza insufficiente ({agent_conf:.2f} < {self.LLM_FALLBACK_MIN_CONFIDENCE}).",
                    llm_used=True,
                    sources=[
                        SourceMetadata(channel=self.llm.llm.provider, trust_score=0.4)
                    ],
                )

        # 10c. Question-Based Reasoner per query ambigue/diagnostiche
        if (
            weak_answer
            and self.question_reasoner is not None
            and route_mode in ("reasoning_required", "deterministic_fact")
        ):
            qb_result = self._question_based_reason(question)
            if qb_result:
                return qb_result

        if agent_res.get("answer") is None:
            return ReasoningResult(
                answer=None,
                confidence=0.0,
                steps=agent_steps,
                explanation="Non ho abbastanza informazioni nei canali attuali per rispondere.",
            )

        return ReasoningResult(
            answer=agent_res["answer"],
            confidence=agent_res.get("confidence", 0.0),
            reasoning_type="multi_agent_collaboration",
            steps=agent_steps,
            explanation=final_explanation,
            verified=verified,
            sources=[],
        )

    def _parse_question(self, question: str) -> dict:
        """Analisi NLP con mappatura delle entità."""
        parsed = parse(question)
        return {
            "intent": parsed.intent,
            "operation": parsed.operation,
            "entities": [e.name for e in parsed.entities],
            "numbers": parsed.numbers,
            "operators": parsed.operators,
            "relations": parsed.relations,
            "confidence": parsed.confidence,
            "_parsed": parsed,
        }

    def _is_capability_question(self, raw: str, normalized: str, parsed) -> bool:
        """Riconosce domande su identità/capacità con euristiche robuste."""
        if parsed.intent == "identity":
            return True

        text = normalized
        if not text:
            return False

        # Pattern IT/EN più ampi (evita dipendenza da stringhe esatte).
        patterns = [
            r"\bchi\s+sei\b",
            r"\bdimmi\s+di\s+te\b",
            r"\b(cosa|che)\b.*\b(sai|puoi)\b.*\b(fare|aiutare)\b",
            r"\b(in\s+cosa|come)\b.*\bpuoi\b.*\b(aiutare)\b",
            r"\b(quali|che)\b.*\b(tue|tuoi)\b.*\b(capacità|capacita|funzioni|abilità|abilita)\b",
            r"\bwhat\s+can\s+you\s+do\b",
            r"\bhow\s+can\s+you\s+help\b",
            r"\btell\s+me\s+about\s+yourself\b",
        ]
        for pat in patterns:
            if re.search(pat, text):
                return True

        # Fallback euristico per domande brevi su "tu + poter/sapere + azione".
        tokens = text.split()
        if len(tokens) <= 12 and any(t in tokens for t in ["tu", "you"]):
            has_modal = any(t in tokens for t in ["puoi", "sai", "can"])
            has_action = any(
                t in tokens
                for t in [
                    "fare",
                    "aiutare",
                    "help",
                    "do",
                ]
            )
            if has_modal and has_action:
                return True

        return False

    def _classify_route_mode(self, raw: str, parsed) -> str:
        """
        Classifica la query per policy di routing.
        - deterministic_fact: dovrebbe rispondere da KG/tool locale, no web by default
        - date_time: data/ora locali
        - open_world: richiede ricerca esterna
        - reasoning_required: inferenza/logica da conoscenza interna
        """
        text = (raw or "").lower().strip()
        if not text:
            return "reasoning_required"

        if self._is_datetime_question(text):
            return "date_time"

        if "capitale" in text:
            return "deterministic_fact"

        intent = getattr(parsed, "intent", "general")
        if intent in {"search"}:
            return "open_world"

        if any(
            k in text
            for k in ["news", "ultime notizie", "quotazione", "meteo", "oggi in"]
        ):
            return "open_world"

        if intent in {
            "calculate",
            "verify",
            "compare",
            "explain",
            "define",
            "identity",
        }:
            return "reasoning_required"

        return "reasoning_required"

    def what_do_you_know(self) -> dict:
        """Mostra tutto ciò che l'engine ha imparato."""
        return {
            "concepts": self.knowledge.list_all(),
            "rules": self.rules.list_all(),
            "conversation_turns": len(self.conversation_history),
        }

    def _is_datetime_question(self, normalized: str) -> bool:
        """Riconosce domande semplici su data/giorno/ora."""
        if not normalized:
            return False
        patterns = [
            r"\bche\s+giorno\b",
            r"\bgiorno\s+e\b",
            r"\bgiorno\s+è\b",
            r"\bche\s+data\b",
            r"\bdata\s+di\s+oggi\b",
            r"\boggi\b",
            r"\bche\s+ora\b",
            r"\bora\s+attuale\b",
            r"\btoday\b",
            r"\bwhat\s+day\b",
            r"\bwhat\s+time\b",
            r"\btoday'?s\s+date\b",
        ]
        return any(re.search(p, normalized) for p in patterns)

    def _extract_country_name_for_capital(self, raw: str) -> str | None:
        """Estrae il paese da pattern comuni: 'capitale del/della X'."""
        if not raw:
            return None
        text = raw.strip()
        m = re.search(
            r"\bcapitale\s+d(?:el|ella|ei|egli|elle)\s+([A-Za-zÀ-ÖØ-öø-ÿ' ]+)",
            text,
            re.IGNORECASE,
        )
        if not m:
            return None
        country = m.group(1).strip(" ?!.;,:'\"")
        if not country:
            return None
        return country[:1].upper() + country[1:].lower()

    def _clean_web_summary(self, text: str) -> str:
        """Pulisce snippet web (entity HTML, tag residui, spazi)."""
        if not text:
            return ""
        cleaned = html_lib.unescape(text)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned[:600]

    def _question_based_reason(self, question: str) -> ReasoningResult | None:
        """Usa QuestionReasoner per query ambigue/diagnostiche."""
        if not self.question_reasoner:
            return None

        if self.question_reasoner.space.active:
            top = self.question_reasoner.space.get_top_hypothesis()
            if top:
                answer = (
                    f"Basandomi sul ragionamento probabilistico: {top.name} "
                    f"(confidenza: {top.probability:.0%})"
                )
                return ReasoningResult(
                    answer=answer,
                    confidence=top.probability,
                    reasoning_type="question_based",
                    steps=[],
                    explanation="Risposta da Question-Based Reasoner.",
                    verified=False,
                )

        return None
