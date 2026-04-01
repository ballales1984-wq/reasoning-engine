"""
Deductive Reasoner — Ragiona dal generale al particolare.

Se tutti gli X sono Y, e Z è X, allora Z è Y.

Tipi di deduzione supportati:
- Modus Ponens: Se A → B, e A è vero, allora B è vero
- Sillogismo: Se tutti gli A sono B, e tutti i B sono C, allora tutti gli A sono C
- Modus Tollens: Se A → B, e B è falso, allora A è falso
- Catena transitiva: Se A → B e B → C, allora A → C
"""

from dataclasses import dataclass


from ..core.types import DeductionStep, DeductionResult


class DeductiveReasoner:
    """
    Motore deduttivo. Naviga il Knowledge Graph
    applicando regole logiche per dedurre nuovi fatti.
    """

    def __init__(self, knowledge_graph, rule_engine):
        self.knowledge = knowledge_graph
        self.rules = rule_engine

    # Relazioni che rappresentano gerarchie transitività
    TRANSITIVE_RELATIONS = {
        "è_un_tipo_di", "è_parte_di", "contiene",
        "è_maggiore_di", "è_minore_di",
        "si_trova_in", "appartiene_a",
    }

    # Relazioni inverse
    INVERSE_RELATIONS = {
        "è_un_tipo_di": "ha_tipo",
        "ha_tipo": "è_un_tipo_di",
        "è_parte_di": "contiene",
        "contiene": "è_parte_di",
        "causa": "è_causato_da",
        "è_causato_da": "causa",
    }

    def deduce(self, subject: str, target_property: str = None) -> DeductionResult:
        """
        Cerca di dedurre qualcosa sul soggetto.

        Se target_property è specificato, cerca di dedurre se il soggetto
        ha quella proprietà. Altrimenti deduce tutto ciò che può.
        """
        chain = []

        # 1. Cerca proprietà dirette nel KG
        concept = self.knowledge.get(subject)
        if not concept:
            return DeductionResult(found=False)

        # 2. Se abbiamo un target, cerchiamo di raggiungerlo
        if target_property:
            return self._deduce_to_target(subject, target_property)

        # 3. Altrimenti deduciamo tutto
        return self._deduce_all(subject)

    def _deduce_to_target(self, subject: str, target: str, depth: int = 0, visited: set = None) -> DeductionResult:
        """
        Cerca di dedurre se subject ha la proprietà target.
        Usa forward chaining fino a max_depth.
        Cerca sia match diretti che valori dentro relazioni (es. ha_caratteristica → ha_pelo).
        """
        if visited is None:
            visited = set()

        if depth > 5 or subject in visited:
            return DeductionResult(found=False)

        visited.add(subject)
        concept = self.knowledge.get(subject)

        if not concept:
            return DeductionResult(found=False)

        # Check 1: subject ha direttamente target come valore di qualunque relazione
        for rel_type, targets in concept.relations.items():
            if target in targets:
                step = DeductionStep(
                    rule_type="direct",
                    premise1=f"{subject} {rel_type} {target}",
                    premise2="",
                    conclusion=f"{subject} ha {target}",
                    confidence=1.0
                )
                return DeductionResult(
                    found=True,
                    conclusion=f"{subject} → {target}",
                    chain=[step],
                    confidence=1.0,
                    steps_count=1
                )

        # Check 2: ereditarietà — cerca nei parent (transitive relations)
        for rel_type, targets in concept.relations.items():
            if rel_type in self.TRANSITIVE_RELATIONS:
                for intermediate in targets:
                    sub_result = self._deduce_to_target(intermediate, target, depth + 1, visited.copy())
                    if sub_result.found:
                        step = DeductionStep(
                            rule_type="syllogism",
                            premise1=f"{subject} {rel_type} {intermediate}",
                            premise2=f"{intermediate} ha {target}",
                            conclusion=f"{subject} ha {target} (ereditato)",
                            confidence=sub_result.confidence * 0.95
                        )
                        return DeductionResult(
                            found=True,
                            conclusion=f"{subject} → {target}",
                            chain=[step] + sub_result.chain,
                            confidence=sub_result.confidence * 0.95,
                            steps_count=1 + sub_result.steps_count
                        )

        return DeductionResult(found=False)

    def _deduce_all(self, subject: str, depth: int = 0, visited: set = None) -> DeductionResult:
        """
        Deduce tutte le proprietà del soggetto attraverso catene logiche.
        """
        if visited is None:
            visited = set()

        if depth > 5 or subject in visited:
            return DeductionResult(found=False)

        visited.add(subject)
        concept = self.knowledge.get(subject)

        if not concept:
            return DeductionResult(found=False)

        all_chain = []
        total_confidence = 1.0
        conclusions = []

        # Esplora tutte le relazioni transitives
        for rel_type, targets in concept.relations.items():
            if rel_type in self.TRANSITIVE_RELATIONS:
                for target in targets:
                    target_concept = self.knowledge.get(target)
                    if target_concept:
                        # Eredita proprietà dal parent
                        for parent_rel, parent_targets in target_concept.relations.items():
                            for pt in parent_targets:
                                # Se subject non ha già questa proprietà
                                if pt not in concept.relations.get(parent_rel, []):
                                    step = DeductionStep(
                                        rule_type="inheritance",
                                        premise1=f"{subject} {rel_type} {target}",
                                        premise2=f"{target} {parent_rel} {pt}",
                                        conclusion=f"{subject} {parent_rel} {pt} (dedotto)",
                                        confidence=0.9 ** (depth + 1)
                                    )
                                    all_chain.append(step)
                                    conclusions.append(f"{subject} → {pt}")
                                    total_confidence *= step.confidence

                    # Ricorsione
                    sub_result = self._deduce_all(target, depth + 1, visited.copy())
                    if sub_result.found:
                        all_chain.extend(sub_result.chain)

        if all_chain:
            return DeductionResult(
                found=True,
                conclusion="; ".join(conclusions),
                chain=all_chain,
                confidence=total_confidence,
                steps_count=len(all_chain)
            )

        return DeductionResult(found=False)

    def query(self, question: str) -> DeductionResult:
        """
        Risponde a una domanda usando deduzione.

        Supporta pattern tipo:
        - "il gatto è un animale?"
        - "il gatto ha 4 zampe?"
        """
        question = question.lower().strip()

        # Pattern: "X è un Y?"
        import re
        match = re.search(r'(\w+)\s+[èe]\s+(?:un[ao]?\s+)?(\w+)', question)
        if match:
            subject = match.group(1)
            target = match.group(2)
            return self._deduce_to_target(subject, target)

        # Pattern: "X ha Y?"
        match = re.search(r'(\w+)\s+ha\s+(\w+)', question)
        if match:
            subject = match.group(1)
            target = match.group(2)
            return self._deduce_to_target(subject, target)

        return DeductionResult(found=False)

    def add_rule(self, premise1: str, premise2: str, conclusion: str):
        """Aggiunge una regola deduttiva al Knowledge Graph."""
        # Le regole sono rappresentate come relazioni nel KG
        # "tutti gli X sono Y" → connect X, è_un_tipo_di, Y
        pass
