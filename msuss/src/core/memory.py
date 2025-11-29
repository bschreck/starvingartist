import json
import time
from typing import List, Dict, Any

class Memory:
    def __init__(self, filepath: str = "memory.json"):
        self.filepath = filepath
        self.experiences: List[Dict[str, Any]] = []
        self.creations: List[Dict[str, Any]] = []
        self._load()

    def add_experience(self, description: str, tags: List[str], sentiment: float = 0.0):
        experience = {
            "timestamp": time.time(),
            "type": "experience",
            "description": description,
            "tags": tags,
            "sentiment": sentiment
        }
        self.experiences.append(experience)
        self._save()

    def add_creation(self, content: str, metadata: Dict[str, Any]):
        creation = {
            "timestamp": time.time(),
            "type": "creation",
            "content": content,
            "metadata": metadata,
            "critiques": []
        }
        self.creations.append(creation)
        self._save()

    def add_critique(self, creation_index: int, critique: str, score: float):
        if 0 <= creation_index < len(self.creations):
            self.creations[creation_index]["critiques"].append({
                "timestamp": time.time(),
                "critique": critique,
                "score": score
            })
            self._save()

    def get_recent_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        # Combine and sort by timestamp
        all_items = self.experiences + self.creations
        all_items.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_items[:limit]

    def _save(self):
        data = {
            "experiences": self.experiences,
            "creations": self.creations
        }
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def _load(self):
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                self.experiences = data.get("experiences", [])
                self.creations = data.get("creations", [])
        except FileNotFoundError:
            pass
