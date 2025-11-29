import pytest
from src.core.personality import Personality

def test_personality_initialization():
    p = Personality("Test", {"openness": 0.5}, {"color": "blue"}, ["flaw1"])
    assert p.name == "Test"
    assert p.traits["openness"] == 0.5
    assert p.mood == "neutral"

def test_personality_evolution_positive():
    p = Personality("Test", {}, {}, [])
    p.mood = "neutral"
    p.energy_level = 0.5
    
    experience = {"type": "critique", "score": 0.9, "sentiment": 1}
    p.evolve(experience)
    
    assert p.mood == "ecstatic"
    assert p.energy_level > 0.5

def test_personality_evolution_negative():
    p = Personality("Test", {}, {}, ["sensitive to criticism"])
    p.mood = "neutral"
    p.energy_level = 0.5
    
    # Score < 0.3 triggers depressed mood
    experience = {"type": "critique", "score": 0.2, "sentiment": -1}
    p.evolve(experience)
    
    assert p.mood == "depressed"
    assert p.energy_level < 0.5

def test_save_load(tmp_path):
    f = tmp_path / "p.json"
    p = Personality("Test", {"t": 1}, {}, [])
    p.save(str(f))
    
    p2 = Personality.load(str(f))
    assert p2.name == p.name
    assert p2.traits == p.traits
