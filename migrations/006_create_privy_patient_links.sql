-- Create privy_patient_links table for linking Privy MPC wallets to patient records
-- This enables the "claim your wallet" flow for WhatsApp users

CREATE TABLE IF NOT EXISTS privy_patient_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    privy_id TEXT NOT NULL UNIQUE,
    patient_wallet TEXT NOT NULL,
    linked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_privy_patient_links_privy_id ON privy_patient_links(privy_id);
CREATE INDEX IF NOT EXISTS idx_privy_patient_links_patient_wallet ON privy_patient_links(patient_wallet);
CREATE INDEX IF NOT EXISTS idx_privy_patient_links_linked_at ON privy_patient_links(linked_at DESC);

-- Add comments
COMMENT ON TABLE privy_patient_links IS 'Links Privy MPC wallet users to their patient records (for WhatsApp → Web app migration)';
COMMENT ON COLUMN privy_patient_links.privy_id IS 'Privy user ID (format: did:privy:...)';
COMMENT ON COLUMN privy_patient_links.patient_wallet IS 'Original custodial wallet address from WhatsApp';
COMMENT ON COLUMN privy_patient_links.linked_at IS 'When the user claimed their wallet via Privy';
