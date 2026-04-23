-- Migration: Create Encrypted Reports Tables
-- Uses Privy wallet-based encryption for lab reports
-- Zero-knowledge architecture: backend never sees plaintext

-- Table: encrypted_reports
-- Stores metadata for encrypted lab reports
CREATE TABLE IF NOT EXISTS encrypted_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id TEXT NOT NULL,  -- Privy wallet address
    ipfs_hash TEXT NOT NULL,   -- IPFS hash of encrypted data
    iv TEXT NOT NULL,          -- Initialization vector for AES decryption
    report_type TEXT NOT NULL, -- blood_test, xray, mri, etc.
    timestamp BIGINT NOT NULL, -- Report timestamp (ms since epoch)
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for fast queries
    INDEX idx_patient_id (patient_id),
    INDEX idx_timestamp (timestamp DESC)
);

-- Table: report_access_grants
-- Manages doctor access to encrypted reports
CREATE TABLE IF NOT EXISTS report_access_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES encrypted_reports(id) ON DELETE CASCADE,
    patient_id TEXT NOT NULL,     -- Patient's wallet address
    doctor_address TEXT NOT NULL, -- Doctor's wallet address
    encrypted_key TEXT NOT NULL,  -- Patient's key encrypted with doctor's key
    expires_at BIGINT NOT NULL,   -- Expiration timestamp (ms since epoch)
    granted_at TIMESTAMP DEFAULT NOW(),
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP,
    
    -- Indexes for access checks
    INDEX idx_doctor_address (doctor_address),
    INDEX idx_report_id (report_id),
    INDEX idx_expires_at (expires_at),
    
    -- Prevent duplicate grants
    UNIQUE(report_id, doctor_address)
);

-- Table: report_access_logs
-- Audit log for report access (compliance)
CREATE TABLE IF NOT EXISTS report_access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES encrypted_reports(id) ON DELETE CASCADE,
    accessor_address TEXT NOT NULL, -- Who accessed the report
    access_type TEXT NOT NULL,      -- view, download, grant, revoke
    accessed_at TIMESTAMP DEFAULT NOW(),
    ip_address TEXT,
    user_agent TEXT,
    
    -- Index for audit queries
    INDEX idx_report_access (report_id, accessed_at DESC),
    INDEX idx_accessor (accessor_address, accessed_at DESC)
);

-- Comments for documentation
COMMENT ON TABLE encrypted_reports IS 'Encrypted lab reports using Privy wallet-based encryption';
COMMENT ON TABLE report_access_grants IS 'Doctor access grants for encrypted reports';
COMMENT ON TABLE report_access_logs IS 'Audit log for report access (HIPAA compliance)';

COMMENT ON COLUMN encrypted_reports.patient_id IS 'Privy wallet address (patient)';
COMMENT ON COLUMN encrypted_reports.ipfs_hash IS 'IPFS hash of encrypted report data';
COMMENT ON COLUMN encrypted_reports.iv IS 'AES initialization vector (base64)';

COMMENT ON COLUMN report_access_grants.encrypted_key IS 'Patient encryption key encrypted with doctor public key';
COMMENT ON COLUMN report_access_grants.expires_at IS 'Access expiration timestamp (ms since epoch)';
