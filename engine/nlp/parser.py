"""
NLP Parser — Trasforma testo grezzo in struttura comprensibile.

Componenti:
1. Tokenizer — splitta e normalizza il testo
2. Intent Classifier — capisce cosa vuole l'utente
3. Entity Extractor — estrae numeri, concetti, operatori
"""

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Entity:
    """Un'entità estratta dal testo."""

    name: str  # Nome dell'entità
    entity_type: str  # number, concept, operator
    value: Any = None  # Valore (es. 6 per "sei")
    position: tuple = (0, 0)  # Posizione nel testo originale


@dataclass
class ParsedQuery:
    """Output del parser — quello che l'engine capisce."""

    raw: str  # Input originale
    intent: str = "general"  # Intent classificato
    entities: list = field(default_factory=list)
    relations: list = field(default_factory=list)
    numbers: list = field(default_factory=list)
    operators: list = field(default_factory=list)
    confidence: float = 0.5
    language: str = "it"
    operation: str = "unknown"
    channel: str = "user_interaction"


# ============================================================
# TOKENIZER
# ============================================================

# Parole italiane da ignorare
STOP_WORDS_IT = {
    "il",
    "lo",
    "la",
    "i",
    "gli",
    "le",
    "un",
    "uno",
    "una",
    "di",
    "del",
    "dello",
    "della",
    "dei",
    "degli",
    "delle",
    "a",
    "al",
    "allo",
    "alla",
    "ai",
    "agli",
    "alle",
    "da",
    "dal",
    "dallo",
    "dalla",
    "dai",
    "dagli",
    "dalle",
    "in",
    "nel",
    "nello",
    "nella",
    "nei",
    "negli",
    "nelle",
    "con",
    "col",
    "su",
    "sul",
    "sullo",
    "sulla",
    "sui",
    "sugli",
    "sulle",
    "per",
    "tra",
    "fra",
    "e",
    "ed",
    "o",
    "ma",
    "che",
    "chi",
    "cui",
    "è",
    "sono",
    "siamo",
    "siete",
    "era",
    "erano",
    "ho",
    "hai",
    "ha",
    "abbiamo",
    "avete",
    "hanno",
    "mi",
    "ti",
    "ci",
    "vi",
    "ne",
    "questo",
    "questa",
    "questi",
    "queste",
    "quello",
    "quella",
    "quelli",
    "quelle",
    "come",
    "quando",
    "dove",
    "perché",
    "quanto",
    "quanti",
    "quante",
    "se",
    "anche",
    "ancora",
    "già",
    "poi",
    "così",
}

# Parole inglesi da ignorare
STOP_WORDS_EN = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "shall",
    "should",
    "may",
    "might",
    "must",
    "can",
    "could",
    "i",
    "you",
    "he",
    "she",
    "it",
    "we",
    "they",
    "me",
    "him",
    "her",
    "us",
    "them",
    "my",
    "your",
    "his",
    "her",
    "its",
    "our",
    "their",
    "this",
    "that",
    "these",
    "those",
    "what",
    "which",
    "who",
    "whom",
    "where",
    "when",
    "why",
    "how",
    "and",
    "but",
    "or",
    "nor",
    "not",
    "so",
    "yet",
    "both",
    "either",
    "neither",
    "each",
    "every",
    "all",
    "any",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "only",
    "own",
    "same",
    "than",
    "too",
    "very",
    "to",
    "of",
    "in",
    "for",
    "on",
    "with",
    "at",
    "by",
    "from",
    "up",
    "about",
    "into",
    "over",
    "after",
    "under",
    "again",
    "then",
    "once",
}

STOP_WORDS = STOP_WORDS_IT | STOP_WORDS_EN

# Numeri italiani scritti in parole → valore
WORD_NUMBERS = {
    "zero": 0,
    "uno": 1,
    "una": 1,
    "due": 2,
    "tre": 3,
    "quattro": 4,
    "cinque": 5,
    "sei": 6,
    "sette": 7,
    "otto": 8,
    "nove": 9,
    "dieci": 10,
    "undici": 11,
    "dodici": 12,
    "tredici": 13,
    "quattordici": 14,
    "quindici": 15,
    "sedici": 16,
    "diciassette": 17,
    "diciotto": 18,
    "diciannove": 19,
    "venti": 20,
    "trenta": 30,
    "quaranta": 40,
    "cinquanta": 50,
    "sessanta": 60,
    "settanta": 70,
    "ottanta": 80,
    "novanta": 90,
    "cento": 100,
    "mille": 1000,
    # English
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
    "thousand": 1000,
}


def tokenize(text: str) -> list[str]:
    """Splitta il testo in token significativi, preservando il case."""
    text = text.strip()
    # Rimuovi punteggiatura eccetto operatori matematici
    text = re.sub(r'[.,;:!?"\'()]', " ", text)
    tokens = text.split()
    return tokens


def remove_stop_words(tokens: list[str]) -> list[str]:
    """Rimuove parole vuote mantenendo quelle significative (IT + EN)."""
    return [t for t in tokens if t not in STOP_WORDS]


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
        # English
        r"how much",
        r"what is \d",
        r"calculate",
        r"solve",
        r"compute",
        r"factorial",
        r"square root",
        r"power",
        r"area of",
        r"volume of",
        r"pythag",
        r"hypotenuse",
        r"percent",
    ],
    "define": [
        r"cosa [èe]",
        r"cos['’]?[eè]",
        r"cos\s+[eè]",
        r"definisci",
        r"che cos['’]?[eè]",
        r"che cos\s+[eè]",
        r"che cosa [èe]",
        r"spiegami",
        r"dimmi cos['’]?[eè]",
        r"dimmi cos\s+[eè]",
        r"significato di",
        # English
        r"what is",
        r"what are",
        r"define",
        r"explain",
        r"meaning of",
        r"tell me about",
    ],
    "compare": [
        r"qual[e]? [èe] (più|il più)",
        r"differenza tra",
        r"confronta",
        r"(meglio|peggio|maggiore|minore)",
        r"è (maggiore|minore|uguale)",
        # English
        r"compare",
        r"difference between",
        r"which is (bigger|smaller|greater|less|better|worse)",
        r"is.*greater than",
        r"is.*less than",
    ],
    "explain": [
        r"perch[eé]",
        r"come (funziona|mai|è possibile)",
        r"come fa",
        r"spiegami come",
        r"in che modo",
        # English
        r"why",
        r"how (does|do|can|could|would|should)",
        r"explain how",
        r"what makes",
    ],
    "verify": [
        r"[èe] vero che",
        r"[èe] corretto",
        r"conferma",
        r"verifica",
        r"[èe] giusto",
        r"è (vero|falso)",
        r"(il|la|i|le)\s+\w+\s+[èe]\s+(?:un[ao]?\s+)\w+\?",
        r"(il|la)\s+\w+\s+ha\s+\w+\?",
        r"(il|la)\s+\w+\s+fa\s+",
        r"(il|la)\s+\w+\s+(allatta|vola|nuota|corre|abbaia|miagola|canta)\??",
        r"(il|la)\s+\w+\s+si\s+(muove|trova|comporta)\??",
        # English
        r"is it true",
        r"is.*correct",
        r"confirm",
        r"verify",
        r"is.*right",
        r"is.*true",
        r"is.*false",
        r"does.*(have|can|is|are)",
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
        # English
        r"^the \w+ is",
        r"^a \w+ is",
        r"^an \w+ is",
        r"^(\w+) is a",
        r"^remember",
        r"^learn",
        r"^know that",
        r"^memorize",
    ],
    "identity": [
        r"chi [èe]i",
        r"come ti chiami",
        r"cosa (sei|fai|puoi fare|puoi dirmi di te)",
        r"(cosa|che)\s+(sai|puoi)\s+fare",
        r"(in cosa|come)\s+(mi\s+)?puoi\s+aiutare",
        r"(quali|che)\s+sono\s+(le\s+)?(tue|i tuoi)\s+(capacità|capacita|funzioni|abilità|abilita)",
        r"(cosa|che)\s+puoi\s+fare\s+per\s+me",
        r"qual[ei] (sono|è) (le tue|il tuo|la tua) (funzioni|obiettivi|caratteristiche)",
        r"dimmi di te",
        r"chi sei",
        r"cosa puoi fare",
        # English
        r"who are you",
        r"what are you",
        r"what can you do",
        r"how can you help",
        r"what can you help me with",
        r"what do you know how to do",
        r"tell me about yourself",
        r"your name",
    ],
    "search": [
        r"cerca",
        r"trova",
        r"cercami",
        r"trovami",
        r"informazioni su",
        # English
        r"search",
        r"find",
        r"look up",
        r"google",
        r"information about",
    ],
    "code": [
        r"esegui (il )?codice",
        r"run (this )?code",
        r"esegui python",
        r"run python",
        r"scrivi (un )?codice",
        r"write (a )?code",
        r"genera (un )?codice",
        r"generate (a )?code",
        r"debug",
    ],
    "statistics": [
        r"media",
        r"mediana",
        r"moda",
        r"deviazione standard",
        r"varianza",
        r"regressione",
        # English
        r"mean",
        r"median",
        r"mode",
        r"standard deviation",
        r"variance",
        r"regression",
        r"average",
    ],
    "calculus": [
        r"derivat[ae]",
        r"integr[ae]",
        r"limit[ei]",
        r"calcolo",
        # English
        r"derivativ[ei]",
        r"integr[ae]l",
        r"limit",
        r"calculus",
        r"differentiate",
    ],
    "matrix": [
        r"matric[ei]",
        r"determinante",
        r"inversa",
        r"trasposta",
        # English
        r"matrix",
        r"matrices",
        r"determinant",
        r"inverse",
        r"transpose",
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
    # Italian
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
    "lunedì",
    "martedì",
    "mercoledì",
    "giovedì",
    "venerdì",
    "sabato",
    "domenica",
    "metro",
    "metri",
    "chilogrammo",
    "chilogrammi",
    "kg",
    "grammi",
    "litri",
    "litro",
    "euro",
    "dollari",
    # English
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "meter",
    "meters",
    "kilogram",
    "kilograms",
    "pound",
    "pounds",
    "liter",
    "liters",
    "dollar",
    "dollars",
}


def extract_numbers(text: str) -> list[tuple[float, str]]:
    """Estrae numeri dal testo (cimali e parole)."""
    results = []

    # Numeri scritti con cifre (inclusi decimali e negativi)
    for match in re.finditer(r"-?\d+\.?\d*", text):
        val = float(match.group())
        results.append((val, match.group()))

    # Numeri scritti in parole
    words = text.lower().split()
    for word in words:
        if word in WORD_NUMBERS:
            results.append((WORD_NUMBERS[word], word))

    return results


def extract_concepts(text: str) -> list[str]:
    """Estrae concetti/entità dal testo (IT + EN)."""
    tokens = tokenize(text)
    concepts = []

    # Parole spurie da rimuovere (artefatti di parsing)
    spurious = {
        "cos",
        "che",
        "cosa",
        "qual",
        "quale",
        "significato",
        "definisci",
        "spiegami",
        "dimmi",
        "what",
        "which",
        "tell",
        "give",
        "find",
        "search",
        "look",
    }

    for token in tokens:
        # Verifica in minuscolo per stop words e spurious
        token_lower = token.lower()
        if token_lower in STOP_WORDS or token_lower in spurious:
            continue
        if token_lower in NOISE_WORDS:
            continue
        if re.match(r"^-?\d+\.?\d*$", token):
            continue
        if len(token) < 2:
            continue
        # Aggiunge il token originale (preservando il case)
        concepts.append(token)

    return concepts


def extract_operators(text: str) -> list[str]:
    """Estrae operatori matematici e logici dal testo."""
    operators = []

    # Operatori matematici simbolici
    op_map = {
        "+": "addition",
        "-": "subtraction",
        "*": "multiplication",
        "×": "multiplication",
        "/": "division",
        "÷": "division",
        "^": "power",
        "**": "power",
        "=": "equals",
    }
    for symbol, name in op_map.items():
        if symbol in text:
            operators.append(name)

    # Operatori matematici in italiano
    word_ops = {
        "più": "addition",
        "somma": "addition",
        "piu": "addition",
        "meno": "subtraction",
        "sottrai": "subtraction",
        "per": "multiplication",
        "volte": "multiplication",
        "diviso": "division",
        "dividendo": "division",
        "elevato": "power",
        "uguale": "equals",
    }
    text_lower = text.lower()
    for word, name in word_ops.items():
        if word in text_lower:
            if name not in operators:
                operators.append(name)

    # Operatori logici
    logic_ops = {
        "e": "and",
        "o": "or",
        "non": "not",
        "se": "if",
        "allora": "then",
        "oppure": "or",
        "inoltre": "and",
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
    text_lower = re.sub(r"\?$", "", text_lower)  # rimuovi ? finale

    # Articoli da rimuovere dai match
    articles = r"(?:il |la |i |le |lo |un |una )?"
    articles_en = r"(?:the |a |an )?"

    # Pattern di relazione (Italiano + Inglese)
    relation_patterns = [
        # Italiano
        (r"(\w+)\s+[èe]\s+" + articles + r"(\w+)", "è_un"),
        (r"(\w+)\s+ha\s+" + articles + r"(\w+)", "ha_caratteristica"),
        (r"(\w+)\s+[èe]\s+(\w+)\s+di\s+(\w+)", "è_di"),
        (r"(\w+)\s+(?:sta|si trova)\s+(?:in|a|dentro|sopra|sotto)\s+(\w+)", "si_trova"),
        (r"(\w+)\s+(?:causa|provoca|genera)\s+(\w+)", "causa"),
        (r"(\w+)\s+(?:[èe] simile a|assomiglia a)\s+(\w+)", "simile_a"),
        (r"(\w+)\s+fa\s+(?:il\s+|la\s+|i\s+|le\s+)?(.+)", "fa"),
        (
            r"(\w+)\s+(allatta|vola|nuota|corre|abbaia|miagola|canta)",
            "ha_caratteristica",
        ),
        (r"(\w+)\s+si\s+(muove|trova|comporta)", "ha_caratteristica_si"),
        # English
        (r"(\w+)\s+is\s+(?:a|an|the)?\s*(\w+)", "is_a"),
        (r"(\w+)\s+has\s+(?:a|an|the)?\s*(\w+)", "has_property"),
        (r"(\w+)\s+can\s+(\w+)", "can"),
        (r"(\w+)\s+lives\s+in\s+(\w+)", "lives_in"),
        (r"(\w+)\s+causes\s+(\w+)", "causes"),
        (r"(\w+)\s+is\s+similar\s+to\s+(\w+)", "similar_to"),
    ]

    for pattern, rel_type in relation_patterns:
        for match in re.finditer(pattern, text_lower):
            groups = match.groups()
            if len(groups) >= 2:
                subj = groups[0]
                obj = groups[1].strip().rstrip("?")
                # Salta se soggetto o oggetto sono articoli/stop words
                if subj not in STOP_WORDS and len(subj) > 1:
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

    if ("elevato" in text_lower or "alla" in text_lower) and (
        "seconda" in text_lower or "terza" in text_lower
    ):
        return "power"

    # Equazioni
    if "=" in text and re.search(r"[a-z]", text_lower):
        return "equation"

    # Operazioni base - funziona per qualsiasi intent (non solo "calculate")
    if operators:
        if (
            "addition" in operators
            or "più" in text_lower
            or "piu" in text_lower
            or "somma" in text_lower
        ):
            return "addition"
        if "subtraction" in operators or "meno" in text_lower:
            return "subtraction"
        if "multiplication" in operators or ("per" in text_lower and len(numbers) >= 2):
            return "multiplication"
        if "division" in operators or "diviso" in text_lower:
            return "division"

    # Se ha numeri e un operatore simbolico (funziona anche senza intent "calculate")
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
