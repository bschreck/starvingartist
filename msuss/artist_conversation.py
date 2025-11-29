import os
import sys
import random

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.personality import Personality
from core.memory import Memory
from skills.text_gen import TextGenerationSkill

ARTISTS_DIR = "artists"

def discover_artists():
    """Discover all available artists by scanning the artists directory."""
    if not os.path.exists(ARTISTS_DIR):
        return []
    
    artists = []
    for name in os.listdir(ARTISTS_DIR):
        artist_path = os.path.join(ARTISTS_DIR, name)
        if os.path.isdir(artist_path):
            personality_path = os.path.join(artist_path, "personality.json")
            if os.path.exists(personality_path):
                artists.append(name)
    
    return artists

def load_artist(name):
    """Load an artist's personality and memory."""
    artist_dir = os.path.join(ARTISTS_DIR, name)
    personality = Personality.load(os.path.join(artist_dir, "personality.json"))
    memory = Memory(os.path.join(artist_dir, "memory.json"))
    return personality, memory, artist_dir

def get_random_creation(memory):
    """Get a random creation from memory."""
    if not memory.creations:
        return None
    return random.choice(memory.creations)

def cross_critique(critic_personality, artwork_content):
    """Generate a critique from one artist about another's work."""
    skill = TextGenerationSkill()
    
    prompt = f"""
    You are an AI artist with the following characteristics:
    
    Personality traits: {critic_personality.traits}
    Current emotions: {critic_personality.emotions}
    Obsessions/concepts: {critic_personality.concepts}
    Aesthetic preference: {critic_personality.preferences.get('aesthetic')}
    Confidence level: {critic_personality.confidence:.2f}
    
    You are critiquing another artist's work:
    
    "{artwork_content[:500]}..."
    
    Provide an honest critique from YOUR unique perspective. Consider:
    - How does this work align or clash with your own aesthetic?
    - What can you learn from this approach?
    - What new concepts or emotions does this evoke in you?
    
    Be authentic to your personality traits and confidence level.
    
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

def artist_conversation(num_critiques=None):
    """Run a conversation between artists."""
    print("=== ARTIST COLLABORATION SESSION ===\n")
    
    # Discover all available artists
    artist_names = discover_artists()
    
    if len(artist_names) < 2:
        print(f"Need at least 2 artists for collaboration! Found: {len(artist_names)}")
        print("Run 'python create_artist.py all' to create artists.")
        return
    
    # Load all artists
    artists = {}
    for name in artist_names:
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
        print("Need at least 2 valid artists for collaboration!")
        return
    
    print(f"\n--- Cross-Critique Session ({len(artists)} artists) ---\n")
    
    # Determine number of critiques
    if num_critiques is None:
        num_critiques = len(artists)
    
    # Generate random critique pairs
    available_critics = list(artists.keys())
    
    for _ in range(num_critiques):
        if len(available_critics) < 2:
            # Reset if we've used everyone
            available_critics = list(artists.keys())
        
        # Pick random critic
        critic_name = random.choice(available_critics)
        available_critics.remove(critic_name)
        
        # Pick random subject (different from critic)
        possible_subjects = [name for name in artists.keys() if name != critic_name]
        if not possible_subjects:
            continue
        
        subject_name = random.choice(possible_subjects)
        
        critic = artists[critic_name]
        subject = artists[subject_name]
        
        # Pick random work from subject
        random_work = get_random_creation(subject["memory"])
        if not random_work:
            print(f"{critic['personality'].name} has nothing to critique from {subject['personality'].name}\n")
            continue
        
        print(f"\n{critic['personality'].name} critiques {subject['personality'].name}'s work:")
        print(f"Current state: {critic['personality'].mood.upper()}, Confidence: {critic['personality'].confidence:.2f}")
        print(f"Obsessions: {critic['personality'].concepts}\n")
        
        result = cross_critique(
            critic["personality"],
            random_work.get("content", "")
        )
        
        print(f"Score: {result['score']:.2f}")
        print(f"Critique: {result['critique'][:300]}...")
        
        # Update critic's state based on the experience
        critic_changed = False
        if result["new_concepts"]:
            print(f"\n💡 {critic['personality'].name} discovered: {result['new_concepts']}")
            for concept in result["new_concepts"]:
                if concept.lower() not in [c.lower() for c in critic["personality"].concepts]:
                    critic["personality"].concepts.append(concept.lower())
                    if len(critic["personality"].concepts) > 6:
                        removed = critic["personality"].concepts.pop(0)
                        print(f"   Forgot: {removed}")
                    critic_changed = True
        
        if result["emotional_impact"]:
            print(f"\n😶 {critic['personality'].name}'s emotional shift: {result['emotional_impact']}")
            for emotion, delta in result["emotional_impact"].items():
                if emotion in critic["personality"].emotions:
                    critic["personality"].emotions[emotion] = min(1.0, 
                        critic["personality"].emotions[emotion] + delta)
                    critic_changed = True
        
        # Update subject's state based on receiving critique
        subject_changed = False
        score = result['score']
        
        # Confidence adjustment based on score
        if score >= 0.8:
            # High praise increases confidence
            subject["personality"].confidence = min(1.0, subject["personality"].confidence + 0.05)
            subject_changed = True
            print(f"\n⬆️ {subject['personality'].name}'s confidence increased to {subject['personality'].confidence:.2f}")
        elif score <= 0.5:
            # Harsh criticism decreases confidence
            subject["personality"].confidence = max(0.0, subject["personality"].confidence - 0.05)
            subject_changed = True
            print(f"\n⬇️ {subject['personality'].name}'s confidence decreased to {subject['personality'].confidence:.2f}")
        
        # Emotional impact on subject
        if score >= 0.8:
            # Positive critique increases joy, decreases melancholy
            if "joy" in subject["personality"].emotions:
                subject["personality"].emotions["joy"] = min(1.0, subject["personality"].emotions["joy"] + 0.1)
            if "melancholy" in subject["personality"].emotions:
                subject["personality"].emotions["melancholy"] = max(0.0, subject["personality"].emotions["melancholy"] - 0.05)
            subject_changed = True
            print(f"   {subject['personality'].name} feels validated")
        elif score <= 0.5:
            # Negative critique affects emotions based on personality
            if subject["personality"].traits.get("neuroticism", 0.5) > 0.6:
                # Neurotic artists take it hard
                if "melancholy" in subject["personality"].emotions:
                    subject["personality"].emotions["melancholy"] = min(1.0, subject["personality"].emotions["melancholy"] + 0.1)
                if "anger" in subject["personality"].emotions:
                    subject["personality"].emotions["anger"] = min(1.0, subject["personality"].emotions["anger"] + 0.05)
                subject_changed = True
                print(f"   {subject['personality'].name} feels wounded")
            else:
                # Less neurotic artists are more resilient
                if "anger" in subject["personality"].emotions:
                    subject["personality"].emotions["anger"] = min(1.0, subject["personality"].emotions["anger"] + 0.05)
                subject_changed = True
                print(f"   {subject['personality'].name} feels defensive")
        
        # Save updated personalities
        if critic_changed:
            critic["personality"].save(os.path.join(critic["dir"], "personality.json"))
        if subject_changed:
            subject["personality"].save(os.path.join(subject["dir"], "personality.json"))
        
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
    import argparse
    parser = argparse.ArgumentParser(description="Artist collaboration and cross-critique")
    parser.add_argument("-n", "--num-critiques", type=int, help="Number of critiques to generate (default: number of artists)")
    args = parser.parse_args()
    
    artist_conversation(num_critiques=args.num_critiques)

