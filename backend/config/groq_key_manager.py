""""
Groq API Key Manager with Intelligent Rotation
Handles multiple API keys with automatic failover and cooldown management
"""

import os
import time
from typing import Optional, Dict, List
from loguru import logger
from groq import Groq
from groq import (
    RateLimitError,
    AuthenticationError,
    APIError,
    APITimeoutError,
    APIConnectionError
)


class GroqKeyManager:
    """
    Manages multiple Groq API keys with intelligent rotation and failover.
    
    Features:
    - Sequential key rotation (KEY_1 → KEY_2 → KEY_3 → KEY_4)
    - 30-minute cooldown for failed keys
    - Automatic error detection and switching
    - Exhaustion handling when all keys fail
    """
    
    # Error messages that trigger key rotation
    ROTATION_ERRORS = [
        "rate_limit_exceeded",
        "quota_exceeded",
        "key_expired",
        "unauthorized",
        "invalid_api_key",
        "context_length_exceeded",
        "token_usage_limit_reached",
        "request_timeout",
        "internal_server_error"
    ]
    
    def __init__(self):
        """Initialize the key manager with 4 Groq API keys from environment"""
        self.keys: List[str] = []
        self.current_key_index: int = 0
        self.failed_keys: Dict[str, float] = {}  # key -> timestamp of failure
        self.cooldown_period: int = 30 * 60  # 30 minutes in seconds
        
        # Load keys from environment
        self._load_keys()
        
        logger.info(f"GroqKeyManager initialized with {len(self.keys)} API keys")
    
    def _load_keys(self):
        """Load API keys from environment variables"""
        for i in range(1, 5):
            key_name = f"GROQ_API_KEY_{i}"
            key = os.getenv(key_name)
            if key:
                self.keys.append(key)
                logger.info(f"Loaded {key_name}")
            else:
                logger.warning(f"{key_name} not found in environment")
        
        if not self.keys:
            raise ValueError("No Groq API keys found. Please set GROQ_API_KEY_1 through GROQ_API_KEY_4")
    
    def _is_key_available(self, key: str) -> bool:
        """Check if a key is available (not in cooldown)"""
        if key not in self.failed_keys:
            return True
        
        # Check if cooldown period has passed
        failed_time = self.failed_keys[key]
        current_time = time.time()
        
        if current_time - failed_time >= self.cooldown_period:
            # Cooldown expired, remove from failed list
            del self.failed_keys[key]
            logger.info(f"Key cooldown expired, re-enabling key (index: {self.keys.index(key) + 1})")
            return True
        
        return False
    
    def _mark_key_as_failed(self, key: str):
        """Mark a key as failed with current timestamp"""
        self.failed_keys[key] = time.time()
        key_index = self.keys.index(key) + 1
        logger.warning(f"Marked GROQ_API_KEY_{key_index} as failed. Cooldown: 30 minutes")
    
    def _should_rotate(self, error: Exception) -> bool:
        """Determine if an error should trigger key rotation"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Check for specific error types
        if isinstance(error, (RateLimitError, AuthenticationError, APITimeoutError)):
            return True
        
        # Check for error messages
        for rotation_error in self.ROTATION_ERRORS:
            if rotation_error in error_str or rotation_error in error_type:
                return True
        
        # Check for 5xx errors
        if "5" in error_str and ("server" in error_str or "error" in error_str):
            return True
        
        return False
    
    def get_next_available_key(self) -> Optional[str]:
        """
        Get the next available API key.
        Returns None if all keys are exhausted.
        """
        if not self.keys:
            return None
        
        # Try to find an available key starting from current index
        attempts = 0
        while attempts < len(self.keys):
            key = self.keys[self.current_key_index]
            
            if self._is_key_available(key):
                logger.debug(f"Using GROQ_API_KEY_{self.current_key_index + 1}")
                return key
            
            # Move to next key
            self.current_key_index = (self.current_key_index + 1) % len(self.keys)
            attempts += 1
        
        # All keys are in cooldown
        logger.error("All Groq API keys are in cooldown or exhausted")
        return None
    
    def get_client(self) -> Optional[Groq]:
        """
        Get a Groq client with an available API key.
        Returns None if no keys are available.
        """
        key = self.get_next_available_key()
        if not key:
            return None
        
        return Groq(api_key=key)
    
    def handle_error(self, error: Exception, current_key: str) -> bool:
        """
        Handle an error and determine if key rotation is needed.
        
        Args:
            error: The exception that occurred
            current_key: The API key that was being used
        
        Returns:
            True if key was rotated, False otherwise
        """
        if not self._should_rotate(error):
            # Error doesn't require rotation
            return False
        
        # Mark current key as failed
        self._mark_key_as_failed(current_key)
        
        # Move to next key
        old_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
        
        logger.info(f"Rotated from KEY_{old_index + 1} to KEY_{self.current_key_index + 1}")
        return True
    
    def get_status(self) -> Dict:
        """Get current status of all keys"""
        status = {
            "total_keys": len(self.keys),
            "current_key_index": self.current_key_index + 1,
            "failed_keys": [],
            "available_keys": []
        }
        
        for i, key in enumerate(self.keys):
            key_num = i + 1
            if self._is_key_available(key):
                status["available_keys"].append(key_num)
            else:
                failed_time = self.failed_keys[key]
                remaining_cooldown = self.cooldown_period - (time.time() - failed_time)
                status["failed_keys"].append({
                    "key_number": key_num,
                    "cooldown_remaining_minutes": round(remaining_cooldown / 60, 1)
                })
        
        return status
    
    def is_exhausted(self) -> bool:
        """Check if all keys are exhausted (in cooldown)"""
        return all(not self._is_key_available(key) for key in self.keys)


# Global singleton instance
_key_manager: Optional[GroqKeyManager] = None


def get_key_manager() -> GroqKeyManager:
    """Get or create the global key manager instance"""
    global _key_manager
    if _key_manager is None:
        _key_manager = GroqKeyManager()
    return _key_manager


def reset_key_manager():
    """Reset the global key manager (useful for testing)"""
    global _key_manager
    _key_manager = None
