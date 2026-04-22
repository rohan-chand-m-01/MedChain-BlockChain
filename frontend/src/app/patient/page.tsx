'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { usePrivy } from '@privy-io/react-auth';
import { useAuth } from '@/contexts/AuthContext';
import { hasRole, hasAnyRole } from '@/lib/auth';
import {
    getPatientRecords,
    deleteRecord as apiDeleteRecord,
    updateRecord,
    checkRecordCache,
    cloneRecord,
    getAppointments,
    analyzeReport,
} from '@/lib/api';
import FileUpload from '@/components/FileUpload';
import ChatBot from '@/components/ChatBot';
import TavusVideo from '@/components/TavusVideo';
import AccessManager from '@/components/AccessManager';
import MedicalDisclaimer from '@/components/MedicalDisclaimer';
import AnalysisView from './components/AnalysisView';
import AppointmentsView from './components/AppointmentsView';
import DigitalTwin from '@/components/DigitalTwin';
import EditorialSidebar from '@/components/EditorialSidebar';
import EditorialTopNav from '@/components/EditorialTopNav';
import AuthMethodIndicator from '@/components/AuthMethodIndicator';
import { generateEncryptionKey, encryptFile, decryptFileFromIPFS } from '@/lib/encryption';
import { uploadToIPFS, isIPFSConfigured } from '@/lib/ipfs';

// ... (Interface declarations identical to original) ...
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
    const { isAuthenticated, userId, authMethod } = useAuth();
    const { user } = usePrivy();
    const [records, setRecords] = useState<Analysis[]>([]);
    const [selectedRecord, setSelectedRecord] = useState<Analysis | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [activeTab, setActiveTab] = useState<'analysis' | 'chat' | 'avatar' | 'access' | 'appointments' | 'twin' | 'profile'>('analysis');
    const [uploadStatus, setUploadStatus] = useState('');
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    useEffect(() => {
        // Wait for auth to be fully loaded
        if (isAuthenticated === undefined) return;
        
        if (!isAuthenticated) { 
            console.log('[Patient Dashboard] Not authenticated, redirecting to home');
            router.push('/'); 
            return; 
        }
        
        // Check if user has selected a role (stored in localStorage)
        const userRole = localStorage.getItem('userRole');
        if (!userRole) {
            console.log('[Patient Dashboard] No role selected, redirecting to register');
            router.push('/register?role=patient');
            return;
        }
        
        // If user selected doctor role, redirect to doctor dashboard
        if (userRole === 'doctor') {
            console.log('[Patient Dashboard] User is a doctor, redirecting to doctor dashboard');
            router.push('/doctor');
            return;
        }
        
        console.log('[Patient Dashboard] User authenticated as patient, loading data');
        if (userId) {
            loadRecords();
            loadAppointments();
        }
    }, [isAuthenticated, userId, router]);

    const loadRecords = async () => {
        if (!userId) return;
        try {
            console.log('[Patient Dashboard] Loading records for user:', userId);
            const { records: data } = await getPatientRecords(userId);
            console.log('[Patient Dashboard] Records loaded from DATABASE:', data?.length || 0, 'records');
            console.log('[Patient Dashboard] Records data:', data);
            console.log('[Patient Dashboard] First record sample:', data?.[0]);
            if (data && data.length > 0) {
                setRecords(data as Analysis[]);
                
                // Backup to localStorage AFTER loading from database
                try {
                    localStorage.setItem(`medichain_records_${userId}`, JSON.stringify(data));
                    console.log('[Patient Dashboard] ✅ Backed up', data.length, 'records to localStorage');
                } catch (storageErr) {
                    console.warn('[Patient Dashboard] Failed to backup to localStorage:', storageErr);
                }
                
                if (!selectedRecord) setSelectedRecord(data[0] as Analysis);
            } else {
                console.log('[Patient Dashboard] No records in database, checking localStorage...');
                // Only use localStorage if database is empty
                try {
                    const backup = localStorage.getItem(`medichain_records_${userId}`);
                    if (backup) {
                        const backupData = JSON.parse(backup);
                        console.log('[Patient Dashboard] Loaded from localStorage backup:', backupData.length, 'records');
                        setRecords(backupData as Analysis[]);
                        if (backupData.length > 0 && !selectedRecord) setSelectedRecord(backupData[0] as Analysis);
                    }
                } catch (storageErr) {
                    console.error('[Patient Dashboard] Failed to load from localStorage:', storageErr);
                }
            }
        } catch (err) {
            console.error('Failed to load records from database:', err);
            
            // Try to load from localStorage backup only if API fails
            try {
                const backup = localStorage.getItem(`medichain_records_${userId}`);
                if (backup) {
                    const backupData = JSON.parse(backup);
                    console.log('[Patient Dashboard] API failed, loaded from localStorage backup:', backupData.length, 'records');
                    setRecords(backupData as Analysis[]);
                    if (backupData.length > 0 && !selectedRecord) setSelectedRecord(backupData[0] as Analysis);
                }
            } catch (storageErr) {
                console.error('[Patient Dashboard] Failed to load from localStorage:', storageErr);
            }
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

    /**
     * Fast regex-based PII redaction — no ML model needed.
     * Scrubs common PII patterns from medical text.
     */
    const redactPII = (text: string): string => {
        let redacted = text;
        // SSN patterns (xxx-xx-xxxx, xxx xx xxxx)
        redacted = redacted.replace(/\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b/g, '[REDACTED-SSN]');
        // Phone numbers
        redacted = redacted.replace(/(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g, '[REDACTED-PHONE]');
        // Email addresses
        redacted = redacted.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[REDACTED-EMAIL]');
        // Dates of birth patterns (DOB: ..., Date of Birth: ..., Born: ...)
        redacted = redacted.replace(/(DOB|Date of Birth|Born)\s*[:\-]?\s*\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}/gi, '$1: [REDACTED-DOB]');
        // Named fields (Patient Name:, Name:, Patient:)
        redacted = redacted.replace(/(Patient\s*Name|Patient|Name)\s*[:\-]\s*[A-Z][a-zA-Z]+(\s+[A-Z][a-zA-Z]+){0,3}/g, '$1: [REDACTED-NAME]');
        // MRN / Medical Record Numbers
        redacted = redacted.replace(/(MRN|Medical Record Number|Record\s*#?)\s*[:\-]?\s*[A-Z0-9-]{4,}/gi, '$1: [REDACTED-MRN]');
        // Addresses (simple: number + street name patterns)
        redacted = redacted.replace(/\b\d{1,5}\s+[A-Z][a-zA-Z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Court|Ct)\.?\b/gi, '[REDACTED-ADDRESS]');
        return redacted;
    };

    const handleFileUpload = async (file: File) => {
        if (!userId) return;
        
        console.log('[Upload] Starting upload for file:', file.name);
        setIsUploading(true);
        setUploadStatus('');

        // DISABLED CACHE - Always perform fresh analysis for accurate results
        // The cache was causing issues where different files with same name
        // would show identical analysis results
        console.log('[Upload] Cache disabled - performing fresh analysis');

        try {
            let fileKey: string = '';
            let encryptionKeyForUser: string | null = null;
            let fileBase64: string = '';

            // Convert file to base64 for backend processing
            setUploadStatus('📄 Processing file...');
            
            const buffer = await file.arrayBuffer();
            const bytes = new Uint8Array(buffer);
            let binary = '';
            for (let i = 0; i < bytes.length; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            fileBase64 = btoa(binary);
            const fileTypeForBackend = file.type || 'application/pdf';

            // Safety guard: never send an empty file_base64
            if (!fileBase64) {
                throw new Error('Failed to process file for upload. The file may be empty or corrupted.');
            }

            // 2. SKIP IPFS FOR NOW - Direct analysis
            // IPFS upload is optional and can be added later
            let cid: string | null = null;
            let encryptionIv: string | null = null;
            let keyHash: string | null = null;
            
            // Try IPFS upload with timeout (optional, non-blocking)
            if (false) { // Disabled IPFS for now - change to true to enable
                try {
                    setUploadStatus('🔐 Encrypting original file...');
                    
                    const key = generateEncryptionKey();
                    encryptionKeyForUser = key;
                    const { encryptedBlob, iv: ivString, keyHash: hash } = await encryptFile(file, key);

                    setUploadStatus('🌐 Uploading to IPFS (optional)...');
                    
                    // Add timeout to IPFS upload
                    const uploadPromise = uploadToIPFS(encryptedBlob, file.name, {
                        patient: userId || 'unknown',
                        iv: ivString,
                    });
                    
                    const timeoutPromise = new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('IPFS upload timeout')), 30000)
                    );
                    
                    const result = await Promise.race([uploadPromise, timeoutPromise]) as any;
                    cid = result.cid;
                    encryptionIv = ivString;
                    keyHash = hash;
                    
                    console.log('[Upload] ✅ IPFS upload successful:', cid);
                } catch (ipfsError) {
                    console.warn('[Upload] ⚠️ IPFS upload failed (non-critical):', ipfsError);
                    setUploadStatus('⚠️ IPFS upload skipped, continuing with analysis...');
                    // Continue without IPFS
                }
            }

            setUploadStatus('🤖 Analyzing with AI...');
            
            const analysis: any = await analyzeReport({
                file_base64: fileBase64,
                file_type: fileTypeForBackend,
                patient_wallet: userId,
                file_name: file.name,
            });

            if (analysis?.error) {
                throw new Error(`Analysis Failed: ${analysis.error}`);
            }

            // Update record with IPFS data if available
            if (cid && keyHash && encryptionIv && analysis.analysis.id && !analysis.analysis.id.startsWith('temp_')) {
                try {
                    await updateRecord(analysis.analysis.id, {
                        file_url: `ipfs://${cid}`,
                        file_fingerprint: keyHash,
                        ipfs_cid: cid,
                        encryption_iv: encryptionIv,
                    });
                } catch (updateError) {
                    console.warn('[Upload] ⚠️ Failed to update record with IPFS data:', updateError);
                }
            }

            // Store proof on Stellar blockchain (optional)
            if (cid) {
                try {
                    setUploadStatus('⛓️ Storing proof on Stellar blockchain...');
                    console.log('[Upload] Calling Stellar store-proof with:', {
                        ipfs_hash: cid,
                        risk_score: analysis.analysis.risk_score || 50,
                        risk_level: analysis.analysis.risk_level || 'medium'
                    });
                    
                    const stellarResponse = await fetch('/api/stellar/store-proof', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            ipfs_hash: cid,
                            risk_score: analysis.analysis.risk_score || 50,
                            risk_level: analysis.analysis.risk_level || 'medium'
                        })
                    });

                    console.log('[Upload] Stellar response status:', stellarResponse.status);
                    
                    if (stellarResponse.ok) {
                        const stellarData = await stellarResponse.json();
                        console.log('[Upload] ✅ Stellar proof stored successfully!');
                        console.log('[Upload] Transaction hash:', stellarData.tx_hash);
                        setUploadStatus('✅ Proof stored on Stellar blockchain!');
                    } else {
                        const errorText = await stellarResponse.text();
                        console.error('[Upload] ⚠️ Stellar storage failed:', stellarResponse.status, errorText);
                    }
                } catch (stellarError) {
                    console.error('[Upload] Stellar storage error:', stellarError);
                }
            }

            setUploadStatus('');
            if (encryptionKeyForUser) {
                // Create a Blob containing the key
                const keyBlob = new Blob([encryptionKeyForUser], { type: 'text/plain' });
                const keyUrl = URL.createObjectURL(keyBlob);

                // Create an invisible download link to save the key
                const a = document.createElement('a');
                a.href = keyUrl;
                a.download = `medichain-key-${file.name}.txt`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(keyUrl);

                alert(`✅ File encrypted & uploaded!\n\n🛑 We have automatically downloaded your Encryption Key as a file.\n\nPLEASE STORE IT SECURELY. If you lose it, you can never decrypt this file again.`);
            }

            // Wait for database to save, then refresh from database
            console.log('[Upload] ✅ Analysis complete, refreshing from database...');
            await loadRecords();  // This will load from database and backup to localStorage
            setRefreshTrigger(prev => prev + 1);
            
            // Switch to twin tab to show new analysis
            setActiveTab('twin');
            console.log('[Upload] ✅ Upload complete!');

        } catch (err: any) {
            console.error('[Upload] Upload failed:', err);
            setUploadStatus(`Upload failed: ${err.message || 'Unknown error'}`);
            alert(`Upload failed: ${err.message || 'Unknown error'}`);
        } finally {
            console.log('[Upload] Upload process complete, resetting isUploading');
            setIsUploading(false);
        }
    };

    const deleteRecord = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm('Are you sure you want to delete this record?')) return;

        const originalRecords = [...records];
        setRecords(prev => prev.filter(r => r.id !== id));
        if (selectedRecord?.id === id) setSelectedRecord(null);

        try {
            await apiDeleteRecord(id);
            await loadRecords();
        } catch (err: any) {
            console.error('Failed to delete:', err);
            setRecords(originalRecords);
            alert(`Failed to delete record: ${err.message || 'Unknown error'}`);
        }
    };

    const handleViewDocument = async () => {
        if (!selectedRecord || !(selectedRecord as any).ipfs_cid || !(selectedRecord as any).encryption_key) {
            alert('Cannot view document: missing IPFS CID or encryption key.');
            return;
        }

        const cid = (selectedRecord as any).ipfs_cid;
        const key = (selectedRecord as any).encryption_key;
        const iv = (selectedRecord as any).encryption_iv;

        try {
            setUploadStatus('🔓 Decrypting document...');
            const blob = await decryptFileFromIPFS(cid, key, iv);
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
        } catch (err: any) {
            console.error('Decryption failed:', err);
            alert(`Failed to decrypt document: ${err.message}`);
        } finally {
            setUploadStatus('');
        }
    };

    if (!isAuthenticated || !userId) return null;

    const handleDeleteRecord = async (recordId: string) => {
        try {
            console.log('[Delete] Deleting record:', recordId);
            
            // Call the delete API
            await apiDeleteRecord(recordId);
            
            // Remove from local state
            const updatedRecords = records.filter(r => r.id !== recordId);
            setRecords(updatedRecords);
            
            // Update localStorage backup
            localStorage.setItem('medicalRecordsBackup', JSON.stringify(updatedRecords));
            
            // If the deleted record was selected, select another one
            if (selectedRecord?.id === recordId) {
                setSelectedRecord(updatedRecords.length > 0 ? updatedRecords[0] : null);
            }
            
            console.log('[Delete] Record deleted successfully');
        } catch (error) {
            console.error('[Delete] Failed to delete record:', error);
            alert('Failed to delete record. Please try again.');
        }
    };

    return (
        <div className="flex min-h-screen bg-[#f7f9fb]">
            <EditorialSidebar 
                activeTab={activeTab} 
                onTabChange={(tab) => {
                    if (tab === 'profile') {
                        router.push('/profile');
                    } else {
                        setActiveTab(tab as typeof activeTab);
                    }
                }}
                records={records}
                selectedRecordId={selectedRecord?.id || null}
                onRecordSelect={(recordId) => {
                    console.log('[Sidebar] Record selected:', recordId);
                    const record = records.find(r => r.id === recordId);
                    console.log('[Sidebar] Found record:', record);
                    if (record) {
                        setSelectedRecord(record);
                        setActiveTab('analysis'); // Switch to analysis tab when selecting a record
                        console.log('[Sidebar] Selected record set, switching to analysis tab');
                    } else {
                        console.warn('[Sidebar] Record not found in records array');
                    }
                }}
                onRecordDelete={handleDeleteRecord}
            />

            <div className="flex-1 flex flex-col min-w-0">
                <EditorialTopNav />

                {/* Main Content */}
                <main className="pl-72 pr-8 py-8 flex flex-col gap-8 flex-1">
                    {/* Main Content Area */}
                    <div className="bg-white rounded-xl border border-[#c3c6d7]/20 shadow-[0_12px_32px_-4px_rgba(44,52,52,0.06)] overflow-hidden flex flex-col" style={{minHeight: 'calc(100vh - 16rem)'}}>
                        {selectedRecord ? (
                            <div className="p-8 flex-1 overflow-y-auto custom-scrollbar">
                                {/* Analysis panel */}
                                {activeTab === 'analysis' && (
                                    <div className="animate-fade-in">
                                        {/* Upload Button - Floating Action */}
                                        <div className="flex justify-between items-center mb-6">
                                            <div>
                                                <h2 className="text-2xl font-bold text-[#191c1e]">Medical Analysis</h2>
                                                <p className="text-sm text-[#737686] mt-1">AI-powered insights from your medical reports</p>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                {/* Refresh Button */}
                                                <button
                                                    onClick={() => {
                                                        console.log('[Manual Refresh] User clicked refresh button');
                                                        loadRecords();
                                                    }}
                                                    className="flex items-center gap-2 bg-white hover:bg-gray-50 text-gray-700 px-4 py-3 rounded-xl font-semibold text-sm border border-gray-200 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5"
                                                    title="Refresh records list"
                                                >
                                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                        <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                                    </svg>
                                                    Refresh
                                                </button>
                                                
                                                {/* Export Records Button */}
                                                <button
                                                    onClick={() => {
                                                        try {
                                                            const backup = localStorage.getItem(`medichain_records_${userId}`);
                                                            if (backup) {
                                                                const blob = new Blob([backup], { type: 'application/json' });
                                                                const url = URL.createObjectURL(blob);
                                                                const a = document.createElement('a');
                                                                a.href = url;
                                                                a.download = `medichain-records-backup-${new Date().toISOString().split('T')[0]}.json`;
                                                                document.body.appendChild(a);
                                                                a.click();
                                                                document.body.removeChild(a);
                                                                URL.revokeObjectURL(url);
                                                                alert('✅ Records exported successfully!');
                                                            } else {
                                                                alert('⚠️ No backup records found in localStorage');
                                                            }
                                                        } catch (err) {
                                                            console.error('Export failed:', err);
                                                            alert('❌ Failed to export records');
                                                        }
                                                    }}
                                                    className="flex items-center gap-2 bg-white hover:bg-gray-50 text-gray-700 px-4 py-3 rounded-xl font-semibold text-sm border border-gray-200 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5"
                                                    title="Export records backup"
                                                >
                                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                    </svg>
                                                    Export
                                                </button>
                                                
                                                {/* Upload Button */}
                                                <label className="cursor-pointer group">
                                                    <div className="flex items-center gap-2 bg-[#2563eb] hover:bg-[#1d4ed8] text-white px-5 py-3 rounded-xl font-semibold text-sm shadow-lg shadow-[#2563eb]/20 transition-all hover:shadow-xl hover:shadow-[#2563eb]/30 hover:-translate-y-0.5">
                                                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                            <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                                        </svg>
                                                        {isUploading ? 'Uploading...' : 'Upload New Report'}
                                                    </div>
                                                    <input
                                                        type="file"
                                                        accept=".pdf,.jpg,.jpeg,.png"
                                                        onChange={(e) => {
                                                            const file = e.target.files?.[0];
                                                            if (file) handleFileUpload(file);
                                                        }}
                                                        disabled={isUploading}
                                                        className="hidden"
                                                    />
                                                </label>
                                            </div>
                                        </div>

                                        {/* Upload Status */}
                                        {uploadStatus && (
                                            <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 flex items-center gap-3 animate-fade-in">
                                                <div className="w-5 h-5 rounded-full border-2 border-[#2563eb] border-t-transparent animate-spin shrink-0"></div>
                                                <div className="flex-1">
                                                    <p className="text-sm font-semibold text-blue-900">{uploadStatus}</p>
                                                    <p className="text-xs text-blue-600 mt-0.5">This may take a few moments...</p>
                                                </div>
                                            </div>
                                        )}

                                        <AnalysisView record={selectedRecord} />
                                    </div>
                                )}

                                {/* Chat panel */}
                                {activeTab === 'chat' && userId && (
                                    <div className="animate-fade-in h-full">
                                        <ChatBot patientWallet={userId} />
                                    </div>
                                )}

                                {/* Avatar panel */}
                                {activeTab === 'avatar' && (
                                    <div className="animate-fade-in">
                                        <TavusVideo
                                            summary={selectedRecord.summary}
                                            riskScore={selectedRecord.risk_score}
                                            conditions={selectedRecord.conditions}
                                            specialist={selectedRecord.specialist}
                                            urgency={selectedRecord.urgency}
                                        />
                                    </div>
                                )}

                                {/* Digital Twin (3D Body) */}
                                {activeTab === 'twin' && (
                                    <div className="animate-fade-in">
                                        <DigitalTwin analysisData={selectedRecord} recordId={selectedRecord.id} />
                                    </div>
                                )}

                                {/* Access control panel */}
                                {activeTab === 'access' && (
                                    <div className="animate-fade-in max-w-3xl">
                                        <AccessManager
                                            analysisId={selectedRecord.id}
                                            recordId={selectedRecord.record_id}
                                            patientWallet={userId}
                                        />
                                    </div>
                                )}

                                {/* Appointments panel */}
                                {activeTab === 'appointments' && (
                                    <div className="animate-fade-in">
                                        <AppointmentsView address={userId || ''} />
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="p-12 text-center flex-1 flex flex-col items-center justify-center">
                                {activeTab === 'analysis' ? (
                                    <div className="max-w-2xl mx-auto w-full animate-fade-in">
                                        {/* Modern Upload Area */}
                                        <label className="cursor-pointer group block">
                                            <div className="relative bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-3xl border-2 border-dashed border-blue-200 hover:border-blue-400 transition-all duration-300 p-16 hover:shadow-2xl hover:shadow-blue-100">
                                                {/* Background Pattern */}
                                                <div className="absolute inset-0 opacity-5">
                                                    <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
                                                        <defs>
                                                            <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
                                                                <circle cx="16" cy="16" r="1" fill="currentColor" className="text-blue-600"/>
                                                            </pattern>
                                                        </defs>
                                                        <rect width="100%" height="100%" fill="url(#grid)" />
                                                    </svg>
                                                </div>

                                                {/* Content */}
                                                <div className="relative z-10">
                                                    {/* Icon */}
                                                    <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-3xl flex items-center justify-center mb-6 mx-auto shadow-xl shadow-blue-500/30 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                                                        <svg className="w-12 h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                            <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                                        </svg>
                                                    </div>

                                                    {/* Text */}
                                                    <h3 className="text-3xl font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors">
                                                        {isUploading ? 'Processing Your Report...' : 'Upload Medical Report'}
                                                    </h3>
                                                    <p className="text-base text-gray-600 mb-6 max-w-md mx-auto leading-relaxed">
                                                        {isUploading 
                                                            ? 'Our AI is analyzing your medical data. This may take a few moments.'
                                                            : 'Drop your medical report here or click to browse. Our AI will analyze it instantly.'
                                                        }
                                                    </p>

                                                    {/* Upload Status or File Types */}
                                                    {uploadStatus ? (
                                                        <div className="w-full max-w-md mx-auto">
                                                            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-2xl p-6 shadow-xl">
                                                                <div className="flex items-center gap-4 mb-4">
                                                                    <div className="w-12 h-12 rounded-full border-4 border-blue-600 border-t-transparent animate-spin shrink-0"></div>
                                                                    <div className="flex-1 text-left">
                                                                        <p className="text-lg font-bold text-blue-900 mb-1">{uploadStatus}</p>
                                                                        <p className="text-sm text-blue-700">Please wait while we process your report...</p>
                                                                    </div>
                                                                </div>
                                                                
                                                                {/* Progress Steps */}
                                                                <div className="space-y-2 mt-4 pt-4 border-t border-blue-200">
                                                                    <div className="flex items-center gap-2 text-xs text-blue-700">
                                                                        <div className={`w-2 h-2 rounded-full ${uploadStatus.includes('Processing') ? 'bg-blue-600 animate-pulse' : uploadStatus.includes('Encrypting') || uploadStatus.includes('Uploading') || uploadStatus.includes('Analyzing') ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                                                                        <span className={uploadStatus.includes('Processing') ? 'font-semibold' : ''}>Processing file</span>
                                                                    </div>
                                                                    <div className="flex items-center gap-2 text-xs text-blue-700">
                                                                        <div className={`w-2 h-2 rounded-full ${uploadStatus.includes('Encrypting') ? 'bg-blue-600 animate-pulse' : uploadStatus.includes('Uploading') || uploadStatus.includes('Analyzing') ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                                                                        <span className={uploadStatus.includes('Encrypting') ? 'font-semibold' : ''}>Encrypting data</span>
                                                                    </div>
                                                                    <div className="flex items-center gap-2 text-xs text-blue-700">
                                                                        <div className={`w-2 h-2 rounded-full ${uploadStatus.includes('Uploading') ? 'bg-blue-600 animate-pulse' : uploadStatus.includes('Analyzing') ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                                                                        <span className={uploadStatus.includes('Uploading') ? 'font-semibold' : ''}>Uploading to IPFS</span>
                                                                    </div>
                                                                    <div className="flex items-center gap-2 text-xs text-blue-700">
                                                                        <div className={`w-2 h-2 rounded-full ${uploadStatus.includes('Analyzing') ? 'bg-blue-600 animate-pulse' : 'bg-gray-300'}`}></div>
                                                                        <span className={uploadStatus.includes('Analyzing') ? 'font-semibold' : ''}>AI Analysis</span>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ) : (
                                                        <div className="inline-flex items-center gap-3 bg-white/80 backdrop-blur-sm px-6 py-3 rounded-2xl shadow-lg border border-gray-200 group-hover:border-blue-300 group-hover:shadow-xl transition-all">
                                                            <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                            </svg>
                                                            <span className="text-sm font-medium text-gray-700">PDF, JPG, PNG — up to 10MB</span>
                                                        </div>
                                                    )}

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
                                            </div>
                                            <input
                                                type="file"
                                                accept=".pdf,.jpg,.jpeg,.png"
                                                onChange={(e) => {
                                                    const file = e.target.files?.[0];
                                                    if (file) handleFileUpload(file);
                                                }}
                                                disabled={isUploading}
                                                className="hidden"
                                            />
                                        </label>
                                    </div>
                                ) : (
                                    <div>
                                        <div className="w-24 h-24 bg-[#eceef0] rounded-full flex items-center justify-center mb-6 border border-[#c3c6d7]/20">
                                            <span className="material-symbols-outlined text-5xl text-[#737686]">folder_open</span>
                                        </div>
                                        <h3 className="text-2xl font-semibold text-[#191c1e] mb-2">No Record Selected</h3>
                                        <p className="text-[#737686] max-w-sm mx-auto">Upload a medical document to generate an AI analysis and view your health insights.</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                <div className="mt-8">
                    <MedicalDisclaimer />
                </div>
            </main>

            {/* Footer */}
            <footer className="flex flex-col md:flex-row justify-between items-center py-8 pl-72 pr-8 mt-auto w-full bg-slate-50 dark:bg-slate-900 border-t border-slate-200/10">
                <p className="text-xs text-slate-400 dark:text-slate-500">
                    © 2024 MediChain AI. All rights reserved.
                </p>
                <div className="flex gap-6 mt-4 md:mt-0">
                    <a className="text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity" href="#">
                        Privacy Policy
                    </a>
                    <a className="text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity" href="#">
                        Terms of Service
                    </a>
                    <a className="text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity" href="#">
                        HIPAA Compliance
                    </a>
                    <a className="text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity" href="#">
                        Support
                    </a>
                </div>
            </footer>
        </div>
    </div>
    );
}
