-- Secure Time-Bound Access Control System
-- Migration: Create access_grants table

CREATE TABLE IF NOT EXISTS access_grants (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Parties involved
    patient_wallet TEXT NOT NULL,
    doctor_wallet TEXT NOT NULL,
    analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,
    
    -- Access scope
    grant_type TEXT NOT NULL CHECK (grant_type IN ('single_file', 'all_files')),
    
    -- Encrypted key (wrapped with doctor's public key)
    -- SECURITY: Server cannot decrypt this - only doctor with private key can
    wrapped_encryption_key TEXT NOT NULL,
    key_wrapping_algorithm TEXT DEFAULT 'RSA-OAEP-SHA256',
    
    -- Time bounds
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accessed_at TIMESTAMP WITH TIME ZONE, -- First access time
    last_accessed_at TIMESTAMP WITH TIME ZONE, -- Last access time
    
    -- Access limits
    access_count INTEGER DEFAULT 0 CHECK (access_count >= 0),
    max_access_count INTEGER CHECK (max_access_count IS NULL OR max_access_count > 0),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_by TEXT, -- patient_wallet or 'system'
    revocation_reason TEXT,
    
    -- Audit trail
    ip_address TEXT,
    user_agent TEXT,
    
    -- Constraints
    CONSTRAINT valid_expiry CHECK (expires_at > granted_at),
    CONSTRAINT valid_grant_type_with_analysis CHECK (
        (grant_type = 'single_file' AND analysis_id IS NOT NULL) OR
        (grant_type = 'all_files')
    )
);

-- Indexes for performance
CREATE INDEX idx_access_grants_doctor_active 
    ON access_grants(doctor_wallet, is_active) 
    WHERE is_active = TRUE;

CREATE INDEX idx_access_grants_patient 
    ON access_grants(patient_wallet);

CREATE INDEX idx_access_grants_analysis 
    ON access_grants(analysis_id) 
    WHERE analysis_id IS NOT NULL;

CREATE INDEX idx_access_grants_expiry 
    ON access_grants(expires_at) 
    WHERE is_active = TRUE;

-- Comments for documentation
COMMENT ON TABLE access_grants IS 'Time-bound access control for encrypted medical files. Implements zero-knowledge architecture where server never sees unwrapped encryption keys.';

COMMENT ON COLUMN access_grants.wrapped_encryption_key IS 'File encryption key wrapped (encrypted) with doctor''s RSA public key. Only doctor can unwrap with their private key.';

COMMENT ON COLUMN access_grants.grant_type IS 'single_file: Access to one specific analysis. all_files: Access to all patient files (time-bound).';

COMMENT ON COLUMN access_grants.max_access_count IS 'Optional limit on number of times doctor can access the file. NULL means unlimited.';

-- Row Level Security (RLS) policies
ALTER TABLE access_grants ENABLE ROW LEVEL SECURITY;

-- Policy: Patients can view their own grants
CREATE POLICY patient_view_own_grants ON access_grants
    FOR SELECT
    USING (patient_wallet = current_setting('request.jwt.claims', true)::json->>'sub');

-- Policy: Doctors can view grants given to them
CREATE POLICY doctor_view_granted_access ON access_grants
    FOR SELECT
    USING (doctor_wallet = current_setting('request.jwt.claims', true)::json->>'sub');

-- Policy: Patients can create grants
CREATE POLICY patient_create_grants ON access_grants
    FOR INSERT
    WITH CHECK (patient_wallet = current_setting('request.jwt.claims', true)::json->>'sub');

-- Policy: Patients can revoke their own grants
CREATE POLICY patient_revoke_grants ON access_grants
    FOR UPDATE
    USING (patient_wallet = current_setting('request.jwt.claims', true)::json->>'sub');

-- Policy: Doctors can update access tracking (log access)
CREATE POLICY doctor_log_access ON access_grants
    FOR UPDATE
    USING (
        doctor_wallet = current_setting('request.jwt.claims', true)::json->>'sub'
        AND is_active = TRUE
    );

-- Function to auto-expire grants (run via cron job)
CREATE OR REPLACE FUNCTION expire_old_grants()
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    UPDATE access_grants
    SET 
        is_active = FALSE,
        revoked_at = NOW(),
        revoked_by = 'system',
        revocation_reason = 'expired'
    WHERE 
        is_active = TRUE
        AND expires_at < NOW();
    
    GET DIAGNOSTICS expired_count = ROW_COUNT;
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION expire_old_grants() IS 'Automatically expires grants past their expiry time. Run this via cron job every hour.';

-- Trigger to validate access count doesn't exceed max
CREATE OR REPLACE FUNCTION check_access_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.max_access_count IS NOT NULL AND NEW.access_count >= NEW.max_access_count THEN
        NEW.is_active := FALSE;
        NEW.revoked_at := NOW();
        NEW.revoked_by := 'system';
        NEW.revocation_reason := 'access_limit_reached';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_access_limit
    BEFORE UPDATE ON access_grants
    FOR EACH ROW
    WHEN (NEW.access_count IS DISTINCT FROM OLD.access_count)
    EXECUTE FUNCTION check_access_limit();

COMMENT ON TRIGGER enforce_access_limit ON access_grants IS 'Automatically revokes grant when access count reaches max_access_count.';
