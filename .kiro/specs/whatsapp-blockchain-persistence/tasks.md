# Implementation Plan: WhatsApp Blockchain Persistence + Insurance Verification

## Overview

This implementation plan transforms the existing WhatsApp medical report analysis feature into a blockchain-verified, privacy-preserving medical record system. The implementation follows a layered approach: backend services → WhatsApp handler integration → smart contract modifications → verification API → frontend verification page → database migration → comprehensive testing.

The design uses Python for backend services, Solidity for smart contracts, and TypeScript/React for the frontend verification page.

## Tasks

- [x] 1. Set up project infrastructure and dependencies
  - Install required Python packages: `cryptography`, `web3`, `httpx`, `eth-utils`
  - Install Hardhat dependencies for smart contract testing
  - Create environment variables in `.env.example` and backend `.env.example`
  - Add `SERVER_ENCRYPTION_SECRET`, `PINATA_API_KEY`, `PINATA_SECRET_KEY`, `ETHEREUM_RPC_URL`, `ETHEREUM_PRIVATE_KEY`, `CONTRACT_ADDRESS`
  - _Requirements: 8.7, 9.2, 9.3_

- [x] 2. Implement cryptographic utilities
  - [x] 2.1 Create hash computer utility
    - Create `backend/services/hash_computer.py`
    - Implement `sha256()` method for phone number hashing
    - Implement `keccak256()` method for commitment hash computation
    - _Requirements: 2.2, 8.5, 8.6, 1.4_
  
  - [ ]* 2.2 Write property test for hash determinism
    - **Property 5: Commitment Hash Determinism**
    - **Validates: Requirements 1.4**
  
  - [x] 2.3 Create AES encryptor service
    - Create `backend/services/aes_encryptor.py`
    - Implement `derive_key()` using PBKDF2-HMAC-SHA256 with 100,000 iterations
    - Implement `encrypt()` with AES-256-CBC and unique IV generation
    - Implement `decrypt()` with IV extraction and decryption
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 12.1_
  
  - [ ]* 2.4 Write property tests for encryption
    - **Property 1: Encryption Round-Trip Preservation**
    - **Validates: Requirements 12.1**
  
  - [ ]* 2.5 Write property test for IV uniqueness
    - **Property 2: Encryption IV Uniqueness**
    - **Validates: Requirements 8.3, 12.3**
  
  - [ ]* 2.6 Write property test for key derivation consistency
    - **Property 3: Encryption Key Derivation Consistency**
    - **Validates: Requirements 2.5, 8.2**
  
  - [ ]* 2.7 Write unit tests for encryption edge cases
    - Test decryption failure with incorrect key
    - Test decryption failure with corrupted data
    - Test empty plaintext encryption
    - _Requirements: 12.4, 12.5_

- [x] 3. Checkpoint - Ensure cryptographic tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement IPFS uploader service
  - [x] 4.1 Create IPFS uploader with Pinata integration
    - Create `backend/services/ipfs_uploader.py`
    - Implement `upload()` method with Pinata API integration
    - Implement timeout handling (30 seconds)
    - Implement retry logic with exponential backoff (3 attempts)
    - Implement `pin()` method for ensuring persistence
    - Add custom exceptions: `IPFSTimeoutError`, `IPFSAuthError`, `IPFSUploadError`
    - _Requirements: 1.3, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  
  - [ ]* 4.2 Write property test for IPFS CID format validation
    - **Property 4: IPFS Upload Returns Valid CID**
    - **Validates: Requirements 1.3, 9.4**
  
  - [ ]* 4.3 Write unit tests for IPFS error handling
    - Test timeout exception after 30 seconds
    - Test authentication failure handling
    - Test network failure handling
    - Test retry logic with mock failures
    - _Requirements: 9.6, 3.1, 3.2, 3.3_

- [x] 5. Implement blockchain client service
  - [x] 5.1 Create blockchain client with web3.py
    - Create `backend/services/blockchain_client.py`
    - Implement `store_record()` method with transaction signing
    - Implement `verify_record()` method for on-chain verification
    - Implement `compute_commitment_hash()` using keccak256
    - Add gas estimation and transaction confirmation logic
    - Add custom exceptions: `BlockchainGasError`, `BlockchainNetworkError`, `BlockchainTransactionError`
    - _Requirements: 1.4, 1.5, 1.6, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_
  
  - [ ]* 5.2 Write unit tests for blockchain client
    - Test transaction signing and submission
    - Test gas estimation
    - Test network failure handling
    - Test transaction revert handling
    - Mock web3 provider for testing
    - _Requirements: 3.4, 3.5, 3.6_

- [x] 6. Checkpoint - Ensure service layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [-] 7. Modify smart contract for WhatsApp records
  - [x] 7.1 Add WhatsApp record storage to MediChainRecords.sol
    - Open `blockchain/contracts/MediChainRecords.sol`
    - Add `WhatsAppRecord` struct with `commitmentHash`, `timestamp`, `exists` fields
    - Add mapping `mapping(bytes32 => WhatsAppRecord) public whatsappRecords`
    - Implement `storeWhatsAppRecord(bytes32 _commitmentHash)` function
    - Implement `verifyWhatsAppRecord(bytes32 _recordId)` view function
    - Add `WhatsAppRecordStored` event
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_
  
  - [ ]* 7.2 Write smart contract tests
    - **Property 13: Smart Contract Record Creation Completeness**
    - **Property 14: Smart Contract Verification Correctness**
    - Test storeRecord with valid commitment hash
    - Test verifyRecord returns true for existing records
    - Test verifyRecord returns false for non-existent records
    - Test RecordStored event emission
    - Test timestamp is set to block.timestamp
    - Test Record.exists is set to true
    - Use Hardhat testing framework
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9_
  
  - [ ] 7.3 Deploy smart contract to testnet
    - Update deployment script in `blockchain/scripts/deploy_and_save.ts`
    - Deploy to Ethereum Sepolia testnet
    - Save contract address to environment variables
    - Verify contract on Etherscan
    - _Requirements: 4.1_

- [x] 8. Create database migration for whatsapp_records table
  - [x] 8.1 Create migration file
    - Create `backend/migrations/003_create_whatsapp_records.sql`
    - Define table with columns: `id`, `phone_hash`, `ipfs_cid`, `commitment_hash`, `tx_hash`, `risk_level`, `risk_score`, `created_at`, `deleted_at`
    - Add index on `tx_hash` for fast verification lookups
    - Add index on `phone_hash` for patient record queries
    - Add index on `created_at` for chronological queries
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10_
  
  - [ ]* 8.2 Write property test for phone hash privacy
    - **Property 6: Phone Hash Privacy Preservation**
    - **Validates: Requirements 2.1, 2.2**

- [x] 9. Implement blockchain persistence in WhatsApp handler
  - [x] 9.1 Create persistence orchestration function
    - Open `backend/routes/whatsapp.py`
    - Create `persist_to_blockchain()` async function
    - Implement encryption step using AES encryptor
    - Implement IPFS upload step with error handling
    - Implement commitment hash computation
    - Implement blockchain storage with error handling
    - Implement database record insertion
    - Implement raw report deletion
    - Implement verification URL construction
    - Return `PersistenceResult` with success status and data
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9, 1.10_
  
  - [x] 9.2 Integrate persistence into webhook handler
    - Modify `whatsapp_webhook()` function
    - Call `persist_to_blockchain()` after AI analysis completes
    - Wrap persistence call in try-except for graceful degradation
    - Send verification URL to patient via Twilio if persistence succeeds
    - Log errors without blocking analysis response
    - _Requirements: 1.8, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_
  
  - [ ]* 9.3 Write property tests for privacy preservation
    - **Property 7: Blockchain Privacy Preservation**
    - **Property 8: Verification Page Privacy Preservation**
    - **Property 9: Raw Report Cleanup After Upload**
    - **Validates: Requirements 2.3, 2.4, 2.7, 2.8, 1.9, 2.6**
  
  - [ ]* 9.4 Write property tests for non-blocking behavior
    - **Property 10: Non-Blocking Analysis on IPFS Failure**
    - **Property 11: Non-Blocking Analysis on Blockchain Failure**
    - **Property 12: Error Logging on Persistence Failure**
    - **Validates: Requirements 3.1, 3.3, 3.4, 3.6, 3.7, 3.8, 3.2, 3.5**
  
  - [ ]* 9.5 Write unit tests for persistence flow
    - Test successful end-to-end persistence
    - Test IPFS failure graceful degradation
    - Test blockchain failure graceful degradation
    - Test database insertion
    - Test verification URL construction
    - Mock all external services
    - _Requirements: 1.7, 1.8, 1.10_

- [ ] 10. Checkpoint - Ensure WhatsApp handler tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement verification API endpoint
  - [x] 11.1 Create verification endpoint
    - Create `backend/routes/verify.py`
    - Implement `GET /api/verify/{tx_hash}` endpoint
    - Query database for record matching transaction hash
    - Return 404 if record not found
    - Query blockchain for on-chain verification
    - Return JSON with verification status, risk_level, timestamp, ipfs_cid, commitment_hash
    - Ensure no PII (phone_hash, patient identifiers) in response
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
  
  - [x] 11.2 Register verification router in main.py
    - Open `backend/main.py`
    - Import verify router
    - Add `app.include_router(verify.router, prefix="/api")`
    - _Requirements: 5.1_
  
  - [ ]* 11.3 Write property tests for verification endpoint
    - **Property 15: Verification Endpoint Database Lookup**
    - **Property 16: Verification Endpoint Blockchain Cross-Check**
    - **Property 17: Verification Endpoint Response Completeness**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8**
  
  - [ ]* 11.4 Write unit tests for verification endpoint
    - Test successful verification with valid tx_hash
    - Test 404 response for non-existent tx_hash
    - Test blockchain verification cross-check
    - Test response does not include PII
    - Mock database and blockchain client
    - _Requirements: 5.7, 5.8_

- [x] 12. Implement frontend verification page
  - [x] 12.1 Create verification page component
    - Create `frontend/src/app/verify/[hash]/page.tsx`
    - Implement data fetching from `/api/verify/{tx_hash}` endpoint
    - Implement loading state
    - Implement error state for not found records
    - _Requirements: 6.1, 6.8_
  
  - [x] 12.2 Implement verification status banner
    - Display green banner with checkmark for verified records
    - Display red banner with X for not found records
    - Use Tailwind CSS for styling
    - _Requirements: 6.3_
  
  - [x] 12.3 Implement record details card
    - Display risk level with appropriate emoji (🟢/🟡/🔴)
    - Display timestamp in human-readable format
    - Use card layout with Tailwind CSS
    - _Requirements: 6.4_
  
  - [x] 12.4 Implement blockchain proof card
    - Display transaction hash with copy-to-clipboard button
    - Display commitment hash with copy-to-clipboard button
    - Display Etherscan link for blockchain explorer
    - Use card layout with Tailwind CSS
    - _Requirements: 6.5, 11.3, 11.4, 11.5_
  
  - [x] 12.5 Implement insurance verification instructions section
    - Display step-by-step instructions for insurance providers
    - Display instructions to verify on-chain using Smart_Contract.verifyRecord
    - Display disclaimer about proof of existence vs medical content
    - _Requirements: 11.1, 11.2, 11.6, 11.7_
  
  - [x] 12.6 Implement mobile-first responsive design
    - Use Tailwind CSS utility classes
    - Test on mobile viewport (375px width)
    - Ensure readability in WhatsApp in-app browser
    - Add dark mode support
    - _Requirements: 6.7_
  
  - [ ]* 12.7 Write property tests for verification page
    - **Property 18: Verification Page Wallet-Independent Access**
    - **Property 19: Verification Page Data Fetching**
    - **Property 20: Verification Page Status Banner Correctness**
    - **Property 21: Verification Page Content Completeness**
    - **Validates: Requirements 6.2, 6.8, 6.3, 6.4, 6.5**
  
  - [ ]* 12.8 Write unit tests for verification page component
    - Test component renders with valid data
    - Test component shows loading state
    - Test component shows error state for 404
    - Test copy-to-clipboard functionality
    - Test Etherscan link construction
    - Mock API responses
    - _Requirements: 6.1, 6.3, 6.4, 6.5_

- [ ] 13. Checkpoint - Ensure verification page tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Add optional MetaMask integration (enhancement)
  - [ ] 14.1 Create MetaMask connection component
    - Create `frontend/src/components/MetaMaskVerification.tsx`
    - Implement wallet connection with `window.ethereum`
    - Implement on-chain verification using ethers.js
    - Display on-chain record data
    - Handle wallet not installed case
    - _Requirements: 6.1 (optional enhancement)_
  
  - [ ] 14.2 Integrate MetaMask component into verification page
    - Add MetaMask component below insurance instructions
    - Make it collapsible/optional
    - Add "Advanced: Verify with MetaMask" section
    - _Requirements: 6.1 (optional enhancement)_
  
  - [ ]* 14.3 Write unit tests for MetaMask integration
    - Test wallet connection flow
    - Test on-chain verification
    - Test wallet not installed handling
    - Mock window.ethereum
    - _Requirements: 6.1 (optional enhancement)_

- [ ] 15. Implement comprehensive property-based tests
  - [ ]* 15.1 Write property test for IPFS upload timeout
    - **Property 22: IPFS Upload Timeout Handling**
    - **Validates: Requirements 9.6**
  
  - [ ]* 15.2 Write property test for IPFS pinning
    - **Property 23: IPFS Upload Pinning**
    - **Validates: Requirements 9.7**
  
  - [ ]* 15.3 Write property test for database record completeness
    - **Property 26: Database Record Persistence Completeness**
    - **Validates: Requirements 1.10**
  
  - [ ]* 15.4 Write property test for verification URL construction
    - **Property 27: Verification URL Construction**
    - **Validates: Requirements 1.7**
  
  - [ ]* 15.5 Write property test for verification URL delivery
    - **Property 28: Verification URL Delivery**
    - **Validates: Requirements 1.8**

- [ ] 16. Implement integration tests
  - [ ]* 16.1 Write end-to-end integration test
    - Test complete flow: WhatsApp → Analysis → Encryption → IPFS → Blockchain → Verification
    - Use test database and mock Twilio
    - Use local Hardhat network for blockchain
    - Use mock Pinata API
    - _Requirements: All requirements_
  
  - [ ]* 16.2 Write IPFS failure integration test
    - Test graceful degradation when IPFS fails
    - Verify patient still receives analysis
    - Verify error is logged
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ]* 16.3 Write blockchain failure integration test
    - Test graceful degradation when blockchain fails
    - Verify patient still receives analysis
    - Verify error is logged
    - _Requirements: 3.4, 3.5, 3.6_
  
  - [ ]* 16.4 Write verification page load integration test
    - Test verification page loads with valid tx_hash
    - Test data fetching from API
    - Test UI rendering
    - _Requirements: 6.1, 6.8_

- [x] 17. Update environment configuration and documentation
  - [x] 17.1 Update environment variable examples
    - Update `.env.example` with new variables
    - Update `backend/.env.example` with new variables
    - Update `frontend/env.example` with contract address
    - Add comments explaining each variable
    - _Requirements: 8.7, 9.2, 9.3_
  
  - [x] 17.2 Create deployment documentation
    - Document Pinata account setup
    - Document Ethereum RPC provider setup (Infura/Alchemy)
    - Document smart contract deployment process
    - Document environment variable configuration
    - Document database migration execution
    - _Requirements: All requirements_

- [ ] 18. Final checkpoint - Ensure all tests pass
  - Run all unit tests
  - Run all property-based tests
  - Run all integration tests
  - Run smart contract tests
  - Verify 90%+ backend coverage
  - Verify 100% smart contract coverage
  - Verify 80%+ frontend coverage
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at reasonable breaks
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows
- The implementation uses Python for backend, Solidity for smart contracts, and TypeScript/React for frontend
- All blockchain operations are wrapped in error handling to ensure graceful degradation
- Privacy is enforced at every layer: encryption, hashing, and no PII storage
