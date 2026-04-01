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

    def __init__(self, knowledge_graph, rule_engine):
        self.knowledge = knowledge_graph
        self.rules = rule_engine
        self._sp = None  # Lazy loading per sympy
        self._register_advanced_rules()
        self._register_math_concepts()

    def _ensure_sympy(self):
        """Carica sympy solo se richiesto."""
        if self._sp is None:
            try:
                import sympy
                self._sp = sympy
            except ImportError:
                raise ImportError("Libreria 'sympy' non trovata. Installa con: pip install sympy")

    def solve_symbolically(self, equation_str: str, variable: str = "x") -> dict:
        """Risolve un'equazione in modo simbolico utilizzando sympy."""
        self._ensure_sympy()
        try:
            # Pulisce l'equazione (es. "x^2 = 4" -> "x**2 - 4")
            if "=" in equation_str:
                left, right = equation_str.split("=")
                expr_str = f"({left}) - ({right})"
            else:
                expr_str = equation_str
            
            expr_str = expr_str.replace("^", "**")
            
            x = self._sp.Symbol(variable)
            expr = self._sp.parse_expr(expr_str)
            solutions = self._sp.solve(expr, x)
            
            # Semplificazione
            simplified = self._sp.simplify(expr)
            
            return {
                "success": True,
                "original": equation_str,
                "solutions": [str(s) for s in solutions],
                "simplified_expression": str(simplified),
                "channel": "symbolic_math"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def calculate_calculus(self, func_str: str, variable: str = "x", 
                           op: str = "diff") -> dict:
        """Calcola derivate o integrali simbolici."""
        self._ensure_sympy()
        try:
            x = self._sp.Symbol(variable)
            expr = self._sp.parse_expr(func_str.replace("^", "**"))
            
            if op == "diff":
                result = self._sp.diff(expr, x)
                desc = "derivata"
            elif op == "integrate":
                result = self._sp.integrate(expr, x)
                desc = "integrale"
            else:
                return {"success": False, "error": "Operazione non supportata"}
                
            return {
                "success": True,
                "operation": desc,
                "expression": func_str,
                "result": str(result),
                "channel": "symbolic_math"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _register_advanced_rules(self):
        """Registra regole matematiche avanzate."""

        # Potenze
        self.rules.add_rule(
            "power",
            lambda base, exp: base**exp,
            description="Calcola base elevato a esponente: base^exp",
            inputs=["number", "number"],
            output_type="number",
        )

        # Radice quadrata
        self.rules.add_rule(
            "sqrt",
            lambda n: math.sqrt(n) if n >= 0 else None,
            description="Calcola la radice quadrata",
            inputs=["number"],
            output_type="number",
        )

        # Percentuale
        self.rules.add_rule(
            "percentage",
            lambda value, percent: value * percent / 100,
            description="Calcola il percentuale di un valore",
            inputs=["number", "number"],
            output_type="number",
        )

        # Fattoriale
        self.rules.add_rule(
            "factorial",
            lambda n: math.factorial(int(n)) if n >= 0 and n == int(n) else None,
            description="Calcola il fattoriale: n!",
            inputs=["number"],
            output_type="number",
        )

        # Modulo (resto della divisione)
        self.rules.add_rule(
            "modulo",
            lambda a, b: a % b if b != 0 else None,
            description="Calcola il resto della divisione: a mod b",
            inputs=["number", "number"],
            output_type="number",
        )

        # Logaritmo
        self.rules.add_rule(
            "log",
            lambda n, base=10: math.log(n, base) if n > 0 else None,
            description="Calcola il logaritmo",
            inputs=["number", "number"],
            output_type="number",
        )

        # Valore assoluto
        self.rules.add_rule(
            "abs",
            lambda n: abs(n),
            description="Calcola il valore assoluto",
            inputs=["number"],
            output_type="number",
        )

        # Minimo e massimo
        self.rules.add_rule(
            "min",
            lambda a, b: min(a, b),
            description="Trova il minimo tra due numeri",
            inputs=["number", "number"],
            output_type="number",
        )

        self.rules.add_rule(
            "max",
            lambda a, b: max(a, b),
            description="Trova il massimo tra due numeri",
            inputs=["number", "number"],
            output_type="number",
        )

        # Arrotondamento
        self.rules.add_rule(
            "round",
            lambda n, decimals=0: round(n, int(decimals)),
            description="Arrotonda un numero",
            inputs=["number", "number"],
            output_type="number",
        )

        # === GEOMETRIA ===

        # Area del cerchio
        self.rules.add_rule(
            "area_circle",
            lambda r: math.pi * r**2,
            description="Area del cerchio: π × r²",
            inputs=["number"],
            output_type="number",
        )

        # Perimetro del cerchio (circonferenza)
        self.rules.add_rule(
            "perimeter_circle",
            lambda r: 2 * math.pi * r,
            description="Circonferenza: 2 × π × r",
            inputs=["number"],
            output_type="number",
        )

        # Area del rettangolo
        self.rules.add_rule(
            "area_rectangle",
            lambda w, h: w * h,
            description="Area del rettangolo: base × altezza",
            inputs=["number", "number"],
            output_type="number",
        )

        # Area del triangolo
        self.rules.add_rule(
            "area_triangle",
            lambda b, h: 0.5 * b * h,
            description="Area del triangolo: (base × altezza) / 2",
            inputs=["number", "number"],
            output_type="number",
        )

        # Teorema di Pitagora
        self.rules.add_rule(
            "pythagoras",
            lambda a, b: math.sqrt(a**2 + b**2),
            description="Teorema di Pitagora: c = √(a² + b²)",
            inputs=["number", "number"],
            output_type="number",
        )

        # Volume del cubo
        self.rules.add_rule(
            "volume_cube",
            lambda l: l**3,
            description="Volume del cubo: l³",
            inputs=["number"],
            output_type="number",
        )

        # Volume della sfera
        self.rules.add_rule(
            "volume_sphere",
            lambda r: (4 / 3) * math.pi * r**3,
            description="Volume della sfera: (4/3) × π × r³",
            inputs=["number"],
            output_type="number",
        )

    def _register_math_concepts(self):
        """Registra concetti matematici nel knowledge graph."""

        concepts = {
            "pi greco": {
                "description": "Il rapporto tra circonferenza e diametro di un cerchio, circa 3.14159",
                "examples": ["3.14159...", "π", "22/7 (approssimazione)"],
                "category": "math/constants",
            },
            "numero primo": {
                "description": "Un numero divisibile solo per 1 e per se stesso",
                "examples": ["2", "3", "5", "7", "11", "13"],
                "category": "math/numbers",
            },
            "frazione": {
                "description": "Una parte di un intero, scritta come numeratore/denominatore",
                "examples": ["1/2 = 0.5", "3/4 = 0.75", "1/3 = 0.333..."],
                "category": "math/fractions",
            },
            "percentuale": {
                "description": "Una parte per cento. 50% = 50/100 = 0.5",
                "examples": ["50% = metà", "25% = un quarto", "100% = tutto"],
                "category": "math/percentages",
            },
            "potenza": {
                "description": "Moltiplicare un numero per se stesso n volte. 2³ = 2×2×2 = 8",
                "examples": ["2² = 4", "3³ = 27", "10² = 100"],
                "category": "math/powers",
            },
            "radice quadrata": {
                "description": "Il numero che moltiplicato per se stesso dà il risultato. √9 = 3",
                "examples": ["√4 = 2", "√9 = 3", "√16 = 4"],
                "category": "math/roots",
            },
            "fattoriale": {
                "description": "Il prodotto di tutti i numeri da 1 a n. 5! = 5×4×3×2×1 = 120",
                "examples": ["3! = 6", "4! = 24", "5! = 120"],
                "category": "math/factorial",
            },
            "equazione": {
                "description": "Un'uguaglianza con una o più incognite da risolvere",
                "examples": ["x + 3 = 7 → x = 4", "2x = 10 → x = 5"],
                "category": "math/equations",
            },
        }

        for name, data in concepts.items():
            self.knowledge.add(
                name,
                description=data["description"],
                examples=data["examples"],
                category=data["category"],
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
            "prima": "1",
            "seconda": "2",
            "terza": "3",
            "quarta": "4",
            "quinta": "5",
            "sesta": "6",
            "settima": "7",
            "ottava": "8",
            "nona": "9",
            "decima": "10",
        }
        text_for_numbers = text
        for word, num in ordinal_map.items():
            text_for_numbers = text_for_numbers.replace(word, num)

        numbers = [float(x) for x in re.findall(r"-?\d+\.?\d*", text_for_numbers)]

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
        if "=" in text and re.search(r"[a-z]", text):
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
                return {
                    "answer": result,
                    "explanation": f"{numbers[0]}^{numbers[1]} = {result}",
                }

            elif operation == "sqrt" and len(numbers) >= 1:
                result = self.rules.get_rule("sqrt").apply(numbers[0])
                return {"answer": result, "explanation": f"√{numbers[0]} = {result}"}

            elif operation == "percentage" and len(numbers) >= 2:
                result = self.rules.get_rule("percentage").apply(numbers[1], numbers[0])
                return {
                    "answer": result,
                    "explanation": f"{numbers[0]}% di {numbers[1]} = {result}",
                }

            elif operation == "factorial" and len(numbers) >= 1:
                result = self.rules.get_rule("factorial").apply(numbers[0])
                return {
                    "answer": result,
                    "explanation": f"{int(numbers[0])}! = {result}",
                }

            elif operation == "area_circle" and len(numbers) >= 1:
                result = self.rules.get_rule("area_circle").apply(numbers[0])
                return {
                    "answer": result,
                    "explanation": f"Area cerchio (r={numbers[0]}): π × {numbers[0]}² = {result:.4f}",
                }

            elif operation == "area_rectangle" and len(numbers) >= 2:
                result = self.rules.get_rule("area_rectangle").apply(
                    numbers[0], numbers[1]
                )
                return {
                    "answer": result,
                    "explanation": f"Area rettangolo: {numbers[0]} × {numbers[1]} = {result}",
                }

            elif operation == "area_triangle" and len(numbers) >= 2:
                result = self.rules.get_rule("area_triangle").apply(
                    numbers[0], numbers[1]
                )
                return {
                    "answer": result,
                    "explanation": f"Area triangolo: ({numbers[0]} × {numbers[1]}) / 2 = {result}",
                }

            elif operation == "perimeter_circle" and len(numbers) >= 1:
                result = self.rules.get_rule("perimeter_circle").apply(numbers[0])
                return {
                    "answer": result,
                    "explanation": f"Circonferenza (r={numbers[0]}): 2 × π × {numbers[0]} = {result:.4f}",
                }

            elif operation == "pythagoras" and len(numbers) >= 2:
                result = self.rules.get_rule("pythagoras").apply(numbers[0], numbers[1])
                return {
                    "answer": result,
                    "explanation": f"Ipotenusa: √({numbers[0]}² + {numbers[1]}²) = {result:.4f}",
                }

            elif operation == "volume_cube" and len(numbers) >= 1:
                result = self.rules.get_rule("volume_cube").apply(numbers[0])
                return {
                    "answer": result,
                    "explanation": f"Volume cubo (l={numbers[0]}): {numbers[0]}³ = {result}",
                }

            elif operation == "volume_sphere" and len(numbers) >= 1:
                result = self.rules.get_rule("volume_sphere").apply(numbers[0])
                return {
                    "answer": result,
                    "explanation": f"Volume sfera (r={numbers[0]}): (4/3) × π × {numbers[0]}³ = {result:.4f}",
                }

            elif operation == "equation":
                return self.solve_equation(parsed.get("expression", ""))

            elif operation == "eval":
                expr = parsed.get("expression", "")
                # Sostituisci simboli
                expr = expr.replace("×", "*").replace("÷", "/")
                # Rimuovi testo non matematico
                expr = re.sub(r"[^0-9+\-*/.() ]", "", expr)
                result = eval(expr)
                return {
                    "answer": result,
                    "explanation": f"{parsed.get('expression', '')} = {result}",
                }

        except Exception as e:
            return {"answer": None, "explanation": f"Errore: {str(e)}"}

        return {
            "answer": None,
            "explanation": "Non riesco a risolvere questa espressione",
        }

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
                    match = re.match(r"(-?\d+\.?\d*)\s*[*×]?\s*x", left_clean)
                    if match:
                        coeff = float(match.group(1))
                    else:
                        coeff = 1

                    # Trova la costante
                    const_match = re.search(r"[+-]\s*(\d+\.?\d*)\s*$", left_clean)
                    if const_match:
                        const = float(const_match.group(0).replace(" ", ""))
                    else:
                        const = 0

                # Risolvi: coeff * x + const = right
                # x = (right - const) / coeff
                if coeff == 0:
                    return {
                        "answer": None,
                        "explanation": "Impossibile: x ha coefficiente 0",
                    }

                x = (right - const) / coeff
                return {
                    "answer": x,
                    "explanation": f"{left} = {right}\nx = ({right} - {const}) / {coeff} = {x}",
                }

        except Exception as e:
            return {
                "answer": None,
                "explanation": f"Errore nel risolvere l'equazione: {str(e)}",
            }

        return {"answer": None, "explanation": "Formato equazione non riconosciuto"}

    # ============================================================
    # CALCOLO: DERIVATE NUMERICHE E INTEGRALI
    # ============================================================

    def derivative(self, func_str: str, x: float, h: float = 1e-7) -> dict:
        """
        Calcola la derivata numerica di una funzione in un punto.

        Esempi:
            derivative("x**2", 3) → 6.0
            derivative("sin(x)", 0) → 1.0
        """
        try:
            ns = {
                "x": x,
                "math": math,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "exp": math.exp,
                "log": math.log,
                "sqrt": math.sqrt,
                "pi": math.pi,
                "e": math.e,
            }
            f = lambda val: eval(func_str, {"__builtins__": {}}, {**ns, "x": val})
            deriv = (f(x + h) - f(x - h)) / (2 * h)
            return {
                "answer": deriv,
                "explanation": f"d/dx[{func_str}] in x={x} ≈ {deriv:.6f}",
            }
        except Exception as e:
            return {"answer": None, "explanation": f"Errore derivata: {e}"}

    def integral(self, func_str: str, a: float, b: float, n: int = 10000) -> dict:
        """
        Calcola l'integrale definito (metodo dei trapezi).

        Esempi:
            integral("x**2", 0, 1) → 0.333...
            integral("sin(x)", 0, 3.14159) → 2.0
        """
        try:
            ns = {
                "x": 0,
                "math": math,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "exp": math.exp,
                "log": math.log,
                "sqrt": math.sqrt,
                "pi": math.pi,
                "e": math.e,
            }
            f = lambda val: eval(func_str, {"__builtins__": {}}, {**ns, "x": val})

            h = (b - a) / n
            total = 0.5 * (f(a) + f(b))
            for i in range(1, n):
                total += f(a + i * h)
            result = total * h

            return {
                "answer": result,
                "explanation": f"∫[{a},{b}] {func_str} dx ≈ {result:.6f} (n={n} trapezi)",
            }
        except Exception as e:
            return {"answer": None, "explanation": f"Errore integrale: {e}"}

    def limit(self, func_str: str, x: float, side: str = "both") -> dict:
        """
        Stima il limite di una funzione in un punto.

        Esempi:
            limit("sin(x)/x", 0) → 1.0
        """
        try:
            ns = {
                "x": x,
                "math": math,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "exp": math.exp,
                "log": math.log,
                "sqrt": math.sqrt,
                "pi": math.pi,
                "e": math.e,
            }
            f = lambda val: eval(func_str, {"__builtins__": {}}, {**ns, "x": val})

            h = 1e-5
            if side == "left" or side == "both":
                left_val = f(x - h)
            if side == "right" or side == "both":
                right_val = f(x + h)

            if side == "left":
                result = left_val
            elif side == "right":
                result = right_val
            else:
                result = (left_val + right_val) / 2
                if abs(left_val - right_val) > 0.01:
                    return {
                        "answer": None,
                        "explanation": f"Limite non esiste: sin={left_val:.6f}, des={right_val:.6f}",
                    }

            return {
                "answer": result,
                "explanation": f"lim(x→{x}) {func_str} ≈ {result:.6f}",
            }
        except Exception as e:
            return {"answer": None, "explanation": f"Errore limite: {e}"}

    # ============================================================
    # STATISTICHE
    # ============================================================

    def stats_mean(self, data: list) -> dict:
        """Media aritmetica."""
        if not data:
            return {"answer": None, "explanation": "Lista vuota"}
        result = sum(data) / len(data)
        return {
            "answer": result,
            "explanation": f"Media({len(data)} valori) = {result:.4f}",
        }

    def stats_median(self, data: list) -> dict:
        """Mediana."""
        sorted_d = sorted(data)
        n = len(sorted_d)
        if n == 0:
            return {"answer": None, "explanation": "Lista vuota"}
        if n % 2 == 1:
            result = sorted_d[n // 2]
        else:
            result = (sorted_d[n // 2 - 1] + sorted_d[n // 2]) / 2
        return {"answer": result, "explanation": f"Mediana({n} valori) = {result}"}

    def stats_mode(self, data: list) -> dict:
        """Moda (valore più frequente)."""
        if not data:
            return {"answer": None, "explanation": "Lista vuota"}
        freq = {}
        for v in data:
            freq[v] = freq.get(v, 0) + 1
        max_freq = max(freq.values())
        modes = [k for k, v in freq.items() if v == max_freq]
        return {
            "answer": modes[0] if len(modes) == 1 else modes,
            "explanation": f"Moda = {modes} (frequenza {max_freq})",
        }

    def stats_std(self, data: list) -> dict:
        """Deviazione standard e varianza."""
        n = len(data)
        if n < 2:
            return {"answer": None, "explanation": "Servono almeno 2 valori"}
        mean = sum(data) / n
        variance = sum((x - mean) ** 2 for x in data) / (n - 1)
        std = math.sqrt(variance)
        return {
            "answer": std,
            "explanation": f"σ = {std:.4f}, σ² = {variance:.4f} (media={mean:.4f})",
        }

    def stats_regression(self, xs: list, ys: list) -> dict:
        """Regressione lineare: y = mx + q."""
        n = len(xs)
        if n < 2 or n != len(ys):
            return {"answer": None, "explanation": "Liste non valide"}
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        ss_xy = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
        ss_xx = sum((xs[i] - mean_x) ** 2 for i in range(n))
        if ss_xx == 0:
            return {"answer": None, "explanation": "Varianza x = 0"}
        m = ss_xy / ss_xx
        q = mean_y - m * mean_x
        ss_res = sum((ys[i] - (m * xs[i] + q)) ** 2 for i in range(n))
        ss_tot = sum((ys[i] - mean_y) ** 2 for i in range(n))
        r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0
        return {
            "answer": {"slope": m, "intercept": q, "r_squared": r2},
            "explanation": f"y = {m:.4f}x + {q:.4f} (R² = {r2:.4f})",
        }

    # ============================================================
    # MATRICI
    # ============================================================

    def matrix_add(self, A: list, B: list) -> dict:
        """Somma di due matrici."""
        try:
            rows, cols = len(A), len(A[0])
            if len(B) != rows or len(B[0]) != cols:
                return {"answer": None, "explanation": "Dimensioni diverse"}
            result = [[A[i][j] + B[i][j] for j in range(cols)] for i in range(rows)]
            return {"answer": result, "explanation": f"Somma matrici {rows}x{cols}"}
        except Exception as e:
            return {"answer": None, "explanation": f"Errore: {e}"}

    def matrix_multiply(self, A: list, B: list) -> dict:
        """Moltiplicazione di due matrici."""
        try:
            rows_a, cols_a = len(A), len(A[0])
            rows_b, cols_b = len(B), len(B[0])
            if cols_a != rows_b:
                return {
                    "answer": None,
                    "explanation": f"Impossibile: {cols_a} ≠ {rows_b}",
                }
            result = [
                [sum(A[i][k] * B[k][j] for k in range(cols_a)) for j in range(cols_b)]
                for i in range(rows_a)
            ]
            return {
                "answer": result,
                "explanation": f"Prodotto {rows_a}x{cols_a} × {rows_b}x{cols_b} = {rows_a}x{cols_b}",
            }
        except Exception as e:
            return {"answer": None, "explanation": f"Errore: {e}"}

    def matrix_transpose(self, A: list) -> dict:
        """Trasposta di una matrice."""
        try:
            result = [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]
            return {
                "answer": result,
                "explanation": f"Trasposta {len(A)}x{len(A[0])} → {len(A[0])}x{len(A)}",
            }
        except Exception as e:
            return {"answer": None, "explanation": f"Errore: {e}"}

    def matrix_determinant(self, A: list) -> dict:
        """Determinante di una matrice quadrata (cofattori)."""
        try:
            n = len(A)
            if n == 1:
                return {"answer": A[0][0], "explanation": f"det = {A[0][0]}"}
            if n == 2:
                det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
                return {"answer": det, "explanation": f"det = {det}"}
            det = 0
            for j in range(n):
                minor = [[A[i][k] for k in range(n) if k != j] for i in range(1, n)]
                det += ((-1) ** j) * A[0][j] * self.matrix_determinant(minor)["answer"]
            return {"answer": det, "explanation": f"det({n}x{n}) = {det:.6f}"}
        except Exception as e:
            return {"answer": None, "explanation": f"Errore: {e}"}

    def matrix_inverse(self, A: list) -> dict:
        """Inversa di una matrice (Gauss-Jordan)."""
        try:
            n = len(A)
            aug = [A[i][:] + [1 if i == j else 0 for j in range(n)] for i in range(n)]
            for col in range(n):
                max_row = col
                for row in range(col + 1, n):
                    if abs(aug[row][col]) > abs(aug[max_row][col]):
                        max_row = row
                aug[col], aug[max_row] = aug[max_row], aug[col]
                if abs(aug[col][col]) < 1e-10:
                    return {"answer": None, "explanation": "Matrice singolare"}
                pivot = aug[col][col]
                aug[col] = [x / pivot for x in aug[col]]
                for row in range(n):
                    if row != col:
                        factor = aug[row][col]
                        aug[row] = [
                            aug[row][j] - factor * aug[col][j] for j in range(2 * n)
                        ]
            result = [row[n:] for row in aug]
            return {"answer": result, "explanation": f"Inversa {n}x{n}"}
        except Exception as e:
            return {"answer": None, "explanation": f"Errore: {e}"}

    # ============================================================
    # SEQUENZE E PROGRESSIONI
    # ============================================================

    def fibonacci(self, n: int) -> dict:
        """Calcola i primi n numeri di Fibonacci."""
        if n <= 0:
            return {"answer": [], "explanation": "n deve essere > 0"}
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[-1] + fib[-2])
        fib = fib[:n]
        return {"answer": fib, "explanation": f"Fibonacci({n}): {fib}"}

    def arithmetic_sequence(self, a1: float, d: float, n: int) -> dict:
        """Progressione aritmetica: a_k = a1 + (k-1)*d."""
        seq = [a1 + i * d for i in range(n)]
        sn = n * (2 * a1 + (n - 1) * d) / 2
        return {
            "answer": {"sequence": seq, "sum": sn},
            "explanation": f"a1={a1}, d={d}, n={n} → S_n = {sn}",
        }

    def geometric_sequence(self, a1: float, r: float, n: int) -> dict:
        """Progressione geometrica: a_k = a1 * r^(k-1)."""
        seq = [a1 * (r**i) for i in range(n)]
        if r == 1:
            sn = a1 * n
        else:
            sn = a1 * (1 - r**n) / (1 - r)
        return {
            "answer": {"sequence": seq, "sum": sn},
            "explanation": f"a1={a1}, r={r}, n={n} → S_n = {sn}",
        }

    def prime_check(self, n: int) -> dict:
        """Verifica se un numero è primo."""
        if n < 2:
            return {"answer": False, "explanation": f"{n} non è primo"}
        if n < 4:
            return {"answer": True, "explanation": f"{n} è primo"}
        if n % 2 == 0 or n % 3 == 0:
            return {"answer": False, "explanation": f"{n} non è primo"}
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return {
                    "answer": False,
                    "explanation": f"{n} non è primo (divisibile per {i})",
                }
            i += 6
        return {"answer": True, "explanation": f"{n} è primo"}

    def prime_factors(self, n: int) -> dict:
        """Fattorizzazione in numeri primi."""
        if n < 2:
            return {"answer": [], "explanation": f"{n} non fattorizzabile"}
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return {
            "answer": factors,
            "explanation": f"Fattori primi: {' × '.join(map(str, factors))}",
        }
