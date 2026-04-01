"""
BrowsingTool — Navigazione avanzata e scraping testuale.
Permette all'engine di "leggere" il contenuto completo di pagine web.
"""

import httpx
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional

class BrowsingTool:
    """
    Tool per la navigazione profonda (Deep Browsing).
    Estrae il contenuto testuale pulito da URL specifici.
    """

    def __init__(self, engine=None):
        self.engine = engine
        self.channel_name = "web_browsing"
        self.trust_score = 0.75 # Un po' meno di news ufficiali, ma più di uno snippet
        self.timeout = 10.0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def browse_url(self, url: str) -> Dict[str, Any]:
        """Scarica e pulisce il contenuto di un URL."""
        try:
            with httpx.Client(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                
            # 1. Parsing HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 2. Pulizia: Rimuovi elementi non testuali
            for script_or_style in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script_or_style.decompose()
            
            # 3. Estrai testo
            text = soup.get_text(separator=" ")
            
            # 4. Normalizzazione: Rimuovi spazi extra e righe vuote
            text = re.sub(r'\s+', ' ', text).strip()
            
            # 5. Prendi solo i primi 5000 caratteri per evitare overload
            summary_text = text[:5000]
            
            return {
                "success": True,
                "url": url,
                "title": soup.title.string if soup.title else "N/A",
                "content": summary_text,
                "length": len(summary_text),
                "channel": self.channel_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }

    def summarize_page(self, url: str) -> dict:
        """Esegue il browse e prova a sintetizzare il punto chiave."""
        res = self.browse_url(url)
        if not res["success"]:
            return res
        
        # In una versione futura qui potremmo chiamare un LLM per un riassunto vero
        # Per ora restituiamo l'estratto pulito.
        return res
