'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, useUser } from '@clerk/nextjs';
import { isPatient } from '@/lib/auth';
import {
    getPatientRecords,
    getAppointments,
    analyzeReport,
} from '@/lib/api';
import EditorialSidebar from '@/components/EditorialSidebar';
import AnalysisView from './components/AnalysisView';
import AppointmentsView from './components/AppointmentsView';
import ChatBot from '@/components/ChatBot';
import TavusVideo from '@/components/TavusVideo';
import AccessManager from '@/components/AccessManager';
import DigitalTwin from '@/components/DigitalTwin';

interface Analysis {
    id: string;
    file_name: string;
    file_url: string;
    summary: string;
    risk_score: number;
    conditions: string[];
    specialist: string;
    urgency: string;
    record_hash: string;
    tx_hash?: string;
    record_id?: number;
    created_at: string;
    organ_data?: Record<string, any>;
}

interface Appointment {
    id: string;
    patient_wallet: string;
    doctor_wallet: string;
    date: string;
    time: string;
    status: string;
    reason: string;
    meeting_link?: string;
    doctor_name?: string;
    doctor_specialty?: string;
}

export default function PatientDashboard() {
    const router = useRouter();
    const { isSignedIn, userId } = useAuth();
    const { user } = useUser();
    const [records, setRecords] = useState<Analysis[]>([]);
    const [selectedRecord, setSelectedRecord] = useState<Analysis | null>(null);
    const [activeTab, setActiveTab] = useState<string>('analysis');
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [uploading, setUploading] = useState(false);
    const [uploadError, setUploadError] = useState('');

    useEffect(() => {
        if (!isSignedIn) { router.push('/'); return; }
        if (!isPatient(user)) { router.push('/register'); return; }
        if (userId) {
            loadRecords();
            loadAppointments();
        }
    }, [isSignedIn, userId, user, router]);

    const loadRecords = async () => {
        if (!userId) return;
        try {
            const { records: data } = await getPatientRecords(userId);
            if (data) {
                setRecords(data as Analysis[]);
                if (data.length > 0 && !selectedRecord) setSelectedRecord(data[0] as Analysis);
            }
        } catch (err) {
            console.error('Failed to load records:', err);
        }
    };

    const loadAppointments = async () => {
        if (!userId) return;
        try {
            const { appointments } = await getAppointments(userId);
            setAppointments(appointments as Appointment[]);
        } catch (err) {
            console.error('Failed to load appointments:', err);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file || !userId) return;

        setUploading(true);
        setUploadError('');

        try {
            // Convert file to base64
            const buffer = await file.arrayBuffer();
            const bytes = new Uint8Array(buffer);
            let binary = '';
            for (let i = 0; i < bytes.length; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            const fileBase64 = btoa(binary);
            const fileType = file.type || 'application/pdf';

            // Analyze the report
            const result = await analyzeReport({
                file_base64: fileBase64,
                file_type: fileType,
                patient_wallet: userId,
                file_name: file.name,
            });

            if (result) {
                await loadRecords();
            } else {
                setUploadError('Upload failed');
            }
        } catch (err: any) {
            setUploadError(err.message || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    if (!isSignedIn || !userId) return null;

    return (
        <div className="flex min-h-screen bg-[#f7f9fb]">
            {/* Sidebar */}
            <EditorialSidebar activeTab={activeTab} onTabChange={setActiveTab} />

            {/* Main Content - Full Screen */}
            <main className="flex-1 ml-64 p-8">
                {/* Analysis View */}
                {activeTab === 'analysis' && (
                    <div className="animate-fade-in h-full">
                        <div className="mb-6 flex items-center justify-between">
                            <div>
                                <h2 className="text-3xl font-headline font-bold text-[#191c1e]">
                                    Medical Analysis
                                </h2>
                                <p className="text-[#434655] mt-1">
                                    AI-powered analysis of your medical reports
                                </p>
                            </div>
                            
                            {/* File Upload Button - Only show when records exist */}
                            {selectedRecord && (
                                <label className="cursor-pointer group">
                                    <div className="flex items-center gap-2 bg-[#2563eb] hover:bg-[#1d4ed8] text-white px-5 py-3 rounded-xl font-semibold text-sm shadow-lg shadow-[#2563eb]/20 transition-all hover:shadow-xl hover:shadow-[#2563eb]/30 hover:-translate-y-0.5">
                                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                        </svg>
                                        {uploading ? 'Uploading...' : 'Upload New Report'}
                                    </div>
                                    <input
                                        type="file"
                                        accept=".pdf,.jpg,.jpeg,.png"
                                        onChange={handleFileUpload}
                                        disabled={uploading}
                                        className="hidden"
                                    />
                                </label>
                            )}
                        </div>

                        {/* Upload Error */}
                        {uploadError && (
                            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
                                {uploadError}
                            </div>
                        )}

                        {selectedRecord ? (
                            <AnalysisView record={selectedRecord} />
                        ) : (
                            <div className="bg-white rounded-3xl p-12 text-center border border-[#e0e3e5] max-w-2xl mx-auto">
                                {/* Modern Upload Area */}
                                <label className="cursor-pointer group block">
                                    <div className="relative bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-3xl border-2 border-dashed border-blue-200 hover:border-blue-400 transition-all duration-300 p-16 hover:shadow-2xl hover:shadow-blue-100">
                                        {/* Icon */}
                                        <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-3xl flex items-center justify-center mb-6 mx-auto shadow-xl shadow-blue-500/30 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                                            <svg className="w-12 h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                            </svg>
                                        </div>

                                        {/* Text */}
                                        <h3 className="text-3xl font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors">
                                            {uploading ? 'Processing Your Report...' : 'Upload Medical Report'}
                                        </h3>
                                        <p className="text-base text-gray-600 mb-6 max-w-md mx-auto leading-relaxed">
                                            {uploading 
                                                ? 'Our AI is analyzing your medical data. This may take a few moments.'
                                                : 'Drop your medical report here or click to browse. Our AI will analyze it instantly.'
                                            }
                                        </p>

                                        {/* File Types */}
                                        <div className="inline-flex items-center gap-3 bg-white/80 backdrop-blur-sm px-6 py-3 rounded-2xl shadow-lg border border-gray-200 group-hover:border-blue-300 group-hover:shadow-xl transition-all">
                                            <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                            <span className="text-sm font-medium text-gray-700">PDF, JPG, PNG — up to 10MB</span>
                                        </div>

                                        {/* Features */}
                                        <div className="grid grid-cols-3 gap-4 mt-10 max-w-xl mx-auto">
                                            <div className="text-center">
                                                <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center mx-auto mb-2 shadow-sm">
                                                    <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                        <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                                    </svg>
                                                </div>
                                                <p className="text-xs font-semibold text-gray-700">Instant AI Analysis</p>
                                            </div>
                                            <div className="text-center">
                                                <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center mx-auto mb-2 shadow-sm">
                                                    <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                                    </svg>
                                                </div>
                                                <p className="text-xs font-semibold text-gray-700">Secure & Private</p>
                                            </div>
                                            <div className="text-center">
                                                <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center mx-auto mb-2 shadow-sm">
                                                    <svg className="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                                    </svg>
                                                </div>
                                                <p className="text-xs font-semibold text-gray-700">Smart Insights</p>
                                            </div>
                                        </div>
                                    </div>
                                    <input
                                        type="file"
                                        accept=".pdf,.jpg,.jpeg,.png"
                                        onChange={handleFileUpload}
                                        disabled={uploading}
                                        className="hidden"
                                    />
                                </label>
                            </div>
                        )}
                    </div>
                )}

                {/* 3D Anatomy View */}
                {activeTab === 'twin' && (
                    <div className="animate-fade-in h-full">
                        <div className="mb-6">
                            <h2 className="text-3xl font-headline font-bold text-[#191c1e]">
                                Neural Body Scanner
                            </h2>
                            <p className="text-[#434655] mt-1">
                                Interactive 3D anatomical visualization
                            </p>
                        </div>
                        {selectedRecord ? (
                            <div className="bg-white rounded-3xl border border-[#e0e3e5] overflow-hidden h-[calc(100vh-12rem)]">
                                <DigitalTwin analysisData={selectedRecord} recordId={selectedRecord.id} />
                            </div>
                        ) : (
                            <div className="bg-white rounded-3xl p-12 text-center border border-[#e0e3e5]">
                                <div className="w-16 h-16 rounded-full bg-[#dbe1ff] mx-auto mb-4 flex items-center justify-center">
                                    <span className="material-symbols-outlined text-[#004ac6] text-3xl">
                                        view_in_ar
                                    </span>
                                </div>
                                <h3 className="text-xl font-bold text-[#191c1e] mb-2">
                                    No Data Available
                                </h3>
                                <p className="text-[#434655]">
                                    Upload a medical report to visualize your health data in 3D
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {/* AI Chat View */}
                {activeTab === 'chat' && (
                    <div className="animate-fade-in h-full">
                        <div className="mb-6">
                            <h2 className="text-3xl font-headline font-bold text-[#191c1e]">
                                AI Medical Assistant
                            </h2>
                            <p className="text-[#434655] mt-1">
                                Chat with our AI-powered medical assistant
                            </p>
                        </div>
                        <div className="bg-white rounded-3xl border border-[#e0e3e5] overflow-hidden h-[calc(100vh-12rem)]">
                            <ChatBot patientWallet={userId} />
                        </div>
                    </div>
                )}

                {/* Video Consult View */}
                {activeTab === 'avatar' && (
                    <div className="animate-fade-in h-full">
                        <div className="mb-6">
                            <h2 className="text-3xl font-headline font-bold text-[#191c1e]">
                                AI Doctor Avatar
                            </h2>
                            <p className="text-[#434655] mt-1">
                                Video consultation with AI-powered doctor avatar
                            </p>
                        </div>
                        {selectedRecord ? (
                            <div className="bg-white rounded-3xl border border-[#e0e3e5] overflow-hidden">
                                <TavusVideo
                                    summary={selectedRecord.summary}
                                    riskScore={selectedRecord.risk_score}
                                    conditions={selectedRecord.conditions}
                                    specialist={selectedRecord.specialist}
                                    urgency={selectedRecord.urgency}
                                />
                            </div>
                        ) : (
                            <div className="bg-white rounded-3xl p-12 text-center border border-[#e0e3e5]">
                                <div className="w-16 h-16 rounded-full bg-[#dbe1ff] mx-auto mb-4 flex items-center justify-center">
                                    <span className="material-symbols-outlined text-[#004ac6] text-3xl">
                                        videocam
                                    </span>
                                </div>
                                <h3 className="text-xl font-bold text-[#191c1e] mb-2">
                                    No Analysis Available
                                </h3>
                                <p className="text-[#434655]">
                                    Upload a medical report to consult with the AI doctor
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {/* Data Access View */}
                {activeTab === 'access' && (
                    <div className="animate-fade-in h-full">
                        <div className="mb-6">
                            <h2 className="text-3xl font-headline font-bold text-[#191c1e]">
                                Data Access Control
                            </h2>
                            <p className="text-[#434655] mt-1">
                                Manage who can access your medical records
                            </p>
                        </div>
                        {selectedRecord ? (
                            <div className="bg-white rounded-3xl border border-[#e0e3e5] p-8">
                                <AccessManager
                                    analysisId={selectedRecord.id}
                                    recordId={selectedRecord.record_id}
                                    patientWallet={userId}
                                />
                            </div>
                        ) : (
                            <div className="bg-white rounded-3xl p-12 text-center border border-[#e0e3e5]">
                                <div className="w-16 h-16 rounded-full bg-[#dbe1ff] mx-auto mb-4 flex items-center justify-center">
                                    <span className="material-symbols-outlined text-[#004ac6] text-3xl">
                                        lock
                                    </span>
                                </div>
                                <h3 className="text-xl font-bold text-[#191c1e] mb-2">
                                    No Records to Share
                                </h3>
                                <p className="text-[#434655]">
                                    Upload a medical report to manage access permissions
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {/* Appointments View */}
                {activeTab === 'appointments' && (
                    <div className="animate-fade-in h-full">
                        <div className="mb-6">
                            <h2 className="text-3xl font-headline font-bold text-[#191c1e]">
                                Appointments
                            </h2>
                            <p className="text-[#434655] mt-1">
                                Manage your medical appointments
                            </p>
                        </div>
                        <div className="bg-white rounded-3xl border border-[#e0e3e5] p-8">
                            <AppointmentsView address={userId} />
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
