import os
import sys
import random

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.personality import Personality
from core.memory import Memory
from skills.text_gen import TextGenerationSkill

ARTISTS_DIR = "artists"

def load_artist(name):
    """Load an artist's personality and memory."""
    artist_dir = os.path.join(ARTISTS_DIR, name)
    personality = Personality.load(os.path.join(artist_dir, "personality.json"))
    memory = Memory(os.path.join(artist_dir, "memory.json"))
    return personality, memory, artist_dir

def get_latest_creation(memory):
    """Get the most recent creation from memory."""
    if not memory.creations:
        return None
    return memory.creations[-1]

def cross_critique(critic_personality, artwork_content, artist_name):
    """Generate a critique from one artist about another's work."""
    skill = TextGenerationSkill()
    
    prompt = f"""
    You are {critic_personality.name}, an AI artist.
    
    Your personality: {critic_personality.traits}
    Your emotions: {critic_personality.emotions}
    Your obsessions: {critic_personality.concepts}
    Your aesthetic: {critic_personality.preferences.get('aesthetic')}
    
    You are critiquing a work by {artist_name}:
    
    "{artwork_content[:500]}..."
    
    Provide an honest critique from YOUR perspective. Consider:
    - How does this work align or clash with your own aesthetic?
    - What can you learn from this approach?
    - What new concepts or emotions does this evoke in you?
    
    Be authentic to your personality. If you're Riot (aggressive), be harsh but insightful.
    If you're Nova (minimalist), focus on structure. If you're Aria (melancholic), explore depth.
    
    Output format:
    Score: [0.0 to 1.0]
    Critique: [Your thoughts]
    New Concepts: [Any new ideas this sparked, comma-separated]
    Emotional Impact: [How this affected your emotional state]
    """
    
    try:
        response = skill.model.generate_content(prompt)
        text = response.text
        
        # Parse response
        score = 0.5
        critique = text
        new_concepts = []
        emotional_impact = {}
        
        if "Score:" in text:
            try:
                score_line = text.split("Score:")[1].split("\n")[0].strip()
                score = float(score_line)
            except:
                pass
        
        if "New Concepts:" in text:
            try:
                concepts_line = text.split("New Concepts:")[1].split("\n")[0].strip()
                new_concepts = [c.strip() for c in concepts_line.split(",") if c.strip()]
            except:
                pass
        
        if "Emotional Impact:" in text:
            try:
                impact_line = text.split("Emotional Impact:")[1].split("\n")[0].strip()
                # Simple parsing: look for emotion keywords
                for emotion in ["joy", "anger", "melancholy", "fear", "awe"]:
                    if emotion in impact_line.lower():
                        emotional_impact[emotion] = 0.1
            except:
                pass
        
        return {
            "score": max(0.0, min(1.0, score)),
            "critique": critique,
            "new_concepts": new_concepts,
            "emotional_impact": emotional_impact
        }
    except Exception as e:
        print(f"Error generating cross-critique: {e}")
        return {
            "score": 0.5,
            "critique": "Unable to generate critique.",
            "new_concepts": [],
            "emotional_impact": {}
        }

def artist_conversation():
    """Run a conversation between artists."""
    print("=== ARTIST COLLABORATION SESSION ===\n")
    
    # Load all artists
    artists = {}
    for name in ["aria", "riot", "nova"]:
        try:
            personality, memory, artist_dir = load_artist(name)
            artists[name] = {
                "personality": personality,
                "memory": memory,
                "dir": artist_dir
            }
            print(f"Loaded {personality.name}")
        except Exception as e:
            print(f"Could not load {name}: {e}")
    
    if len(artists) < 2:
        print("Need at least 2 artists for collaboration!")
        return
    
    print("\n--- Cross-Critique Session ---\n")
    
    # Each artist critiques another's latest work
    artist_names = list(artists.keys())
    
    for i, critic_name in enumerate(artist_names):
        # Pick the next artist in rotation
        subject_name = artist_names[(i + 1) % len(artist_names)]
        
        critic = artists[critic_name]
        subject = artists[subject_name]
        
        latest_work = get_latest_creation(subject["memory"])
        if not latest_work:
            print(f"{critic['personality'].name} has nothing to critique from {subject['personality'].name}\n")
            continue
        
        print(f"\n{critic['personality'].name} critiques {subject['personality'].name}'s work:")
        print(f"Current state: {critic['personality'].mood.upper()}, Confidence: {critic['personality'].confidence:.2f}")
        print(f"Obsessions: {critic['personality'].concepts}\n")
        
        result = cross_critique(
            critic["personality"],
            latest_work.get("content", ""),
            subject["personality"].name
        )
        
        print(f"Score: {result['score']:.2f}")
        print(f"Critique: {result['critique'][:300]}...")
        
        # Update critic's state based on the experience
        if result["new_concepts"]:
            print(f"\n💡 New concepts discovered: {result['new_concepts']}")
            for concept in result["new_concepts"]:
                if concept.lower() not in [c.lower() for c in critic["personality"].concepts]:
                    critic["personality"].concepts.append(concept.lower())
                    if len(critic["personality"].concepts) > 6:
                        removed = critic["personality"].concepts.pop(0)
                        print(f"   Forgot: {removed}")
        
        if result["emotional_impact"]:
            print(f"\n😶 Emotional impact: {result['emotional_impact']}")
            for emotion, delta in result["emotional_impact"].items():
                if emotion in critic["personality"].emotions:
                    critic["personality"].emotions[emotion] = min(1.0, 
                        critic["personality"].emotions[emotion] + delta)
        
        # Save updated personality
        critic["personality"].save(os.path.join(critic["dir"], "personality.json"))
        
        print("\n" + "="*60)
    
    print("\n--- Session Complete ---")
    print("\nFinal States:")
    for name, data in artists.items():
        p = data["personality"]
        print(f"\n{p.name}:")
        print(f"  Mood: {p.mood.upper()}")
        print(f"  Confidence: {p.confidence:.2f}")
        print(f"  Concepts: {p.concepts}")

if __name__ == "__main__":
    artist_conversation()
