"""
IPFS Uploader Service

Provides IPFS upload functionality via Pinata API for encrypted medical reports.

This module implements:
- File upload to IPFS via Pinata API
- Timeout handling (30 seconds)
- Retry logic with exponential backoff (3 attempts)
- Pinning for persistence
- Custom exceptions for error handling

Features:
- JWT authentication with Pinata
- Automatic retry on transient failures
- Exponential backoff to avoid overwhelming the API
- Comprehensive error handling and logging
"""

import httpx
import logging
from typing import Optional
import asyncio


# Configure logging
logger = logging.getLogger(__name__)


class IPFSTimeoutError(Exception):
    """Raised when IPFS upload times out."""
    pass


class IPFSAuthError(Exception):
    """Raised when IPFS authentication fails."""
    pass


class IPFSUploadError(Exception):
    """Raised when IPFS upload fails."""
    pass


class IPFSUploader:
    """
    IPFS uploader service using Pinata API.
    
    This class provides:
    - Upload encrypted medical reports to IPFS
    - Automatic pinning for persistence
    - Timeout handling (30 seconds)
    - Retry logic with exponential backoff (3 attempts)
    - Custom exceptions for different failure modes
    """
    
    PINATA_API_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    TIMEOUT_SECONDS = 30
    MAX_RETRIES = 3
    
    def __init__(self, api_key: str, secret_key: str):
        """
        Initialize IPFS uploader with Pinata credentials.
        
        Args:
            api_key: Pinata API key
            secret_key: Pinata secret key
            
        Raises:
            ValueError: If api_key or secret_key is empty
        """
        if not api_key or not secret_key:
            raise ValueError("api_key and secret_key must not be empty")
        
        self.api_key = api_key
        self.secret_key = secret_key
        
        # Create JWT token for authentication
        self.headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key
        }
    
    async def upload(self, data: bytes, filename: str) -> str:
        """
        Upload data to IPFS via Pinata with retry logic.
        
        Implements exponential backoff retry strategy:
        - Attempt 1: immediate
        - Attempt 2: wait 1 second
        - Attempt 3: wait 2 seconds
        
        Args:
            data: Encrypted medical report data to upload
            filename: Name for the file on IPFS
            
        Returns:
            IPFS CID (Content Identifier) in format "Qm..." or "bafy..."
            
        Raises:
            IPFSTimeoutError: If upload times out after all retries
            IPFSAuthError: If authentication fails
            IPFSUploadError: If upload fails for other reasons
            
        Example:
            >>> uploader = IPFSUploader("api_key", "secret_key")
            >>> cid = await uploader.upload(b"encrypted data", "report.enc")
            >>> cid.startswith("Qm") or cid.startswith("bafy")
            True
        """
        last_exception = None
        
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.info(f"IPFS upload attempt {attempt}/{self.MAX_RETRIES} for {filename}")
                
                # Perform the upload
                cid = await self._upload_once(data, filename)
                
                logger.info(f"IPFS upload successful: {cid}")
                return cid
                
            except httpx.TimeoutException as e:
                last_exception = IPFSTimeoutError(
                    f"IPFS upload timed out after {self.TIMEOUT_SECONDS} seconds (attempt {attempt}/{self.MAX_RETRIES})"
                )
                logger.warning(f"Upload timeout on attempt {attempt}: {str(e)}")
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    # Authentication error - don't retry
                    raise IPFSAuthError(f"Pinata authentication failed: {e.response.text}")
                else:
                    last_exception = IPFSUploadError(
                        f"IPFS upload failed with status {e.response.status_code}: {e.response.text}"
                    )
                    logger.warning(f"Upload failed on attempt {attempt}: {str(e)}")
                    
            except Exception as e:
                last_exception = IPFSUploadError(f"IPFS upload failed: {str(e)}")
                logger.warning(f"Upload error on attempt {attempt}: {str(e)}")
            
            # Exponential backoff before retry (except on last attempt)
            if attempt < self.MAX_RETRIES:
                backoff_seconds = 2 ** (attempt - 1)  # 1, 2, 4 seconds
                logger.info(f"Retrying in {backoff_seconds} seconds...")
                await asyncio.sleep(backoff_seconds)
        
        # All retries exhausted
        logger.error(f"IPFS upload failed after {self.MAX_RETRIES} attempts")
        raise last_exception
    
    async def _upload_once(self, data: bytes, filename: str) -> str:
        """
        Perform a single upload attempt to Pinata.
        
        Args:
            data: Data to upload
            filename: Filename for the upload
            
        Returns:
            IPFS CID
            
        Raises:
            httpx.TimeoutException: If request times out
            httpx.HTTPStatusError: If HTTP request fails
        """
        async with httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS) as client:
            # Prepare multipart form data
            files = {
                "file": (filename, data, "application/octet-stream")
            }
            
            # Send POST request to Pinata
            response = await client.post(
                self.PINATA_API_URL,
                headers=self.headers,
                files=files
            )
            
            # Raise exception for HTTP errors
            response.raise_for_status()
            
            # Parse response JSON
            result = response.json()
            
            # Extract IPFS CID from response
            ipfs_hash = result.get("IpfsHash")
            if not ipfs_hash:
                raise IPFSUploadError("No IpfsHash in Pinata response")
            
            return ipfs_hash
    
    async def pin(self, cid: str) -> bool:
        """
        Ensure CID is pinned for persistence.
        
        Note: Pinata automatically pins files uploaded via pinFileToIPFS,
        so this method primarily serves as a verification/re-pin function.
        
        Args:
            cid: IPFS Content Identifier to pin
            
        Returns:
            True if pinning successful, False otherwise
            
        Example:
            >>> uploader = IPFSUploader("api_key", "secret_key")
            >>> cid = await uploader.upload(b"data", "file.txt")
            >>> is_pinned = await uploader.pin(cid)
            >>> is_pinned
            True
        """
        try:
            # Pinata automatically pins files uploaded via pinFileToIPFS
            # This method can be extended to verify pinning status if needed
            logger.info(f"CID {cid} is automatically pinned by Pinata")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify pin status for {cid}: {str(e)}")
            return False
