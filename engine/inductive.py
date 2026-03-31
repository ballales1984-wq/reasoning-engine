"""
Inductive Reasoner — Ragiona dal particolare al generale.

Dati esempi, trova il pattern comune e crea una regola generale.

Esempio:
  Esempi: "il cane ha 4 zampe", "il gatto ha 4 zampe", "il cavallo ha 4 zampe"
  Induzione: "I mammiferi terrestri tipicamente hanno 4 zampe"
"""

from dataclasses import dataclass, field
from collections import Counter


@dataclass
class Pattern:
    """Un pattern estratto da esempi."""
    description: str             # Descrizione del pattern
    attribute: str               # L'attributo comune
    value: any                   # Il valore comune
    frequency: int               # Quante volte appare
    total_examples: int          # Totale esempi analizzati
    confidence: float = 0.0      # Frequenza / Totale


@dataclass
class InductionResult:
    """Risultato di un'induzione."""
    found: bool
    patterns: list = field(default_factory=list)
    rules_created: list = field(default_factory=list)
    explanation: str = ""


class InductiveReasoner:
    """
    Motore induttivo. Trova pattern in esempi e crea regole generali.
    """

    def __init__(self, knowledge_graph, rule_engine):
        self.knowledge = knowledge_graph
        self.rules = rule_engine
        self.learned_patterns = []

    def induce_from_examples(self, examples: list[str]) -> InductionResult:
        """
        Analizza una lista di esempi e cerca pattern comuni.

        Gli esempi sono frasi tipo:
        - "il cane ha 4 zampe"
        - "il gatto ha 4 zampe"
        """
        if len(examples) < 2:
            return InductionResult(
                found=False,
                explanation="Servono almeno 2 esempi per indurre un pattern"
            )

        patterns = []
        rules_created = []

        # Estrai fatti dagli esempi
        facts = self._extract_facts(examples)

        # Raggruppa per tipo di relazione
        by_relation = {}
        for fact in facts:
            key = fact["relation"]
            if key not in by_relation:
                by_relation[key] = []
            by_relation[key].append(fact)

        # Cerca pattern per ogni relazione
        for relation, relation_facts in by_relation.items():
            # Raggruppa per valore
            values = Counter(f["value"] for f in relation_facts)
            subjects = [f["subject"] for f in relation_facts]

            for value, count in values.items():
                frequency = count / len(relation_facts)

                if frequency >= 0.8:  # 80% degli esempi condividono questo valore
                    # Trova la categoria comune dei soggetti
                    common_category = self._find_common_category(subjects)

                    pattern = Pattern(
                        description=f"{common_category or 'questi oggetti'} {relation} {value}",
                        attribute=relation,
                        value=value,
                        frequency=count,
                        total_examples=len(relation_facts),
                        confidence=frequency
                    )
                    patterns.append(pattern)

                    # Crea una regola generale
                    if common_category:
                        rule_desc = f"I {common_category} {relation} {value}"
                    else:
                        rule_desc = f"Oggetti simili a {subjects[0]} {relation} {value}"

                    rules_created.append({
                        "rule": rule_desc,
                        "subjects": subjects,
                        "relation": relation,
                        "value": value,
                        "confidence": frequency
                    })

        # Cerca pattern numerici
        numeric_patterns = self._find_numeric_patterns(facts)
        patterns.extend(numeric_patterns)

        if patterns:
            explanation = "📊 **Pattern trovati:**\n\n"
            for p in patterns:
                bar = "█" * int(p.confidence * 10)
                explanation += f"  • {p.description}\n"
                explanation += f"    Confidenza: {bar} {p.confidence:.0%} ({p.frequency}/{p.total_examples} esempi)\n"

            return InductionResult(
                found=True,
                patterns=patterns,
                rules_created=rules_created,
                explanation=explanation
            )

        return InductionResult(
            found=False,
            explanation="Non ho trovato pattern evidenti negli esempi"
        )

    def induce_from_knowledge(self) -> InductionResult:
        """
        Cerca pattern nella conoscenza esistente nel Knowledge Graph.
        """
        all_concepts = self.knowledge.list_all()
        if len(all_concepts) < 3:
            return InductionResult(found=False, explanation="Pochi concetti per induzione")

        patterns = []

        # Raggruppa concetti per categoria
        by_category = {}
        for c in all_concepts:
            cat = c.get("category", "general")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(c)

        # Per ogni categoria, trova relazioni comuni
        for category, concepts in by_category.items():
            if len(concepts) < 2:
                continue

            # Raccogli tutte le relazioni
            all_relations = []
            for c in concepts:
                for rel_type, targets in c.get("relations", {}).items():
                    for target in targets:
                        all_relations.append((rel_type, target))

            # Trova relazioni frequenti
            relation_counts = Counter(all_relations)
            for (rel_type, target), count in relation_counts.items():
                if count >= 2:
                    confidence = count / len(concepts)
                    pattern = Pattern(
                        description=f"I {category} tendono ad avere {rel_type} → {target}",
                        attribute=rel_type,
                        value=target,
                        frequency=count,
                        total_examples=len(concepts),
                        confidence=confidence
                    )
                    patterns.append(pattern)

        if patterns:
            return InductionResult(
                found=True,
                patterns=patterns,
                explanation=f"Trovati {len(patterns)} pattern nella conoscenza esistente"
            )

        return InductionResult(found=False)

    def _extract_facts(self, examples: list[str]) -> list[dict]:
        """Estrae fatti strutturati da frasi."""
        import re
        facts = []

        for example in examples:
            example = example.lower().strip()

            # Pattern: "X ha Y" → X ha Y
            match = re.search(r'(?:il|la|i|le|lo|un|una)\s+(\w+)\s+ha\s+(?:il|la|i|le|lo|un|una)?\s*(\w+(?:\s+\w+)?)', example)
            if match:
                facts.append({
                    "subject": match.group(1),
                    "relation": "ha",
                    "value": match.group(2).strip()
                })
                continue

            # Pattern: "X è Y" → X è Y
            match = re.search(r'(?:il|la|i|le|lo|un|una)\s+(\w+)\s+[èe]\s+(?:un[ao]?\s+)?(\w+)', example)
            if match:
                facts.append({
                    "subject": match.group(1),
                    "relation": "è",
                    "value": match.group(2)
                })
                continue

            # Pattern numerico: "X Y N" (es. "cane ha 4 zampe")
            match = re.search(r'(\w+)\s+(?:ha|con)\s+(\d+)\s+(\w+)', example)
            if match:
                facts.append({
                    "subject": match.group(1),
                    "relation": "ha",
                    "value": f"{match.group(2)} {match.group(3)}"
                })
                continue

            # Fallback: salva come fatto generico
            facts.append({
                "subject": example.split()[0] if example.split() else "unknown",
                "relation": "generico",
                "value": example
            })

        return facts

    def _find_common_category(self, subjects: list[str]) -> str:
        """Trova la categoria comune di una lista di soggetti nel KG."""
        categories = []
        for subject in subjects:
            concept = self.knowledge.get(subject)
            if concept:
                categories.append(concept.category)

        if not categories:
            return ""

        # Se tutti hanno la stessa categoria
        if len(set(categories)) == 1 and categories[0] != "general":
            return categories[0]

        # Cerca antenati comuni
        for subject in subjects:
            concept = self.knowledge.get(subject)
            if concept:
                parents = concept.relations.get("è_un_tipo_di", [])
                for parent in parents:
                    parent_concept = self.knowledge.get(parent)
                    if parent_concept and parent_concept.category != "general":
                        return parent

        return ""

    def _find_numeric_patterns(self, facts: list[dict]) -> list[Pattern]:
        """Trova pattern numerici negli esempi."""
        import re
        patterns = []

        # Raggruppa per relazione e cerca valori numerici
        numeric_facts = {}
        for fact in facts:
            value = str(fact["value"])
            numbers = re.findall(r'\d+', value)
            if numbers:
                key = fact["relation"]
                if key not in numeric_facts:
                    numeric_facts[key] = []
                numeric_facts[key].append(int(numbers[0]))

        for relation, values in numeric_facts.items():
            if len(values) >= 2:
                # Tutti uguali?
                if len(set(values)) == 1:
                    patterns.append(Pattern(
                        description=f"Tutti hanno {relation} = {values[0]}",
                        attribute=relation,
                        value=values[0],
                        frequency=len(values),
                        total_examples=len(values),
                        confidence=1.0
                    ))

        return patterns
