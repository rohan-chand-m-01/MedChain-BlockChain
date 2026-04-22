# Privy-Based Decentralized Lab Report Encryption

## 🎯 Overview

MediChain uses **Privy's embedded wallet** to manage encryption keys for lab reports. This provides a **passwordless, decentralized** solution where users can recover access via social login without remembering passwords or managing private keys.

## 🔐 How It Works

### 1. User Authentication
- User logs in with Privy (Google, email, passkey, or wallet)
- Privy creates/recovers an **embedded MPC wallet** automatically
- No passwords to remember!

### 2. Key Derivation
```typescript
// Deterministic message signing
const message = `MediChain Key Derivation\nPatient: ${patientId}\nPurpose: Lab Report Encryption`;
const signature = await wallet.signMessage(message);

// Derive encryption key from signature
const encryptionKey = SHA256(signature);
```

**Key Properties:**
- Same message → same signature → same key (deterministic)
- Different users → different keys (user-specific)
- Recoverable via social login (no password needed)

### 3. Client-Side Encryption
```typescript
// Encrypt report with AES-256-CBC
const iv = generateRandomIV();
const encrypted = AES.encrypt(reportData, encryptionKey, { iv });

// Store encrypted data + IV
await uploadToDatabase({ encrypted, iv, patientId });
```

**Security:**
- Encryption happens in browser (client-side)
- Backend never sees plaintext
- Each encryption uses unique IV

### 4. Access Control
```typescript
// Grant doctor access
const doctorKey = await doctorWallet.deriveKey();
const encryptedPatientKey = AES.encrypt(patientKey, doctorKey);

// Store access grant
await database.insert('report_access_grants', {
  report_id,
  doctor_address,
  encrypted_key: encryptedPatientKey,
  expires_at: Date.now() + 7 * 24 * 60 * 60 * 1000, // 7 days
});
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User (Browser)                           │
├─────────────────────────────────────────────────────────────┤
│  1. Login with Privy (Google/Email/Passkey)                 │
│  2. Privy creates/recovers embedded wallet (MPC)            │
│  3. Wallet signs message → derives encryption key           │
│  4. Encrypt report client-side (AES-256-CBC)                │
│  5. Upload encrypted data to InsForge                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  InsForge Database                          │
├─────────────────────────────────────────────────────────────┤
│  encrypted_reports:                                         │
│    - patient_id (wallet address)                            │
│    - ipfs_hash (encrypted data)                             │
│    - iv (initialization vector)                             │
│    - report_type, timestamp                                 │
│                                                              │
│  report_access_grants:                                      │
│    - report_id, doctor_address                              │
│    - encrypted_key (patient key encrypted with doctor key)  │
│    - expires_at, revoked                                    │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
frontend/
├── src/
│   ├── services/
│   │   └── privyKeyManager.ts          # Core encryption logic
│   ├── hooks/
│   │   └── useLabReportEncryption.ts   # React hook for encryption
│   ├── components/
│   │   └── LabReportUpload.tsx         # Upload UI component
│   ├── app/
│   │   ├── encrypted-reports/
│   │   │   └── page.tsx                # Main demo page
│   │   └── api/
│   │       └── upload-encrypted-report/
│   │           └── route.ts            # API route for uploads
│   └── contexts/
│       └── PrivyProvider.tsx           # Privy configuration

backend/
└── migrations/
    └── 008_create_encrypted_reports_tables.sql  # Database schema
```

## 🚀 Usage

### 1. Upload Encrypted Report

```tsx
import { useLabReportEncryption } from '@/hooks/useLabReportEncryption';

function UploadComponent() {
  const { encryptReport, isReady } = useLabReportEncryption();

  const handleUpload = async (reportData: string) => {
    // Encrypt with Privy wallet
    const encrypted = await encryptReport(reportData, 'blood_test');

    // Upload to backend
    await fetch('/api/upload-encrypted-report', {
      method: 'POST',
      body: JSON.stringify(encrypted),
    });
  };

  return <button onClick={handleUpload}>Upload Report</button>;
}
```

### 2. View Encrypted Report

```tsx
const { decryptReport } = useLabReportEncryption();

const handleView = async (report) => {
  // Decrypt with Privy wallet
  const decrypted = await decryptReport(
    report.ipfs_hash,
    report.iv,
    report.patient_id
  );

  console.log(decrypted); // Original report data
};
```

### 3. Grant Doctor Access

```tsx
const { grantAccess } = useLabReportEncryption();

const handleGrantAccess = async (doctorAddress: string) => {
  // Encrypt patient's key with doctor's key
  const { encryptedKey, expiresAt } = await grantAccess(
    doctorAddress,
    7 // days
  );

  // Store in database
  await database.insert('report_access_grants', {
    report_id,
    doctor_address: doctorAddress,
    encrypted_key: encryptedKey,
    expires_at: expiresAt,
  });
};
```

## 🔑 Key Benefits

### For Users
✅ **No passwords to remember** - Login with Google, email, or passkey  
✅ **Social recovery** - Recover access anytime via Privy  
✅ **Biometric auth** - Face ID, Touch ID, Windows Hello  
✅ **Seamless UX** - No wallet management complexity  

### For Developers
✅ **Zero-knowledge** - Backend never sees plaintext  
✅ **Deterministic keys** - Same user = same key  
✅ **Client-side encryption** - Maximum security  
✅ **Simple API** - Easy to integrate  

### For Security
✅ **AES-256-CBC encryption** - Industry standard  
✅ **Unique IV per encryption** - Prevents pattern analysis  
✅ **MPC wallet** - Distributed key management  
✅ **Time-bound access** - Automatic expiration  

## 🔒 Security Considerations

### What's Protected
- ✅ Report content (encrypted client-side)
- ✅ Encryption keys (derived from wallet signature)
- ✅ Access control (time-bound, revocable)

### What's Public
- ⚠️ Patient wallet address (public by design)
- ⚠️ Report metadata (type, timestamp)
- ⚠️ Access grant existence (not the key itself)

### Best Practices
1. **Always use HTTPS** - Prevent MITM attacks
2. **Validate wallet signatures** - Ensure authenticity
3. **Audit access logs** - Track who accessed what
4. **Rotate keys periodically** - Re-encrypt with new keys
5. **Backup encrypted data** - Multiple storage locations

## 🧪 Testing

### Test Encryption/Decryption
```bash
cd frontend
npm run dev
# Visit http://localhost:3000/encrypted-reports
```

### Test Access Grants
1. Login as patient
2. Upload encrypted report
3. Grant access to doctor (use doctor's wallet address)
4. Login as doctor
5. View patient's report

## 📊 Database Schema

### encrypted_reports
```sql
CREATE TABLE encrypted_reports (
    id UUID PRIMARY KEY,
    patient_id TEXT NOT NULL,        -- Privy wallet address
    ipfs_hash TEXT NOT NULL,         -- Encrypted report data
    iv TEXT NOT NULL,                -- Initialization vector
    report_type TEXT NOT NULL,       -- blood_test, xray, etc.
    timestamp BIGINT NOT NULL,       -- Report timestamp
    created_at TIMESTAMP DEFAULT NOW()
);
```

### report_access_grants
```sql
CREATE TABLE report_access_grants (
    id UUID PRIMARY KEY,
    report_id UUID REFERENCES encrypted_reports(id),
    patient_id TEXT NOT NULL,        -- Patient's wallet
    doctor_address TEXT NOT NULL,    -- Doctor's wallet
    encrypted_key TEXT NOT NULL,     -- Patient key encrypted with doctor key
    expires_at BIGINT NOT NULL,      -- Expiration timestamp
    granted_at TIMESTAMP DEFAULT NOW(),
    revoked BOOLEAN DEFAULT FALSE
);
```

## 🎓 Learn More

- [Privy Documentation](https://docs.privy.io/)
- [AES-256-CBC Encryption](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)
- [MPC Wallets](https://www.privy.io/blog/mpc-wallets)
- [InsForge Database](https://docs.insforge.com/database)

## 🤝 Contributing

To add new features:
1. Update `privyKeyManager.ts` for core logic
2. Update `useLabReportEncryption.ts` for React integration
3. Add UI components as needed
4. Update database schema if required

## 📝 License

MIT License - See LICENSE file for details

---

**Built with ❤️ using Privy + InsForge + Next.js**
