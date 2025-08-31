"""GitHub Automation System."""

__version__ = "2.0.0"
__author__ = "GitHub Automation"
__description__ = "Streamlined GitHub automation for DSR generation and project management"

# Core components
from .core.commit_parser import CommitParser, CommitData
from .core.api_client import APIClient  
from .core.daily_reporter import DailyReporter, TodoItem, BranchSummary
from .core.project_sync import BoardSync, TaskStatus, TaskPriority, TaskItem

# Plugin system
from .plugins import PluginManager, AutomationPlugin

__all__ = [
    # Core classes
    'CommitParser',
    'CommitData',
    'APIClient',
    'DailyReporter', 
    'TodoItem',
    'BranchSummary',
    'BoardSync',
    'TaskStatus',
    'TaskPriority', 
    'TaskItem',
    
    # Plugin system
    'PluginManager',
    'AutomationPlugin'
]
