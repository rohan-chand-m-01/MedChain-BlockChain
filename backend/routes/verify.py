import os
import logging
from fastapi import APIRouter, HTTPException
from pathlib import Path
from dotenv import load_dotenv

# Load from root .env file
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')

from services.insforge import db_select_single
from services.blockchain_client import BlockchainClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Verification"])


@router.get("/verify/{record_id}")
async def verify_record(record_id: str):
    """
    Verify a medical report by record ID.
    
    Returns verification status, risk level, timestamp, IPFS CID, and commitment hash.
    Does NOT return any PII (phone_hash, patient identifiers).
    
    Args:
        record_id: Blockchain record ID (bytes32 as hex string)
        
    Returns:
        dict: {
            "verified": bool,
            "risk_level": str,
            "risk_score": int,
            "timestamp": str,
            "ipfs_cid": str,
            "commitment_hash": str,
            "record_id": str,
            "blockchain_verified": bool
        }
    """
    try:
        logger.info(f"🔍 Verifying record with record_id: {record_id}")
        
        # Query database for record
        record = await db_select_single(
            table="whatsapp_records",
            filters={"record_id": record_id},
            select="risk_level,risk_score,created_at,ipfs_cid,commitment_hash,record_id"
        )
        
        if not record:
            logger.warning(f"❌ Record not found for record_id: {record_id}")
            raise HTTPException(status_code=404, detail="Record not found")
        
        logger.info(f"✓ Found record in database: {record['ipfs_cid']}")
        
        # Cross-check with blockchain
        blockchain_verified = False
        blockchain_risk_score = None
        blockchain_risk_level = None
        blockchain_timestamp = None
        
        try:
            blockchain_client = BlockchainClient(
                rpc_url=os.getenv("ETHEREUM_RPC_URL", "http://127.0.0.1:8545"),
                contract_address=os.getenv("CONTRACT_ADDRESS", ""),
                private_key=os.getenv("GAS_WALLET_PRIVATE_KEY", "")
            )
            
            # Verify on-chain
            blockchain_record = await blockchain_client.verify_record(record_id)
            blockchain_verified = blockchain_record.get("exists", False)
            blockchain_risk_score = blockchain_record.get("risk_score")
            blockchain_risk_level = blockchain_record.get("risk_level")
            blockchain_timestamp = blockchain_record.get("timestamp")
            
            logger.info(f"✓ Blockchain verification: exists={blockchain_verified}, risk_score={blockchain_risk_score}")
            
        except Exception as blockchain_error:
            logger.warning(f"⚠️ Blockchain verification failed (non-blocking): {blockchain_error}")
            # Continue even if blockchain verification fails
        
        # Return verification data (no PII)
        return {
            "verified": True,
            "risk_level": record["risk_level"],
            "risk_score": record["risk_score"],
            "timestamp": record["created_at"],
            "ipfs_cid": record["ipfs_cid"],
            "commitment_hash": record["commitment_hash"],
            "record_id": record["record_id"],
            "blockchain_verified": blockchain_verified,
            "blockchain_risk_score": blockchain_risk_score,
            "blockchain_risk_level": blockchain_risk_level,
            "blockchain_timestamp": blockchain_timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Verification error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Verification failed")
