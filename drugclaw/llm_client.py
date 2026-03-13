"""
LLM client wrapper for OpenAI-compatible Navigator API
"""
import openai
from typing import List, Dict, Any, Optional
import json

class LLMClient:
    """Wrapper for OpenAI-compatible LLM API"""
    
    def __init__(self, config):
        """Initialize LLM client with configuration"""
        self.config = config
        self.client = openai.OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.base_url
        )
        self.model = config.MODEL_NAME
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate (overrides config)
            json_mode: Whether to request JSON output
            
        Returns:
            Generated text response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.config.TEMPERATURE,
            max_tokens=max_tokens or self.config.MAX_TOKENS
        )
        return response.choices[0].message.content
    
    def generate_json(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate a JSON response from the LLM
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            
        Returns:
            Parsed JSON dictionary
        """
        # Add instruction for JSON output
        messages_with_json = messages.copy()
        if messages_with_json[-1]['role'] == 'user':
            messages_with_json[-1]['content'] += (
                "\n\nProvide your response as valid JSON only, "
                "with no additional text or markdown formatting."
            )
        
        response_text = self.generate(
            messages=messages_with_json,
            temperature=temperature or 0.3  # Lower temperature for structured output
        )
        
        # Try to parse JSON, handling potential markdown formatting
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON response: {e}")
    
    def list_models(self) -> List[str]:
        """List available models"""
        response = self.client.models.list()
        return [model.id for model in response.data]
