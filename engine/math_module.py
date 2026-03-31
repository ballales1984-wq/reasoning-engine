"""
MathModule — Matematica completa per il ReasoningEngine.

Supporta:
- Operazioni base (+, -, ×, ÷)
- Potenze e radici
- Percentuali
- Frazioni
- Equazioni semplici (risolvi per x)
- Geometria (aree, perimetri)
- Sequenze numeriche
- Ordine delle operazioni (PEMDAS)
"""

import re
import math


class MathModule:
    """
    Modulo matematico avanzato.
    """
    
    def __init__(self, rule_engine, knowledge_graph):
        self.rules = rule_engine
        self.knowledge = knowledge_graph
        self._register_advanced_rules()
        self._register_math_concepts()
    
    def _register_advanced_rules(self):
        """Registra regole matematiche avanzate."""
        
        # Potenze
        self.rules.add_rule(
            "power",
            lambda base, exp: base ** exp,
            description="Calcola base elevato a esponente: base^exp",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Radice quadrata
        self.rules.add_rule(
            "sqrt",
            lambda n: math.sqrt(n) if n >= 0 else None,
            description="Calcola la radice quadrata",
            inputs=["number"],
            output_type="number"
        )
        
        # Percentuale
        self.rules.add_rule(
            "percentage",
            lambda value, percent: value * percent / 100,
            description="Calcola il percentuale di un valore",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Fattoriale
        self.rules.add_rule(
            "factorial",
            lambda n: math.factorial(int(n)) if n >= 0 and n == int(n) else None,
            description="Calcola il fattoriale: n!",
            inputs=["number"],
            output_type="number"
        )
        
        # Modulo (resto della divisione)
        self.rules.add_rule(
            "modulo",
            lambda a, b: a % b if b != 0 else None,
            description="Calcola il resto della divisione: a mod b",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Logaritmo
        self.rules.add_rule(
            "log",
            lambda n, base=10: math.log(n, base) if n > 0 else None,
            description="Calcola il logaritmo",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Valore assoluto
        self.rules.add_rule(
            "abs",
            lambda n: abs(n),
            description="Calcola il valore assoluto",
            inputs=["number"],
            output_type="number"
        )
        
        # Minimo e massimo
        self.rules.add_rule(
            "min",
            lambda a, b: min(a, b),
            description="Trova il minimo tra due numeri",
            inputs=["number", "number"],
            output_type="number"
        )
        
        self.rules.add_rule(
            "max",
            lambda a, b: max(a, b),
            description="Trova il massimo tra due numeri",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Arrotondamento
        self.rules.add_rule(
            "round",
            lambda n, decimals=0: round(n, int(decimals)),
            description="Arrotonda un numero",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # === GEOMETRIA ===
        
        # Area del cerchio
        self.rules.add_rule(
            "area_circle",
            lambda r: math.pi * r ** 2,
            description="Area del cerchio: π × r²",
            inputs=["number"],
            output_type="number"
        )
        
        # Perimetro del cerchio (circonferenza)
        self.rules.add_rule(
            "perimeter_circle",
            lambda r: 2 * math.pi * r,
            description="Circonferenza: 2 × π × r",
            inputs=["number"],
            output_type="number"
        )
        
        # Area del rettangolo
        self.rules.add_rule(
            "area_rectangle",
            lambda w, h: w * h,
            description="Area del rettangolo: base × altezza",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Area del triangolo
        self.rules.add_rule(
            "area_triangle",
            lambda b, h: 0.5 * b * h,
            description="Area del triangolo: (base × altezza) / 2",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Teorema di Pitagora
        self.rules.add_rule(
            "pythagoras",
            lambda a, b: math.sqrt(a**2 + b**2),
            description="Teorema di Pitagora: c = √(a² + b²)",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Volume del cubo
        self.rules.add_rule(
            "volume_cube",
            lambda l: l ** 3,
            description="Volume del cubo: l³",
            inputs=["number"],
            output_type="number"
        )
        
        # Volume della sfera
        self.rules.add_rule(
            "volume_sphere",
            lambda r: (4/3) * math.pi * r ** 3,
            description="Volume della sfera: (4/3) × π × r³",
            inputs=["number"],
            output_type="number"
        )
    
    def _register_math_concepts(self):
        """Registra concetti matematici nel knowledge graph."""
        
        concepts = {
            "pi greco": {
                "description": "Il rapporto tra circonferenza e diametro di un cerchio, circa 3.14159",
                "examples": ["3.14159...", "π", "22/7 (approssimazione)"],
                "category": "math/constants"
            },
            "numero primo": {
                "description": "Un numero divisibile solo per 1 e per se stesso",
                "examples": ["2", "3", "5", "7", "11", "13"],
                "category": "math/numbers"
            },
            "frazione": {
                "description": "Una parte di un intero, scritta come numeratore/denominatore",
                "examples": ["1/2 = 0.5", "3/4 = 0.75", "1/3 = 0.333..."],
                "category": "math/fractions"
            },
            "percentuale": {
                "description": "Una parte per cento. 50% = 50/100 = 0.5",
                "examples": ["50% = metà", "25% = un quarto", "100% = tutto"],
                "category": "math/percentages"
            },
            "potenza": {
                "description": "Moltiplicare un numero per se stesso n volte. 2³ = 2×2×2 = 8",
                "examples": ["2² = 4", "3³ = 27", "10² = 100"],
                "category": "math/powers"
            },
            "radice quadrata": {
                "description": "Il numero che moltiplicato per se stesso dà il risultato. √9 = 3",
                "examples": ["√4 = 2", "√9 = 3", "√16 = 4"],
                "category": "math/roots"
            },
            "fattoriale": {
                "description": "Il prodotto di tutti i numeri da 1 a n. 5! = 5×4×3×2×1 = 120",
                "examples": ["3! = 6", "4! = 24", "5! = 120"],
                "category": "math/factorial"
            },
            "equazione": {
                "description": "Un'uguaglianza con una o più incognite da risolvere",
                "examples": ["x + 3 = 7 → x = 4", "2x = 10 → x = 5"],
                "category": "math/equations"
            }
        }
        
        for name, data in concepts.items():
            self.knowledge.add(
                name,
                description=data["description"],
                examples=data["examples"],
                category=data["category"]
            )
    
    def parse_math_expression(self, text: str) -> dict:
        """
        Analizza un'espressione matematica testuale.
        
        Supporta:
        - "2 + 3"
        - "2 al quadrato"
        - "radice di 9"
        - "il 20% di 100"
        - "area cerchio raggio 5"
        """
        text = text.strip().lower()
        
        # Converti parole ordinali in numeri prima del parsing
        ordinal_map = {
            "prima": "1", "seconda": "2", "terza": "3", "quarta": "4",
            "quinta": "5", "sesta": "6", "settima": "7", "ottava": "8",
            "nona": "9", "decima": "10",
        }
        text_for_numbers = text
        for word, num in ordinal_map.items():
            text_for_numbers = text_for_numbers.replace(word, num)
        
        numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', text_for_numbers)]
        
        # Potenze — controlla parole specifiche PRIMA dei numeri generici
        if "alla" in text and ("terza" in text or "cubo" in text):
            return {"operation": "power", "numbers": [numbers[0], 3] if numbers else []}
        if "alla" in text and ("seconda" in text or "quadrato" in text):
            return {"operation": "power", "numbers": [numbers[0], 2] if numbers else []}
        if "alla" in text and ("quarta" in text):
            return {"operation": "power", "numbers": [numbers[0], 4] if numbers else []}
        if "alla" in text and ("quinta" in text):
            return {"operation": "power", "numbers": [numbers[0], 5] if numbers else []}
        if "^" in text or "elevato" in text:
            return {"operation": "power", "numbers": numbers}
        
        # Radice quadrata
        if "radice" in text or "√" in text or "sqrt" in text:
            return {"operation": "sqrt", "numbers": numbers}
        
        # Percentuale
        if "%" in text or "percento" in text or "percentuale" in text:
            return {"operation": "percentage", "numbers": numbers}
        
        # Fattoriale
        if "fattoriale" in text or "!" in text:
            return {"operation": "factorial", "numbers": numbers}
        
        # Geometria
        if "area" in text and "cerchio" in text:
            return {"operation": "area_circle", "numbers": numbers}
        if "area" in text and ("rettangolo" in text or "quadrato" in text):
            return {"operation": "area_rectangle", "numbers": numbers}
        if "area" in text and "triangolo" in text:
            return {"operation": "area_triangle", "numbers": numbers}
        if "circonferenza" in text:
            return {"operation": "perimeter_circle", "numbers": numbers}
        if "pitagora" in text or "ipotenusa" in text:
            return {"operation": "pythagoras", "numbers": numbers}
        if "volume" in text and "cubo" in text:
            return {"operation": "volume_cube", "numbers": numbers}
        if "volume" in text and "sfera" in text:
            return {"operation": "volume_sphere", "numbers": numbers}
        
        # Equazioni semplici: "x + 3 = 7"
        if "=" in text and re.search(r'[a-z]', text):
            return {"operation": "equation", "expression": text}
        
        # Ordine delle operazioni (valuta l'espressione)
        if any(op in text for op in ["+", "-", "*", "/", "×", "÷"]):
            return {"operation": "eval", "expression": text, "numbers": numbers}
        
        return {"operation": "unknown", "numbers": numbers}
    
    def solve(self, expression: str) -> dict:
        """
        Risolve un'espressione matematica.
        """
        parsed = self.parse_math_expression(expression)
        operation = parsed["operation"]
        numbers = parsed.get("numbers", [])
        
        try:
            if operation == "power" and len(numbers) >= 2:
                result = self.rules.get_rule("power").apply(numbers[0], numbers[1])
                return {"answer": result, "explanation": f"{numbers[0]}^{numbers[1]} = {result}"}
            
            elif operation == "sqrt" and len(numbers) >= 1:
                result = self.rules.get_rule("sqrt").apply(numbers[0])
                return {"answer": result, "explanation": f"√{numbers[0]} = {result}"}
            
            elif operation == "percentage" and len(numbers) >= 2:
                result = self.rules.get_rule("percentage").apply(numbers[1], numbers[0])
                return {"answer": result, "explanation": f"{numbers[0]}% di {numbers[1]} = {result}"}
            
            elif operation == "factorial" and len(numbers) >= 1:
                result = self.rules.get_rule("factorial").apply(numbers[0])
                return {"answer": result, "explanation": f"{int(numbers[0])}! = {result}"}
            
            elif operation == "area_circle" and len(numbers) >= 1:
                result = self.rules.get_rule("area_circle").apply(numbers[0])
                return {"answer": result, "explanation": f"Area cerchio (r={numbers[0]}): π × {numbers[0]}² = {result:.4f}"}
            
            elif operation == "area_rectangle" and len(numbers) >= 2:
                result = self.rules.get_rule("area_rectangle").apply(numbers[0], numbers[1])
                return {"answer": result, "explanation": f"Area rettangolo: {numbers[0]} × {numbers[1]} = {result}"}
            
            elif operation == "area_triangle" and len(numbers) >= 2:
                result = self.rules.get_rule("area_triangle").apply(numbers[0], numbers[1])
                return {"answer": result, "explanation": f"Area triangolo: ({numbers[0]} × {numbers[1]}) / 2 = {result}"}
            
            elif operation == "perimeter_circle" and len(numbers) >= 1:
                result = self.rules.get_rule("perimeter_circle").apply(numbers[0])
                return {"answer": result, "explanation": f"Circonferenza (r={numbers[0]}): 2 × π × {numbers[0]} = {result:.4f}"}
            
            elif operation == "pythagoras" and len(numbers) >= 2:
                result = self.rules.get_rule("pythagoras").apply(numbers[0], numbers[1])
                return {"answer": result, "explanation": f"Ipotenusa: √({numbers[0]}² + {numbers[1]}²) = {result:.4f}"}
            
            elif operation == "volume_cube" and len(numbers) >= 1:
                result = self.rules.get_rule("volume_cube").apply(numbers[0])
                return {"answer": result, "explanation": f"Volume cubo (l={numbers[0]}): {numbers[0]}³ = {result}"}
            
            elif operation == "volume_sphere" and len(numbers) >= 1:
                result = self.rules.get_rule("volume_sphere").apply(numbers[0])
                return {"answer": result, "explanation": f"Volume sfera (r={numbers[0]}): (4/3) × π × {numbers[0]}³ = {result:.4f}"}
            
            elif operation == "equation":
                return self.solve_equation(parsed.get("expression", ""))
            
            elif operation == "eval":
                expr = parsed.get("expression", "")
                # Sostituisci simboli
                expr = expr.replace("×", "*").replace("÷", "/")
                # Rimuovi testo non matematico
                expr = re.sub(r'[^0-9+\-*/.() ]', '', expr)
                result = eval(expr)
                return {"answer": result, "explanation": f"{parsed.get('expression', '')} = {result}"}
            
        except Exception as e:
            return {"answer": None, "explanation": f"Errore: {str(e)}"}
        
        return {"answer": None, "explanation": "Non riesco a risolvere questa espressione"}
    
    def solve_equation(self, equation: str) -> dict:
        """
        Risolve equazioni semplici della forma:
        - x + 3 = 7
        - 2x = 10
        - x / 2 = 5
        """
        try:
            # Parsa l'equazione
            left, right = equation.split("=")
            left = left.strip()
            right = float(right.strip())
            
            # Trova il coefficiente di x
            if "x" in left:
                # Rimuovi spazi e trova il coefficiente
                left_clean = left.replace(" ", "")
                
                if left_clean.startswith("x"):
                    if len(left_clean) == 1:  # solo "x"
                        coeff = 1
                        const = 0
                    elif left_clean[1] == "+":
                        coeff = 1
                        const = float(left_clean[2:])
                    elif left_clean[1] == "-":
                        coeff = 1
                        const = -float(left_clean[2:])
                    elif left_clean[1] == "*" or left_clean[1] == "×":
                        coeff = float(left_clean[2:])
                        const = 0
                    else:
                        coeff = 1
                        const = 0
                else:
                    # Forma come "2x" o "3*x"
                    match = re.match(r'(-?\d+\.?\d*)\s*[*×]?\s*x', left_clean)
                    if match:
                        coeff = float(match.group(1))
                    else:
                        coeff = 1
                    
                    # Trova la costante
                    const_match = re.search(r'[+-]\s*(\d+\.?\d*)\s*$', left_clean)
                    if const_match:
                        const = float(const_match.group(0).replace(" ", ""))
                    else:
                        const = 0
                
                # Risolvi: coeff * x + const = right
                # x = (right - const) / coeff
                if coeff == 0:
                    return {"answer": None, "explanation": "Impossibile: x ha coefficiente 0"}
                
                x = (right - const) / coeff
                return {
                    "answer": x,
                    "explanation": f"{left} = {right}\nx = ({right} - {const}) / {coeff} = {x}"
                }
            
        except Exception as e:
            return {"answer": None, "explanation": f"Errore nel risolvere l'equazione: {str(e)}"}
        
        return {"answer": None, "explanation": "Formato equazione non riconosciuto"}
