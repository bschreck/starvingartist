import os
import json
from typing import List, Dict, Tuple, Optional
from core.personality import Personality
from core.memory import Memory

class ArtistManager:
    def __init__(self, artists_dir: str = "artists"):
        self.artists_dir = artists_dir

    def discover_artists(self) -> List[str]:
        """Discover all available artists by scanning the artists directory."""
        if not os.path.exists(self.artists_dir):
            return []
        
        artists = []
        for name in os.listdir(self.artists_dir):
            artist_path = os.path.join(self.artists_dir, name)
            if os.path.isdir(artist_path):
                personality_path = os.path.join(artist_path, "personality.json")
                if os.path.exists(personality_path):
                    artists.append(name)
        
        return artists

    def load_artist(self, name: str) -> Tuple[Personality, Memory, str]:
        """Load an artist's personality and memory."""
        artist_dir = os.path.join(self.artists_dir, name)
        if not os.path.exists(artist_dir):
            raise FileNotFoundError(f"Artist directory not found: {artist_dir}")
            
        personality = Personality.load(os.path.join(artist_dir, "personality.json"))
        memory = Memory(os.path.join(artist_dir, "memory.json"))
        return personality, memory, artist_dir

    def save_artist(self, name: str, artist_data: Dict) -> None:
        """Save an artist's personality to disk."""
        # artist_data is expected to be the dict structure used in the app
        # {"personality": p, "memory": m, "dir": d}
        # Or we can just take personality and dir directly
        if "personality" in artist_data and "dir" in artist_data:
            artist_data["personality"].save(os.path.join(artist_data["dir"], "personality.json"))
        else:
            # Fallback or error if structure doesn't match
            pass

    def get_artist_goal(self, name: str) -> str:
        """Load an artist's goal."""
        artist_dir = os.path.join(self.artists_dir, name)
        goal_path = os.path.join(artist_dir, "goal.txt")
        if os.path.exists(goal_path):
            with open(goal_path, "r") as f:
                return f.read().strip()
        return ""
