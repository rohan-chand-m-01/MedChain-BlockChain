# WhatsApp Notification System - Implementation Complete

## Overview
Doctors now receive instant WhatsApp notifications when patients grant them access to medical records.

## How It Works

### 1. Patient Grants Access
When a patient grants access to a doctor via the UI:
```typescript
// Frontend calls
POST /api/access-grants/simple
{
  patient_wallet: "0x...",
  doctor_wallet: "0x...",
  analysis_id: "uuid",
  expires_in_hours: 24
}
```

### 2. Backend Processes Grant
The backend (`backend/routes/access_control.py`):
1. Creates/updates the access grant in database
2. Looks up doctor's WhatsApp phone number from `doctor_profiles`
3. Looks up patient's name from `patient_profiles`
4. Fetches analysis details (file name, risk score, summary)
5. Sends WhatsApp notification via Twilio

### 3. Doctor Receives Notification
Doctor gets a WhatsApp message like:

```
🏥 NEW MEDICAL RECORD ACCESS

Hello Dr. Smith,

Patient John Doe has granted you access to their medical records.

📄 Document: Lab Report - Blood Test
⚠️ Risk Level: MEDIUM (Risk Score: 65)
⏰ Access Expires: 24 hours

🔗 View full records: https://medichain.app/doctor

_Powered by MediChain AI_
```

## Code Changes

### File: `backend/routes/access_control.py`

**Added:**
1. Import `DoctorNotifier` service
2. Helper function `_send_access_notification()` 
3. Notification call in `create_simple_access_grant()`

**Key Features:**
- ✅ Looks up doctor's WhatsApp number from profile
- ✅ Looks up patient's name from profile
- ✅ Fetches document details from analysis
- ✅ Sends formatted WhatsApp message
- ✅ Handles errors gracefully (doesn't fail grant if notification fails)
- ✅ Logs success/failure for debugging

## Notification Content

The WhatsApp message includes:
- **Doctor's name** (personalized greeting)
- **Patient's name** (who granted access)
- **Document name** (e.g., "Lab Report - Blood Test")
- **Risk level** (LOW/MEDIUM/HIGH with emoji)
- **Risk score** (0-100)
- **Access duration** (hours until expiry)
- **Link to dashboard** (to view records)

## Prerequisites

For notifications to work, both parties must have profiles set up:

### Doctor Must Have:
- Profile created at `/profile`
- WhatsApp phone number in format: `+1234567890`
- Phone stored as: `whatsapp:+1234567890` (auto-formatted)

### Patient Must Have:
- Profile created at `/profile`
- Full name entered

## Testing

### 1. Setup Profiles
```bash
# Doctor logs in and goes to /profile
# Enters: Name, WhatsApp number (+1234567890)
# Saves profile

# Patient logs in and goes to /profile  
# Enters: Full name, WhatsApp number
# Saves profile
```

### 2. Grant Access
```bash
# Patient uploads medical report
# Patient grants access to doctor (24 hours)
# System automatically sends WhatsApp notification
```

### 3. Check Logs
```bash
# Backend terminal shows:
✓ WhatsApp notification sent to doctor 0x...
```

### 4. Doctor Receives Message
- Doctor's phone receives WhatsApp message
- Message includes all details
- Doctor can click link to view dashboard

## Error Handling

The system handles these scenarios gracefully:

1. **Doctor has no phone number** → Logs warning, grant still succeeds
2. **Patient has no name** → Uses "Unknown Patient"
3. **Analysis not found** → Logs warning, grant still succeeds
4. **Twilio API fails** → Logs error, grant still succeeds
5. **Network error** → Logs error, grant still succeeds

**Important:** Access grants NEVER fail due to notification errors. Notifications are best-effort.

## Environment Variables Required

In `backend/.env`:
```env
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
PUBLIC_WEBHOOK_URL=https://your-domain.com
```

## Database Tables Used

1. **doctor_profiles** - Stores doctor's WhatsApp number
2. **patient_profiles** - Stores patient's name
3. **analyses** - Stores document details
4. **access_grants** - Stores access permissions

## Real-time Dashboard Updates

To show new grants immediately on doctor dashboard, add polling:

```typescript
// In doctor dashboard
useEffect(() => {
  const interval = setInterval(async () => {
    const grants = await fetch('/api/access-grants/doctor/active?doctor_wallet=...');
    setGrants(await grants.json());
  }, 10000); // Poll every 10 seconds
  
  return () => clearInterval(interval);
}, []);
```

## Demo Flow

1. **Patient** uploads medical report → Gets analysis
2. **Patient** clicks "Grant Access to Doctor" → Selects doctor, sets 24 hours
3. **System** creates access grant in database
4. **System** sends WhatsApp notification to doctor
5. **Doctor** receives WhatsApp message on phone
6. **Doctor** opens dashboard → Sees new grant immediately
7. **Doctor** clicks on grant → Views patient's medical records
8. **System** logs access for audit trail

## Benefits

- ✅ **Instant notifications** - Doctors know immediately when they have new records to review
- ✅ **No app required** - Works via WhatsApp (everyone has it)
- ✅ **Rich context** - Includes patient name, risk level, document type
- ✅ **Time-bound** - Shows expiry time so doctor knows urgency
- ✅ **Direct link** - One click to view records
- ✅ **Audit trail** - All notifications logged
- ✅ **Graceful degradation** - Works even if notification fails

## Next Steps

1. Add profile setup prompt on first login
2. Add "Profile" link to navigation
3. Add real-time polling to doctor dashboard
4. Add notification preferences (email, SMS, WhatsApp)
5. Add notification history view
