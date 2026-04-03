from groq import Groq
import os
from config.groq_key_manager import get_key_manager

# Primary model configuration (Llama 3.3 70B)
PRIMARY_MODEL = "llama-3.3-70b-versatile"

# Fallback model configuration (Mixtral)
FALLBACK_MODEL = "mixtral-8x7b-32768"

# Model temperature settings
DEFAULT_TEMPERATURE = 0.3
LOW_TEMPERATURE = 0.1

# Get key manager instance
key_manager = get_key_manager()

# Get a Groq client (will use first available key)
groq_client = key_manager.get_client()

# Model instances for agno compatibility
from agno.models.groq import Groq as GroqModel

# Get first available key for agno models
first_key = key_manager.get_next_available_key()

model = GroqModel(
    id=PRIMARY_MODEL,
    api_key=first_key
)

model2 = GroqModel(
    id=FALLBACK_MODEL,
    api_key=first_key
)
def get_groq_completion(
    messages,
    model=PRIMARY_MODEL,
    temperature=DEFAULT_TEMPERATURE,
    max_tokens=8096
):
    """
    Get completion from Groq API with automatic key rotation
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model ID (default: llama-3.3-70b-versatile)
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        
    Returns:
        Response content string
    """
    max_retries = 4  # Try all 4 keys
    
    for attempt in range(max_retries):
        try:
            # Get client with current available key
            client = key_manager.get_client()
            
            if client is None:
                raise Exception("All Groq API keys are exhausted")
            
            current_key = key_manager.keys[key_manager.current_key_index]
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        except Exception as e:
            # Get current key
            current_key = key_manager.keys[key_manager.current_key_index]
            
            # Handle error and rotate if needed
            rotated = key_manager.handle_error(e, current_key)
            
            if not rotated:
                # Try fallback model if primary fails
                if model == PRIMARY_MODEL and attempt == 0:
                    print(f"Primary model failed, trying fallback: {str(e)}")
                    return get_groq_completion(
                        messages,
                        model=FALLBACK_MODEL,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                raise
            
            # Key was rotated, continue to next attempt
            if attempt < max_retries - 1:
                print(f"Retrying with next available key...")
                continue
            else:
                raise
