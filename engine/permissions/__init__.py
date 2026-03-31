"""
Permissions System — Come Claude Code.
"""

from enum import Enum
from typing import Optional


class PermissionLevel(Enum):
    READ = "read"
    EXECUTE = "execute"
    WRITE = "write"
    ADMIN = "admin"


class PermissionChecker:
    """Verifica permessi, come Claude Code."""
    
    def __init__(self):
        self.default_level = PermissionLevel.EXECUTE
        self.tool_permissions = {}
        self.blocked_tools = set()
    
    def set_permission(self, tool_name: str, level: PermissionLevel):
        """Imposta permesso per un tool."""
        self.tool_permissions[tool_name] = level
    
    def block(self, tool_name: str):
        """Blocca un tool."""
        self.blocked_tools.add(tool_name)
    
    def check(self, tool_name: str, required: PermissionLevel) -> bool:
        """Verifica se un tool ha il permesso richiesto."""
        if tool_name in self.blocked_tools:
            return False
        
        tool_level = self.tool_permissions.get(tool_name, self.default_level)
        levels = {PermissionLevel.READ: 0, PermissionLevel.EXECUTE: 1, 
                  PermissionLevel.WRITE: 2, PermissionLevel.ADMIN: 3}
        
        return levels.get(tool_level, 0) >= levels.get(required, 0)
    
    def get_stats(self) -> dict:
        return {
            "total_tools": len(self.tool_permissions),
            "blocked_tools": len(self.blocked_tools),
            "default_level": self.default_level.value
        }
