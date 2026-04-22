/**
 * api.ts — Centralized backend API client for MediChain AI frontend.
 *
 * All calls go through the FastAPI backend (NEXT_PUBLIC_API_URL).
 * No secrets, API keys, or service credentials are held here.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Types ───────────────────────────────────────────────────────────────────

export interface AnalyzeReportPayload {
    file_base64: string;
    file_type: string;
    patient_wallet: string;
    file_name: string;
}

export interface ChatPayload {
    patient_wallet: string;
    message: string;
}

export interface TavusVideoPayload {
    summary: string;
    risk_score: number;
    conditions?: string[];
    specialist?: string;
    urgency?: string;
}

export interface OrganAnalysisPayload {
    organName: string;
    analysisText: Record<string, unknown>;
}

export interface DoctorProfilePayload {
    name: string;
    specialty: string;
    bio: string;
}

export interface ConsultationNotePayload {
    patient_wallet: string;
    analysis_id: string;
    note: string;
}

export interface CreateAppointmentPayload {
    patient_wallet: string;
    doctor_wallet: string;
    date: string;
    time: string;
    reason: string;
}

export interface UpdateRecordPayload {
    tx_hash?: string;
    record_id?: number;
    file_url?: string;
    ipfs_cid?: string;
    file_fingerprint?: string;
    encryption_iv?: string;
    organ_data?: Record<string, any>;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

async function post<T>(path: string, body: unknown): Promise<T> {
    let res;
    try {
        res = await fetch(`${API_URL}${path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
    } catch (err: any) {
        throw new Error(`Connection failed: Could not reach backend at ${API_URL}`);
    }
    if (!res.ok) {
        const errorText = await res.text();
        let errorDetail = `Request failed: ${res.status}`;
        
        try {
            const errorJson = JSON.parse(errorText);
            errorDetail = errorJson.detail || errorJson.message || errorDetail;
        } catch {
            // If not JSON, use the text directly if it's short
            if (errorText && errorText.length < 200) {
                errorDetail = errorText;
            }
        }
        
        console.error('[API Error]', {
            path,
            status: res.status,
            statusText: res.statusText,
            error: errorDetail,
            fullResponse: errorText
        });
        
        throw new Error(errorDetail);
    }
    return res.json();
}

async function get<T>(path: string): Promise<T> {
    let res;
    try {
        res = await fetch(`${API_URL}${path}`);
    } catch (err: any) {
        throw new Error(`Connection failed: Could not reach backend at ${API_URL}`);
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `Request failed: ${res.status}`);
    }
    return res.json();
}

async function patch<T>(path: string, body: unknown): Promise<T> {
    let res;
    try {
        res = await fetch(`${API_URL}${path}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
    } catch (err: any) {
        throw new Error(`Connection failed: Could not reach backend at ${API_URL}`);
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `Request failed: ${res.status}`);
    }
    return res.json();
}

async function del<T>(path: string): Promise<T> {
    let res;
    try {
        res = await fetch(`${API_URL}${path}`, { method: "DELETE" });
    } catch (err: any) {
        throw new Error(`Connection failed: Could not reach backend at ${API_URL}`);
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `Request failed: ${res.status}`);
    }
    return res.json();
}

// ─── AI / Analysis ───────────────────────────────────────────────────────────

/** Upload and analyze a medical report (PDF/Image). */
export const analyzeReport = (payload: AnalyzeReportPayload) =>
    post("/api/analyze-report", payload);

/** Send a chat message to the AI health assistant. */
export const sendChatMessage = (payload: ChatPayload) =>
    post("/api/chat", payload);

/** Generate a Tavus AI doctor video for a medical analysis. */
export const generateTavusVideo = (payload: TavusVideoPayload) =>
    post("/api/tavus-video", payload);

/** Check the status of a Tavus video by its ID. */
export const getTavusVideoStatus = (videoId: string) =>
    get(`/api/tavus-video?video_id=${encodeURIComponent(videoId)}`);

/** Get AI analysis for a specific organ based on report data. */
export const analyzeOrgan = (payload: OrganAnalysisPayload) =>
    post<{ organAnalysis: any }>("/api/analyze-organ", payload);

// ─── Records ─────────────────────────────────────────────────────────────────

/** Fetch all medical analysis records for a patient wallet. */
export const getPatientRecords = (wallet: string) =>
    get<{ success: boolean; records: any[] }>(`/api/records/${encodeURIComponent(wallet)}`);

/** Delete an analysis record by ID. */
export const deleteRecord = (id: string) =>
    del<{ success: boolean }>(`/api/records/${encodeURIComponent(id)}`);

/** Patch an analysis record (tx_hash, IPFS fields, etc.). */
export const updateRecord = (id: string, payload: UpdateRecordPayload) =>
    patch<{ success: boolean; record: any }>(`/api/records/${encodeURIComponent(id)}`, payload);

/** Check if a record with the same file name already exists (cache check). */
export const checkRecordCache = (patient_wallet: string, file_name: string) =>
    post<{ exists: boolean; record: any | null }>("/api/records/check-cache", { patient_wallet, file_name });

/** Clone an existing record row (for cached re-uploads). */
export const cloneRecord = (payload: Record<string, any>) =>
    post<{ success: boolean; record: any }>("/api/records/clone", payload);

// ─── Appointments ─────────────────────────────────────────────────────────────

/** Fetch all appointments for a patient wallet (enriched with doctor info). */
export const getAppointments = (wallet: string) =>
    get<{ success: boolean; appointments: any[] }>(`/api/appointments/${encodeURIComponent(wallet)}`);

/** Cancel an appointment by ID. */
export const cancelAppointment = (id: string) =>
    patch<{ success: boolean }>(`/api/appointments/${encodeURIComponent(id)}/cancel`, {});

/** Get booked slots for a specific doctor on a given date. */
export const getBookedSlots = (doctorWallet: string, date: string) =>
    get<{ success: boolean; booked_slots: string[] }>(`/api/appointments/slots/${encodeURIComponent(doctorWallet)}/${encodeURIComponent(date)}`);

/** Create a new appointment request. */
export const createAppointment = (payload: CreateAppointmentPayload) =>
    post<{ success: boolean }>(`/api/appointments`, payload);

// ─── Doctor Dashboard ───────────────────────────────────────────────────────

/** Get list of all doctors, optionally filtered by specialty. */
export const getAllDoctors = (specialty?: string) => {
    const query = specialty ? `?specialty=${encodeURIComponent(specialty)}` : "";
    return get<{ success: boolean; doctors: any[] }>(`/api/doctors${query}`);
}

export const getDoctorProfile = (wallet: string) =>
    get<{ success: boolean; profiles: any[] }>(`/api/doctor/profile/${encodeURIComponent(wallet)}`);

export const upsertDoctorProfile = (wallet: string, payload: DoctorProfilePayload) =>
    post<{ success: boolean }>(`/api/doctor/profile/${encodeURIComponent(wallet)}`, payload);

export const getDoctorGrants = (wallet: string) =>
    get<{ success: boolean; grants: any[] }>(`/api/doctor/grants/${encodeURIComponent(wallet)}`);

export const getDoctorAppointments = (wallet: string) =>
    get<{ success: boolean; appointments: any[] }>(`/api/doctor/appointments/${encodeURIComponent(wallet)}`);

export const updateDoctorAppointmentStatus = (id: string, status: string) =>
    patch<{ success: boolean }>(`/api/doctor/appointments/${encodeURIComponent(id)}`, { status });

export const getConsultationNotes = (doctorWallet: string, patientWallet: string) =>
    get<{ success: boolean; notes: any[] }>(`/api/doctor/notes/${encodeURIComponent(doctorWallet)}/${encodeURIComponent(patientWallet)}`);

export const addConsultationNote = (doctorWallet: string, payload: ConsultationNotePayload) =>
    post<{ success: boolean }>(`/api/doctor/notes/${encodeURIComponent(doctorWallet)}`, payload);

// ─── Access Grants ───────────────────────────────────────────────────────────

export const getAccessGrants = (analysisId: string) =>
    get<{ success: boolean; grants: any[] }>(`/api/access-grants/analysis/${encodeURIComponent(analysisId)}`);

export const apiGrantAccess = (payload: { patient_wallet: string; doctor_wallet: string; analysis_id: string; expires_at?: number }) =>
    post<{ success: boolean }>(`/api/access-grants`, payload);

export const apiRevokeAccess = (payload: { doctor_wallet: string; analysis_id: string }) =>
    patch<{ success: boolean }>(`/api/access-grants/revoke`, payload);

/** Simplified access grant (without encryption) for demo/development */
export const createSimpleAccessGrant = (payload: {
    patient_wallet: string;
    doctor_wallet: string;
    analysis_id: string;
    expires_in_hours?: number;
}) => post<{ success: boolean; grant_id: string; expires_at: string; message: string }>(
    '/api/access-grants/simple',
    { expires_in_hours: 24, ...payload }
);

/** Check if doctor has access to a specific analysis */
export const checkDoctorAccess = (doctor_wallet: string, analysis_id: string) =>
    get<{ success: boolean; has_access: boolean; grant?: any }>(
        `/api/access-grants/check?doctor_wallet=${encodeURIComponent(doctor_wallet)}&analysis_id=${encodeURIComponent(analysis_id)}`
    );

/** Get active grants for patient */
export const getPatientActiveGrants = (patient_wallet: string) =>
    get<{ success: boolean; grants: any[]; total: number }>(
        `/api/access-grants/patient/active?patient_wallet=${encodeURIComponent(patient_wallet)}`
    );

/** Revoke access grant */
export const revokeAccessGrant = (grant_id: string, patient_wallet: string, reason?: string) =>
    post<{ success: boolean; message: string }>(
        `/api/access-grants/${encodeURIComponent(grant_id)}/revoke?patient_wallet=${encodeURIComponent(patient_wallet)}`,
        { reason: reason || 'patient_revoked' }
    );

// ─── AI Medical Intern ───────────────────────────────────────────────────────

/** Get AI-generated patient briefing */
export const getPatientBriefing = (patient_wallet: string) =>
    post<{ success: boolean; briefing: any }>(
        `/api/ai/briefing/${encodeURIComponent(patient_wallet)}`,
        {}
    );

/** Get priority-sorted patient list for doctor */
export const getPriorityPatients = (doctor_wallet: string, limit?: number) =>
    get<{ success: boolean; patients: any[]; total: number }>(
        `/api/ai/priority-patients/${encodeURIComponent(doctor_wallet)}${limit ? `?limit=${limit}` : ''}`
    );

/** Chat with AI about specific patient (RAG-based) */
export const chatWithAI = (patient_wallet: string, query: string) =>
    post<{ success: boolean; response: string; query: string }>(
        '/api/ai/chat',
        { patient_wallet, query }
    );

/** Get Jira-style task board for doctor */
export const getTaskBoard = (doctor_wallet: string) =>
    get<{ success: boolean; tasks: any; counts: any }>(
        `/api/ai/task-board/${encodeURIComponent(doctor_wallet)}`
    );

/** Generate treatment plan suggestions */
export const suggestTreatmentPlan = (diagnosis: string, patient_context: any) =>
    post<{ success: boolean; treatment_plan: any }>(
        '/api/ai/treatment-plan',
        { diagnosis, patient_context }
    );

// ─── Patient Profiles ────────────────────────────────────────────────────────

export interface PatientProfilePayload {
    full_name: string;
    date_of_birth?: string;
    phone?: string;
    email?: string;
}

/** Get patient profile */
export const getPatientProfile = (patient_wallet: string) =>
    get<{ success: boolean; profile: any }>(
        `/api/patient/profile/${encodeURIComponent(patient_wallet)}`
    );

/** Create/update patient profile */
export const upsertPatientProfile = (patient_wallet: string, payload: PatientProfilePayload) =>
    post<{ success: boolean }>(
        `/api/patient/profile/${encodeURIComponent(patient_wallet)}`,
        payload
    );

/** Get list of patients for doctor (for chatbot selector) */
export const listPatientsForDoctor = (doctor_wallet: string) =>
    get<{ success: boolean; patients: any[] }>(
        `/api/patient/list-for-doctor/${encodeURIComponent(doctor_wallet)}`
    );

// ─── Payment Requests ────────────────────────────────────────────────────────

export interface PaymentRequestPayload {
    patient_wallet: string;
    amount: string;
    reason: string;
}

export interface PaymentRequestUpdatePayload {
    status: string;
    tx_hash?: string;
}

/** Doctor creates a payment request to a patient. */
export const createPaymentRequest = (doctorWallet: string, payload: PaymentRequestPayload) =>
    post<{ success: boolean; request: any }>(`/api/payment-requests?doctor_wallet=${encodeURIComponent(doctorWallet)}`, payload);

/** Patient fetches all payment requests sent to them. */
export const getPatientPaymentRequests = (wallet: string) =>
    get<{ success: boolean; requests: any[] }>(`/api/payment-requests/patient/${encodeURIComponent(wallet)}`);

/** Doctor fetches all payment requests they have sent. */
export const getDoctorPaymentRequests = (wallet: string) =>
    get<{ success: boolean; requests: any[] }>(`/api/payment-requests/doctor/${encodeURIComponent(wallet)}`);

/** Patient updates a payment request status (paid/declined). */
export const updatePaymentRequest = (id: string, payload: PaymentRequestUpdatePayload) =>
    patch<{ success: boolean }>(`/api/payment-requests/${encodeURIComponent(id)}`, payload);

