'use client';

import { useState, useEffect, useRef } from 'react';
import { useContract } from '@/hooks/useContract';
import { getAllDoctors, getAccessGrants, createSimpleAccessGrant, apiRevokeAccess } from '@/lib/api';

interface AccessManagerProps {
    analysisId: string;
    recordId?: number;
    patientWallet?: string;
}

interface Doctor {
    wallet_address: string;
    name: string;
    specialty: string;
}

const SPECIALTY_ICONS: Record<string, string> = {
    'Radiology': '📡',
    'Endocrinology': '🧬',
    'Dermatology': '🧴',
    'Neurology': '🧠',
    'Cardiology': '❤️',
    'General Practice': '🩺',
    'Oncology': '🔬',
    'Pediatrics': '🧸',
    'Orthopedics': '🦴',
};

export default function AccessManager({ analysisId, recordId, patientWallet }: AccessManagerProps) {
    const { grantAccess, revokeAccess, getUserRole } = useContract();
    const [doctors, setDoctors] = useState<Doctor[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    const [isGranting, setIsGranting] = useState(false);
    const [isRevoking, setIsRevoking] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
    const [grantedDoctors, setGrantedDoctors] = useState<string[]>([]);
    
    // Timebound access states
    const [selectedDuration, setSelectedDuration] = useState<number | 'custom'>(2);
    const [customHours, setCustomHours] = useState('');
    const [showDurationSelector, setShowDurationSelector] = useState(false);

    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        loadDoctors();
        loadAccessGrants();
    }, [analysisId]);

    const loadAccessGrants = async () => {
        try {
            const { grants } = await getAccessGrants(analysisId);
            if (grants) {
                // Deduplicate wallet addresses
                const unique = [...new Set(grants.map((d: any) => d.doctor_wallet as string))];
                setGrantedDoctors(unique);
            }
        } catch (err) {
            console.error('Failed to load access grants:', err);
        }
    };

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const loadDoctors = async () => {
        try {
            const { doctors: data } = await getAllDoctors();
            if (data) {
                setDoctors(data as Doctor[]);
            }
        } catch (err) {
            console.error('Failed to load doctors:', err);
        }
    };

    const handleGrant = async () => {
        if (!selectedDoctor) return;

        // Validate duration
        let durationHours: number;
        if (selectedDuration === 'custom') {
            const parsed = parseFloat(customHours);
            if (isNaN(parsed) || parsed <= 0) {
                setMessage({ type: 'error', text: 'Please enter a valid number of hours' });
                return;
            }
            durationHours = parsed;
        } else {
            durationHours = selectedDuration;
        }

        setIsGranting(true);
        setMessage(null);

        const hasBlockchainRecord = recordId !== undefined;

        try {
            let blockchainSuccess = false;

            if (hasBlockchainRecord) {
                try {
                    await grantAccess(selectedDoctor.wallet_address, recordId!);
                    blockchainSuccess = true;
                } catch (blockchainErr: any) {
                    console.warn('Blockchain grant failed, falling back to DB-only:', blockchainErr);
                    const errMsg = blockchainErr?.reason || blockchainErr?.message || '';
                    // If user explicitly rejected the tx, stop. Don't do DB grant.
                    if (errMsg.includes('user rejected') || errMsg.includes('ACTION_REJECTED')) {
                        setMessage({ type: 'error', text: 'Transaction rejected in wallet. Access not granted.' });
                        setIsGranting(false);
                        return;
                    }
                    // Otherwise fall through to DB-only
                }
            }

            // Sync to DB regardless of blockchain outcome
            if (patientWallet) {
                await createSimpleAccessGrant({
                    patient_wallet: patientWallet,
                    doctor_wallet: selectedDoctor.wallet_address,
                    analysis_id: analysisId,
                    expires_in_hours: durationHours,
                });
            }

            // Deduplicate — only add if not already in list
            setGrantedDoctors(prev =>
                prev.includes(selectedDoctor.wallet_address)
                    ? prev
                    : [...prev, selectedDoctor.wallet_address]
            );

            if (blockchainSuccess) {
                setMessage({ type: 'success', text: `✅ Access granted to ${selectedDoctor.name} for ${durationHours}h (on-chain + database)` });
            } else {
                setMessage({ type: 'success', text: `✅ Access granted to ${selectedDoctor.name} for ${durationHours}h` });
            }

            setSelectedDoctor(null);
            setSearchQuery('');
            setShowDurationSelector(false);
            setSelectedDuration(2);
            setCustomHours('');
        } catch (err: any) {
            console.error('Grant access DB error:', err);
            const errorMsg = err?.message || 'Unknown error';
            setMessage({ type: 'error', text: `Failed to grant access: ${errorMsg.slice(0, 120)}` });
        } finally {
            setIsGranting(false);
        }
    };

    const handleRevoke = async (doctorWallet: string) => {
        if (recordId === undefined) return;
        setIsRevoking(true);
        setMessage(null);
        try {
            await revokeAccess(doctorWallet, recordId);

            // Sync with Supabase (deactivate previous grants)
            await apiRevokeAccess({
                doctor_wallet: doctorWallet,
                analysis_id: analysisId
            });

            setGrantedDoctors(prev => prev.filter(d => d !== doctorWallet));
            setMessage({ type: 'success', text: `Access revoked from doctor` });
        } catch (err: any) {
            setMessage({ type: 'error', text: 'Failed to revoke access' });
        } finally {
            setIsRevoking(false);
        }
    };

    const filteredDoctors = doctors.filter(doc =>
        doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (doc.specialty && doc.specialty.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    return (
        <div className="space-y-4 max-w-2xl">
            {/* MANAGE ACCESS Block */}
            <div className="bg-white border-2 border-black p-5 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-[#FFB800] border-2 border-black rounded-lg flex items-center justify-center shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                        <span className="text-2xl">🔐</span>
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-black tracking-widest uppercase font-serif">Manage Access</h3>
                        <p className="text-[13px] text-gray-700 font-mono tracking-tight">Control who views this medical record</p>
                    </div>
                </div>
            </div>

            {/* Custom Dropdown */}
            <div className="relative" ref={dropdownRef}>
                <div
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="w-full bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-4 flex justify-between items-center cursor-pointer hover:bg-gray-50 transition-colors"
                >
                    <span className="font-bold text-gray-600 uppercase text-sm tracking-wide">
                        {selectedDoctor ? selectedDoctor.name : 'Select a doctor...'}
                    </span>
                    <span className="font-bold text-black text-xs">
                        {isDropdownOpen ? '▲' : '▼'}
                    </span>
                </div>

                {isDropdownOpen && (
                    <div className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] z-50">
                        {/* Search Input */}
                        <div className="p-3 border-b-2 border-black bg-white">
                            <input
                                type="text"
                                placeholder="SEARCH DOCTORS..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-white border-2 border-black px-3 py-2 font-mono text-xs uppercase tracking-wide focus:outline-none shadow-[inset_2px_2px_0px_0px_rgba(0,0,0,0.1)] focus:bg-gray-50"
                                onClick={(e) => e.stopPropagation()}
                            />
                        </div>

                        {/* Dropdown Options */}
                        <div className="max-h-[300px] overflow-y-auto w-full custom-scrollbar">
                            {filteredDoctors.length === 0 ? (
                                <div className="p-4 text-center text-gray-500 font-mono text-sm uppercase">No doctors found</div>
                            ) : (
                                filteredDoctors.map(doc => {
                                    const isSelected = selectedDoctor?.wallet_address === doc.wallet_address;
                                    return (
                                        <div
                                            key={doc.wallet_address}
                                            onClick={() => {
                                                setSelectedDoctor(doc);
                                                setIsDropdownOpen(false);
                                                setSearchQuery('');
                                            }}
                                            className={`relative flex items-center gap-4 p-4 border-b border-gray-200 last:border-b-0 cursor-pointer transition-colors group hover:bg-gray-50/80 ${isSelected ? 'bg-gray-50' : ''}`}
                                        >
                                            <div className="text-2xl drop-shadow-sm transform group-hover:scale-110 transition-transform">
                                                {SPECIALTY_ICONS[doc.specialty] || '🧑‍⚕️'}
                                            </div>
                                            <div className="flex-1">
                                                <div className="font-bold text-black text-[15px]">{doc.name}</div>
                                                <div className="text-[13px] text-gray-500 font-mono mt-0.5">{doc.specialty}</div>
                                            </div>
                                            {/* Cyan highlight bar on right/hover */}
                                            <div className={`absolute right-0 top-0 bottom-0 w-2 ${isSelected ? 'bg-cyan-400 border-l border-black' : 'group-hover:bg-cyan-200'} transition-colors`} />
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Duration Selector */}
            {selectedDoctor && (
                <div className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-5">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 bg-[#A78BFA] border-2 border-black rounded-lg flex items-center justify-center shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                            <span className="text-xl">⏱️</span>
                        </div>
                        <div>
                            <h4 className="font-bold tracking-widest uppercase text-sm font-serif">Access Duration</h4>
                            <p className="text-[11px] text-gray-600 font-mono">How long should access last?</p>
                        </div>
                    </div>

                    {/* Duration Buttons */}
                    <div className="grid grid-cols-2 gap-3 mb-3">
                        {[
                            { value: 1, label: '1 Hour', icon: '⚡' },
                            { value: 2, label: '2 Hours', icon: '⏰' },
                            { value: 24, label: '24 Hours', icon: '📅' },
                            { value: 'custom' as const, label: 'Custom', icon: '⚙️' },
                        ].map((option) => (
                            <button
                                key={option.value}
                                onClick={() => setSelectedDuration(option.value)}
                                className={`relative p-4 border-2 border-black font-bold uppercase text-xs tracking-wider transition-all duration-200 ${
                                    selectedDuration === option.value
                                        ? 'bg-[#A78BFA] text-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] -translate-y-1 -translate-x-1'
                                        : 'bg-white text-gray-700 hover:bg-gray-50 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]'
                                }`}
                            >
                                <div className="flex items-center justify-center gap-2">
                                    <span className="text-lg">{option.icon}</span>
                                    <span>{option.label}</span>
                                </div>
                                {selectedDuration === option.value && (
                                    <div className="absolute top-1 right-1 w-3 h-3 bg-[#A3E635] border border-black rounded-full" />
                                )}
                            </button>
                        ))}
                    </div>

                    {/* Custom Hours Input */}
                    {selectedDuration === 'custom' && (
                        <div className="mt-3 p-4 bg-gray-50 border-2 border-black">
                            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-2 font-mono">
                                Enter Hours
                            </label>
                            <input
                                type="number"
                                value={customHours}
                                onChange={(e) => setCustomHours(e.target.value)}
                                placeholder="e.g., 0.5, 6, 48"
                                min="0.1"
                                step="0.5"
                                className="w-full bg-white border-2 border-black px-4 py-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-[#A78BFA] shadow-[inset_2px_2px_0px_0px_rgba(0,0,0,0.1)]"
                            />
                            <p className="text-[10px] text-gray-500 mt-2 font-mono uppercase tracking-wide">
                                💡 Examples: 0.5 = 30 min, 6 = 6 hours, 48 = 2 days
                            </p>
                        </div>
                    )}

                    {/* Duration Info */}
                    <div className="mt-3 p-3 bg-[#FEF3C7] border-2 border-[#F59E0B]">
                        <p className="text-xs font-mono text-gray-800">
                            ⚠️ Access will automatically expire after the selected duration
                        </p>
                    </div>
                </div>
            )}

            {/* Grant Button */}
            <button
                onClick={handleGrant}
                disabled={isGranting || !selectedDoctor}
                className={`w-full border-2 border-black p-4 font-bold uppercase text-sm tracking-widest transition-all duration-200 ${selectedDoctor
                    ? 'bg-retro-accent-green hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-1 hover:-translate-x-1 text-black'
                    : 'bg-white/80 text-gray-500 shadow-[inset_2px_2px_0px_0px_rgba(0,0,0,0.05)] cursor-not-allowed'
                    }`}
            >
                {isGranting ? 'Granting Access...' : selectedDoctor ? `Grant Access to ${selectedDoctor.name}` : 'Select a doctor first'}
            </button>

            {/* Message Area */}
            {message && (
                <div className={`p-4 border-2 border-black font-mono text-sm font-bold uppercase tracking-wide ${message.type === 'success' ? 'bg-[#A3E635] text-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]' : 'bg-[#F87171] text-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'}`}>
                    {message.text}
                </div>
            )}

            {/* Granted Doctors Area */}
            {grantedDoctors.length > 0 && (
                <div className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-5 mt-8">
                    <h4 className="font-bold tracking-widest uppercase border-b-2 border-black pb-3 mb-4 text-sm font-serif">Granted Doctors</h4>
                    <div className="space-y-4">
                        {grantedDoctors.map((docWallet, idx) => {
                            const doc = doctors.find(d => d.wallet_address === docWallet);
                            return (
                                <div key={`${docWallet}-${idx}`} className="flex items-center justify-between border-2 border-gray-200 hover:border-black p-3 bg-gray-50 transition-colors">
                                    <div className="flex items-center gap-4">
                                        <div className="text-2xl drop-shadow-sm">{SPECIALTY_ICONS[doc?.specialty || ''] || '🧑‍⚕️'}</div>
                                        <div>
                                            <div className="font-bold text-sm text-black">{doc?.name || 'Unknown Doctor'}</div>
                                            <div className="text-[11px] font-mono text-gray-500 mt-1 uppercase">Wallet: {docWallet.slice(0, 8)}...{docWallet.slice(-6)}</div>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => handleRevoke(docWallet)}
                                        disabled={isRevoking}
                                        className="text-xs font-bold text-black border-2 border-black px-4 py-2 bg-[#F87171] hover:bg-red-400 hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all disabled:opacity-50 disabled:hover:shadow-none uppercase tracking-wider"
                                    >
                                        REVOKE
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
