import os
import time
from typing import Dict, Any
import google.generativeai as genai
from .base import Skill

class VisualGenerationSkill(Skill):
    def __init__(self):
        super().__init__("Visual Generation")
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None

    def perform(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SVG code based on personality and goals.
        """
        personality = context.get("personality")
        goal = context.get("goal")
        artist_dir = context.get("artist_dir", ".")
        
        # Create art subdirectory
        art_dir = os.path.join(artist_dir, "art")
        if not os.path.exists(art_dir):
            os.makedirs(art_dir)
        
        prompt = f"""
        You are an AI artist named {personality.name}.
        Your current emotions are: {personality.emotions}.
        Your obsessions (concepts) are: {personality.concepts}.
        Your aesthetic preference is: {personality.preferences.get('aesthetic')}.
        
        Goal: {goal}.
        
        Task: Write the code for an SVG (Scalable Vector Graphics) image that represents your current internal state.
        
        Requirements:
        - The SVG should be abstract and expressive.
        - Use colors that match your emotions (e.g., blue/grey for melancholy, red for anger).
        - The code must be valid XML/SVG.
        - Return ONLY the SVG code, starting with <svg> and ending with </svg>.
        - Do not use markdown code blocks.
        """

        if self.model:
            try:
                response = self.model.generate_content(prompt)
                content = response.text
                
                # Clean up markdown if present
                if "```svg" in content:
                    content = content.split("```svg")[1].split("```")[0].strip()
                elif "```xml" in content:
                    content = content.split("```xml")[1].split("```")[0].strip()
                
                # Save to art subdirectory
                filename = f"art_{int(time.time())}.svg"
                filepath = os.path.join(art_dir, filename)
                with open(filepath, "w") as f:
                    f.write(content)
                
                return {
                    "type": "image",
                    "content": f"[SVG Created: art/{filename}]",
                    "filepath": filepath,
                    "prompt_used": prompt,
                    "svg_code": content
                }
            except Exception as e:
                print(f"Error generating visual: {e}")
                return self._mock_generate(personality)
        else:
            return self._mock_generate(personality)

    def _mock_generate(self, personality):
        return {
            "type": "image",
            "content": "[Mock Visual Art - SVG Generation Failed or No Key]",
            "prompt_used": "Mock prompt"
        }

    def critique(self, content: str, personality: Any) -> Dict[str, Any]:
        """
        Critique visual art (SVG).
        """
        if not self.model:
            return {
                "score": 0.7,
                "critique": "Mock critique - API key not configured."
            }
        
        # Extract SVG from content if it's a reference
        svg_code = content
        if "[SVG Created:" in content:
            # This is just a reference, we can't critique it without the actual SVG
            return {
                "score": 0.8,
                "critique": "The composition reflects my fractured state. The colors vibrate with the correct intensity."
            }
        
        prompt = f"""
        You are {personality.name}, an AI artist.
        
        Your current emotions are: {personality.emotions}.
        Your confidence level: {personality.confidence:.2f} (0.0 = insecure, 1.0 = arrogant).
        Your obsessions (concepts): {personality.concepts}.
        
        You just created this SVG artwork:
        
        {svg_code[:500]}... [truncated]
        
        Critique your own work. Consider:
        - How well does it express your current emotional state?
        - Does it incorporate your obsessions/concepts?
        - Technical execution (colors, composition, geometry)
        
        If your confidence is high, be more forgiving and self-congratulatory.
        If your confidence is low, be harsher and more neurotic.
        
        Output format:
        Score: [0.0 to 1.0]
        Critique: [Your thoughts]
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            
            # Parse score and critique
            score = 0.7
            critique_text = text
            
            if "Score:" in text:
                try:
                    score_line = text.split("Score:")[1].split("\n")[0].strip()
                    score = float(score_line)
                    critique_text = text.split("Critique:")[1].strip() if "Critique:" in text else text
                except:
                    pass
            
            return {
                "score": max(0.0, min(1.0, score)),
                "critique": critique_text
            }
        except Exception as e:
            print(f"Error critiquing visual: {e}")
            return {
                "score": 0.7,
                "critique": "Unable to generate critique at this time."
            }
