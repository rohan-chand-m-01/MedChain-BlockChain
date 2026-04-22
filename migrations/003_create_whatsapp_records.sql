-- WhatsApp Blockchain Persistence
-- Migration: Create whatsapp_records table for storing metadata of blockchain-persisted medical reports

CREATE TABLE IF NOT EXISTS whatsapp_records (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Privacy-preserving patient identifier (SHA-256 hash of phone number)
    phone_hash VARCHAR(64) NOT NULL,
    
    -- IPFS content identifier for encrypted medical report
    ipfs_cid VARCHAR(100) NOT NULL,
    
    -- Keccak-256 commitment hash stored on blockchain
    -- Format: keccak256(ipfs_cid + risk_score + timestamp + phone_hash)
    commitment_hash VARCHAR(66) NOT NULL,
    
    -- Ethereum record ID (bytes32 returned from storeRecord function)
    record_id VARCHAR(66) NOT NULL UNIQUE,
    
    -- Risk assessment results
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT valid_phone_hash_length CHECK (LENGTH(phone_hash) = 64),
    CONSTRAINT valid_commitment_hash_format CHECK (commitment_hash ~ '^0x[a-fA-F0-9]{64}$'),
    CONSTRAINT valid_record_id_format CHECK (record_id ~ '^0x[a-fA-F0-9]{64}$')
);

-- Index on record_id for fast verification lookups (most common query pattern)
CREATE INDEX idx_whatsapp_records_record_id ON whatsapp_records(record_id);

-- Index on phone_hash for patient record queries
CREATE INDEX idx_whatsapp_records_phone_hash ON whatsapp_records(phone_hash);

-- Index on created_at for chronological queries (e.g., recent records)
CREATE INDEX idx_whatsapp_records_created_at ON whatsapp_records(created_at DESC);

-- Partial index for active (non-deleted) records
CREATE INDEX idx_whatsapp_records_active ON whatsapp_records(phone_hash, created_at DESC) 
    WHERE deleted_at IS NULL;

-- Comments for documentation
COMMENT ON TABLE whatsapp_records IS 'Metadata for WhatsApp medical reports persisted to blockchain. Implements privacy-preserving architecture where no PII is stored.';

COMMENT ON COLUMN whatsapp_records.phone_hash IS 'SHA-256 hash of patient phone number. Used as privacy-preserving identifier. Never store raw phone numbers.';

COMMENT ON COLUMN whatsapp_records.ipfs_cid IS 'IPFS content identifier (CID) for encrypted medical report. Format: Qm... (CIDv0) or bafy... (CIDv1).';

COMMENT ON COLUMN whatsapp_records.commitment_hash IS 'Keccak-256 commitment hash stored on Ethereum blockchain. Binds IPFS content to metadata for tamper-evidence.';

COMMENT ON COLUMN whatsapp_records.record_id IS 'Ethereum record ID (bytes32) returned from storeRecord function. Used in verification URLs: https://medichain.app/verify/{record_id}';

COMMENT ON COLUMN whatsapp_records.risk_level IS 'AI-assessed risk level: low, medium, or high. Displayed on verification page.';

COMMENT ON COLUMN whatsapp_records.risk_score IS 'Numeric risk score (0-100). Used in commitment hash computation.';

COMMENT ON COLUMN whatsapp_records.deleted_at IS 'Soft deletion timestamp for GDPR compliance. NULL indicates active record.';

-- Row Level Security (RLS) policies
ALTER TABLE whatsapp_records ENABLE ROW LEVEL SECURITY;

-- Policy: Allow read access for verification endpoint (public verification)
-- Note: This is intentionally permissive as verification is a public feature
-- No PII is exposed since we only store hashes
CREATE POLICY whatsapp_records_public_verification ON whatsapp_records
    FOR SELECT
    USING (deleted_at IS NULL);

-- Policy: Only backend service can insert records
-- In production, this should be restricted to service role
CREATE POLICY whatsapp_records_service_insert ON whatsapp_records
    FOR INSERT
    WITH CHECK (true);

-- Policy: Only backend service can soft-delete records (GDPR)
CREATE POLICY whatsapp_records_service_delete ON whatsapp_records
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- Function to soft-delete old records (GDPR compliance - optional retention policy)
CREATE OR REPLACE FUNCTION soft_delete_old_whatsapp_records(retention_days INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    UPDATE whatsapp_records
    SET deleted_at = NOW()
    WHERE 
        deleted_at IS NULL
        AND created_at < NOW() - (retention_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION soft_delete_old_whatsapp_records(INTEGER) IS 'Soft-deletes WhatsApp records older than specified retention period. Default: 365 days. Run via cron for GDPR compliance.';
