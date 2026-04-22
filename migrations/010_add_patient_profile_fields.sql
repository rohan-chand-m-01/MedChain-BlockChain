-- Add additional patient profile fields
-- Run this migration to add gender, blood type, allergies, and emergency contact fields

-- Add new columns to patient_profiles table
ALTER TABLE patient_profiles 
ADD COLUMN IF NOT EXISTS gender VARCHAR(50),
ADD COLUMN IF NOT EXISTS blood_type VARCHAR(10),
ADD COLUMN IF NOT EXISTS allergies TEXT,
ADD COLUMN IF NOT EXISTS emergency_contact VARCHAR(255),
ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(50);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_patient_profiles_full_name ON patient_profiles(full_name);
CREATE INDEX IF NOT EXISTS idx_patient_profiles_blood_type ON patient_profiles(blood_type);

-- Add comment to table
COMMENT ON COLUMN patient_profiles.gender IS 'Patient gender (male, female, other, prefer_not_to_say)';
COMMENT ON COLUMN patient_profiles.blood_type IS 'Patient blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)';
COMMENT ON COLUMN patient_profiles.allergies IS 'Known allergies (medications, food, etc.)';
COMMENT ON COLUMN patient_profiles.emergency_contact IS 'Emergency contact person name';
COMMENT ON COLUMN patient_profiles.emergency_contact_phone IS 'Emergency contact phone number';
