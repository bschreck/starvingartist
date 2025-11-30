import os
import sys
import random

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.artist_manager import ArtistManager
from core.critique import CritiqueService

def get_random_creation(memory):
    """Get a random creation from memory. Returns (index, creation) tuple."""
    if not memory.creations:
        return None
    
    idx = random.randrange(len(memory.creations))
    return idx, memory.creations[idx]

def artist_conversation(num_critiques=None):
    """Run a conversation between artists."""
    print("=== ARTIST COLLABORATION SESSION ===\n")
    
    manager = ArtistManager()
    critique_service = CritiqueService()
    
    # Discover all available artists
    artist_names = manager.discover_artists()
    
    if len(artist_names) < 2:
        print(f"Need at least 2 artists for collaboration! Found: {len(artist_names)}")
        print("Run 'python create_artist.py all' to create artists.")
        return
    
    # Load all artists
    artists = {}
    for name in artist_names:
        try:
            personality, memory, artist_dir = manager.load_artist(name)
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
        # Default: each artist critiques one other artist in a circle
        num_critiques = len(artists)
        
        # Shuffle artist order for variety
        artist_names = list(artists.keys())
        random.shuffle(artist_names)
        
        # Create circular critique pairs
        critique_pairs = []
        for i in range(len(artist_names)):
            critic_name = artist_names[i]
            subject_name = artist_names[(i + 1) % len(artist_names)]
            critique_pairs.append((critic_name, subject_name))
    else:
        # Custom number: generate random pairs
        critique_pairs = []
        available_critics = list(artists.keys())
        
        for _ in range(num_critiques):
            if len(available_critics) < 2:
                available_critics = list(artists.keys())
            
            critic_name = random.choice(available_critics)
            available_critics.remove(critic_name)
            
            possible_subjects = [name for name in artists.keys() if name != critic_name]
            if not possible_subjects:
                continue
            
            subject_name = random.choice(possible_subjects)
            critique_pairs.append((critic_name, subject_name))
    
    # Execute critiques
    for critic_name, subject_name in critique_pairs:
        
        critic = artists[critic_name]
        subject = artists[subject_name]
        
        # Pick random work from subject
        random_work_data = get_random_creation(subject["memory"])
        if not random_work_data:
            print(f"{critic['personality'].name} has nothing to critique from {subject['personality'].name}\n")
            continue
        
        work_idx, work = random_work_data
        
        print(f"\n{critic['personality'].name} critiques {subject['personality'].name}'s work:")
        print(f"Current state: {critic['personality'].mood.upper()}, Confidence: {critic['personality'].confidence:.2f}")
        print(f"Obsessions: {critic['personality'].concepts}\n")
        
        result = critique_service.generate_critique(
            critic["personality"],
            work.get("content", "")
        )
        
        print(f"Score: {result['score']:.2f}")
        print(f"Critique: {result['critique']}...")
        
        # Process critique result and update states
        critic_changed, subject_changed = critique_service.process_critique_result(critic, subject, result)
        
        # Save critique to subject's memory
        critique_service.save_critique_to_memory(subject, critic_name, result['critique'], result['score'], creation_index=work_idx)
        
        # Save updated personalities
        if critic_changed:
            manager.save_artist(critic_name, critic)
        if subject_changed:
            manager.save_artist(subject_name, subject)
        
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

