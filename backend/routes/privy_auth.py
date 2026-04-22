"""
Privy Authentication Routes
Verify Privy JWT tokens and manage user sessions
"""
import os
import logging
import httpx
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Privy Authentication"])


class PrivyUser(BaseModel):
    privy_id: str
    email: Optional[str] = None
    wallet_address: Optional[str] = None
    created_at: datetime


@router.get("/privy/verify")
async def verify_privy_token(authorization: str = Header(None)):
    """
    Verify Privy JWT token and return user information.
    
    This endpoint validates the Privy authentication token and extracts user data.
    The token is verified against Privy's public keys.
    
    Headers:
        Authorization: Bearer <privy_token>
    
    Returns:
        {
            "valid": true,
            "user": {
                "privy_id": "...",
                "email": "...",
                "wallet_address": "0x...",
                "created_at": "..."
            }
        }
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify token with Privy API
        privy_app_id = os.getenv("PRIVY_APP_ID")
        privy_app_secret = os.getenv("PRIVY_APP_SECRET")
        
        if not privy_app_id or not privy_app_secret:
            raise HTTPException(status_code=500, detail="Privy not configured")
        
        # Call Privy verification endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://auth.privy.io/api/v1/verification_keys",
                headers={
                    "privy-app-id": privy_app_id,
                    "privy-app-secret": privy_app_secret,
                    "Authorization": f"Bearer {token}"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"Privy verification failed: {response.status_code} - {response.text}")
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_data = response.json()
            
            # Extract user information
            privy_user = PrivyUser(
                privy_id=user_data.get("id"),
                email=user_data.get("email", {}).get("address"),
                wallet_address=user_data.get("wallet", {}).get("address"),
                created_at=datetime.fromisoformat(user_data.get("created_at", datetime.now().isoformat()))
            )
            
            logger.info(f"✓ Privy token verified for user: {privy_user.privy_id}")
            
            return {
                "valid": True,
                "user": privy_user.dict()
            }
            
    except httpx.HTTPError as e:
        logger.error(f"Privy API error: {e}")
        raise HTTPException(status_code=503, detail="Privy service unavailable")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/privy/link-patient")
async def link_privy_to_patient(
    privy_id: str,
    patient_wallet: str,
    authorization: str = Header(None)
):
    """
    Link Privy user to existing patient record.
    
    This allows users who started with WhatsApp (custodial wallet) to
    claim their records using Privy MPC wallet.
    
    Body:
        {
            "privy_id": "did:privy:...",
            "patient_wallet": "0x..." (existing custodial wallet)
        }
    
    Returns:
        {
            "success": true,
            "message": "Privy account linked to patient records"
        }
    """
    # Verify token first
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify the token belongs to the claimed privy_id
        verification = await verify_privy_token(authorization=f"Bearer {token}")
        
        if not verification["valid"] or verification["user"]["privy_id"] != privy_id:
            raise HTTPException(status_code=403, detail="Token does not match privy_id")
        
        # Link in database (using InsForge)
        from services.insforge import db_insert, db_query
        
        # Check if link already exists
        existing_link = await db_query(
            "privy_patient_links",
            filters={"privy_id": privy_id}
        )
        
        if existing_link and len(existing_link) > 0:
            return {
                "success": True,
                "message": "Privy account already linked",
                "existing": True
            }
        
        # Create new link
        await db_insert("privy_patient_links", {
            "privy_id": privy_id,
            "patient_wallet": patient_wallet,
            "linked_at": datetime.now().isoformat()
        })
        
        logger.info(f"✓ Linked Privy {privy_id} to patient {patient_wallet}")
        
        return {
            "success": True,
            "message": "Privy account linked to patient records",
            "existing": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to link Privy account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/privy/patient/{privy_id}")
async def get_patient_by_privy(
    privy_id: str,
    authorization: str = Header(None)
):
    """
    Get patient wallet address from Privy ID.
    
    This allows the frontend to fetch patient records using Privy authentication.
    
    Returns:
        {
            "privy_id": "did:privy:...",
            "patient_wallet": "0x...",
            "linked_at": "..."
        }
    """
    # Verify token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    try:
        verification = await verify_privy_token(authorization=authorization)
        
        if not verification["valid"] or verification["user"]["privy_id"] != privy_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Fetch link from database
        from services.insforge import db_query
        
        links = await db_query(
            "privy_patient_links",
            filters={"privy_id": privy_id}
        )
        
        if not links or len(links) == 0:
            raise HTTPException(status_code=404, detail="No patient record linked to this Privy account")
        
        link = links[0]
        
        return {
            "privy_id": link["privy_id"],
            "patient_wallet": link["patient_wallet"],
            "linked_at": link["linked_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch patient link: {e}")
        raise HTTPException(status_code=500, detail=str(e))
