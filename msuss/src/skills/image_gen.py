import os
import time
from typing import Dict, Any
from .base import Skill

class ImageGenerationSkill(Skill):
    def __init__(self):
        super().__init__("Image Generation")
        # Initialize Gemini client
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            from google import genai
            self.client = genai.Client(api_key=api_key)
            self.model_name = "gemini-3-pro-image-preview"
        else:
            self.client = None
            print("Warning: GEMINI_API_KEY not found. Image generation will fail.")
    
    def perform(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate images using Gemini Imagen API based on personality and goals.
        """
        personality = context.get("personality")
        goal = context.get("goal")
        artist_dir = context.get("artist_dir", ".")
        
        # Create art subdirectory
        art_dir = os.path.join(artist_dir, "art")
        if not os.path.exists(art_dir):
            os.makedirs(art_dir)
        
        # Build prompt based on personality
        aesthetic = personality.preferences.get('aesthetic', 'abstract')
        dominant_emotion = personality.mood
        concepts = ', '.join(personality.concepts[:3])
        
        # Create a concise prompt for image generation
        prompt = f"Generate a piece of {aesthetic} artwork expressing {dominant_emotion}. Themes: {concepts}. Style: emotional, conceptual, expressive. Do not include the words from this prompt in the image."
        
        # Generate filename
        timestamp = int(time.time())
        filename = f"art_{timestamp}"
        filepath = os.path.join(art_dir, f"{filename}.png")
        
        if not self.client:
            return {
                "type": "image",
                "content": "[Image Generation Failed: No API key]",
                "filepath": filepath,
                "prompt_used": prompt
            }
        
        print(f"\n[Generating image with Gemini...]")
        print(f"Prompt: {prompt}")
        
        try:
            # Generate image using Gemini API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            
            # Save the generated image
            image_saved = False
            for part in response.parts:
                if part.text is not None:
                    print(f"Response text: {part.text}")
                elif part.inline_data is not None:
                    # Get the image and save it
                    image = part.as_image()
                    image.save(filepath)
                    print(f"[Image saved to: {filepath}]")
                    image_saved = True
                    break
            
            if image_saved:
                return {
                    "type": "image",
                    "content": f"[Image Created: art/{filename}.png]",
                    "filepath": filepath,
                    "prompt_used": prompt
                }
            else:
                raise Exception("No image data returned from API")
                
        except Exception as e:
            print(f"Error generating image: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            
            return {
                "type": "image",
                "content": f"[Image Generation Failed: {str(e)}]",
                "filepath": filepath,
                "prompt_used": prompt
            }
    
    def critique(self, content: str, personality: Any) -> Dict[str, Any]:
        """
        Critique visual art (images).
        Since we can't easily analyze the generated images programmatically,
        we provide a moderate conceptual critique.
        """
        # Extract a moderate score based on confidence
        base_score = 0.6 + (personality.confidence * 0.2)
        
        # Generate a brief conceptual critique
        critique_text = f"The visual composition attempts to capture the {personality.mood} state. "
        critique_text += f"The integration of {personality.concepts[0] if personality.concepts else 'core concepts'} "
        critique_text += "shows promise, though the full impact requires direct observation."
        
        return {
            "score": base_score,
            "critique": critique_text
        }


