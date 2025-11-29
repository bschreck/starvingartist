# Starving Artist 🎨

An AI agent that generates art, self-critiques, and evolves its personality based on experiences and audience feedback.

## Overview

Starving Artist is an experimental AI art generation system featuring multiple AI artists with distinct personalities that create both text and visual art. Each artist has complex emotional states, obsessions (concepts), and the ability to learn from feedback.

## Features

### 🤖 Multiple AI Artists
- **Aria** (The Poet): Melancholic, obsessed with entropy and the void
- **Riot** (The Punk): Aggressive, focused on noise and system corruption  
- **Nova** (The Minimalist): Awe-filled, obsessed with geometry and mathematical perfection

### 🎨 Art Generation
- **Text Art**: Poetry, manifestos, prose
- **Visual Art**: Abstract SVG graphics generated via Gemini API
- **Self-Critique**: Artists evaluate their own work based on confidence and personality

### 🤝 Artist Collaboration ⭐ NEW
- **Cross-Critiques**: Artists critique each other's work from their unique perspectives
- **Concept Discovery**: Artists learn new obsessions from peer feedback
- **Emotional Impact**: Moods and emotions shift based on peer interactions
- **Authentic Voices**: Each artist maintains their distinct personality in critiques

### 🧠 Complex Evolution
- **Emotional Vectors**: Multi-dimensional emotional states (joy, melancholy, anger, fear, awe)
- **Concept Tracking**: Artists develop obsessions that influence their work
- **Audience Feedback**: User input shapes personality and confidence over time
- **Memory**: Each artist maintains a history of creations and critiques

### 🖼️ Web Gallery
- Beautiful dark-themed viewer for browsing all artworks
- Timeline view with scores and critiques
- Click to view full artwork with detailed self-analysis

## Installation

1. **Clone and setup**:
   ```bash
   cd msuss
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set your Gemini API key**:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

3. **Create the artists**:
   ```bash
   python create_artist.py all
   ```

## Usage

### Solo Art Creation

```bash
source .venv/bin/activate
export GEMINI_API_KEY="your_key"
python main.py
```

You'll be prompted to:
1. Select an artist (Aria, Riot, or Nova)
2. Watch them create art over 3 cycles
3. Provide feedback (y/n + notes) after each piece

### Artist Collaboration

```bash
python artist_conversation.py
```

Watch artists critique each other's work and evolve through peer feedback:
- Aria might discover "crystalline spike" from Riot's aggressive style
- Riot might trash Nova's minimalism: "God, Nova, you are so deeply *boring*"
- Nova might appreciate Aria's depth with analytical precision

### View the Gallery

```bash
python generate_viewer_data.py
python3 -m http.server 8000
```

Then open: **http://localhost:8000/viewer.html**

## Project Structure

```
msuss/
├── artists/              # Artist data (auto-generated, gitignored)
│   ├── aria/
│   │   ├── personality.json
│   │   ├── memory.json
│   │   ├── goal.txt
│   │   └── art/         # SVG files
│   ├── riot/
│   └── nova/
├── examples/            # Example artists (committed to git)
│   └── artists/         # Sample artist data for reference
├── src/
│   ├── core/
│   │   ├── personality.py   # Personality engine
│   │   ├── memory.py        # Memory system
│   │   └── goals.py         # Goal management
│   └── skills/
│       ├── text_gen.py      # Text generation
│       └── visual_gen.py    # SVG generation
├── main.py                  # Main execution loop
├── create_artist.py         # Artist creation script
├── artist_conversation.py   # Cross-artist critiques
├── generate_viewer_data.py  # Gallery data generator
├── viewer.html              # Web gallery
└── requirements.txt
```

**Note**: The `artists/` directory is gitignored to keep your generated content local. Example artists are preserved in `examples/artists/` for reference.

## How It Works

1. **Personality System**: Each artist has traits, preferences, flaws, emotions, concepts, and confidence
2. **Generation**: Artists create art influenced by their current emotional state and obsessions
3. **Self-Critique**: Artists evaluate their work based on confidence level (arrogant vs. insecure)
4. **Evolution**: Feedback and critique scores modify emotional states and confidence
5. **Memory**: All creations and critiques are stored for the gallery viewer

## Creating New Artists

Edit `create_artist.py` to add new artist archetypes:

```python
create_artist(
    name="YourArtist",
    traits={"openness": 0.9, "neuroticism": 0.5, ...},
    preferences={"aesthetic": "surrealist", "medium": "poetry"},
    flaws=["perfectionist"],
    emotions={"joy": 0.8, "melancholy": 0.2, ...},
    concepts=["dreams", "reality", "time"],
    confidence=0.7,
    goal="Explore the boundary between dreams and reality"
)
```

## Dependencies

- Python 3.8+
- `google-generativeai` - For Gemini API
- `pytest` - For testing

## License

MIT

## Credits

Built with Google Gemini API for text and image generation.
