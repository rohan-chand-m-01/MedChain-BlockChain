# Timebound Access UI - AccessManager Component

## Overview
Added professional timebound access duration selector to the AccessManager component with preset buttons and custom time input.

## Visual Design

### Duration Selector Card
- **Header**: Purple icon (⏱️) with "Access Duration" title
- **Layout**: 2x2 grid of duration buttons
- **Style**: Retro brutalist design matching the existing UI
- **Border**: 2px black borders with shadow effects

### Duration Buttons (2x2 Grid)

#### Preset Options
1. **1 Hour** ⚡
   - Quick access for brief consultations
   - Icon: Lightning bolt

2. **2 Hours** ⏰ (Default)
   - Standard consultation duration
   - Icon: Alarm clock

3. **24 Hours** 📅
   - Full day access
   - Icon: Calendar

4. **Custom** ⚙️
   - Flexible custom duration
   - Icon: Settings gear

### Button States

#### Unselected
- White background
- Gray text
- 2px shadow
- Hover: Light gray background

#### Selected
- Purple background (#A78BFA)
- Black text
- 4px shadow (elevated)
- Translate effect (-1px, -1px)
- Green indicator dot (top-right)

### Custom Time Input

When "Custom" is selected:
- **Input Field**: Number input with mono font
- **Placeholder**: "e.g., 0.5, 6, 48"
- **Step**: 0.5 hours
- **Min**: 0.1 hours
- **Style**: Inset shadow, black border
- **Help Text**: Examples with emoji
  - 💡 0.5 = 30 min
  - 💡 6 = 6 hours
  - 💡 48 = 2 days

### Warning Banner
- Yellow background (#FEF3C7)
- Orange border (#F59E0B)
- Warning icon: ⚠️
- Message: "Access will automatically expire after the selected duration"

## User Flow

1. **Select Doctor**: Choose from dropdown
2. **Duration Appears**: Selector shows automatically
3. **Choose Duration**: Click preset or custom
4. **Enter Custom** (if needed): Type hours in input
5. **Grant Access**: Click main button
6. **Confirmation**: Success message shows duration

## Technical Implementation

### New State Variables
```typescript
const [selectedDuration, setSelectedDuration] = useState<number | 'custom'>(2);
const [customHours, setCustomHours] = useState('');
const [showDurationSelector, setShowDurationSelector] = useState(false);
```

### Duration Calculation
```typescript
let durationHours: number;
if (selectedDuration === 'custom') {
    durationHours = parseFloat(customHours);
} else {
    durationHours = selectedDuration;
}

const expiresAt = Date.now() + (durationHours * 60 * 60 * 1000);
```

### Validation
- Checks if custom hours is a valid positive number
- Shows error message if invalid
- Prevents grant if validation fails

### API Update
Updated `apiGrantAccess` to accept optional `expires_at` parameter:
```typescript
{ 
  patient_wallet: string;
  doctor_wallet: string;
  analysis_id: string;
  expires_at?: number;  // New optional field
}
```

## Visual Hierarchy

### Component Order
1. Manage Access Header
2. Doctor Dropdown
3. **Duration Selector** (new - shows when doctor selected)
4. Grant Access Button
5. Success/Error Message
6. Granted Doctors List

### Spacing
- Consistent 4-unit gaps between sections
- 3-unit gaps between duration buttons
- 5-unit padding in cards

## Design Consistency

### Matches Existing Style
✓ Retro brutalist aesthetic
✓ 2px black borders
✓ Shadow effects (2px, 4px)
✓ Uppercase tracking-wide text
✓ Mono font for technical info
✓ Color-coded sections

### Color Palette
- **Purple** (#A78BFA): Duration theme
- **Green** (#A3E635): Success/selected indicator
- **Yellow** (#FEF3C7): Warning background
- **Orange** (#F59E0B): Warning border
- **Black**: Borders and text
- **White**: Backgrounds

## User Experience Improvements

### Clear Visual Feedback
- Selected button elevates with shadow
- Green dot indicator on active choice
- Disabled state for invalid selections
- Loading state during grant process

### Helpful Guidance
- Icons for each duration option
- Example values for custom input
- Warning about auto-expiration
- Success message includes duration

### Accessibility
- Large touch targets (44px+)
- Clear focus states
- Semantic HTML
- Descriptive labels
- Keyboard navigation support

## Success Message Enhancement

### Before
```
✅ Access granted to Dr. Emily Rodriguez
```

### After
```
✅ Access granted to Dr. Emily Rodriguez for 2h
```

Shows the duration in the confirmation message for clarity.

## Edge Cases Handled

1. **Invalid Custom Input**: Shows error message
2. **Empty Custom Input**: Validation prevents grant
3. **Negative Numbers**: Min attribute prevents
4. **Non-numeric Input**: parseFloat returns NaN, caught by validation
5. **Doctor Not Selected**: Duration selector hidden
6. **Reset on Success**: Duration resets to default (2 hours)

## Mobile Responsive

- 2x2 grid maintains on mobile
- Buttons stack properly
- Touch-friendly sizes
- Readable text at all sizes

## Future Enhancements

Potential improvements:
- Add date/time picker for precise expiration
- Show countdown timer for active grants
- Add "Extend Access" button for granted doctors
- Display remaining time in granted doctors list
- Add preset for common durations (4h, 12h, 48h)
- Remember user's preferred duration
- Add bulk grant with same duration
