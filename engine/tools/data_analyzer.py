"""
DataAnalysisTool — Analisi dati strutturati per il ReasoningEngine.
Utilizza pandas per calcoli statistici, aggregazioni e analisi di trend.
"""

from typing import Any, Dict, List, Optional


class DataAnalysisTool:
    """
    Tool per l'analisi di dati (CSV, JSON, Liste).
    Implementato come Canale di Analisi Interna.
    """

    def __init__(self, engine=None):
        self.engine = engine
        self.channel_name = "data_analysis"
        self._pd = None  # Lazy loading

    def _ensure_pd(self):
        """Carica pandas solo se necessario."""
        if self._pd is None:
            try:
                import pandas as pd
                self._pd = pd
            except ImportError:
                raise ImportError("Libreria 'pandas' non trovata. Installa con: pip install pandas")

    def analyze_series(self, data: list, name: str = "valore") -> dict:
        """Esegue un'analisi statistica di base su una serie di numeri."""
        self._ensure_pd()
        try:
            df = self._pd.Series(data)
            stats = df.describe().to_dict()
            
            result = {
                "success": True,
                "name": name,
                "stats": stats,
                "trend": "crescente" if df.iloc[-1] > df.iloc[0] else "decrescente",
                "volatility": float(df.std() / df.mean()) if df.mean() != 0 else 0,
                "channel": self.channel_name
            }
            
            # Se l'engine è collegato, insegna questi insight
            if self.engine:
                self.engine.learn(
                    concept=f"analisi_{name}",
                    examples=[f"Media: {stats['mean']}", f"Trend: {result['trend']}"],
                    description=f"Insight statistici su {name}",
                    category="data/stats",
                    channel=self.channel_name,
                    trust_score=0.9
                )
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_csv(self, filepath: str) -> dict:
        """Carica e analizza un file CSV."""
        self._ensure_pd()
        try:
            df = self._pd.read_csv(filepath)
            info = {
                "rows": len(df),
                "columns": list(df.columns),
                "summary": df.describe().to_dict()
            }
            return {
                "success": True,
                "info": info,
                "channel": self.channel_name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def calculate_correlation(self, data1: list, data2: list) -> dict:
        """Calcola la correlazione tra due serie di dati."""
        self._ensure_pd()
        try:
            s1 = self._pd.Series(data1)
            s2 = self._pd.Series(data2)
            corr = float(s1.corr(s2))
            
            return {
                "success": True,
                "correlation": corr,
                "strength": "forte" if abs(corr) > 0.7 else "debole",
                "channel": self.channel_name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
