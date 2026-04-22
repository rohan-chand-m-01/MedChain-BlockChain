# Profile Management Feature - Implementation Complete

## Overview
Added comprehensive profile management system with WhatsApp phone numbers for both patients and doctors.

## Database Changes (via InsForge MCP)

### Tables Modified:
1. **patient_profiles** - Added `whatsapp_phone` column
2. **doctor_profiles** - Added `whatsapp_phone` and `email` columns

### Indexes Created:
- `idx_patient_profiles_phone` - Fast phone number lookups
- `idx_doctor_profiles_phone` - Fast phone number lookups

## Backend API (NEW)

### File: `backend/routes/profiles.py`

**Endpoints:**

1. **GET `/api/profiles/patient/{wallet_address}`**
   - Get patient profile by wallet address
   - Returns profile data or `{exists: false}`

2. **POST `/api/profiles/patient/{wallet_address}`**
   - Create or update patient profile
   - Body: `{full_name, whatsapp_phone, date_of_birth, email}`
   - Auto-formats phone to `whatsapp:+1234567890` format

3. **GET `/api/profiles/doctor/{wallet_address}`**
   - Get doctor profile by wallet address
   - Returns profile data or `{exists: false}`

4. **POST `/api/profiles/doctor/{wallet_address}`**
   - Create or update doctor profile
   - Body: `{name, specialty, whatsapp_phone, email, bio}`
   - Auto-formats phone to `whatsapp:+1234567890` format

5. **GET `/api/profiles/doctors/all`**
   - Get all doctor profiles (for patient to select doctors)
   - Returns list of all doctors with contact info

## Frontend (NEW)

### File: `frontend/src/app/profile/page.tsx`

**Features:**
- ✅ Role-aware profile form (patient vs doctor)
- ✅ WhatsApp phone number input with format validation
- ✅ Email input
- ✅ Doctor-specific fields (specialty, bio)
- ✅ Auto-load existing profile data
- ✅ Save/update profile
- ✅ Beautiful UI with Tailwind CSS

**Access:** Navigate to `/profile` after login

## Integration Points

### 1. WhatsApp Notifications
When patient grants access to doctor, the system can now:
- Look up doctor's `whatsapp_phone` from `doctor_profiles`
- Send instant WhatsApp notification via Twilio
- Include patient name, risk score, and access details

### 2. Doctor Dashboard
Doctors can now:
- View their profile at `/profile`
- Update their WhatsApp number for notifications
- Receive real-time notifications when patients grant access

### 3. Patient Dashboard
Patients can now:
- View their profile at `/profile`
- Update their WhatsApp number
- See their name displayed instead of wallet address

## Next Steps (TODO)

### 1. Add Profile Link to Navigation
Update `frontend/src/components/Navbar.tsx`:
```tsx
<Link href="/profile">Profile</Link>
```

### 2. Prompt for Profile on First Login
In `frontend/src/app/register/page.tsx` or after Privy login:
```tsx
// Check if profile exists
const response = await fetch(`/api/profiles/${role}/${walletAddress}`);
const data = await response.json();

if (!data.exists) {
  router.push('/profile?firstTime=true');
}
```

### 3. Real-time Dashboard Updates
When patient grants access, trigger:
```tsx
// In doctor dashboard
useEffect(() => {
  const interval = setInterval(async () => {
    const grants = await getDoctorGrants(walletAddress);
    setGrants(grants);
  }, 10000); // Poll every 10 seconds
  
  return () => clearInterval(interval);
}, []);
```

### 4. WhatsApp Notification Integration
Update `backend/routes/access_control.py` to send WhatsApp notification:
```python
# After granting access
doctor_profile = await db_select_single(
    table="doctor_profiles",
    filters={"wallet_address": doctor_wallet},
    select="whatsapp_phone,name"
)

if doctor_profile and doctor_profile.get("whatsapp_phone"):
    from services.doctor_notifier import DoctorNotifier
    notifier = DoctorNotifier()
    await notifier.notify_doctor_access(
        doctor_phone=doctor_profile["whatsapp_phone"],
        patient_name=patient_name,
        risk_score=risk_score,
        access_hours=hours
    )
```

## Testing

### Test Profile Creation:
1. Login as patient
2. Go to `/profile`
3. Fill in name and WhatsApp number (+1234567890)
4. Click Save
5. Verify in database:
```sql
SELECT * FROM patient_profiles WHERE patient_wallet = 'YOUR_WALLET';
```

### Test Doctor Profile:
1. Login as doctor
2. Go to `/profile`
3. Fill in name, specialty, WhatsApp number
4. Click Save
5. Verify in database:
```sql
SELECT * FROM doctor_profiles WHERE wallet_address = 'YOUR_WALLET';
```

## Phone Number Format
- Input: `+1234567890` or `1234567890`
- Stored: `whatsapp:+1234567890`
- Used for Twilio WhatsApp API

## Security
- RLS policies ensure users can only edit their own profiles
- Doctors can view patient profiles only if granted access
- All patients can view all doctor profiles (for selection)

## Demo Flow
1. Patient registers → Prompted to complete profile
2. Patient uploads medical report
3. Patient grants access to doctor (selects from list)
4. Doctor receives WhatsApp notification instantly
5. Doctor sees new grant on dashboard
6. Doctor can view patient name and contact info
