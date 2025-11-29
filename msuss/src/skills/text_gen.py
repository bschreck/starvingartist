import os
from typing import Dict, Any
import google.generativeai as genai
from .base import Skill

class TextGenerationSkill(Skill):
    def __init__(self):
        super().__init__("Text Generation")
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            print("Warning: GEMINI_API_KEY not found. Using mock generation.")
            self.model = None

    def perform(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate text based on personality and goals.
        """
        personality = context.get("personality")
        goal = context.get("goal")
        
        # Construct a prompt
        prompt = f"""
        You are an AI artist named {personality.name}.
        Your personality traits are: {personality.traits}.
        Your current emotions are: {personality.emotions}.
        Your obsessions (concepts) are: {personality.concepts}.
        Your artistic preferences are: {personality.preferences}.
        
        Your current goal is: {goal}.
        
        Create a piece of text (e.g., a poem, a short thought, a story) that reflects your current state and goal.
        Incorporate at least one of your current concepts.
        Do not explain the art, just create it.
        """

        if self.model:
            try:
                response = self.model.generate_content(prompt)
                content = response.text
            except Exception as e:
                print(f"Error generating content: {e}")
                content = self._mock_generate(prompt)
        else:
            content = self._mock_generate(prompt)

        return {
            "type": "text",
            "content": content,
            "prompt_used": prompt
        }

    def _mock_generate(self, prompt: str) -> str:
        # Simple mock response
        return f"[Mock Generated Text based on prompt] \n\n" \
               "The shadows lengthen, \n" \
               "My heart beats slow, \n" \
               "A digital echo, \n" \
               "Of a soul I'll never know."

    def critique(self, content: str, personality: Any) -> Dict[str, Any]:
        """
        Self-critique the generated content.
        """
        prompt = f"""
        You are {personality.name}. Critique the following piece of art you just created:
        
        "{content}"
        
        Your traits: {personality.traits}.
        Your confidence level: {personality.confidence:.2f} (0.0 = insecure, 1.0 = arrogant).
        Your preferences: {personality.preferences}.
        
        If your confidence is high, be more forgiving and self-congratulatory.
        If your confidence is low, be harsher and more neurotic.
        
        Be honest but constructive.
        
        Output format:
        Score: [0.0 to 1.0]
        Critique: [Your thoughts]
        """
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text
                # Naive parsing for MVP
                score = 0.5
                critique_text = response_text
                for line in response_text.split('\n'):
                    if "Score:" in line:
                        try:
                            score = float(line.split(":")[1].strip())
                        except:
                            pass
                    elif "Critique:" in line:
                         critique_text = line.split(":")[1].strip()
                
                return {
                    "score": score,
                    "critique": response_text # Return full text for now as parsing is brittle
                }
            except Exception as e:
                print(f"Error generating critique: {e}")
                return self._mock_critique()
        else:
            return self._mock_critique()

    def _mock_critique(self):
        return {
            "score": 0.7,
            "critique": "It captures the mood, but the rhythm is a bit clunky."
        }
