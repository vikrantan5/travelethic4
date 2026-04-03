"""
Payment Repository
Handles user payment status and premium tracking
"""

from loguru import logger
from services.db_service import get_db_pool
from models.payment import UserPlannerStatus
from datetime import datetime, timezone


async def get_user_planner_status(user_id: str) -> UserPlannerStatus:
    """
    Get user's planner status (free usage, premium status, etc.)
    
    Args:
        user_id: User ID
        
    Returns:
        UserPlannerStatus with user's current status
    """
    pool = get_db_pool()
    
    async with pool.acquire() as conn:
        # Check if user exists in user_planner_status table
        row = await conn.fetchrow(
            """
            SELECT user_id, has_used_free_planner, total_planners_created, is_premium
            FROM user_planner_status
            WHERE user_id = $1
            """,
            user_id,
        )
        
        if row:
            return UserPlannerStatus(
                user_id=row["user_id"],
                has_used_free_planner=row["has_used_free_planner"],
                total_planners_created=row["total_planners_created"],
                is_premium=row["is_premium"],
            )
        else:
            # Create new user status entry
            await conn.execute(
                """
                INSERT INTO user_planner_status 
                (user_id, has_used_free_planner, total_planners_created, is_premium, created_at)
                VALUES ($1, $2, $3, $4, $5)
                """,
                user_id,
                False,
                0,
                False,
                datetime.now(timezone.utc),
            )
            
            return UserPlannerStatus(
                user_id=user_id,
                has_used_free_planner=False,
                total_planners_created=0,
                is_premium=False,
            )


async def update_user_premium_status(user_id: str, is_premium: bool) -> None:
    """
    Update user's premium status
    
    Args:
        user_id: User ID
        is_premium: Premium status to set
    """
    pool = get_db_pool()
    
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_planner_status 
            (user_id, has_used_free_planner, total_planners_created, is_premium, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                is_premium = $4,
                updated_at = $6
            """,
            user_id,
            False,
            0,
            is_premium,
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
        )
    
    logger.info(f"Updated premium status for user {user_id} to {is_premium}")


async def increment_planner_count(user_id: str) -> None:
    """
    Increment user's planner creation count and mark free planner as used
    
    Args:
        user_id: User ID
    """
    pool = get_db_pool()
    
    async with pool.acquire() as conn:
        # Get current status
        status = await get_user_planner_status(user_id)
        
        # Update count and free planner status
        await conn.execute(
            """
            UPDATE user_planner_status 
            SET 
                total_planners_created = total_planners_created + 1,
                has_used_free_planner = true,
                updated_at = $2
            WHERE user_id = $1
            """,
            user_id,
            datetime.now(timezone.utc),
        )
    
    logger.info(f"Incremented planner count for user {user_id}")


async def create_payment_transaction(
    user_id: str,
    razorpay_order_id: str,
    amount: int,
    currency: str,
    plan_type: str
) -> int:
    """
    Create a new payment transaction record
    
    Args:
        user_id: User ID
        razorpay_order_id: Razorpay order ID
        amount: Payment amount in paise
        currency: Currency code
        plan_type: Type of plan being purchased
        
    Returns:
        Transaction ID
    """
    pool = get_db_pool()
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO payment_transactions 
            (user_id, razorpay_order_id, amount, currency, plan_type, status, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
            """,
            user_id,
            razorpay_order_id,
            amount,
            currency,
            plan_type,
            'pending',
            datetime.now(timezone.utc),
        )
        
        transaction_id = row["id"]
        logger.info(f"Created payment transaction {transaction_id} for user {user_id}")
        return transaction_id


async def update_payment_transaction(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    status: str
) -> None:
    """
    Update payment transaction with payment details
    
    Args:
        razorpay_order_id: Razorpay order ID
        razorpay_payment_id: Razorpay payment ID
        razorpay_signature: Razorpay signature
        status: Payment status (success/failed)
    """
    pool = get_db_pool()
    
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE payment_transactions
            SET 
                razorpay_payment_id = $2,
                razorpay_signature = $3,
                status = $4,
                updated_at = $5
            WHERE razorpay_order_id = $1
            """,
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature,
            status,
            datetime.now(timezone.utc),
        )
    
    logger.info(f"Updated payment transaction for order {razorpay_order_id} to status: {status}")





async def get_user_payment_history(user_id: str) -> list:
    """
    Get user's payment transaction history
    
    Args:
        user_id: User ID
        
    Returns:
        List of payment transactions
    """
    pool = get_db_pool()
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT 
                id, 
                razorpay_order_id,
                razorpay_payment_id,
                razorpay_signature,
                amount,
                currency,
                plan_type,
                status,
                created_at,
                updated_at
            FROM payment_transactions
            WHERE user_id = $1
            ORDER BY created_at DESC
            """,
            user_id,
        )
        
        transactions = []
        for row in rows:
            transactions.append({
                "id": row["id"],
                "razorpay_order_id": row["razorpay_order_id"],
                "razorpay_payment_id": row["razorpay_payment_id"],
                "amount": row["amount"],
                "currency": row["currency"],
                "plan_type": row["plan_type"],
                "status": row["status"],
                "created_at": row["created_at"].isoformat(),
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
            })
        
        return transactions