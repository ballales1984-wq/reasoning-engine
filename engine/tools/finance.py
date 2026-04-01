"""
FinanceModule — Ragionamento finanziario per il ReasoningEngine.

Supporta:
- Interesse semplice e composto
- ROI (Return on Investment)
- Analisi costi-benefici
- Calcoli finanziari base
- Concetti di investimento
- Analisi rischio/rendimento
"""


import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class FinancialResult:
    """Risultato di un calcolo finanziario."""
    operation: str
    input_values: dict
    result: float | str
    explanation: str
    confidence: float = 1.0


class FinanceModule:
    """Modulo di ragionamento finanziario."""
    
    def __init__(self, knowledge_graph, rule_engine):
        self.knowledge = knowledge_graph
        self.rules = rule_engine
        self._register_financial_rules()
        self._register_financial_concepts()
    
    def _register_financial_rules(self):
        """Registra regole finanziarie."""
        
        # Interesse semplice: I = P × r × t
        self.rules.add_rule(
            "simple_interest",
            lambda p, r, t: p * r * t,
            description="Interesse semplice: Capitale × Tasso × Tempo",
            inputs=["number", "number", "number"],
            output_type="number"
        )
        
        # Interesse composto: A = P × (1 + r)^t
        self.rules.add_rule(
            "compound_interest",
            lambda p, r, t: p * (1 + r) ** t,
            description="Interesse composto: Capitale × (1 + Tasso)^Tempo",
            inputs=["number", "number", "number"],
            output_type="number"
        )
        
        # ROI: (Guadagno - Costo) / Costo × 100
        self.rules.add_rule(
            "roi",
            lambda gain, cost: ((gain - cost) / cost) * 100 if cost != 0 else 0,
            description="ROI: (Guadagno - Costo) / Costo × 100",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Valore futuro
        self.rules.add_rule(
            "future_value",
            lambda pv, rate, periods: pv * (1 + rate) ** periods,
            description="Valore futuro di un investimento",
            inputs=["number", "number", "number"],
            output_type="number"
        )
        
        # Valore presente
        self.rules.add_rule(
            "present_value",
            lambda fv, rate, periods: fv / (1 + rate) ** periods if (1 + rate) ** periods != 0 else 0,
            description="Valore presente di un importo futuro",
            inputs=["number", "number", "number"],
            output_type="number"
        )
        
        # Rata del mutuo (formula ammortamento)
        self.rules.add_rule(
            "mortgage_payment",
            lambda principal, rate, periods: (
                principal * (rate * (1 + rate) ** periods) / ((1 + rate) ** periods - 1)
                if ((1 + rate) ** periods - 1) != 0 else principal / periods
            ),
            description="Rata mensile mutuo",
            inputs=["number", "number", "number"],
            output_type="number"
        )
        
        # Margine di profitto
        self.rules.add_rule(
            "profit_margin",
            lambda revenue, cost: ((revenue - cost) / revenue) * 100 if revenue != 0 else 0,
            description="Margine di profitto: (Ricavi - Costi) / Ricavi × 100",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Break-even point
        self.rules.add_rule(
            "break_even",
            lambda fixed_costs, price_per_unit, variable_cost_per_unit: (
                fixed_costs / (price_per_unit - variable_cost_per_unit)
                if (price_per_unit - variable_cost_per_unit) > 0 else float('inf')
            ),
            description="Punto di pareggio: Costi fissi / (Prezzo - Costo variabile)",
            inputs=["number", "number", "number"],
            output_type="number"
        )
        
        # Rendimento annualizzato
        self.rules.add_rule(
            "annualized_return",
            lambda total_return, years: ((1 + total_return) ** (1 / years) - 1) * 100 if years > 0 else 0,
            description="Rendimento annualizzato",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Rapporto rischio/rendimento
        self.rules.add_rule(
            "risk_reward_ratio",
            lambda potential_gain, potential_loss: potential_gain / potential_loss if potential_loss != 0 else float('inf'),
            description="Rapporto rischio/rendimento: Guadagno potenziale / Perdita potenziale",
            inputs=["number", "number"],
            output_type="number"
        )
    
    def _register_financial_concepts(self):
        """Registra concetti finanziari nel knowledge graph."""
        
        concepts = {
            "interesse_semplice": {
                "description": "Interesse calcolato solo sul capitale iniziale. Formula: I = P × r × t",
                "examples": ["1000€ al 5% per 2 anni = 100€ di interesse"],
                "category": "finance/interest"
            },
            "interesse_composto": {
                "description": "Interesse calcolato su capitale + interessi precedenti. L'interesse genera interesse.",
                "examples": ["1000€ al 5% per 2 anni = 102.5€ (non 100€)"],
                "category": "finance/interest"
            },
            "roi": {
                "description": "Return on Investment. Misura la redditività di un investimento.",
                "examples": ["Investi 1000€, guadagni 1200€ → ROI = 20%"],
                "category": "finance/metrics"
            },
            "diversificazione": {
                "description": "Distribuire gli investimenti su diversi asset per ridurre il rischio.",
                "examples": ["Non mettere tutte le uova nello stesso paniere"],
                "category": "finance/strategy"
            },
            "inflazione": {
                "description": "Aumento generale dei prezzi. Riduce il potere d'acquisto nel tempo.",
                "examples": ["Se l'inflazione è 3%, 100€ oggi valgono 97€ tra un anno"],
                "category": "finance/concepts"
            },
            "liquidita": {
                "description": "Facilità con cui un asset può essere convertito in denaro.",
                "examples": ["Contanti = alta liquidità, immobili = bassa liquidità"],
                "category": "finance/concepts"
            },
            "costo_opportunita": {
                "description": "Il costo di non poter fare qualcos'altro con le stesse risorse.",
                "examples": ["Se investi in azioni, il costo opportunità è il rendimento obbligazionario perso"],
                "category": "finance/concepts"
            },
            "rendimento": {
                "description": "Il guadagno o la perdita di un investimento espresso in percentuale.",
                "examples": ["Investi 1000€, valgono 1100€ → rendimento 10%"],
                "category": "finance/metrics"
            },
            "rischio": {
                "description": "La possibilità che un investimento perda valore.",
                "examples": ["Azioni = alto rischio, obbligazioni statali = basso rischio"],
                "category": "finance/concepts"
            },
            "obbligazione": {
                "description": "Titolo di debito. L'emittente si impegna a restituire il capitale + interessi.",
                "examples": ["BOT, BTP, corporate bond"],
                "category": "finance/instruments"
            },
            "azione": {
                "description": "Partecipazione in una società. Dà diritto a dividendi e plusvalenze.",
                "examples": ["Azione Apple, azione Enel"],
                "category": "finance/instruments"
            },
            "fondi_comuni": {
                "description": "Raccolta di capitale di molti investitori, gestito da professionisti.",
                "examples": ["Fondo azionario, fondo bilanciato, ETF"],
                "category": "finance/instruments"
            },
            "etf": {
                "description": "Exchange Traded Fund. Fondo negoziato in borsa, generalmente replica un indice.",
                "examples": ["ETF S&P500, ETF MSCI World"],
                "category": "finance/instruments"
            }
        }
        
        for name, data in concepts.items():
            self.knowledge.add(
                name,
                description=data["description"],
                examples=data["examples"],
                category=data["category"]
            )
    
    def calculate(self, operation: str, **kwargs) -> FinancialResult:
        """
        Esegue un calcolo finanziario.
        
        Esempi:
        - calculate("simple_interest", principal=1000, rate=0.05, years=2)
        - calculate("compound_interest", principal=1000, rate=0.05, years=2)
        - calculate("roi", gain=1200, cost=1000)
        - calculate("mortgage_payment", principal=200000, rate=0.004, periods=360)
        """
        try:
            if operation == "simple_interest":
                p = kwargs.get("principal", 0)
                r = kwargs.get("rate", 0)
                t = kwargs.get("years", kwargs.get("time", 1))
                result = self.rules.get_rule("simple_interest").apply(p, r, t)
                return FinancialResult(
                    operation="simple_interest",
                    input_values={"principal": p, "rate": r, "years": t},
                    result=result,
                    explanation=f"Interesse semplice: {p}€ × {r*100:.1f}% × {t} anni = {result:.2f}€"
                )
            
            elif operation == "compound_interest":
                p = kwargs.get("principal", 0)
                r = kwargs.get("rate", 0)
                t = kwargs.get("years", kwargs.get("time", 1))
                result = self.rules.get_rule("compound_interest").apply(p, r, t)
                interest = result - p
                return FinancialResult(
                    operation="compound_interest",
                    input_values={"principal": p, "rate": r, "years": t},
                    result=result,
                    explanation=f"Interesse composto: {p}€ × (1 + {r*100:.1f}%)^{t} = {result:.2f}€ (interessi: {interest:.2f}€)"
                )
            
            elif operation == "roi":
                gain = kwargs.get("gain", kwargs.get("guadagno", 0))
                cost = kwargs.get("cost", kwargs.get("costo", 0))
                result = self.rules.get_rule("roi").apply(gain, cost)
                return FinancialResult(
                    operation="roi",
                    input_values={"gain": gain, "cost": cost},
                    result=result,
                    explanation=f"ROI: ({gain}€ - {cost}€) / {cost}€ × 100 = {result:.1f}%"
                )
            
            elif operation == "future_value":
                pv = kwargs.get("present_value", kwargs.get("valore_attuale", 0))
                rate = kwargs.get("rate", 0)
                periods = kwargs.get("periods", kwargs.get("periodi", 1))
                result = self.rules.get_rule("future_value").apply(pv, rate, periods)
                return FinancialResult(
                    operation="future_value",
                    input_values={"present_value": pv, "rate": rate, "periods": periods},
                    result=result,
                    explanation=f"Valore futuro: {pv}€ × (1 + {rate*100:.1f}%)^{periods} = {result:.2f}€"
                )
            
            elif operation == "mortgage_payment":
                principal = kwargs.get("principal", kwargs.get("capitale", 0))
                rate = kwargs.get("monthly_rate", kwargs.get("tasso_mensile", 0))
                periods = kwargs.get("months", kwargs.get("mesi", 360))
                result = self.rules.get_rule("mortgage_payment").apply(principal, rate, periods)
                total = result * periods
                return FinancialResult(
                    operation="mortgage_payment",
                    input_values={"principal": principal, "monthly_rate": rate, "months": periods},
                    result=result,
                    explanation=f"Rata mensile mutuo: {principal}€ su {periods} mesi al {rate*100:.2f}% = {result:.2f}€/mese (totale: {total:.2f}€)"
                )
            
            elif operation == "profit_margin":
                revenue = kwargs.get("revenue", kwargs.get("ricavi", 0))
                cost = kwargs.get("cost", kwargs.get("costi", 0))
                result = self.rules.get_rule("profit_margin").apply(revenue, cost)
                return FinancialResult(
                    operation="profit_margin",
                    input_values={"revenue": revenue, "cost": cost},
                    result=result,
                    explanation=f"Margine di profitto: ({revenue}€ - {cost}€) / {revenue}€ × 100 = {result:.1f}%"
                )
            
            elif operation == "break_even":
                fixed = kwargs.get("fixed_costs", kwargs.get("costi_fissi", 0))
                price = kwargs.get("price", kwargs.get("prezzo", 0))
                variable = kwargs.get("variable_cost", kwargs.get("costo_variabile", 0))
                result = self.rules.get_rule("break_even").apply(fixed, price, variable)
                return FinancialResult(
                    operation="break_even",
                    input_values={"fixed_costs": fixed, "price": price, "variable_cost": variable},
                    result=result,
                    explanation=f"Punto di pareggio: {fixed}€ / ({price}€ - {variable}€) = {result:.0f} unità"
                )
            
            elif operation == "risk_reward_ratio":
                gain = kwargs.get("potential_gain", kwargs.get("guadagno_potenziale", 0))
                loss = kwargs.get("potential_loss", kwargs.get("perdita_potenziale", 0))
                result = self.rules.get_rule("risk_reward_ratio").apply(gain, loss)
                verdict = "Buono" if result >= 2 else "Accettabile" if result >= 1 else "Rischioso"
                return FinancialResult(
                    operation="risk_reward_ratio",
                    input_values={"potential_gain": gain, "potential_loss": loss},
                    result=result,
                    explanation=f"Rapporto rischio/rendimento: {gain}€ / {loss}€ = {result:.2f} → {verdict}"
                )
            
            else:
                return FinancialResult(
                    operation=operation,
                    input_values=kwargs,
                    result=None,
                    explanation=f"Operazione '{operation}' non riconosciuta",
                    confidence=0.0
                )
        
        except Exception as e:
            return FinancialResult(
                operation=operation,
                input_values=kwargs,
                result=None,
                explanation=f"Errore: {str(e)}",
                confidence=0.0
            )
    
    def parse_financial_question(self, question: str) -> dict:
        """
        Analizza una domanda finanziaria.
        """
        question = question.lower().strip()
        
        if "interesse composto" in question:
            return {"operation": "compound_interest"}
        elif "interesse semplice" in question:
            return {"operation": "simple_interest"}
        elif "roi" in question or "rendimento" in question and "investimento" in question:
            return {"operation": "roi"}
        elif "rata" in question and ("mutuo" in question or "prestito" in question):
            return {"operation": "mortgage_payment"}
        elif "margine" in question and "profitto" in question:
            return {"operation": "profit_margin"}
        elif "pareggio" in question or "break" in question:
            return {"operation": "break_even"}
        elif "rischio" in question and "rendimento" in question:
            return {"operation": "risk_reward_ratio"}
        elif "valore futuro" in question:
            return {"operation": "future_value"}
        
        return {"operation": "unknown"}
