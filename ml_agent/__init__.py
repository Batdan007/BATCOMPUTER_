"""
Machine Learning Agent - A comprehensive ML model management and orchestration system
"""

__version__ = "1.0.0"
__author__ = "ML Agent Team"

from .core import MLAgent
from .models import ModelManager
from .tasks import TaskOrchestrator
from .api import MLAgentAPI
from .config import AgentConfig

__all__ = [
    "MLAgent",
    "ModelManager", 
    "TaskOrchestrator",
    "MLAgentAPI",
    "AgentConfig"
]
