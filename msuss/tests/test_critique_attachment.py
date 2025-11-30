import os
import sys
import unittest
import shutil
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from core.memory import Memory
from core.critique import CritiqueService

class TestCritiqueAttachment(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        self.memory_path = os.path.join(self.test_dir, "memory.json")
        self.memory = Memory(self.memory_path)
        self.critique_service = CritiqueService()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_critique_attachment(self):
        # Create 3 dummy creations
        for i in range(3):
            self.memory.add_creation(f"Creation {i}", {"prompt": f"Prompt {i}"})
        
        # Verify initial state
        self.assertEqual(len(self.memory.creations), 3)
        for creation in self.memory.creations:
            self.assertEqual(len(creation["critiques"]), 0)
        
        # Mock subject dict structure
        subject = {"memory": self.memory}
        
        # Critique the SECOND creation (index 1)
        target_idx = 1
        critique_text = "This is a critique of creation 1"
        score = 0.8
        critic_name = "CriticBot"
        
        self.critique_service.save_critique_to_memory(
            subject, 
            critic_name, 
            critique_text, 
            score, 
            creation_index=target_idx
        )
        
        # Verify critique is attached to index 1
        self.assertEqual(len(self.memory.creations[1]["critiques"]), 1)
        self.assertEqual(self.memory.creations[1]["critiques"][0]["critique"], critique_text)
        self.assertEqual(self.memory.creations[1]["critiques"][0]["critic"], critic_name)
        
        # Verify other creations have NO critiques
        self.assertEqual(len(self.memory.creations[0]["critiques"]), 0)
        self.assertEqual(len(self.memory.creations[2]["critiques"]), 0)
        
        print("\n✅ Verified: Critique attached correctly to target index 1")

if __name__ == '__main__':
    unittest.main()
