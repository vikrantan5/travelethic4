import os
import hmac
import hashlib

from fastapi import APIRouter, HTTPException, status, Depends
from loguru import logger
import razorpay
from models.payment import (
    PaymentCheckRequest,
    PaymentCheckResponse,
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentVerificationRequest,
    PaymentVerificationResponse,
)
from models.user import UserResponse
from repository.payment_repository import (
    get_user_planner_status,
    update_user_premium_status,
    increment_planner_count,
     get_user_payment_history,
)
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/payment", tags=["Payment"])

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)


@router.post(
    "/check",
    response_model=PaymentCheckResponse,
    summary="Check Payment Status",
    description="Check if user can create a planner or needs to pay",
)
async def check_payment_status(request: PaymentCheckRequest) -> PaymentCheckResponse:
    """
    Check if user can create a new planner.

    Returns:
        - can_create_planner: True if user can create planner
        - requires_payment: True if payment is required
        - message: Information message
    """
    try:
        logger.info(f"Checking payment status for user: {request.user_id}")

        user_status = await get_user_planner_status(request.user_id)

        # If user is premium, they can always create planners
        if user_status.is_premium:
            return PaymentCheckResponse(
                can_create_planner=True,
                requires_payment=False,
                message="You have premium access. Create unlimited planners!",
            )

        # If user hasn't used free planner yet
        if not user_status.has_used_free_planner:
            return PaymentCheckResponse(
                can_create_planner=True,
                requires_payment=False,
                message="You can create your first free planner!",
            )

        # User has used free planner and is not premium
        return PaymentCheckResponse(
            can_create_planner=False,
            requires_payment=True,
            message="You have used your free planner. Please upgrade to continue.",
        )

    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check payment status: {str(e)}",
        )


@router.post(
    "/initiate",
    response_model=PaymentInitiateResponse,
    summary="Initiate Payment",
    description="Initiate Razorpay payment for premium plans",
)
async def initiate_payment(
    request: PaymentInitiateRequest,
) -> PaymentInitiateResponse:
    """
    Initiate Razorpay payment for premium plans.

    Args:
        request: Payment initiation request with user_id, plan_type, and amount

    Returns:
        PaymentInitiateResponse with Razorpay order details
    """
    try:
        logger.info(
            f"Initiating payment for user: {request.user_id}, plan: {request.plan_type}"
        )

        # Create Razorpay order
        order_data = {
            "amount": request.amount * 100,  # Amount in paise
            "currency": "INR",
            "receipt": f"order_{request.user_id}_{request.plan_type}",
            "notes": {
                "user_id": request.user_id,
                "plan_type": request.plan_type,
            },
        }

        order = razorpay_client.order.create(data=order_data)
        logger.info(f"Razorpay order created: {order['id']}")

        return PaymentInitiateResponse(
            order_id=order["id"],
            amount=order["amount"],
            currency=order["currency"],
            razorpay_key_id=os.getenv("RAZORPAY_KEY_ID"),
        )

    except Exception as e:
        logger.error(f"Error initiating payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate payment: {str(e)}",
        )


@router.post(
    "/verify",
    response_model=PaymentVerificationResponse,
    summary="Verify Payment",
    description="Verify Razorpay payment and upgrade user to premium",
)
async def verify_payment(
    request: PaymentVerificationRequest,
) -> PaymentVerificationResponse:
    """
    Verify Razorpay payment signature and upgrade user.

    Args:
        request: Payment verification request with Razorpay IDs and signature

    Returns:
        PaymentVerificationResponse with success status
    """
    try:
        logger.info(f"Verifying payment for user: {request.user_id}")

        # Verify signature
        generated_signature = hmac.new(
            os.getenv("RAZORPAY_KEY_SECRET").encode(),
            f"{request.razorpay_order_id}|{request.razorpay_payment_id}".encode(),
            hashlib.sha256,
        ).hexdigest()

        if generated_signature != request.razorpay_signature:
            logger.error("Payment signature verification failed")
            return PaymentVerificationResponse(
                success=False,
                message="Payment verification failed. Invalid signature.",
            )

        # Upgrade user to premium
        await update_user_premium_status(request.user_id, is_premium=True)
        logger.info(f"User {request.user_id} upgraded to premium")

        return PaymentVerificationResponse(
            success=True,
            message="Payment successful! You now have premium access.",
        )

    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}",
        )


@router.post(
    "/record-planner",
    summary="Record Planner Creation",
    description="Record that user has created a planner (for tracking free usage)",
)
async def record_planner_creation(user_id: str):
    """
    Record that a user has created a planner.
    Used to track free planner usage.
    """
    try:
        logger.info(f"Recording planner creation for user: {user_id}")
        await increment_planner_count(user_id)
        return {"success": True, "message": "Planner creation recorded"}

    except Exception as e:
        logger.error(f"Error recording planner creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record planner creation: {str(e)}",
        )


@router.get(
    "/history",
    summary="Get Payment History",
    description="Get user's payment transaction history",
)
async def get_payment_history(current_user: UserResponse = Depends(get_current_user)):
    """
    Get user's payment transaction history.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        List of payment transactions
    """
    try:
        logger.info(f"Fetching payment history for user: {current_user.id}")
        transactions = await get_user_payment_history(current_user.id)
        
        return {
            "success": True,
            "transactions": transactions,
            "total": len(transactions),
        }
    
    except Exception as e:
        logger.error(f"Error fetching payment history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment history: {str(e)}",
        )

@router.get(
    "/user-stats",
    summary="Get User Stats",
    description="Get user's planner statistics",
)
@router.get(
    "/user-stats",
    summary="Get User Stats",
    description="Get user's planner statistics",
)
async def get_user_stats(current_user: UserResponse = Depends(get_current_user)):
    """
    Get user's planner statistics.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        User's planner statistics
    """
    try:
        logger.info(f"Fetching user stats for user: {current_user.id}")
        user_status = await get_user_planner_status(current_user.id)
        
        return {
            "success": True,
            "stats": {
                "has_used_free_planner": user_status.has_used_free_planner,
                "total_planners_created": user_status.total_planners_created,
                "is_premium": user_status.is_premium,
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user stats: {str(e)}",
        )