"""
NLP Parser — Trasforma testo grezzo in struttura comprensibile.

Componenti:
1. Tokenizer — splitta e normalizza il testo
2. Intent Classifier — capisce cosa vuole l'utente
3. Entity Extractor — estrae numeri, concetti, operatori
"""

import re
from dataclasses import dataclass, field


@dataclass
class Entity:
    """Un'entità estratta dal testo."""
    name: str                          # Nome dell'entità
    entity_type: str                   # number, concept, operator
    value: any = None                  # Valore (es. 6 per "sei")
    position: tuple = (0, 0)           # Posizione nel testo originale


@dataclass
class ParsedQuery:
    """Output del parser — quello che l'engine capisce."""
    raw: str                           # Input originale
    intent: str = "general"            # Intent classificato
    entities: list = field(default_factory=list)
    relations: list = field(default_factory=list)
    numbers: list = field(default_factory=list)
    operators: list = field(default_factory=list)
    confidence: float = 0.5
    language: str = "it"
    operation: str = "unknown"         # Per compatibilità con engine esistente


# ============================================================
# TOKENIZER
# ============================================================

# Parole italiane da ignorare
STOP_WORDS_IT = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "del", "dello", "della", "dei", "degli", "delle",
    "a", "al", "allo", "alla", "ai", "agli", "alle",
    "da", "dal", "dallo", "dalla", "dai", "dagli", "dalle",
    "in", "nel", "nello", "nella", "nei", "negli", "nelle",
    "con", "col", "su", "sul", "sullo", "sulla", "sui", "sugli", "sulle",
    "per", "tra", "fra",
    "e", "ed", "o", "ma", "che", "chi", "cui",
    "è", "sono", "siamo", "siete", "era", "erano",
    "ho", "hai", "ha", "abbiamo", "avete", "hanno",
    "mi", "ti", "ci", "vi", "ne",
    "questo", "questa", "questi", "queste",
    "quello", "quella", "quelli", "quelle",
    "come", "quando", "dove", "perché", "quanto", "quanti", "quante",
    "se", "anche", "ancora", "già", "poi", "così",
}

# Numeri italiani scritti in parole → valore
WORD_NUMBERS = {
    "zero": 0, "uno": 1, "una": 1, "due": 2, "tre": 3, "quattro": 4,
    "cinque": 5, "sei": 6, "sette": 7, "otto": 8, "nove": 9,
    "dieci": 10, "undici": 11, "dodici": 12, "tredici": 13,
    "quattordici": 14, "quindici": 15, "sedici": 16,
    "diciassette": 17, "diciotto": 18, "diciannove": 19,
    "venti": 20, "trenta": 30, "quaranta": 40, "cinquanta": 50,
    "sessanta": 60, "settanta": 70, "ottanta": 80, "novanta": 90,
    "cento": 100, "mille": 1000,
}


def tokenize(text: str) -> list[str]:
    """Splitta il testo in token significativi."""
    text = text.strip().lower()
    # Rimuovi punteggiatura eccetto operatori matematici
    text = re.sub(r'[.,;:!?"\'()]', ' ', text)
    tokens = text.split()
    return tokens


def remove_stop_words(tokens: list[str]) -> list[str]:
    """Rimuove parole vuote mantenendo quelle significative."""
    return [t for t in tokens if t not in STOP_WORDS_IT]


# ============================================================
# INTENT CLASSIFIER
# ============================================================

INTENT_PATTERNS = {
    "calculate": [
        r"quanto fa",
        r"calcola",
        r"quanto viene",
        r"fa il conto",
        r"risolvi",
        r"\d+\s*[\+\-\*\/\×\÷]\s*\d+",
        r"fattoriale",
        r"radice",
        r"potenza",
        r"area\s+(cerchio|rettangolo|triangolo|quadrato)",
        r"circonferenza",
        r"volume\s+(cubo|sfera)",
        r"pitagora",
        r"ipotenusa",
        r"\d+\s*%",
        r"percentuale",
        r"il\s+\d+%\s+di",
    ],
    "define": [
        r"cosa [èe]",
        r"cos['']è",
        r"definisci",
        r"che cos['']è",
        r"che cosa [èe]",
        r"spiegami",
        r"dimmi cos['']è",
        r"significato di",
    ],
    "compare": [
        r"qual[e]? [èe] (più|il più)",
        r"differenza tra",
        r"confronta",
        r"(meglio|peggio|maggiore|minore)",
        r"è (maggiore|minore|uguale)",
    ],
    "explain": [
        r"perch[eé]",
        r"come (funziona|mai|è possibile)",
        r"come fa",
        r"spiegami come",
        r"in che modo",
    ],
    "verify": [
        r"[èe] vero che",
        r"[èe] corretto",
        r"conferma",
        r"verifica",
        r"[èe] giusto",
        r"è (vero|falso)",
        r"(il|la|i|le)\s+\w+\s+[èe]\s+(?:un[ao]?\s+)\w+\?",  # il gatto è un animale?
        r"(il|la)\s+\w+\s+ha\s+\w+\?",                        # il cane ha pelo?
        r"(il|la)\s+\w+\s+fa\s+",                               # il gatto fa le fusa?
        r"(il|la)\s+\w+\s+(allatta|vola|nuota|corre|abbaia|miagola|canta)\??",  # il cane allatta?
        r"(il|la)\s+\w+\s+si\s+(muove|trova|comporta)\??",     # il cane si muove?
    ],
    "learn": [
        r"^il \w+ [èe]",
        r"^la \w+ [èe]",
        r"^i \w+ sono",
        r"^le \w+ sono",
        r"^(\w+) = (\w+)",
        r"ricordati",
        r"impara",
        r"sappi che",
        r"memorizza",
    ],
}


def classify_intent(text: str) -> tuple[str, float]:
    """Classifica l'intento del testo. Ritorna (intent, confidence)."""
    text_lower = text.strip().lower()

    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                scores[intent] = scores.get(intent, 0) + 1

    if not scores:
        return "general", 0.3

    # Prendi l'intento con più match
    best = max(scores, key=scores.get)
    confidence = min(0.95, 0.6 + scores[best] * 0.15)
    return best, confidence


# ============================================================
# ENTITY EXTRACTOR
# ============================================================

# Mesi, giorni, unità comuni per evitare false entità
NOISE_WORDS = {
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
    "lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica",
    "metro", "metri", "chilogrammo", "chilogrammi", "kg", "grammi",
    "litri", "litro", "euro", "dollari",
}


def extract_numbers(text: str) -> list[tuple[float, str]]:
    """Estrae numeri dal testo (cimali e parole)."""
    results = []

    # Numeri scritti con cifre (inclusi decimali e negativi)
    for match in re.finditer(r'-?\d+\.?\d*', text):
        val = float(match.group())
        results.append((val, match.group()))

    # Numeri scritti in parole
    words = text.lower().split()
    for word in words:
        if word in WORD_NUMBERS:
            results.append((WORD_NUMBERS[word], word))

    return results


def extract_concepts(text: str) -> list[str]:
    """Estrae concetti/entità dal testo."""
    tokens = tokenize(text)
    concepts = []

    # Parole spurie da rimuovere (artefatti di parsing)
    spurious = {"cos", "che", "cosa", "qual", "quale", "significato", "definisci", "spiegami", "dimmi"}
    
    for token in tokens:
        # Salta numeri, stop words, noise, parole spurie
        if token in STOP_WORDS_IT or token in spurious:
            continue
        if token in NOISE_WORDS:
            continue
        if re.match(r'^-?\d+\.?\d*$', token):
            continue
        if len(token) < 2:
            continue
        concepts.append(token)

    return concepts


def extract_operators(text: str) -> list[str]:
    """Estrae operatori matematici e logici dal testo."""
    operators = []

    # Operatori matematici simbolici
    op_map = {
        '+': 'addition', '-': 'subtraction',
        '*': 'multiplication', '×': 'multiplication',
        '/': 'division', '÷': 'division',
        '^': 'power', '**': 'power',
        '=': 'equals',
    }
    for symbol, name in op_map.items():
        if symbol in text:
            operators.append(name)

    # Operatori matematici in italiano
    word_ops = {
        'più': 'addition', 'somma': 'addition', 'piu': 'addition',
        'meno': 'subtraction', 'sottrai': 'subtraction',
        'per': 'multiplication', 'volte': 'multiplication',
        'diviso': 'division', 'dividendo': 'division',
        'elevato': 'power',
        'uguale': 'equals',
    }
    text_lower = text.lower()
    for word, name in word_ops.items():
        if word in text_lower:
            if name not in operators:
                operators.append(name)

    # Operatori logici
    logic_ops = {
        'e': 'and', 'o': 'or', 'non': 'not',
        'se': 'if', 'allora': 'then',
        'oppure': 'or', 'inoltre': 'and',
    }
    tokens = text_lower.split()
    for token in tokens:
        if token in logic_ops:
            op_name = logic_ops[token]
            if op_name not in operators:
                operators.append(op_name)

    return operators


def extract_relations(text: str) -> list[tuple[str, str, str]]:
    """Estrae relazioni dal testo. Ritorna [(soggetto, relazione, oggetto)]."""
    import re
    relations = []
    text_lower = text.lower().strip()
    text_lower = re.sub(r'\?$', '', text_lower)  # rimuovi ? finale

    # Articoli da rimuovere dai match
    articles = r'(?:il |la |i |le |lo |un |una )?'

    # Pattern di relazione
    relation_patterns = [
        (r'(\w+)\s+[èe]\s+' + articles + r'(\w+)', 'è_un'),
        (r'(\w+)\s+ha\s+' + articles + r'(\w+)', 'ha_caratteristica'),
        (r'(\w+)\s+[èe]\s+(\w+)\s+di\s+(\w+)', 'è_di'),
        (r'(\w+)\s+(?:sta|si trova)\s+(?:in|a|dentro|sopra|sotto)\s+(\w+)', 'si_trova'),
        (r'(\w+)\s+(?:causa|provoca|genera)\s+(\w+)', 'causa'),
        (r'(\w+)\s+(?:[èe] simile a|assomiglia a)\s+(\w+)', 'simile_a'),
        (r'(\w+)\s+fa\s+(?:il\s+|la\s+|i\s+|le\s+)?(.+)', 'fa'),
        (r'(\w+)\s+(allatta|vola|nuota|corre|abbaia|miagola|canta)', 'ha_caratteristica'),
        (r'(\w+)\s+si\s+(muove|trova|comporta)', 'ha_caratteristica_si'),
    ]

    for pattern, rel_type in relation_patterns:
        for match in re.finditer(pattern, text_lower):
            groups = match.groups()
            if len(groups) >= 2:
                subj = groups[0]
                obj = groups[1].strip().rstrip('?')
                # Salta se soggetto o oggetto sono articoli/stop words
                if subj not in STOP_WORDS_IT and len(subj) > 1:
                    relations.append((subj, rel_type, obj))

    return relations


# ============================================================
# PARSER PRINCIPALE
# ============================================================

def parse(text: str) -> ParsedQuery:
    """
    Funzione principale. Prende testo grezzo e ritorna ParsedQuery.

    Esempi:
        parse("quanto fa 15 + 27?")
        → ParsedQuery(intent="calculate", numbers=[15,27], operation="addition")

        parse("cos'è un atomo?")
        → ParsedQuery(intent="define", entities=["atomo"])

        parse("il gatto è un mammifero")
        → ParsedQuery(intent="learn", relations=[("gatto","è_un","mammifero")])
    """
    # 1. Tokenizza
    tokens = tokenize(text)

    # 2. Classifica intent
    intent, confidence = classify_intent(text)

    # 3. Estrai numeri
    raw_numbers = extract_numbers(text)
    numbers = [n[0] for n in raw_numbers]

    # 4. Estrai operatori
    operators = extract_operators(text)

    # 5. Estrai concetti
    concept_tokens = extract_concepts(text)

    # 6. Estrai relazioni
    relations = extract_relations(text)

    # 7. Determina operation per compatibilità con engine esistente
    operation = _infer_operation(text, intent, operators, numbers)

    # 8. Costruisci entità
    entities = []
    for name in concept_tokens:
        entities.append(Entity(name=name, entity_type="concept"))
    for val, raw in raw_numbers:
        entities.append(Entity(name=raw, entity_type="number", value=val))

    return ParsedQuery(
        raw=text,
        intent=intent,
        entities=entities,
        relations=relations,
        numbers=numbers,
        operators=operators,
        confidence=confidence,
        language="it",
        operation=operation,
    )


def _infer_operation(text: str, intent: str, operators: list, numbers: list) -> str:
    """Inferisce il tipo di operazione per compatibilità con RuleEngine."""
    text_lower = text.lower()

    # Cerca operazioni specifiche PRIMA di quelle generiche
    if any(w in text_lower for w in ["cerchio", "circonferenza"]):
        if "area" in text_lower or "superficie" in text_lower:
            return "area_circle"
        if "circonferenza" in text_lower or "perimetro" in text_lower:
            return "perimeter_circle"

    if "rettangolo" in text_lower and "area" in text_lower:
        return "area_rectangle"

    if "triangolo" in text_lower and "area" in text_lower:
        return "area_triangle"

    if "pitagora" in text_lower or "ipotenusa" in text_lower:
        return "pythagoras"

    if "cubo" in text_lower and "volume" in text_lower:
        return "volume_cube"

    if "sfera" in text_lower and "volume" in text_lower:
        return "volume_sphere"

    if "fattoriale" in text_lower:
        return "factorial"

    if "radice" in text_lower or "√" in text:
        return "sqrt"

    if "%" in text_lower or "percentuale" in text_lower or "percento" in text_lower:
        return "percentage"

    if "elevato" in text_lower or "alla" in text_lower and ("seconda" in text_lower or "terza" in text_lower):
        return "power"

    # Equazioni
    if "=" in text and re.search(r'[a-z]', text_lower):
        return "equation"

    # Operazioni base
    if intent == "calculate":
        if "addition" in operators or "più" in text_lower or "somma" in text_lower:
            return "addition"
        if "subtraction" in operators or "meno" in text_lower:
            return "subtraction"
        if "multiplication" in operators or "per" in text_lower and "volte" in text_lower:
            return "multiplication"
        if "division" in operators or "diviso" in text_lower:
            return "division"

        # Se ha numeri e un operatore simbolico
        if len(numbers) >= 2:
            if "+" in text:
                return "addition"
            if "-" in text and not text.strip().startswith("-"):
                return "subtraction"
            if "×" in text or "*" in text:
                return "multiplication"
            if "÷" in text or "/" in text:
                return "division"

    if intent == "define":
        return "lookup"

    return "unknown"
