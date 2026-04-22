# Requirements Document

## Introduction

This document specifies requirements for the WhatsApp Blockchain Persistence + Insurance Verification feature for MediChain AI. The system enables patients to receive medical report analysis via WhatsApp, with automatic blockchain persistence for insurance verification while maintaining strict privacy guarantees. The feature transforms the current ephemeral analysis flow into a verifiable, privacy-preserving medical record system.

## Glossary

- **WhatsApp_Handler**: The FastAPI webhook endpoint that receives WhatsApp messages from Twilio
- **MedGemma_Analyzer**: The AI service that analyzes medical reports and returns risk_score, risk_level, and summary
- **AES_Encryptor**: The encryption service that encrypts medical reports using AES-256
- **IPFS_Uploader**: The service that uploads encrypted reports to IPFS via Pinata API
- **Commitment_Hash**: A keccak256 hash of (ipfs_cid + risk_score + timestamp + sha256(phone_number))
- **Smart_Contract**: The Ethereum smart contract (MediChainRecords.sol) that stores commitment hashes
- **Verification_Page**: The Next.js page at /verify/[hash] that displays blockchain proof
- **Phone_Hash**: SHA-256 hash of the patient's phone number (privacy-preserving identifier)
- **Transaction_Hash**: The Ethereum transaction hash returned after writing to the blockchain
- **Database**: PostgreSQL database storing whatsapp_records table
- **Verification_URL**: The URL sent to patients: https://medichain.app/verify/{transaction_hash}

## Requirements

### Requirement 1: WhatsApp Report Persistence

**User Story:** As a patient, I want my WhatsApp medical report analysis to be permanently stored on the blockchain, so that I can verify it for insurance claims later.

#### Acceptance Criteria

1. WHEN MedGemma_Analyzer completes analysis, THE WhatsApp_Handler SHALL encrypt the report using AES_Encryptor with AES-256
2. WHEN the report is encrypted, THE WhatsApp_Handler SHALL upload it to IPFS_Uploader via Pinata API
3. WHEN IPFS upload succeeds, THE IPFS_Uploader SHALL return an ipfs_cid
4. WHEN ipfs_cid is received, THE WhatsApp_Handler SHALL compute Commitment_Hash as keccak256(ipfs_cid + risk_score + timestamp + Phone_Hash)
5. WHEN Commitment_Hash is computed, THE WhatsApp_Handler SHALL call Smart_Contract.storeRecord(Commitment_Hash)
6. WHEN Smart_Contract write succeeds, THE Smart_Contract SHALL return Transaction_Hash
7. WHEN Transaction_Hash is received, THE WhatsApp_Handler SHALL construct Verification_URL as "https://medichain.app/verify/" + Transaction_Hash
8. WHEN Verification_URL is constructed, THE WhatsApp_Handler SHALL send it to the patient via WhatsApp
9. WHEN IPFS upload completes, THE WhatsApp_Handler SHALL delete the raw medical report from the server
10. WHEN all persistence steps complete, THE WhatsApp_Handler SHALL store Phone_Hash, ipfs_cid, Commitment_Hash, Transaction_Hash, and risk_level in Database

### Requirement 2: Privacy-Preserving Storage

**User Story:** As a patient, I want my personal information protected, so that my medical data remains private even when stored on public blockchain.

#### Acceptance Criteria

1. THE Database SHALL NOT store raw phone numbers
2. THE Database SHALL store Phone_Hash computed as SHA-256 of the phone number
3. THE Smart_Contract SHALL NOT store patient names, phone numbers, or raw medical data
4. THE Smart_Contract SHALL store only Commitment_Hash values
5. WHEN encryption key is needed, THE AES_Encryptor SHALL derive it from Phone_Hash concatenated with server_secret
6. WHEN IPFS upload completes, THE WhatsApp_Handler SHALL delete the raw medical report file from server storage
7. THE Verification_Page SHALL NOT display patient name, phone number, or raw lab values
8. THE Verification_Page SHALL display only risk_level, timestamp, and blockchain proof

### Requirement 3: Graceful Error Handling

**User Story:** As a patient, I want to always receive my medical analysis, so that blockchain failures don't prevent me from getting health information.

#### Acceptance Criteria

1. IF IPFS_Uploader fails, THEN THE WhatsApp_Handler SHALL send the analysis to the patient via WhatsApp
2. IF IPFS_Uploader fails, THEN THE WhatsApp_Handler SHALL log the error
3. IF IPFS_Uploader fails, THEN THE WhatsApp_Handler SHALL skip blockchain persistence
4. IF Smart_Contract write fails, THEN THE WhatsApp_Handler SHALL send the analysis to the patient via WhatsApp
5. IF Smart_Contract write fails, THEN THE WhatsApp_Handler SHALL log the error
6. IF Smart_Contract write fails, THEN THE WhatsApp_Handler SHALL skip blockchain persistence
7. THE WhatsApp_Handler SHALL NOT block patient analysis due to IPFS failures
8. THE WhatsApp_Handler SHALL NOT block patient analysis due to Smart_Contract failures

### Requirement 4: Smart Contract Record Storage

**User Story:** As an insurance provider, I want to verify medical records on the blockchain, so that I can confirm authenticity without accessing private medical data.

#### Acceptance Criteria

1. THE Smart_Contract SHALL define a Record struct with fields: commitmentHash, timestamp, exists
2. THE Smart_Contract SHALL maintain a mapping from Transaction_Hash to Record
3. WHEN storeRecord is called, THE Smart_Contract SHALL create a new Record with the provided Commitment_Hash
4. WHEN storeRecord is called, THE Smart_Contract SHALL set Record.timestamp to block.timestamp
5. WHEN storeRecord is called, THE Smart_Contract SHALL set Record.exists to true
6. WHEN storeRecord is called, THE Smart_Contract SHALL emit RecordStored event with Commitment_Hash and timestamp
7. THE Smart_Contract SHALL provide verifyRecord function that accepts Transaction_Hash
8. WHEN verifyRecord is called with valid Transaction_Hash, THE Smart_Contract SHALL return true
9. WHEN verifyRecord is called with invalid Transaction_Hash, THE Smart_Contract SHALL return false

### Requirement 5: Verification Endpoint

**User Story:** As a patient, I want to access my verification page via the URL sent on WhatsApp, so that I can view blockchain proof of my medical record.

#### Acceptance Criteria

1. THE WhatsApp_Handler SHALL expose GET endpoint at /api/verify/{tx_hash}
2. WHEN /api/verify/{tx_hash} is called, THE WhatsApp_Handler SHALL query Database for record matching Transaction_Hash
3. WHEN record is found, THE WhatsApp_Handler SHALL query Smart_Contract.verifyRecord(tx_hash)
4. WHEN Smart_Contract returns true, THE WhatsApp_Handler SHALL return JSON with verification status "verified"
5. WHEN Smart_Contract returns false, THE WhatsApp_Handler SHALL return JSON with verification status "not_found"
6. WHEN record is found, THE WhatsApp_Handler SHALL return risk_level, timestamp, ipfs_cid, and Commitment_Hash
7. THE WhatsApp_Handler SHALL NOT return Phone_Hash or any patient identifiers
8. WHEN record is not found in Database, THE WhatsApp_Handler SHALL return 404 status

### Requirement 6: Verification Page UI

**User Story:** As a patient, I want a mobile-friendly verification page, so that I can easily view my blockchain proof on my phone.

#### Acceptance Criteria

1. THE Verification_Page SHALL be accessible at /verify/[hash] route
2. THE Verification_Page SHALL work without wallet connection
3. THE Verification_Page SHALL display a verification status banner (green for verified, red for not found)
4. THE Verification_Page SHALL display a record details card showing risk_level and timestamp
5. THE Verification_Page SHALL display a blockchain proof card showing Transaction_Hash and Commitment_Hash
6. THE Verification_Page SHALL display an insurance verification section with instructions
7. THE Verification_Page SHALL use mobile-first responsive design with Tailwind CSS
8. THE Verification_Page SHALL fetch data from /api/verify/{tx_hash} endpoint on page load

### Requirement 7: Database Schema

**User Story:** As a system administrator, I want a database table to store WhatsApp record metadata, so that verification lookups are fast and efficient.

#### Acceptance Criteria

1. THE Database SHALL contain a table named whatsapp_records
2. THE whatsapp_records table SHALL have column phone_hash of type VARCHAR(64) storing SHA-256 hash
3. THE whatsapp_records table SHALL have column ipfs_cid of type VARCHAR(100) storing IPFS content identifier
4. THE whatsapp_records table SHALL have column commitment_hash of type VARCHAR(66) storing keccak256 hash
5. THE whatsapp_records table SHALL have column tx_hash of type VARCHAR(66) storing Ethereum transaction hash
6. THE whatsapp_records table SHALL have column risk_level of type VARCHAR(20) storing risk assessment
7. THE whatsapp_records table SHALL have column created_at of type TIMESTAMP storing record creation time
8. THE whatsapp_records table SHALL have column deleted_at of type TIMESTAMP storing soft deletion time
9. THE whatsapp_records table SHALL have index on tx_hash for fast verification lookups
10. THE whatsapp_records table SHALL have index on phone_hash for patient record queries

### Requirement 8: Encryption and Hashing

**User Story:** As a security engineer, I want strong encryption and hashing, so that patient data is protected at rest and in transit.

#### Acceptance Criteria

1. THE AES_Encryptor SHALL use AES-256 encryption algorithm
2. WHEN encrypting a report, THE AES_Encryptor SHALL derive encryption key from Phone_Hash concatenated with server_secret
3. THE AES_Encryptor SHALL use a unique initialization vector (IV) for each encryption
4. THE AES_Encryptor SHALL prepend the IV to the encrypted data
5. WHEN computing Phone_Hash, THE WhatsApp_Handler SHALL use SHA-256 algorithm
6. WHEN computing Commitment_Hash, THE WhatsApp_Handler SHALL use keccak256 algorithm
7. THE server_secret SHALL be stored in environment variable SERVER_ENCRYPTION_SECRET
8. THE server_secret SHALL be at least 32 bytes of cryptographically random data

### Requirement 9: IPFS Integration

**User Story:** As a developer, I want seamless IPFS integration via Pinata, so that encrypted reports are stored on decentralized storage.

#### Acceptance Criteria

1. THE IPFS_Uploader SHALL use Pinata API for IPFS uploads
2. WHEN uploading to IPFS, THE IPFS_Uploader SHALL use Pinata API key from environment variable PINATA_API_KEY
3. WHEN uploading to IPFS, THE IPFS_Uploader SHALL use Pinata secret key from environment variable PINATA_SECRET_KEY
4. WHEN upload succeeds, THE IPFS_Uploader SHALL return ipfs_cid in format "Qm..." or "bafy..."
5. THE IPFS_Uploader SHALL set timeout of 30 seconds for upload requests
6. IF upload times out, THE IPFS_Uploader SHALL raise timeout exception
7. THE IPFS_Uploader SHALL pin uploaded files to ensure persistence

### Requirement 10: Smart Contract Testing

**User Story:** As a blockchain developer, I want comprehensive smart contract tests, so that I can ensure the contract works correctly before deployment.

#### Acceptance Criteria

1. THE Smart_Contract test suite SHALL test storeRecord function with valid Commitment_Hash
2. THE Smart_Contract test suite SHALL test verifyRecord function returns true for existing records
3. THE Smart_Contract test suite SHALL test verifyRecord function returns false for non-existent records
4. THE Smart_Contract test suite SHALL test RecordStored event is emitted with correct parameters
5. THE Smart_Contract test suite SHALL test multiple records can be stored sequentially
6. THE Smart_Contract test suite SHALL test timestamp is correctly set to block.timestamp
7. THE Smart_Contract test suite SHALL test Record.exists is set to true after storage
8. THE Smart_Contract test suite SHALL use Hardhat testing framework
9. THE Smart_Contract test suite SHALL achieve 100% code coverage for new functions

### Requirement 11: Insurance Verification Instructions

**User Story:** As an insurance provider, I want clear instructions on the verification page, so that I know how to verify the medical record authenticity.

#### Acceptance Criteria

1. THE Verification_Page SHALL display a section titled "Insurance Verification"
2. THE Verification_Page SHALL display step-by-step instructions for insurance providers
3. THE Verification_Page SHALL display the Transaction_Hash in a copyable format
4. THE Verification_Page SHALL display the Commitment_Hash in a copyable format
5. THE Verification_Page SHALL display a link to Etherscan for blockchain explorer verification
6. THE Verification_Page SHALL display instructions to verify the record on-chain using Smart_Contract.verifyRecord
7. THE Verification_Page SHALL display a disclaimer that the page shows proof of existence, not medical content

### Requirement 12: Round-Trip Verification Property

**User Story:** As a quality assurance engineer, I want to verify the encryption round-trip property, so that I can ensure encrypted data can be correctly decrypted.

#### Acceptance Criteria

1. FOR ALL valid medical reports, THE AES_Encryptor SHALL satisfy: decrypt(encrypt(report, key), key) equals report
2. THE AES_Encryptor test suite SHALL test encryption and decryption with sample medical reports
3. THE AES_Encryptor test suite SHALL test encryption produces different ciphertext for same plaintext with different IVs
4. THE AES_Encryptor test suite SHALL test decryption fails with incorrect key
5. THE AES_Encryptor test suite SHALL test decryption fails with corrupted ciphertext
