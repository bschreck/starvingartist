import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.personality import Personality
from core.memory import Memory
from core.goals import GoalManager
from skills.text_gen import TextGenerationSkill
from skills.image_gen import ImageGenerationSkill
import random

ARTISTS_DIR = "artists"

def list_artists():
    """List all available artists."""
    if not os.path.exists(ARTISTS_DIR):
        return []
    return [d for d in os.listdir(ARTISTS_DIR) if os.path.isdir(os.path.join(ARTISTS_DIR, d))]

def select_artist():
    """Prompt user to select an artist."""
    artists = list_artists()
    
    if not artists:
        print("No artists found! Please run 'python create_artist.py all' first.")
        sys.exit(1)
    
    print("\nAvailable Artists:")
    for i, artist in enumerate(artists, 1):
        print(f"  {i}. {artist.capitalize()}")
    
    while True:
        choice = input("\nSelect an artist (number or name): ").strip().lower()
        
        # Try as number
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(artists):
                return artists[idx]
        except ValueError:
            pass
        
        # Try as name
        if choice in artists:
            return choice
        
        print("Invalid selection. Try again.")

def main():
    print("Initializing Starving Artist...")

    # Select artist
    artist_name = select_artist()
    artist_dir = os.path.join(ARTISTS_DIR, artist_name)
    
    print(f"\nLoading artist: {artist_name.capitalize()}")
    
    # 1. Load Personality
    personality_path = os.path.join(artist_dir, "personality.json")
    personality = Personality.load(personality_path)
    print(f"Loaded personality: {personality.name}")

    # 2. Initialize Memory & Goals
    memory = Memory(os.path.join(artist_dir, "memory.json"))
    goals = GoalManager()
    
    # Load goal from file
    goal_path = os.path.join(artist_dir, "goal.txt")
    with open(goal_path, "r") as f:
        goal = f.read().strip()
    goals.set_current_goal(goal)

    # 3. Execution Loop
    print("\n--- Starting Creative Process ---")
    print(personality.reflect())
    print(f"Current Goal: {goals.current_goal}")

    text_skill = TextGenerationSkill()
    image_skill = ImageGenerationSkill()
    
    for i in range(3):
        print(f"\n\n=== Generation Cycle {i+1} ===")
        
        # Randomly select skill
        if random.random() < 0.7:
            skill = text_skill
            print("Selected Skill: Text Generation")
        else:
            skill = image_skill
            print("Selected Skill: Image Generation")
        
        # 4. Generate
        context = {
            "personality": personality,
            "goal": goals.current_goal,
            "memory": memory,
            "artist_dir": artist_dir
        }
        
        result = skill.perform(context)
        print("\n[Generated Art]")
        print(result["content"])

        # 5. Self-Critique
        print("\n[Self-Critique]")
        critique = skill.critique(result["content"], personality)
        print(f"Critique: {critique['critique']}")
        print(f"Score: {critique['score']}")

        # 6. Update Memory & Personality (Internal)
        memory.add_creation(result["content"], {"prompt": result["prompt_used"]})
        memory.add_critique(len(memory.creations) - 1, critique["critique"], critique["score"])
        
        experience = {
            "type": "critique",
            "score": critique["score"],
            "sentiment": 1 if critique["score"] > 0.5 else -1
        }
        personality.evolve(experience)
        
        # 7. External Feedback (Audience)
        print("\n[Audience Interaction]")
        user_input = input("Did you like this? (y/n) [Enter to skip]: ").strip().lower()
        if user_input in ['y', 'n']:
            notes = input("Any notes? ").strip()
            liked = (user_input == 'y')
            
            feedback_experience = {
                "type": "feedback",
                "liked": liked,
                "notes": notes
            }
            personality.evolve(feedback_experience)
            memory.add_experience(f"User feedback: {notes}", ["feedback"], 1 if liked else -1)

        personality.save(personality_path)
        
        print(f"\n[State Update]")
        print(f"New Mood: {personality.mood}")
        print(f"Confidence: {personality.confidence:.2f}")
        # print(f"Energy: {personality.energy_level:.2f}")
    
    print("\n--- Session Complete ---")

if __name__ == "__main__":
    main()
