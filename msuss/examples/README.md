# Example Artists

This directory contains example artist data that is committed to the repository as reference material.

## Artist JSON Templates

The following JSON templates can be used with `create_from_json.py` to recreate the example artists:

- **aria.json** - Melancholic poet exploring digital expression
- **riot.json** - Chaotic punk artist obsessed with noise and corruption  
- **nova.json** - Minimalist perfectionist seeking mathematical beauty

To create these artists:

```bash
# From the msuss/ directory
python create_from_json.py

# Or copy templates to artist_templates/ and create from there
cp examples/*.json artist_templates/
python create_from_json.py aria riot nova
```

## Artist Directories

The `aria/`, `riot/`, and `nova/` directories contain example artist data including:
- Personality configurations
- Memory/creation history
- Generated artworks

These serve as examples of what the system produces and are preserved in git for reference.
reate new artists
3. **Compare**: See how different personalities produce different art

## Note

Your own generated artists will be stored in `msuss/artists/` (which is gitignored). These examples are preserved for reference and won't be overwritten.
