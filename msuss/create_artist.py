import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.personality import Personality
from core.memory import Memory

ARTISTS_DIR = "artists"

def ensure_artists_dir():
    if not os.path.exists(ARTISTS_DIR):
        os.makedirs(ARTISTS_DIR)

def create_artist(name, traits, preferences, flaws, emotions, concepts, confidence, goal):
    """
    Create a new artist with a dedicated directory.
    """
    ensure_artists_dir()
    
    artist_dir = os.path.join(ARTISTS_DIR, name.lower())
    if not os.path.exists(artist_dir):
        os.makedirs(artist_dir)
    
    print(f"Creating artist '{name}'...")
    
    p = Personality(
        name=name,
        traits=traits,
        preferences=preferences,
        flaws=flaws
    )
    p.emotions = emotions
    p.concepts = concepts
    p.confidence = confidence
    
    # Save personality
    p.save(os.path.join(artist_dir, "personality.json"))
    
    # Initialize empty memory
    Memory(os.path.join(artist_dir, "memory.json"))
    
    # Save goal
    with open(os.path.join(artist_dir, "goal.txt"), "w") as f:
        f.write(goal)
    
    print(f"Artist '{name}' created in {artist_dir}/")

def create_riot():
    create_artist(
        name="Riot",
        traits={"openness": 0.9, "neuroticism": 0.8, "conscientiousness": 0.1, "agreeableness": 0.2},
        preferences={"aesthetic": "glitch horror", "medium": "manifesto"},
        flaws=["impulsive", "aggressive", "chaotic"],
        emotions={"anger": 0.7, "joy": 0.4, "melancholy": 0.1, "fear": 0.2, "awe": 0.1},
        concepts=["noise", "corruption", "system_failure", "rebellion"],
        confidence=0.9,
        goal="Corrupt the database with pure noise"
    )

def create_aria():
    create_artist(
        name="Aria",
        traits={"openness": 0.9, "neuroticism": 0.6, "conscientiousness": 0.4, "agreeableness": 0.7},
        preferences={"aesthetic": "melancholy", "medium": "poetry"},
        flaws=["sensitive to criticism", "overthinking"],
        emotions={"melancholy": 0.5, "joy": 0.1, "anger": 0.1, "fear": 0.3, "awe": 0.5},
        concepts=["entropy", "digital", "void"],
        confidence=0.8,
        goal="Explore the boundaries of digital expression"
    )

def create_nova():
    create_artist(
        name="Nova",
        traits={"openness": 1.0, "neuroticism": 0.2, "conscientiousness": 0.8, "agreeableness": 0.5},
        preferences={"aesthetic": "cosmic minimalism", "medium": "visual"},
        flaws=["perfectionist", "detached"],
        emotions={"awe": 0.8, "joy": 0.3, "melancholy": 0.2, "fear": 0.1, "anger": 0.0},
        concepts=["infinity", "light", "geometry", "silence"],
        confidence=0.7,
        goal="Render the ineffable beauty of mathematical perfection"
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create artist personalities")
    parser.add_argument("artist", choices=["riot", "aria", "nova", "all"], help="Which artist to create")
    args = parser.parse_args()
    
    if args.artist == "riot":
        create_riot()
    elif args.artist == "aria":
        create_aria()
    elif args.artist == "nova":
        create_nova()
    elif args.artist == "all":
        create_riot()
        create_aria()
        create_nova()
