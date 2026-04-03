"""
LLM Feature Extractor - Estrae proprietà strutturate da LLM

Quando il Reasoner incontra un concetto nuovo, può chiedere al LLM
le caratteristiche rilevanti per distinguerlo dagli altri.

Flusso:
1. Prende un concetto nuovo + ipotesi esistenti
2. Chiede al LLM: "Quali proprietà distinguono X da Y, Z?"
3. Normalizza la risposta in dict {feature: value}
4. Restituisce dict pronto per HypothesisSpace
"""

from enum import Enum


class FeatureType(Enum):
    """Tipi di feature che il LLM può estrarre."""
    BOOLEAN = "boolean"      # true/false
    CATEGORY = "category"    # categoria discretizzata
    NUMERIC = "numeric"      # valore numerico
    TEXT = "text"          # testo libero


class LLMFeatureExtractor:
    """
    Estrae proprietà strutturate da LLM.
    
    Usage:
        extractor = LLMFeatureExtractor(llm_client)
        features = extractor.extract_features(
            new_concept="lupo",
            existing_hypotheses=["cane", "gatto", "volpe"],
            context="animale mammifero"
        )
    """
    
    # Prompt template per estrarre feature
    EXTRACT_PROMPT = """ Sei un assistente che estrae proprietà rilevanti per distinguere concetti.
    
Nuovo concetto: {new_concept}
Concetti esistenti: {existing}

Per ciascun concetto esistente, elenca 3-5 proprietà booleane che distinguono il nuovo concetto.
Formato richiesto (JSON):
{{
    "proprietà_1": true/false,
    "proprietà_2": true/false,
    ...
}}

Esempio per distinguere "gatto" da "cane":
{{
    "fa_miao": true,
    "cacciatore": true,
    "notturno": true
}}

Rispondi SOLO con JSON válido, niente testo extra."""

    # Prompt per completare con dettagli
    ENRICH_PROMPT = """ Arricchisci le proprietà del concetto "{concept}".

Proprietà attuali: {existing_features}

Aggiungi 2-3 nuove proprietà booleane che potrebbero essere utili per distinguerlo.
Formato JSON:
{{
    "nuova_prop_1": true/false,
    ...
}}

Rispondi SOLO con JSON válido."""

    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: Client LLM (Ollama, OpenAI, etc.)
        """
        self.llm = llm_client
    
    def extract_features(
        self,
        new_concept: str,
        existing_hypotheses: list,
        context: str = ""
    ) -> dict:
        """
        Estrae特征 per distinguere un concetto nuovo.
        
        Args:
            new_concept: Nome del concetto da aggiungere
            existing_hypotheses: Lista di concetti già nel sistema
            context: Contesto aggiuntivo (es. "animale mammifero")
            
        Returns:
            dict di {feature: value}
        """
        # Se non c'è LLM, ritorna dict vuoto
        if not self.llm:
            return {}
        
        # Costruisci prompt
        prompt = self.EXTRACT_PROMPT.format(
            new_concept=new_concept,
            existing=", ".join(existing_hypotheses)
        )
        
        if context:
            prompt += f"\n\nContesto: {context}"
        
        # Chiedi al LLM
        try:
            response = self.llm.chat(prompt)
            text = response.get("message", {}).get("content", "")
            
            # Estrai JSON dalla risposta
            features = self._parse_json(text)
            return features
            
        except Exception as e:
            print(f"LLM Feature Extractor error: {e}")
            return {}
    
    def enrich_features(
        self,
        concept: str,
        existing_features: dict
    ) -> dict:
        """
        Arricchisce feature esistenti con nuove proprietà.
        
        Args:
            concept: Nome concetto
            existing_features: Feature già note
            
        Returns:
            dict combinato
        """
        if not self.llm:
            return existing_features
        
        prompt = self.ENRICH_PROMPT.format(
            concept=concept,
            existing_features=existing_features
        )
        
        try:
            response = self.llm.chat(prompt)
            text = response.get("message", {}).get("content", "")
            
            new_features = self._parse_json(text)
            
            # Merge
            return {**existing_features, **new_features}
            
        except Exception as e:
            print(f"LLM enrich error: {e}")
            return existing_features
    
    def _parse_json(self, text: str) -> dict:
        """
        Estrae JSON da testo LLM.
        
        Args:
            text: Risposta del LLM
            
        Returns:
            dict
        """
        import json
        import re
        
        # Trova il JSON nel testo
        # Cerca tra ```json e ``` o tra { e }
        json_match = re.search(r'\{[\s\S]*\}', text)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Prova a parsare tutto il testo
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        return {}
    
    def suggest_differentiating_question(
        self,
        concept: str,
        existing_features: dict,
        target_hypotheses: list
    ) -> str:
        """
        Suggerisce una domanda per distinguere un concetto.
        
        Args:
            concept: Concetto da distinguere
            existing_features: Feature già note
            target_hypotheses: Ipotesi da escludere
            
        Returns:
            Stringa domanda
        """
        if not self.llm:
            return f"{concept} ha la caratteristica X?"
        
        prompt = f"""Una domanda sì/no utile per distinguere "{concept}" da {target_hypotheses}?

Feature già note: {list(existing_features.keys())}

Rispondi SOLO con una domanda sì/no esclusiva."""
        
        try:
            response = self.llm.chat(prompt)
            text = response.get("message", {}).get("content", "").strip()
            return text
        except:
            return f"{concept} ha questa caracteristica?"


# Demo senza LLM
if __name__ == "__main__":
    # Simula estrazione
    extractor = LLMFeatureExtractor()
    
    print("LLM Feature Extractor")
    print("=" * 40)
    print("\nUsage:")
    print("""
extractor = LLMFeatureExtractor(llm_client)
features = extractor.extract_features(
    new_concept="lupo",
    existing_hypotheses=["cane", "gatto", "volpe"],
    context="animale mammifero"
)
print(features)
# Output: {"selvatico": true, "ulula": true, "caccia_in_branco": true, ...}
""")
    
    print("\nServe un LLM configurato per funzionare.")
    print("Puoi passare il tuo Ollama client o OpenAI client nel costruttore.")