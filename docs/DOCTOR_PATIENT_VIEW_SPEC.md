# Doctor Patient View - Comprehensive Feature Specification

## Overview
Enhanced doctor dashboard with patient-centric view including RAG-based analysis, consultation notes, PDF generation, and medical data visualization.

## User Flow

### 1. Doctor Dashboard
- Lists all patients who granted access
- Shows patient name, risk level, access expiry
- Click patient → Opens detailed patient view

### 2. Patient Detail View (NEW)

#### Layout:
```
┌─────────────────────────────────────────────────────────────┐
│ Patient Profile Card                                         │
│ Name, Age, Gender, Contact, Medical History                 │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────────────────┐
│ Medical Files List   │ Selected File Details                │
│ - Blood Test (Jan)   │ ┌──────────────────────────────────┐ │
│ - X-Ray (Feb)        │ │ AI Analysis Summary              │ │
│ - ECG (Mar)          │ │ Risk Score: 75                   │ │
│                      │ │ Conditions: Diabetes, HTN        │ │
│                      │ └──────────────────────────────────┘ │
│                      │                                      │
│                      │ ┌──────────────────────────────────┐ │
│                      │ │ Medical Graphs                   │ │
│                      │ │ [Glucose Trend Chart]            │ │
│                      │ │ [BP Trend Chart]                 │ │
│                      │ └──────────────────────────────────┘ │
└──────────────────────┴──────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ RAG-Based Comprehensive Analysis                            │
│ AI analyzes ALL patient files together                      │
│ - Longitudinal trends                                       │
│ - Disease progression                                       │
│ - Treatment effectiveness                                   │
│ - Risk factors                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Doctor's Consultation Notes                                 │
│ [Rich text editor]                                          │
│ - Symptoms discussed                                        │
│ - Physical examination findings                             │
│ - Diagnosis                                                 │
│ - Treatment plan                                            │
│ - Follow-up recommendations                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Actions                                                      │
│ [Generate Medical Summary PDF] [Generate Consultation PDF]  │
│ [Edit & Regenerate] [Send to Patient]                      │
└─────────────────────────────────────────────────────────────┘
```

## Features Breakdown

### 1. Patient Profile Card
**Data Sources:**
- `patient_profiles` table
- `analyses` table (for medical history)

**Display:**
- Full name
- Age, Gender
- WhatsApp phone, Email
- Medical conditions (from all analyses)
- Allergies
- Current medications

### 2. Medical Files List
**Data Source:** `analyses` table filtered by patient_wallet

**Display:**
- File name
- Upload date
- File type (Blood Test, X-Ray, ECG, etc.)
- Risk score badge
- Click to view details

### 3. RAG-Based Comprehensive Analysis
**Technology:** 
- Vector embeddings of all patient files
- Gemini AI with long context window
- Retrieval-Augmented Generation

**Process:**
1. Fetch all patient's analyses
2. Combine summaries into single context
3. Send to Gemini with prompt:
   ```
   Analyze this patient's complete medical history.
   Identify trends, disease progression, and risk factors.
   Provide comprehensive assessment and recommendations.
   ```

**Output:**
- Longitudinal health trends
- Disease progression timeline
- Treatment effectiveness analysis
- Risk factor identification
- Preventive care recommendations

### 4. Medical Data Visualization

#### Graphs to Implement:
1. **Glucose Trend** (for diabetic patients)
   - Line chart showing glucose levels over time
   - Normal range shading
   - HbA1c trend

2. **Blood Pressure Trend**
   - Dual-axis chart (Systolic/Diastolic)
   - Normal range indicators
   - Hypertension risk zones

3. **Cholesterol Panel**
   - Multi-line chart (Total, LDL, HDL, Triglycerides)
   - Target ranges

4. **Weight/BMI Trend**
   - Line chart with BMI categories

5. **Lab Values Comparison**
   - Bar chart comparing latest vs previous
   - Abnormal values highlighted

**Library:** Recharts (React charting library)

### 5. Doctor's Consultation Notes

**Features:**
- Rich text editor (TipTap or similar)
- Auto-save drafts
- Templates for common consultations
- Voice-to-text input (optional)

**Sections:**
- Chief Complaint
- History of Present Illness
- Physical Examination
- Assessment/Diagnosis
- Treatment Plan
- Follow-up Instructions
- Prescriptions

### 6. PDF Generation

#### PDF 1: Medical Summary Report
**Content:**
- Patient demographics
- Medical history timeline
- All test results
- AI analysis summary
- Graphs and charts
- Risk assessment

**Format:** Professional medical report template

#### PDF 2: Consultation Report
**Content:**
- Consultation date
- Doctor's details
- Patient's details
- Consultation notes
- Diagnosis
- Treatment plan
- Prescriptions
- Follow-up schedule

**Format:** Standard consultation note format

**Technology:** 
- Backend: ReportLab (Python) or existing `pdf_generator.py`
- Frontend: jsPDF + html2canvas (for graphs)

### 7. Editable Reports

**Workflow:**
1. Doctor reviews AI-generated content
2. Clicks "Edit" button
3. Inline editing of all sections
4. Clicks "Regenerate PDF" with edits
5. Preview before finalizing
6. Download or send to patient

## Database Schema Changes

### New Table: `consultation_notes`
```sql
CREATE TABLE consultation_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_wallet TEXT NOT NULL,
    doctor_wallet TEXT NOT NULL,
    consultation_date TIMESTAMPTZ DEFAULT NOW(),
    chief_complaint TEXT,
    history_present_illness TEXT,
    physical_examination TEXT,
    assessment TEXT,
    diagnosis TEXT,
    treatment_plan TEXT,
    prescriptions JSONB,
    follow_up_instructions TEXT,
    notes TEXT,
    is_draft BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### New Table: `medical_data_points`
```sql
CREATE TABLE medical_data_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_wallet TEXT NOT NULL,
    analysis_id UUID REFERENCES analyses(id),
    data_type TEXT NOT NULL, -- 'glucose', 'bp_systolic', 'bp_diastolic', 'cholesterol', etc.
    value DECIMAL(10,2) NOT NULL,
    unit TEXT, -- 'mg/dL', 'mmHg', etc.
    measured_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Backend API Endpoints

### 1. Get Patient Complete Profile
```
GET /api/doctor/patient/{patient_wallet}/complete
```
Returns:
- Patient profile
- All analyses
- All consultation notes
- Medical data points for graphs

### 2. RAG-Based Comprehensive Analysis
```
POST /api/doctor/patient/{patient_wallet}/comprehensive-analysis
```
Uses Gemini AI to analyze all patient files together

### 3. Save Consultation Notes
```
POST /api/doctor/consultation-notes
PUT /api/doctor/consultation-notes/{note_id}
```

### 4. Generate PDFs
```
POST /api/doctor/generate-pdf/medical-summary
POST /api/doctor/generate-pdf/consultation-report
```

### 5. Get Medical Data for Graphs
```
GET /api/doctor/patient/{patient_wallet}/medical-data?type=glucose,bp,cholesterol
```

## Frontend Components

### 1. `PatientDetailView.tsx`
Main container component

### 2. `PatientProfileCard.tsx`
Patient demographics and summary

### 3. `MedicalFilesList.tsx`
Sidebar with all patient files

### 4. `FileDetailPanel.tsx`
Selected file analysis and details

### 5. `MedicalGraphs.tsx`
All medical data visualizations

### 6. `ComprehensiveAnalysis.tsx`
RAG-based AI analysis display

### 7. `ConsultationNotesEditor.tsx`
Rich text editor for doctor's notes

### 8. `PDFGenerator.tsx`
PDF generation and preview

## Implementation Priority

### Phase 1 (MVP):
1. ✅ Patient profile view
2. ✅ Medical files list
3. ✅ Basic consultation notes
4. ✅ Simple PDF generation

### Phase 2 (Enhanced):
5. ⏳ RAG-based comprehensive analysis
6. ⏳ Medical graphs (glucose, BP, cholesterol)
7. ⏳ Editable reports

### Phase 3 (Advanced):
8. ⏳ Voice-to-text notes
9. ⏳ Real-time collaboration
10. ⏳ Prescription templates

## Technical Stack

**Frontend:**
- React + TypeScript
- Recharts (graphs)
- TipTap (rich text editor)
- jsPDF (client-side PDF)
- Tailwind CSS

**Backend:**
- FastAPI (Python)
- Gemini AI (RAG analysis)
- ReportLab (PDF generation)
- InsForge (database)

## Estimated Development Time

- Patient profile view: 2 hours
- Medical files list: 1 hour
- RAG analysis: 3 hours
- Consultation notes: 2 hours
- PDF generation: 4 hours
- Medical graphs: 4 hours
- Editable reports: 2 hours

**Total: ~18 hours**

## Next Steps

1. Create database tables
2. Build backend API endpoints
3. Create frontend components
4. Integrate RAG analysis
5. Implement PDF generation
6. Add medical graphs
7. Testing and refinement
