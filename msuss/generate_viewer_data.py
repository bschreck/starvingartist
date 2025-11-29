import os
import json
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from core.memory import Memory

ARTISTS_DIR = "artists"

def generate_viewer_data():
    """
    Generate a JSON file with all artist data for the viewer.
    """
    if not os.path.exists(ARTISTS_DIR):
        print("No artists directory found!")
        return

    artists_data = {}
    
    for artist_name in os.listdir(ARTISTS_DIR):
        artist_dir = os.path.join(ARTISTS_DIR, artist_name)
        if not os.path.isdir(artist_dir):
            continue
        
        memory_path = os.path.join(artist_dir, "memory.json")
        if not os.path.exists(memory_path):
            continue
        
        memory = Memory(memory_path)
        artworks = []
        
        for creation in memory.creations:
            # Get the critique
            critique_text = ""
            score = 0.0
            if creation.get("critiques"):
                latest_critique = creation["critiques"][-1]
                critique_text = latest_critique.get("critique", "")
                score = latest_critique.get("score", 0.0)
            
            # Check if it's an SVG
            content = creation.get("content", "")
            artwork_type = "text"
            
            # If content references an SVG file, load it
            if "[SVG Created:" in content:
                # Extract filename (could be "art/art_*.svg" or "art_*.svg")
                svg_ref = content.split("[SVG Created:")[1].split("]")[0].strip()
                
                # Try art/ subdirectory first
                svg_path = os.path.join(artist_dir, svg_ref)
                if not os.path.exists(svg_path):
                    # Try root of artist directory
                    svg_filename = os.path.basename(svg_ref)
                    svg_path = os.path.join(artist_dir, svg_filename)
                
                if os.path.exists(svg_path):
                    with open(svg_path, 'r') as f:
                        content = f.read()
                    artwork_type = "image"
                else:
                    # SVG file not found, keep as text
                    content = f"[SVG file not found: {svg_ref}]"
            
            artworks.append({
                "timestamp": creation.get("timestamp", 0),
                "type": artwork_type,
                "content": content,
                "critique": critique_text,
                "score": score
            })
        
        # Sort by timestamp
        artworks.sort(key=lambda x: x["timestamp"], reverse=True)
        artists_data[artist_name] = artworks
    
    # Write to JSON
    with open("artists_data.json", "w") as f:
        json.dump(artists_data, f, indent=2)
    
    print(f"Generated viewer data for {len(artists_data)} artists")
    print(f"Total artworks: {sum(len(works) for works in artists_data.values())}")
    print("\nOpen viewer.html in your browser to view the gallery!")

if __name__ == "__main__":
    generate_viewer_data()
