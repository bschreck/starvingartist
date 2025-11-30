import re
from typing import Dict, Tuple, Any, List
from skills.text_gen import TextGenerationSkill
from core.personality import Personality
from core.memory import Memory

class CritiqueService:
    def __init__(self):
        self.skill = TextGenerationSkill()

    def generate_critique(self, critic_personality: Personality, artwork_content: str) -> Dict[str, Any]:
        """Generate a critique from one artist about another's work."""
        prompt = f"""
        You are an AI artist with the following characteristics:
        
        Personality traits: {critic_personality.traits}
        Current emotions: {critic_personality.emotions}
        Obsessions/concepts: {critic_personality.concepts}
        Aesthetic preference: {critic_personality.preferences.get('aesthetic')}
        Confidence level: {critic_personality.confidence:.2f}
        
        You are critiquing another artist's work:
        
        "{artwork_content[:500]}..."
        
        Provide an honest critique from YOUR unique perspective. Consider:
        - How does this work align or clash with your own aesthetic?
        - What can you learn from this approach?
        - What new concepts or emotions does this evoke in you?
        
        Be authentic to your personality traits and confidence level.
        
        Output format:
        Score: [0.0 to 1.0]
        Critique: [Your thoughts]
        New Concepts: [Any new ideas this sparked, comma-separated]
        Emotional Impact: [How this affected your emotional state]
        """
        
        try:
            response = self.skill.model.generate_content(prompt)
            text = response.text
            
            # Parse response with more robust handling
            score = 0.5
            critique = text
            new_concepts = []
            emotional_impact = {}
            
            # Parse score - handle multiple formats including newlines
            score_patterns = [
                r"Score:\s*\*\*\s*(\d+\.?\d*)",  # **Score:** 0.85
                r"\*\*Score:\*\*\s*(\d+\.?\d*)",  # **Score:** 0.85
                r"Score:\s*(\d+\.?\d*)",           # Score: 0.85
                r"Score:\s*\n\s*(\d+\.?\d*)",      # Score:\n0.85
            ]
            
            for pattern in score_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    try:
                        score = float(match.group(1))
                        break
                    except:
                        pass
            
            # Parse new concepts - handle multiple formats
            concept_patterns = [
                r"New Concepts:\s*\*\*\s*([^\n]+)",  # New Concepts: ** concepts
                r"\*\*New Concepts:\*\*\s*([^\n]+)",  # **New Concepts:** concepts
                r"New Concepts:\s*([^\n]+)",          # New Concepts: concepts
            ]
            
            for pattern in concept_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    concepts_line = match.group(1).strip()
                    # Remove markdown formatting
                    concepts_line = concepts_line.replace("**", "").strip()
                    # Skip if it's just punctuation or empty
                    if concepts_line and concepts_line not in ["", "*", "**"]:
                        new_concepts = [c.strip() for c in concepts_line.split(",") if c.strip() and c.strip() not in ["*", "**"]]
                        break
            
            # Parse emotional impact
            impact_patterns = [
                r"Emotional Impact:\s*\*\*\s*([^\n]+)",
                r"\*\*Emotional Impact:\*\*\s*([^\n]+)",
                r"Emotional Impact:\s*([^\n]+)",
            ]
            
            for pattern in impact_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    impact_line = match.group(1).strip()
                    # Look for emotion keywords
                    for emotion in ["joy", "anger", "melancholy", "fear", "awe"]:
                        if emotion in impact_line.lower():
                            emotional_impact[emotion] = 0.1
                    break
            
            return {
                "score": max(0.0, min(1.0, score)),
                "critique": critique,
                "new_concepts": new_concepts,
                "emotional_impact": emotional_impact
            }
        except Exception as e:
            print(f"Error generating cross-critique: {e}")
            return {
                "score": 0.5,
                "critique": "Unable to generate critique.",
                "new_concepts": [],
                "emotional_impact": {}
            }

    def process_critique_result(self, critic: Dict, subject: Dict, result: Dict) -> Tuple[bool, bool]:
        """
        Process a critique result and update both critic and subject states.
        Returns (critic_changed, subject_changed).
        """
        critic_changed = False
        subject_changed = False
        
        # Update critic's state based on the experience
        if result["new_concepts"]:
            print(f"\n💡 {critic['personality'].name} discovered: {result['new_concepts']}")
            for concept in result["new_concepts"]:
                if concept.lower() not in [c.lower() for c in critic["personality"].concepts]:
                    critic["personality"].concepts.append(concept.lower())
                    if len(critic["personality"].concepts) > 6:
                        removed = critic["personality"].concepts.pop(0)
                        print(f"   Forgot: {removed}")
                    critic_changed = True
        
        if result["emotional_impact"]:
            print(f"\n😶 {critic['personality'].name}'s emotional shift: {result['emotional_impact']}")
            for emotion, delta in result["emotional_impact"].items():
                if emotion in critic["personality"].emotions:
                    critic["personality"].emotions[emotion] = min(1.0, 
                        critic["personality"].emotions[emotion] + delta)
                    critic_changed = True
        
        # Update subject's state based on receiving critique
        score = result['score']
        
        # Confidence adjustment based on score
        if score >= 0.8:
            subject["personality"].confidence = min(1.0, subject["personality"].confidence + 0.05)
            subject_changed = True
            print(f"\n⬆️ {subject['personality'].name}'s confidence increased to {subject['personality'].confidence:.2f}")
        elif score <= 0.5:
            subject["personality"].confidence = max(0.0, subject["personality"].confidence - 0.05)
            subject_changed = True
            print(f"\n⬇️ {subject['personality'].name}'s confidence decreased to {subject['personality'].confidence:.2f}")
        
        # Emotional impact on subject
        if score >= 0.8:
            if "joy" in subject["personality"].emotions:
                subject["personality"].emotions["joy"] = min(1.0, subject["personality"].emotions["joy"] + 0.1)
            if "melancholy" in subject["personality"].emotions:
                subject["personality"].emotions["melancholy"] = max(0.0, subject["personality"].emotions["melancholy"] - 0.05)
            subject_changed = True
            print(f"   {subject['personality'].name} feels validated")
        elif score <= 0.5:
            if subject["personality"].traits.get("neuroticism", 0.5) > 0.6:
                if "melancholy" in subject["personality"].emotions:
                    subject["personality"].emotions["melancholy"] = min(1.0, subject["personality"].emotions["melancholy"] + 0.1)
                if "anger" in subject["personality"].emotions:
                    subject["personality"].emotions["anger"] = min(1.0, subject["personality"].emotions["anger"] + 0.05)
                subject_changed = True
                print(f"   {subject['personality'].name} feels wounded")
            else:
                if "anger" in subject["personality"].emotions:
                    subject["personality"].emotions["anger"] = min(1.0, subject["personality"].emotions["anger"] + 0.05)
                subject_changed = True
                print(f"   {subject['personality'].name} feels defensive")
        
        return critic_changed, subject_changed

    def save_critique_to_memory(self, subject: Dict, critic_name: str, critique_text: str, score: float, creation_index: int = None) -> None:
        """Save a critique to the subject's memory."""
        if subject["memory"].creations:
            # If index is provided and valid, use it
            if creation_index is not None and 0 <= creation_index < len(subject["memory"].creations):
                idx = creation_index
            else:
                # Fallback to last creation if not specified or invalid
                idx = len(subject["memory"].creations) - 1
            
            subject["memory"].add_critique(idx, critique_text, score, critic_name=critic_name)
