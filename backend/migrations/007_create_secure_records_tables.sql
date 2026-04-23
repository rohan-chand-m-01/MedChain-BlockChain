-- Migration 007: Secure Medical Records with Client-Side Encryption
-- 
-- Security Model:
-- - Files encrypted with AES-256 in browser
-- - AES keys encrypted with patient's Privy wallet signature
-- - Backend stores encrypted keys but CANNOT decrypt them
-- - Only patient's biometric can decrypt

-- Table: secure_medical_records
-- Stores encrypted medical records metadata
CREATE TABLE IF NOT EXISTS secure_medical_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- IPFS storage
    ipfs_hash TEXT NOT NULL,
    
    -- Encrypted AES key (backend CANNOT decrypt this)
    encrypted_aes_key TEXT NOT NULL,
    
    -- Patient's Privy wallet address
    wallet_address TEXT NOT NULL,
    
    -- File metadata
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT,
    
    -- Timestamps
    uploaded_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT unique_ipfs_hash UNIQUE (ipfs_hash)
);

-- Index for fast patient lookups
CREATE INDEX idx_secure_records_wallet ON secure_medical_records(wallet_address);
CREATE INDEX idx_secure_records_created ON secure_medical_records(created_at DESC);

-- Table: secure_access_grants
-- Stores re-encrypted AES keys for doctor access
CREATE TABLE IF NOT EXISTS secure_access_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference to medical record
    record_id UUID NOT NULL REFERENCES secure_medical_records(id) ON DELETE CASCADE,
    
    -- Doctor's Privy wallet address
    doctor_wallet_address TEXT NOT NULL,
    
    -- AES key re-encrypted for doctor's wallet
    doctor_encrypted_aes_key TEXT NOT NULL,
    
    -- Access control
    granted_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    revoked_at TIMESTAMP,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'expired', 'revoked')),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for access control
CREATE INDEX idx_secure_access_doctor ON secure_access_grants(doctor_wallet_address);
CREATE INDEX idx_secure_access_record ON secure_access_grants(record_id);
CREATE INDEX idx_secure_access_status ON secure_access_grants(status);

-- Table: encryption_audit_log
-- Audit trail for encryption/decryption events
CREATE TABLE IF NOT EXISTS encryption_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Event details
    event_type TEXT NOT NULL CHECK (event_type IN ('encrypt', 'decrypt', 'grant_access', 'revoke_access')),
    record_id UUID REFERENCES secure_medical_records(id) ON DELETE SET NULL,
    wallet_address TEXT NOT NULL,
    
    -- Metadata
    ip_address TEXT,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for audit queries
CREATE INDEX idx_audit_wallet ON encryption_audit_log(wallet_address);
CREATE INDEX idx_audit_created ON encryption_audit_log(created_at DESC);

-- Comments for documentation
COMMENT ON TABLE secure_medical_records IS 'Encrypted medical records - backend CANNOT decrypt without patient biometric';
COMMENT ON COLUMN secure_medical_records.encrypted_aes_key IS 'AES key encrypted with patient Privy wallet signature - requires Face ID/Touch ID to decrypt';
COMMENT ON TABLE secure_access_grants IS 'Doctor access grants with re-encrypted AES keys';
COMMENT ON COLUMN secure_access_grants.doctor_encrypted_aes_key IS 'AES key re-encrypted for doctor wallet - doctor can decrypt with their biometric';
