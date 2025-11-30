from flask import Flask, request, jsonify, send_from_directory
import os
import sys
import json
import threading
import random

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.artist_manager import ArtistManager
from core.critique import CritiqueService
from skills.text_gen import TextGenerationSkill
from skills.image_gen import ImageGenerationSkill
from skills.svg_gen import VisualGenerationSkill
import generate_viewer_data

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Initialize services
artist_manager = ArtistManager()
critique_service = CritiqueService()

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'viewer.html')

@app.route('/<path:path>')
def serve_static(path):
    full_path = os.path.join(BASE_DIR, path)
    print(f"DEBUG: Serving static file. Request path: {path}")
    print(f"DEBUG: Full resolved path: {full_path}")
    print(f"DEBUG: File exists? {os.path.exists(full_path)}")
    return send_from_directory(BASE_DIR, path)

@app.route('/api/artists')
def get_artists():
    # Regenerate data to ensure it's fresh
    generate_viewer_data.generate_data()
    with open('artists_data.json', 'r') as f:
        return jsonify(json.load(f))

@app.route('/api/generate', methods=['POST'])
def generate_art():
    data = request.json
    artist_name = data.get('artist')
    
    if not artist_name:
        return jsonify({"error": "Artist name required"}), 400
        
    try:
        # Load artist
        personality, memory, artist_dir = artist_manager.load_artist(artist_name)
        
        # Load goal
        goal = artist_manager.get_artist_goal(artist_name)
            
        # Context for generation
        context = {
            "personality": personality,
            "goal": goal,
            "memory": memory,
            "artist_dir": artist_dir
        }
        
        skill_type = random.choice(["text", "image", "svg"])
        
        if skill_type == "text":
            skill = TextGenerationSkill()
        elif skill_type == "image":
            skill = ImageGenerationSkill()
        else:
            skill = VisualGenerationSkill()
            
        print(f"Generating {skill_type} for {artist_name}...")
        result = skill.perform(context)
        
        # Self-critique
        critique = skill.critique(result["content"], personality)
        
        # Update memory
        memory.add_creation(result["content"], {"prompt": result["prompt_used"]})
        memory.add_critique(len(memory.creations) - 1, critique["critique"], critique["score"], critic_name=artist_name)
        
        # Update personality
        experience = {
            "type": "critique",
            "score": critique["score"],
            "sentiment": 1 if critique["score"] > 0.5 else -1
        }
        personality.evolve(experience)
        artist_manager.save_artist(artist_name, {"personality": personality, "dir": artist_dir})
        
        return jsonify({
            "success": True, 
            "type": skill_type,
            "message": f"Generated {skill_type} art"
        })
        
    except Exception as e:
        print(f"Error generating art: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/critique', methods=['POST'])
def run_critique():
    data = request.json
    critic_name = data.get('critic')
    subject_name = data.get('subject')
    
    if not critic_name or not subject_name:
        return jsonify({"error": "Critic and subject names required"}), 400
        
    try:
        # Load artists
        critic_p, critic_m, critic_dir = artist_manager.load_artist(critic_name)
        subject_p, subject_m, subject_dir = artist_manager.load_artist(subject_name)
        
        critic = {"personality": critic_p, "memory": critic_m, "dir": critic_dir}
        subject = {"personality": subject_p, "memory": subject_m, "dir": subject_dir}
        
        # Get random work
        if not subject["memory"].creations:
             return jsonify({"error": "Subject has no work to critique"}), 404
             
        work_idx = random.randrange(len(subject["memory"].creations))
        random_work = subject["memory"].creations[work_idx]
            
        # Perform critique
        result = critique_service.generate_critique(critic["personality"], random_work.get("content", ""))
        
        # Process results
        critic_changed, subject_changed = critique_service.process_critique_result(critic, subject, result)
        
        # Save critique to memory
        critique_service.save_critique_to_memory(subject, critic_name, result['critique'], result['score'], creation_index=work_idx)
        
        # Save states
        if critic_changed:
            artist_manager.save_artist(critic_name, critic)
        if subject_changed:
            artist_manager.save_artist(subject_name, subject)
            
        return jsonify({
            "success": True,
            "score": result['score'],
            "critique": result['critique'],
            "critic_mood": critic["personality"].mood,
            "subject_confidence": subject["personality"].confidence
        })
        
    except Exception as e:
        print(f"Error running critique: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Starving Artist Server on port 8000...")
    app.run(port=8000, debug=False)
