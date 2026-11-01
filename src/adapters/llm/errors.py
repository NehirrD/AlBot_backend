class LLMAdapterError(Exception):
    """Base exception for LLM adapter errors"""

    
class LLMConnectionError(LLMAdapterError):
    """Raised when connection to the LLM provider fails."""

class LLMTimeoutError(LLMAdapterError):
    """Raised when the LLM request times out."""

class LLMResponseError(LLMAdapterError):
    """Raised when the LLM response is invalid."""

       
