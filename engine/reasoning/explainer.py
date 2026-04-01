"""
Explainer — Il modulo di spiegazione.

Non dà solo la risposta, ma spiega PERCHÉ è quella giusta.
Questo è il superpotere rispetto agli LLM normali.
"""


class Explainer:
    """
    Genera spiegazioni comprensibili del ragionamento.
    """

    def generate(self, steps: list[str], result: dict) -> str:
        """
        Genera una spiegazione testuale del ragionamento.
        """
        explanation = "🧠 **Il mio ragionamento:**\n\n"

        for i, step in enumerate(steps, 1):
            explanation += f"{i}. {step}\n"

        if result and result.get("explanation"):
            explanation += f"\n📊 **Dettaglio:** {result['explanation']}"

        if result and result.get("confidence") is not None:
            confidence = result["confidence"]
            if confidence >= 0.9:
                explanation += "\n\n✅ Sono molto sicuro di questa risposta."
            elif confidence >= 0.7:
                explanation += "\n\n🤔 Sono abbastanza sicuro, ma potrei sbagliare."
            else:
                explanation += "\n\n⚠️ Non sono sicuro. Verifica tu stesso."

        return explanation

    def explain_concept(self, concept) -> str:
        """
        Spiega un concetto in modo comprensibile.
        """
        explanation = f"📚 **{concept.name}**\n\n"

        if concept.description:
            explanation += f"{concept.description}\n\n"

        if concept.examples:
            explanation += "**Esempi:**\n"
            for ex in concept.examples:
                explanation += f"  • {ex}\n"

        if concept.relations:
            explanation += "\n**Collegamenti:**\n"
            for rel_type, targets in concept.relations.items():
                for target in targets:
                    explanation += f"  • {rel_type}: {target}\n"

        return explanation
