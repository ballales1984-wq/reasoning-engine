"""
FinancialDataTool — Canale specializzato per dati finanziari reali.
Utilizza yfinance per recuperare prezzi, ticker e info aziendali.
"""

import time
from typing import Any, Dict, List, Optional


class FinancialDataTool:
    """
    Tool per l'acquisizione di dati finanziari via Yahoo Finance.
    Implementato come Canale di Comunicazione.
    """

    def __init__(self, engine=None):
        self.engine = engine
        self.channel_name = "financial_market"
        self.trust_score = 0.95
        self._yf = None  # Lazy loading

    def _ensure_yf(self):
        """Carica yfinance solo se necessario."""
        if self._yf is None:
            try:
                import yfinance as yf
                self._yf = yf
            except ImportError:
                raise ImportError("Libreria 'yfinance' non trovata. Installa con: pip install yfinance")

    def get_stock_price(self, ticker: str) -> dict:
        """Recupera il prezzo attuale di un'azione."""
        self._ensure_yf()
        try:
            stock = self._yf.Ticker(ticker)
            # Usa fast_info se disponibile o history
            data = stock.history(period="1d")
            if data.empty:
                return {"success": False, "error": f"Nessun dato per {ticker}"}
            
            price = data['Close'].iloc[-1]
            currency = stock.info.get('currency', 'USD')
            
            result = {
                "success": True,
                "ticker": ticker,
                "price": float(price),
                "currency": currency,
                "timestamp": time.time(),
                "channel": self.channel_name
            }
            
            # Se l'engine è collegato, insegna il concetto
            if self.engine:
                self.engine.learn(
                    concept=f"prezzo_{ticker}",
                    examples=[f"{price} {currency}"],
                    description=f"Ultimo prezzo di chiusura per {ticker}",
                    category="finance/stocks",
                    channel=self.channel_name,
                    trust_score=self.trust_score
                )
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_company_info(self, ticker: str) -> dict:
        """Recupera informazioni generali su un'azienda."""
        self._ensure_yf()
        try:
            stock = self._yf.Ticker(ticker)
            info = stock.info
            
            description = info.get('longBusinessSummary', "")
            sector = info.get('sector', "Unknown")
            
            result = {
                "success": True,
                "name": info.get('longName', ticker),
                "description": description,
                "sector": sector,
                "market_cap": info.get('marketCap'),
                "channel": self.channel_name
            }
            
            if self.engine and description:
                self.engine.learn(
                    concept=info.get('longName', ticker),
                    examples=[f"Settore: {sector}", f"Market Cap: {info.get('marketCap')}"],
                    description=description[:200] + "...",
                    category="finance/companies",
                    channel=self.channel_name,
                    trust_score=self.trust_score
                )
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_historical_data(self, ticker: str, period: str = "1mo") -> dict:
        """Recupera dati storici."""
        self._ensure_yf()
        try:
            stock = self._yf.Ticker(ticker)
            hist = stock.history(period=period)
            return {
                "success": True,
                "ticker": ticker,
                "data": hist.to_dict(),
                "channel": self.channel_name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
