"""
Tools Module — Tool Registry, come Claude Code.
"""

from dataclasses import dataclass
from typing import Optional, Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    function: Callable
    permission: str = "execute"  # read, execute, write
    parameters: dict = None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "permission": self.permission,
            "parameters": self.parameters or {}
        }


class ToolRegistry:
    """Registry dei tool, come Claude Code."""
    
    def __init__(self):
        self.tools = {}
    
    def register(self, tool: Tool):
        """Registra un tool."""
        self.tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[Tool]:
        """Ottieni un tool per nome."""
        return self.tools.get(name)
    
    def list_all(self) -> list:
        """Lista tutti i tool."""
        return [t.to_dict() for t in self.tools.values()]
    
    def execute(self, name: str, **kwargs) -> Any:
        """Esegue un tool."""
        tool = self.get(name)
        if not tool:
            return {"error": f"Tool '{name}' non trovato"}
        try:
            return tool.function(**kwargs)
        except Exception as e:
            return {"error": str(e)}
    
    def has_permission(self, name: str, required: str) -> bool:
        """Verifica permesso."""
        tool = self.get(name)
        if not tool:
            return False
        
        levels = {"read": 0, "execute": 1, "write": 2}
        return levels.get(tool.permission, 0) >= levels.get(required, 0)
