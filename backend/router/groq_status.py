""""
Router for Groq API Key Management Status
"""

from fastapi import APIRouter
from loguru import logger
from config.groq_key_manager import get_key_manager

router = APIRouter(prefix="/api/groq", tags=["groq"])


@router.get("/key-status", summary="Get Groq API Key Manager Status")
async def get_key_status():
    """
    Get the current status of all Groq API keys.
    Shows which keys are available and which are in cooldown.
    """
    try:
        key_manager = get_key_manager()
        status = key_manager.get_status()
        
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting key status: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/reset-cooldowns", summary="Reset All Key Cooldowns (Admin)")
async def reset_cooldowns():
    """
    Reset all key cooldowns (for testing/admin purposes).
    This will make all keys available again.
    """
    try:
        key_manager = get_key_manager()
        key_manager.failed_keys.clear()
        
        logger.info("All key cooldowns have been reset")
        
        return {
            "success": True,
            "message": "All key cooldowns have been reset",
            "data": key_manager.get_status()
        }
    except Exception as e:
        logger.error(f"Error resetting cooldowns: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
