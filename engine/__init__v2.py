"""
ReasoningEngine v2 — Architettura completa ispirata a Claude Code.

Struttura:
engine/
├── core/
│   ├── __init__.py          # Motore principale
│   ├── loop.py              # Agent Loop (come query.ts)
│   ├── state.py             # State Management
│   └── context.py           # Context Management
├── tools/
│   ├── __init__.py          # Tool Registry
│   ├── base.py              # Base Tool class
│   ├── math_tool.py         # Matematica
│   ├── knowledge_tool.py    # Knowledge Graph
│   ├── reasoning_tool.py    # Ragionamento
│   ├── memory_tool.py       # Memoria
│   ├── llm_tool.py          # LLM Bridge
│   └── finance_tool.py      # Finanza
├── memory/
│   ├── __init__.py          # Memory System
│   ├── working.py           # Working Memory
│   ├── semantic.py          # Semantic Memory
│   ├── episodic.py          # Episodic Memory
│   └── procedural.py        # Procedural Memory
├── llm/
│   ├── __init__.py          # LLM Bridge
│   ├── client.py            # LLM Client
│   └── providers.py         # Provider abstraction
├── permissions/
│   ├── __init__.py          # Permission System
│   └── checker.py           # Permission checker
├── ui/
│   ├── __init__.py          # UI Layer
│   └── terminal.py          # Terminal UI
├── mcp/
│   ├── __init__.py          # MCP Integration
│   └── server.py            # MCP Server
└── persistence/
    ├── __init__.py          # Persistence Layer
    └── storage.py           # Storage backend
"""

from .core import ReasoningEngine
from .core.loop import ReasoningLoop
from .core.state import StateManager
from .core.context import ContextManager
from .tools import ToolRegistry
from .memory import MemorySystem
from .permissions import PermissionChecker
from .persistence import Storage

__version__ = "2.0.0"
__all__ = [
    "ReasoningEngine",
    "ReasoningLoop", 
    "StateManager",
    "ContextManager",
    "ToolRegistry",
    "MemorySystem",
    "PermissionChecker",
    "Storage"
]
