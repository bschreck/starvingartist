#!/usr/bin/env python3
"""
Create artists from JSON template files.
"""
import os
import sys
import json
import argparse

# Import the shared create_artist function
from create_artist import create_artist

TEMPLATES_DIR = "artist_templates"

def create_artist_from_json(json_path):
    """Create an artist from a JSON template file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Use the shared create_artist function
    result = create_artist(
        name=data['name'],
        traits=data['traits'],
        preferences=data['preferences'],
        flaws=data['flaws'],
        emotions=data['emotions'],
        concepts=data['concepts'],
        confidence=data['confidence'],
        goal=data['goal']
    )
    
    return result is not None

def list_templates():
    """List all available artist templates."""
    if not os.path.exists(TEMPLATES_DIR):
        print(f"No templates directory found at {TEMPLATES_DIR}")
        return []
    
    templates = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.json')]
    return templates

def main():
    parser = argparse.ArgumentParser(description='Create artists from JSON templates')
    parser.add_argument('artists', nargs='*', help='Artist names to create (without .json extension). If none specified, creates all.')
    parser.add_argument('--list', action='store_true', help='List available templates')
    
    args = parser.parse_args()
    
    if args.list:
        templates = list_templates()
        if templates:
            print("Available artist templates:")
            for template in templates:
                print(f"  - {template.replace('.json', '')}")
        return
    
    templates = list_templates()
    
    if not templates:
        print("No templates found!")
        return
    
    # If specific artists requested, filter templates
    if args.artists:
        templates = [f"{name}.json" for name in args.artists if f"{name}.json" in templates]
        if not templates:
            print("No matching templates found!")
            return
    
    print(f"Creating {len(templates)} artist(s)...\n")
    
    created = 0
    for template in templates:
        template_path = os.path.join(TEMPLATES_DIR, template)
        if create_artist_from_json(template_path):
            created += 1
    
    print(f"\n✅ Created {created} new artist(s)!")

if __name__ == "__main__":
    main()
