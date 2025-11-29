from abc import ABC, abstractmethod
from typing import Any, Dict

class Skill(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def perform(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform the skill based on the given context.
        Returns a dictionary with the result.
        """
        pass
