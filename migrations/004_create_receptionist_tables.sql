-- AI Receptionist Database Schema
-- Tables for appointment booking, patient registration, queue management, and payments

-- Patient Profiles (for registration via WhatsApp)
CREATE TABLE IF NOT EXISTS patient_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_hash VARCHAR(64) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    age INT,
    gender VARCHAR(10),
    medical_conditions TEXT,
    current_medications TEXT,
    allergies TEXT,
    emergency_contact VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Clinic/Doctor Information
CREATE TABLE IF NOT EXISTS clinics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    working_hours JSONB, -- {"monday": {"start": "09:00", "end": "18:00"}, ...}
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID REFERENCES clinics(id),
    wallet_address VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(255),
    consultation_fee DECIMAL(10,2),
    available_slots JSONB, -- {"monday": ["10:00", "11:00", "14:00", ...], ...}
    created_at TIMESTAMP DEFAULT NOW()
);

-- Appointments (enhanced version)
CREATE TABLE IF NOT EXISTS appointments_v2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_phone_hash VARCHAR(64) NOT NULL,
    patient_name VARCHAR(255),
    doctor_id UUID REFERENCES doctors(id),
    clinic_id UUID REFERENCES clinics(id),
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, checked_in, in_progress, completed, cancelled, no_show
    reason TEXT,
    notes TEXT,
    queue_position INT,
    check_in_time TIMESTAMP,
    called_time TIMESTAMP,
    completed_time TIMESTAMP,
    meeting_link TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Clinic Queue (real-time queue management)
CREATE TABLE IF NOT EXISTS clinic_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID REFERENCES clinics(id),
    doctor_id UUID REFERENCES doctors(id),
    appointment_id UUID REFERENCES appointments_v2(id),
    patient_phone_hash VARCHAR(64) NOT NULL,
    patient_name VARCHAR(255),
    queue_position INT NOT NULL,
    status VARCHAR(20) DEFAULT 'waiting', -- waiting, called, in_progress, completed, skipped
    check_in_time TIMESTAMP DEFAULT NOW(),
    called_time TIMESTAMP,
    completed_time TIMESTAMP,
    estimated_wait_minutes INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payment Records
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID REFERENCES appointments_v2(id),
    patient_phone_hash VARCHAR(64) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    payment_method VARCHAR(20), -- upi, card, cash, insurance
    upi_transaction_id VARCHAR(255),
    upi_link TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, failed, refunded
    receipt_url TEXT,
    blockchain_tx_hash VARCHAR(66),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Conversation State (for multi-step WhatsApp flows)
CREATE TABLE IF NOT EXISTS conversation_state (
    phone_hash VARCHAR(64) PRIMARY KEY,
    current_flow VARCHAR(50), -- booking, registration, checkin, payment, medical_query
    current_step INT DEFAULT 0,
    context JSONB, -- stores temporary data for the conversation
    language VARCHAR(5) DEFAULT 'en', -- en, kn
    last_message_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reminders (for follow-ups and appointment reminders)
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_phone_hash VARCHAR(64) NOT NULL,
    appointment_id UUID REFERENCES appointments_v2(id),
    reminder_type VARCHAR(50), -- appointment_reminder, follow_up, medication, lab_result
    message TEXT NOT NULL,
    scheduled_for TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_patient_profiles_phone ON patient_profiles(phone_hash);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments_v2(patient_phone_hash);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments_v2(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments_v2(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments_v2(status);
CREATE INDEX IF NOT EXISTS idx_queue_clinic ON clinic_queue(clinic_id);
CREATE INDEX IF NOT EXISTS idx_queue_status ON clinic_queue(status);
CREATE INDEX IF NOT EXISTS idx_payments_appointment ON payments(appointment_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_reminders_scheduled ON reminders(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status);

-- Insert sample clinic and doctors for demo
INSERT INTO clinics (id, name, address, phone, email, working_hours) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'ABC Medical Center', '123 MG Road, Bangalore, Karnataka 560001', '+91-80-12345678', 'contact@abcmedical.com', 
 '{"monday": {"start": "09:00", "end": "18:00"}, "tuesday": {"start": "09:00", "end": "18:00"}, "wednesday": {"start": "09:00", "end": "18:00"}, "thursday": {"start": "09:00", "end": "18:00"}, "friday": {"start": "09:00", "end": "18:00"}, "saturday": {"start": "09:00", "end": "14:00"}}'::jsonb)
ON CONFLICT DO NOTHING;

INSERT INTO doctors (id, clinic_id, name, specialty, consultation_fee, available_slots) VALUES
('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'Dr. Sharma', 'General Physician', 500.00,
 '{"monday": ["10:00", "11:00", "14:00", "15:00", "16:00"], "tuesday": ["10:00", "11:00", "14:00", "15:00", "16:00"], "wednesday": ["10:00", "11:00", "14:00", "15:00", "16:00"], "thursday": ["10:00", "11:00", "14:00", "15:00", "16:00"], "friday": ["10:00", "11:00", "14:00", "15:00", "16:00"]}'::jsonb),
('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', 'Dr. Patel', 'Cardiologist', 800.00,
 '{"monday": ["10:00", "11:30", "14:00", "16:00"], "wednesday": ["10:00", "11:30", "14:00", "16:00"], "friday": ["10:00", "11:30", "14:00", "16:00"]}'::jsonb),
('660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440000', 'Dr. Kumar', 'Endocrinologist', 700.00,
 '{"tuesday": ["10:00", "11:00", "14:00", "15:00"], "thursday": ["10:00", "11:00", "14:00", "15:00"], "saturday": ["10:00", "11:00"]}'::jsonb)
ON CONFLICT DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE patient_profiles IS 'Patient registration data collected via WhatsApp';
COMMENT ON TABLE appointments_v2 IS 'Enhanced appointments table with queue management';
COMMENT ON TABLE clinic_queue IS 'Real-time queue tracking for walk-ins and appointments';
COMMENT ON TABLE payments IS 'Payment records with UPI and blockchain integration';
COMMENT ON TABLE conversation_state IS 'Tracks multi-step WhatsApp conversation flows';
COMMENT ON TABLE reminders IS 'Scheduled reminders for appointments and follow-ups';
