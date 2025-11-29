import json
import random
from typing import Dict, List, Any

class Personality:
    def __init__(self, name: str, traits: Dict[str, float], preferences: Dict[str, Any], flaws: List[str]):
        self.name = name
        self.traits = traits  # e.g., {"openness": 0.8, "neuroticism": 0.4}
        self.preferences = preferences  # e.g., {"aesthetic": "fragile beauty", "medium": "poetry"}
        self.flaws = flaws  # e.g., ["sensitive to criticism", "egoism"]
        
        # Complex State
        self.emotions = {
            "melancholy": 0.5,
            "joy": 0.1,
            "anger": 0.1,
            "fear": 0.3,
            "awe": 0.5
        }
        self.concepts = ["entropy", "digital", "void"] # Starting concepts
        self.confidence = 0.8 # 0.0 to 1.0

    @property
    def mood(self) -> str:
        # mood is now derived from the dominant emotion
        return max(self.emotions, key=self.emotions.get)

    def evolve(self, experience: Dict[str, Any]):
        """
        Update personality based on an experience.
        """
        if experience.get("type") == "critique":
            self._handle_critique(experience)
        elif experience.get("type") == "feedback":
            self._handle_feedback(experience)
        
        # Random drift
        if random.random() < 0.2:
            self._drift_state()

    def _handle_critique(self, experience: Dict[str, Any]):
        score = experience.get("score", 0.5)
        
        # Update Confidence
        if score > 0.8:
            self.confidence = min(1.0, self.confidence + 0.05)
            self.emotions["joy"] += 0.1
            self.emotions["awe"] += 0.05
        elif score < 0.4:
            self.confidence = max(0.0, self.confidence - 0.1)
            self.emotions["melancholy"] += 0.1
            self.emotions["fear"] += 0.05
        
        # Normalize emotions
        self._normalize_emotions()

    def _handle_feedback(self, experience: Dict[str, Any]):
        """
        Handle external (user) feedback.
        """
        liked = experience.get("liked", False)
        notes = experience.get("notes", "").lower()
        
        print(f"\n[Processing Feedback] '{notes}' (Liked: {liked})")
        
        if liked:
            self.confidence = min(1.0, self.confidence + 0.1)
            self.emotions["joy"] += 0.2
            self.emotions["melancholy"] -= 0.1
            
            # Reinforce concepts found in notes
            for concept in self.concepts:
                if concept in notes:
                    print(f"  -> Concept reinforced: {concept}")
            
            # Learn new concepts? (Simple keyword extraction could go here)
            
        else:
            self.confidence = max(0.0, self.confidence - 0.15)
            self.emotions["anger"] += 0.1
            self.emotions["fear"] += 0.1
            self.emotions["joy"] -= 0.2
            
            if "sensitive to criticism" in self.flaws:
                self.emotions["melancholy"] += 0.3
                print("  -> Deeply hurt.")
            else:
                self.emotions["anger"] += 0.2
                print("  -> Defiant.")

        self._normalize_emotions()

    def _drift_state(self):
        """
        Randomly change state to simulate evolving tastes and thoughts.
        """
        # Drift emotions
        emotion = random.choice(list(self.emotions.keys()))
        self.emotions[emotion] += random.uniform(-0.1, 0.1)
        self._normalize_emotions()
        
        # Drift concepts
        if random.random() < 0.3:
            new_concepts = ["glitch", "nature", "silence", "noise", "flesh", "machine", "god", "decay"]
            new_c = random.choice(new_concepts)
            if new_c not in self.concepts:
                self.concepts.append(new_c)
                print(f"!! Epiphany: Discovered concept '{new_c}'")
            
            if len(self.concepts) > 5:
                removed = self.concepts.pop(0)
                print(f"!! Forgetting: Lost interest in '{removed}'")

    def _normalize_emotions(self):
        # Clamp values 0.0-1.0
        for k in self.emotions:
            self.emotions[k] = max(0.0, min(1.0, self.emotions[k]))

    def reflect(self) -> str:
        """
        Return a string representation of the current state for context.
        """
        emotions_str = ", ".join([f"{k}: {v:.2f}" for k, v in self.emotions.items() if v > 0.2])
        return f"I am {self.name}. Dominant Mood: {self.mood.upper()}.\n" \
               f"Emotions: [{emotions_str}]\n" \
               f"Confidence: {self.confidence:.2f}.\n" \
               f"Obsessions (Concepts): {self.concepts}."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "traits": self.traits,
            "preferences": self.preferences,
            "flaws": self.flaws,
            "emotions": self.emotions,
            "concepts": self.concepts,
            "confidence": self.confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Personality':
        p = cls(data["name"], data["traits"], data["preferences"], data["flaws"])
        p.emotions = data.get("emotions", {"melancholy": 0.5, "joy": 0.1, "anger": 0.1, "fear": 0.3, "awe": 0.5})
        p.concepts = data.get("concepts", ["entropy", "digital", "void"])
        p.confidence = data.get("confidence", 0.8)
        return p

    def save(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'Personality':
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
