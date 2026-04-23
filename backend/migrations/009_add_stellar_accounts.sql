-- Add Stellar account fields to users table
-- This links Privy user ID to Stellar keypair

ALTER TABLE users ADD COLUMN IF NOT EXISTS stellar_public_key TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stellar_encrypted_secret TEXT;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_stellar_public_key ON users(stellar_public_key);

-- Add Stellar transaction hash to medical records
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS stellar_tx_hash TEXT;

-- Add index for transaction lookups
CREATE INDEX IF NOT EXISTS idx_medical_records_stellar_tx ON medical_records(stellar_tx_hash);

COMMENT ON COLUMN users.stellar_public_key IS 'Stellar public key (address) for blockchain transactions';
COMMENT ON COLUMN users.stellar_encrypted_secret IS 'Encrypted Stellar secret key (never exposed to client)';
COMMENT ON COLUMN medical_records.stellar_tx_hash IS 'Stellar transaction hash for on-chain proof';
