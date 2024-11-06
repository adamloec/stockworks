import importlib
import pkgutil
import inspect
from typing import Dict, Type
import logging

from .agent import Agent

logger = logging.getLogger(__name__)

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, Type[Agent]] = {}
        self._load_agents()

    def _load_agents(self):
        package = importlib.import_module(__package__)
        
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(f'.{module_name}', package=__package__)
                
                for item_name, item in inspect.getmembers(module):
                    if (inspect.isclass(item) and issubclass(item, Agent) and item != Agent):
                        
                        agent_key = module_name
                        self._agents[agent_key] = item
                        
                        globals()[item_name] = item
                        
                        if '__all__' not in globals():
                            globals()['__all__'] = []
                        if item_name not in globals()['__all__']:
                            globals()['__all__'].append(item_name)
                            
                        logger.info(f"Successfully registered agent: {item_name}")
                        
            except Exception as e:
                logger.error(f"Error loading agent module {module_name}: {str(e)}")

    def get_agent(self, agent_type: str) -> Agent:
        if agent_type not in self._agents:
            available = ', '.join(self._agents.keys())
            raise ValueError(f"Unknown agent type: {agent_type}. Available agents: {available}")
        return self._agents[agent_type]()

    @property
    def available_agents(self) -> Dict[str, Type[Agent]]:
        """Get all available agents"""
        return self._agents.copy()

_registry = AgentRegistry()
get_agent = _registry.get_agent
AVAILABLE_AGENTS = _registry.available_agents

globals()['__all__'].extend(['get_agent', 'AVAILABLE_AGENTS'])