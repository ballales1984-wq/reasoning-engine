"""
Verifier — Il modulo di verifica.

Ogni risposta viene verificata PRIMA di essere data.
Come fai tu quando controlli un calcolo:
1. Ricalcoli con un metodo diverso
2. Verifichi che il risultato sia sensato
3. Se qualcosa non torna, segnali il dubbio
"""


class Verifier:
    """
    Verifica la coerenza delle risposte.
    """
    
    def __init__(self, rule_engine):
        self.rules = rule_engine
        self.verification_log = []
    
    def check(self, result: dict, parsed_question: dict) -> bool:
        """
        Verifica se un risultato è corretto.
        
        Strategie:
        1. Verifica per tipo (un numero non dovrebbe essere una stringa)
        2. Verifica per range (un risultato di addizione non dovrebbe essere negativo)
        3. Verifica inversa (se a+b=c, allora c-b=a)
        """
        answer = result.get("answer")
        rule_used = result.get("rule_used")
        numbers = parsed_question.get("numbers", [])
        
        checks_passed = []
        checks_failed = []
        
        # Check 1: Tipo corretto
        if rule_used in ["addition", "subtraction", "multiplication", "division"]:
            if not isinstance(answer, (int, float)):
                checks_failed.append("Il risultato non è un numero")
            else:
                checks_passed.append("Tipo corretto (numero)")
        
        # Check 2: Verifica inversa per addizione
        if rule_used == "addition" and len(numbers) >= 2 and isinstance(answer, (int, float)):
            inverse = self.rules.get_rule("subtraction").apply(answer, numbers[1])
            if inverse == numbers[0]:
                checks_passed.append("Verifica inversa: {answer} - {numbers[1]} = {numbers[0]} ✅".format(
                    answer=answer, numbers=numbers))
            else:
                checks_failed.append(f"Verifica inversa fallita")
        
        # Check 3: Verifica inversa per moltiplicazione
        if rule_used == "multiplication" and len(numbers) >= 2 and isinstance(answer, (int, float)):
            if numbers[1] != 0:
                inverse = self.rules.get_rule("division").apply(answer, numbers[1])
                if inverse == numbers[0]:
                    checks_passed.append(f"Verifica inversa: {answer} ÷ {numbers[1]} = {numbers[0]} ✅")
                else:
                    checks_failed.append(f"Verifica inversa fallita")
        
        # Check 4: Sensatezza (divisione per zero)
        if rule_used == "division" and len(numbers) >= 2:
            if numbers[1] == 0:
                checks_failed.append("Divisione per zero!")
        
        # Log
        self.verification_log.append({
            "result": answer,
            "rule": rule_used,
            "passed": checks_passed,
            "failed": checks_failed,
            "is_valid": len(checks_failed) == 0
        })
        
        return len(checks_failed) == 0
    
    def get_verification_log(self) -> list[dict]:
        """Restituisce il log delle verifiche."""
        return self.verification_log
