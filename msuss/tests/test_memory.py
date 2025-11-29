import pytest
import os
from src.core.memory import Memory

def test_memory_add_creation(tmp_path):
    f = tmp_path / "mem.json"
    m = Memory(str(f))
    
    m.add_creation("content", {"meta": "data"})
    assert len(m.creations) == 1
    assert m.creations[0]["content"] == "content"

def test_memory_add_critique(tmp_path):
    f = tmp_path / "mem.json"
    m = Memory(str(f))
    
    m.add_creation("content", {})
    m.add_critique(0, "good", 0.8)
    
    assert len(m.creations[0]["critiques"]) == 1
    assert m.creations[0]["critiques"][0]["score"] == 0.8

def test_persistence(tmp_path):
    f = tmp_path / "mem.json"
    m = Memory(str(f))
    m.add_creation("test", {})
    
    m2 = Memory(str(f))
    assert len(m2.creations) == 1
    assert m2.creations[0]["content"] == "test"
