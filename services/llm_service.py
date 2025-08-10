import json
import time
import os
from typing import Dict, Any, Optional
import httpx
from utils import app_logger


class LLMService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL",
                                         "http://localhost:11434")
    
    async def generate_meal_plan(self, prompt: str,
                                 config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meal plan using specified LLM provider"""
        provider = config.get("llm_provider", "openai").lower()
        
        start_time = time.time()
        
        try:
            if provider == "openai":
                result = await self._generate_with_openai(prompt, config)
            elif provider == "anthropic":
                result = await self._generate_with_anthropic(prompt, config)
            elif provider == "ollama":
                result = await self._generate_with_ollama(prompt, config)
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
            
            generation_time = time.time() - start_time
            
            return {
                "success": True,
                "data": result,
                "generation_time": generation_time,
                "provider": provider,
                "model": config.get("model_name", "unknown")
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error in generate_meal_plan with {provider}: {e}")
            return {
                "success": False,
                "error": str(e),
                "generation_time": time.time() - start_time,
                "provider": provider
            }
    
    async def _generate_with_openai(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meal plan using OpenAI GPT"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config.get("model_name", "gpt-4"),
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional nutritionist and meal planning expert. Always respond with valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 4000),
            "response_format": {"type": "json_object"}
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                app_logger.exceptionlogs(f"Failed to parse OpenAI JSON response: {e}")
                raise Exception("Invalid JSON response from OpenAI")
    
    async def _generate_with_anthropic(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meal plan using Anthropic Claude"""
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        headers = {
            "x-api-key": self.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": config.get("model_name", "claude-3-sonnet-20240229"),
            "max_tokens": config.get("max_tokens", 4000),
            "temperature": config.get("temperature", 0.7),
            "messages": [
                {
                    "role": "user",
                    "content": f"You are a professional nutritionist. Respond only with valid JSON format.\n\n{prompt}"
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
            
            result = response.json()
            content = result["content"][0]["text"]
            
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                app_logger.exceptionlogs(f"Failed to parse Anthropic JSON response: {e}")
                raise Exception("Invalid JSON response from Anthropic")
    
    async def _generate_with_ollama(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meal plan using Ollama (local LLM)"""
        payload = {
            "model": config.get("model_name", "llama3.1:70b"),
            "prompt": f"You are a professional nutritionist. Respond only with valid JSON format.\n\n{prompt}",
            "stream": False,
            "options": {
                "temperature": config.get("temperature", 0.7),
                "num_predict": config.get("max_tokens", 4000)
            }
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            result = response.json()
            content = result["response"]
            
            # Try to extract JSON from the response
            try:
                # Sometimes Ollama includes extra text, try to find JSON
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_content = content[start_idx:end_idx]
                    return json.loads(json_content)
                else:
                    return json.loads(content)
            except json.JSONDecodeError as e:
                app_logger.exceptionlogs(f"Failed to parse Ollama JSON response: {e}")
                raise Exception("Invalid JSON response from Ollama")
    
    def create_meal_plan_prompt(self, user_data: Dict[str, Any], nutrition_targets: Dict[str, Any], 
                               activity_data: Optional[Dict[str, Any]] = None) -> str:
        """Create a comprehensive prompt for meal plan generation"""
        
        prompt = f"""
Generate a complete daily meal plan in JSON format for a user with the following profile:

USER PROFILE:
- Gender: {user_data.get('gender', 'Not specified')}
- Food Preference: {user_data.get('food_preference_type', 'omnivore')}
- Cooking Skill Level: {user_data.get('cooking_skill_level', 3)}/5
- Max Prep Time: {user_data.get('max_prep_time_minutes', 45)} minutes
- Preferred Meal Frequency: {user_data.get('preferred_meal_frequency', 3)} meals
- Snack Preference: {user_data.get('snack_preference', True)}

DIETARY RESTRICTIONS:
- Allergies: {user_data.get('allergies', [])}
- Dietary Restrictions: {user_data.get('dietary_restrictions', [])}
- Disliked Foods: {user_data.get('disliked_foods', [])}
- Preferred Cuisines: {user_data.get('preferred_cuisines', [])}

NUTRITION TARGETS:
- Target Calories: {nutrition_targets['calories']} kcal
- Protein: {nutrition_targets['protein_g']}g ({nutrition_targets['protein_percentage']}%)
- Carbohydrates: {nutrition_targets['carbs_g']}g ({nutrition_targets['carbs_percentage']}%)
- Fat: {nutrition_targets['fat_g']}g ({nutrition_targets['fat_percentage']}%)
- Fiber: {nutrition_targets['fiber_g']}g

ACTIVITY LEVEL:
{f"- Today's Activity: {activity_data.get('activity_summary', 'No specific workout data')}" if activity_data else "- No specific workout data for today"}
{f"- Calories Burned: {activity_data.get('calories_burned', 0)} kcal" if activity_data else ""}

REQUIREMENTS:
1. Create exactly 5 meals: breakfast, lunch, dinner, snack_1 (mid-morning), snack_2 (evening)
2. Each meal must include complete nutritional breakdown
3. Provide detailed ingredients list and cooking instructions
4. Consider prep time constraints and cooking skill level
5. Respect all dietary restrictions and preferences
6. Ensure total daily nutrition meets targets (±50 calories acceptable)
7. Include variety in cuisines and cooking methods
8. Make snacks healthy and satisfying

RESPONSE FORMAT (JSON):
{{
  "breakfast": {{
    "meal_name": "Meal name",
    "description": "Brief description",
    "calories": 400,
    "protein_g": 25,
    "carbs_g": 45,
    "fat_g": 12,
    "fiber_g": 8,
    "sodium_mg": 300,
    "sugar_g": 5,
    "prep_time_minutes": 15,
    "cooking_time_minutes": 10,
    "difficulty_level": 2,
    "cuisine_type": "American",
    "ingredients": ["ingredient 1", "ingredient 2"],
    "instructions": ["step 1", "step 2"],
    "is_vegetarian": false,
    "is_vegan": false,
    "is_gluten_free": false,
    "is_dairy_free": false
  }},
  "lunch": {{ ... }},
  "dinner": {{ ... }},
  "snack_1": {{ ... }},
  "snack_2": {{ ... }},
  "daily_summary": {{
    "total_calories": 2000,
    "total_protein_g": 150,
    "total_carbs_g": 200,
    "total_fat_g": 67,
    "total_fiber_g": 35,
    "meets_targets": true,
    "variety_score": 8,
    "prep_time_total": 90
  }}
}}

Generate a nutritious, delicious, and practical meal plan that perfectly matches the user's profile and goals.
"""
        
        return prompt.strip()
