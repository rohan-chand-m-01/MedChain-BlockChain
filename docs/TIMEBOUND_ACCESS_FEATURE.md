# Timebound Access Feature Implementation

## Overview
Added a user-friendly timebound access control system for encrypted lab reports with preset duration options.

## Features Implemented

### 1. Grant Access Modal
Replaced the basic `prompt()` dialogs with a professional modal interface that includes:

- **Doctor Wallet Address Input**: Clean text input for entering the doctor's wallet address
- **Preset Duration Options**: Quick-select buttons for common durations
  - 1 hour
  - 4 hours  
  - 12 hours (default)
  - 24 hours
- **Custom Duration**: Flexible input for any custom duration in hours
  - Supports decimal values (e.g., 0.5 for 30 minutes, 48 for 2 days)
  - Validation for positive numbers
- **Visual Feedback**: 
  - Selected duration highlighted in blue
  - Loading states during grant process
  - Security info box explaining the access grant
- **Action Buttons**: Cancel and Grant Access with proper disabled states

### 2. User Experience Improvements

- **Better Visual Design**: Modal with proper spacing, colors, and transitions
- **Input Validation**: Ensures doctor address and valid duration are provided
- **Clear Feedback**: Shows duration in hours when access is granted
- **Responsive Layout**: Works well on different screen sizes
- **Accessibility**: Proper button states and disabled handling

### 3. Technical Implementation

**File Modified**: `frontend/src/app/encrypted-reports/page.tsx`

**New State Variables**:
```typescript
const [showGrantModal, setShowGrantModal] = useState(false);
const [grantingReportId, setGrantingReportId] = useState<string>('');
const [doctorAddress, setDoctorAddress] = useState('');
const [selectedDuration, setSelectedDuration] = useState<number | 'custom'>(12);
const [customHours, setCustomHours] = useState('');
const [isGranting, setIsGranting] = useState(false);
```

**Key Functions**:
- `openGrantModal(reportId)`: Opens the modal for a specific report
- `closeGrantModal()`: Closes modal and resets state
- `handleGrantAccess()`: Processes the access grant with selected duration

**Duration Conversion**:
- User selects duration in hours (more intuitive)
- Converted to days for the `grantAccess()` function
- Stored as timestamp in database

## Usage Flow

1. Patient clicks "Grant Access" button on a report
2. Modal opens with doctor address input and duration options
3. Patient enters doctor's wallet address
4. Patient selects duration (preset or custom)
5. Patient clicks "Grant Access"
6. System encrypts the key with doctor's public key
7. Access grant stored in database with expiration timestamp
8. Modal closes and reports list refreshes

## Security Features

- Client-side encryption using Privy wallet
- Zero-knowledge architecture (backend never sees plaintext)
- Time-bound access with automatic expiration
- Patient can revoke access anytime
- Encrypted key wrapped with doctor's public key

## Future Enhancements

Potential improvements:
- Add date/time picker for precise expiration times
- Show remaining time for active grants
- Notification when access is about to expire
- Bulk grant access to multiple doctors
- Access history and audit log
