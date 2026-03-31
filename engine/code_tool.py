"""
CodeTool — Coding per il ReasoningEngine.

Permette all'engine di:
- Eseguire codice Python
- Analizzare codice
- Generare codice
- Debuggare errori
"""

import subprocess
import tempfile
import os
import ast
import traceback


class CodeTool:
    """Tool per coding."""
    
    def __init__(self):
        self.execution_history = []
        self.temp_dir = tempfile.mkdtemp(prefix="reasoning_engine_")
    
    def execute(self, code: str, language: str = "python", timeout: int = 30) -> dict:
        """
        Esegue codice.
        
        Supporta: Python
        """
        if language.lower() != "python":
            return {
                'success': False,
                'error': f'Linguaggio {language} non supportato. Usa Python.'
            }
        
        try:
            # Crea file temporaneo
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', 
                                            dir=self.temp_dir, delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Esegui
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Pulisci
            os.unlink(temp_file)
            
            # Registra
            self.execution_history.append({
                'code': code[:200],
                'success': result.returncode == 0
            })
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'error': result.stderr if result.stderr else None,
                    'return_code': result.returncode
                }
            else:
                return {
                    'success': False,
                    'output': result.stdout,
                    'error': result.stderr,
                    'return_code': result.returncode
                }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Timeout dopo {timeout} secondi'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze(self, code: str) -> dict:
        """
        Analizza codice Python (staticamente).
        """
        try:
            tree = ast.parse(code)
            
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(f"{node.module}.{node.names[0].name}")
            
            return {
                'success': True,
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'lines': len(code.split('\n')),
                'complexity': len(functions) + len(classes)
            }
        
        except SyntaxError as e:
            return {
                'success': False,
                'error': f'Errore di sintassi: {e}',
                'line': e.lineno
            }
    
    def generate(self, task: str, style: str = "clean") -> dict:
        """
        Genera codice basandosi su una descrizione.
        
        Genera codice Python semplice basato sul task.
        """
        task_lower = task.lower()
        
        # Pattern matching per generare codice
        if "funzione" in task_lower or "def" in task_lower:
            # Estrai nome funzione
            import re
            match = re.search(r"(?:funzione|def)\s+(\w+)", task_lower)
            func_name = match.group(1) if match else "my_function"
            
            code = f'''def {func_name}():
    """
    Funzione generata automaticamente.
    Task: {task}
    """
    # TODO: implementa la logica
    pass

if __name__ == "__main__":
    result = {func_name}()
    print(result)
'''
            return {
                'success': True,
                'code': code,
                'type': 'function'
            }
        
        elif "classe" in task_lower or "class" in task_lower:
            import re
            match = re.search(r"(?:classe|class)\s+(\w+)", task_lower)
            class_name = match.group(1) if match else "MyClass"
            
            code = f'''class {class_name}:
    """
    Classe generata automaticamente.
    Task: {task}
    """
    
    def __init__(self):
        pass
    
    def __str__(self):
        return f"{class_name} instance"

if __name__ == "__main__":
    obj = {class_name}()
    print(obj)
'''
            return {
                'success': True,
                'code': code,
                'type': 'class'
            }
        
        else:
            # Script generico
            code = f'''"""
Script generato automaticamente.
Task: {task}
"""

def main():
    # TODO: implementa la logica
    print("Task: {task}")

if __name__ == "__main__":
    main()
'''
            return {
                'success': True,
                'code': code,
                'type': 'script'
            }
    
    def debug(self, code: str, error: str) -> dict:
        """
        Analizza un errore e suggerisce fix.
        """
        suggestions = []
        
        error_lower = error.lower()
        
        if "syntaxerror" in error_lower:
            suggestions.append("Controlla parentesi, virgole e due punti")
            suggestions.append("Verifica indentazione")
        
        if "nameerror" in error_lower:
            import re
            match = re.search(r"name '(\w+)' is not defined", error)
            if match:
                var_name = match.group(1)
                suggestions.append(f"Variabile '{var_name}' non definita. Definiscila prima di usarla.")
        
        if "typeerror" in error_lower:
            suggestions.append("Controlla i tipi degli argomenti")
            suggestions.append("Verifica che le funzioni ricevano il numero corretto di argomenti")
        
        if "indexerror" in error_lower:
            suggestions.append("Indice fuori range. Verifica la lunghezza della lista.")
        
        if "keyerror" in error_lower:
            suggestions.append("Chiave non trovata nel dizionario. Usa .get() per evitare errori.")
        
        if "zerodivisionerror" in error_lower:
            suggestions.append("Divisione per zero. Aggiungi un controllo prima di dividere.")
        
        return {
            'error': error,
            'suggestions': suggestions,
            'count': len(suggestions)
        }
    
    def get_stats(self) -> dict:
        """Statistiche."""
        return {
            'executions': len(self.execution_history),
            'successes': sum(1 for e in self.execution_history if e['success']),
            'failures': sum(1 for e in self.execution_history if not e['success'])
        }
