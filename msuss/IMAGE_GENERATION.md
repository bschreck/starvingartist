# Image Generation with Nano Banana

The Starving Artist system now uses Nano Banana (AI image generation) instead of SVG generation for visual art.

## What Changed

- **New**: `src/skills/image_gen.py` - Image generation using Nano Banana
- **Renamed**: `src/skills/visual_gen.py` → `src/skills/svg_gen.py` (inactive, preserved for reference)
- **Updated**: `main.py` now uses `ImageGenerationSkill` instead of `VisualGenerationSkill`

## How It Works

When an artist selects visual generation:
1. A prompt is built from the artist's personality, emotions, concepts, and aesthetic
2. The system requests image generation via Nano Banana
3. Images are saved to `artists/[name]/art/art_[timestamp].png`
4. The artist provides a conceptual self-critique

## Note on Critiques

Since the Python code cannot directly analyze the generated images, visual critiques are currently conceptual and based on the artist's confidence level. Future enhancements could include:
- Image analysis APIs
- User feedback on visual works
- Cross-artist visual critiques with image viewing

## SVG Generation

The original SVG generation code is preserved in `src/skills/svg_gen.py` for reference or future reactivation if needed.
