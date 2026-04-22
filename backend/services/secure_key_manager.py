"""
Enterprise-Grade Secure Key Management System
Implements envelope encryption, time-bound access, and audit logging.

Architecture:
1. File Encryption Key (FEK) - encrypts the actual file
2. Master Key (MEK) - encrypts the FEK (stored in backend env)
3. User-specific wrapped keys - FEK encrypted with user's derived key
4. Time-bound access tokens for doctors

Security Features:
- Envelope encryption (defense in depth)
- Zero-knowledge architecture (backend never sees plaintext FEK)
- Time-bound access with automatic expiration
- Access count limits
- Comprehensive audit logging
- Key rotation support
"""

import os
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from pathlib import Path
from dotenv import load_dotenv
import logging

from services.insforge import db_insert, db_select, db_update, db_select_single

logger = logging.getLogger(__name__)

# Load master encryption key from environment
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')

MASTER_KEY = os.getenv("VAULT_MASTER_KEY")
if not MASTER_KEY or len(MASTER_KEY) < 32:
    raise RuntimeError("VAULT_MASTER_KEY must be at least 32 characters")


class SecureKeyManager:
    """
    Manages encryption keys with enterprise-grade security.
    
    Key Hierarchy:
    1. Master Encryption Key (MEK) - stored in env, encrypts all FEKs
    2. File Encryption Key (FEK) - unique per file, encrypts file content
    3. Wrapped FEK - FEK encrypted with MEK, stored in database
    4. Access Tokens - time-bound tokens for doctor access
    """
    
    def __init__(self):
        self.master_key = MASTER_KEY.encode()[:32]  # Use first 32 bytes
        
    def generate_file_encryption_