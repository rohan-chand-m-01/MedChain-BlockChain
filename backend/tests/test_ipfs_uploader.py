"""
Tests for IPFS Uploader Service

Tests cover:
- Successful upload scenarios
- Timeout handling
- Authentication errors
- Retry logic with exponential backoff
- Pin functionality
- Error handling
"""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch
from backend.services.ipfs_uploader import (
    IPFSUploader,
    IPFSTimeoutError,
    IPFSAuthError,
    IPFSUploadError
)


class TestIPFSUploaderInit:
    """Test IPFSUploader initialization."""
    
    def test_init_with_valid_credentials(self):
        """Test initialization with valid API credentials."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        assert uploader.api_key == "test_api_key"
        assert uploader.secret_key == "test_secret_key"
        assert uploader.headers["pinata_api_key"] == "test_api_key"
        assert uploader.headers["pinata_secret_api_key"] == "test_secret_key"
    
    def test_init_with_empty_api_key(self):
        """Test initialization fails with empty API key."""
        with pytest.raises(ValueError, match="api_key and secret_key must not be empty"):
            IPFSUploader("", "test_secret_key")
    
    def test_init_with_empty_secret_key(self):
        """Test initialization fails with empty secret key."""
        with pytest.raises(ValueError, match="api_key and secret_key must not be empty"):
            IPFSUploader("test_api_key", "")


class TestIPFSUploaderUpload:
    """Test IPFSUploader upload functionality."""
    
    @pytest.mark.asyncio
    async def test_successful_upload(self):
        """Test successful upload returns IPFS CID."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"IpfsHash": "QmTest123"}
        mock_response.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            cid = await uploader.upload(b"test data", "test.txt")
            
            assert cid == "QmTest123"
    
    @pytest.mark.asyncio
    async def test_upload_with_bafy_cid(self):
        """Test upload returns CIDv1 (bafy...) format."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"IpfsHash": "bafyTest456"}
        mock_response.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            cid = await uploader.upload(b"test data", "test.txt")
            
            assert cid == "bafyTest456"
    
    @pytest.mark.asyncio
    async def test_upload_timeout_raises_error(self):
        """Test upload timeout raises IPFSTimeoutError after retries."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Request timed out")
            )
            
            with patch("asyncio.sleep", new_callable=AsyncMock):  # Speed up test
                with pytest.raises(IPFSTimeoutError, match="IPFS upload timed out"):
                    await uploader.upload(b"test data", "test.txt")
    
    @pytest.mark.asyncio
    async def test_upload_auth_error_no_retry(self):
        """Test authentication error raises IPFSAuthError without retry."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "401 Unauthorized",
                    request=Mock(),
                    response=mock_response
                )
            )
            
            with pytest.raises(IPFSAuthError, match="Pinata authentication failed"):
                await uploader.upload(b"test data", "test.txt")
    
    @pytest.mark.asyncio
    async def test_upload_retry_logic(self):
        """Test upload retries 3 times with exponential backoff."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        
        call_count = 0
        
        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # Fail first 2 attempts
                raise httpx.TimeoutException("Timeout")
            else:
                # Succeed on 3rd attempt
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"IpfsHash": "QmSuccess"}
                mock_response.raise_for_status = Mock()
                return mock_response
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                cid = await uploader.upload(b"test data", "test.txt")
                
                assert cid == "QmSuccess"
                assert call_count == 3
                # Verify exponential backoff: 1s, 2s
                assert mock_sleep.call_count == 2
                mock_sleep.assert_any_call(1)
                mock_sleep.assert_any_call(2)
    
    @pytest.mark.asyncio
    async def test_upload_http_error_raises_upload_error(self):
        """Test HTTP error raises IPFSUploadError."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "500 Internal Server Error",
                    request=Mock(),
                    response=mock_response
                )
            )
            
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(IPFSUploadError, match="IPFS upload failed with status 500"):
                    await uploader.upload(b"test data", "test.txt")
    
    @pytest.mark.asyncio
    async def test_upload_missing_ipfs_hash_in_response(self):
        """Test upload raises error when IpfsHash missing from response."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Missing IpfsHash
        mock_response.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(IPFSUploadError, match="No IpfsHash in Pinata response"):
                    await uploader.upload(b"test data", "test.txt")
    
    @pytest.mark.asyncio
    async def test_upload_generic_exception(self):
        """Test generic exception raises IPFSUploadError."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("Network error")
            )
            
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(IPFSUploadError, match="IPFS upload failed: Network error"):
                    await uploader.upload(b"test data", "test.txt")


class TestIPFSUploaderPin:
    """Test IPFSUploader pin functionality."""
    
    @pytest.mark.asyncio
    async def test_pin_returns_true(self):
        """Test pin returns True for valid CID."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        
        result = await uploader.pin("QmTest123")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_pin_with_bafy_cid(self):
        """Test pin works with CIDv1 format."""
        uploader = IPFSUploader("test_api_key", "test_secret_key")
        
        result = await uploader.pin("bafyTest456")
        
        assert result is True


class TestIPFSUploaderConstants:
    """Test IPFSUploader class constants."""
    
    def test_pinata_api_url(self):
        """Test Pinata API URL is correct."""
        assert IPFSUploader.PINATA_API_URL == "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    def test_timeout_seconds(self):
        """Test timeout is 30 seconds."""
        assert IPFSUploader.TIMEOUT_SECONDS == 30
    
    def test_max_retries(self):
        """Test max retries is 3."""
        assert IPFSUploader.MAX_RETRIES == 3
