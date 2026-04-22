'use client';

import { useState, useEffect } from 'react';
import { formatEther } from 'ethers';
import { useContract } from '@/hooks/useContract';
import { getAllDoctors, getPatientPaymentRequests, updatePaymentRequest } from '@/lib/api';

interface PaymentEvent {
    patient: string;
    doctor: string;
    amount: bigint;
    timestamp: number;
    txHash: string;
}

interface Doctor {
    id: string;
    wallet_address: string;
    name: string;
    specialty: string;
}

interface PaymentRequest {
    id: string;
    doctor_wallet: string;
    doctor_name: string;
    patient_wallet: string;
    amount: string;
    reason: string;
    status: string;
    tx_hash?: string;
    created_at: string;
}

interface PaymentViewProps {
    address: string;
    viewType: 'patient' | 'doctor';
}

export default function PaymentView({ address, viewType }: PaymentViewProps) {
    const { payDoctor, getPaymentEvents } = useContract();

    // Pay form state
    const [doctors, setDoctors] = useState<Doctor[]>([]);
    const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [showDropdown, setShowDropdown] = useState(false);
    const [amount, setAmount] = useState('');
    const [isPaying, setIsPaying] = useState(false);
    const [txResult, setTxResult] = useState<{ hash: string; success: boolean } | null>(null);
    const [error, setError] = useState('');

    // Payment requests state
    const [paymentRequests, setPaymentRequests] = useState<PaymentRequest[]>([]);
    const [approvingId, setApprovingId] = useState<string | null>(null);

    // History state
    const [payments, setPayments] = useState<PaymentEvent[]>([]);
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);

    useEffect(() => {
        loadPayments();
        if (viewType === 'patient') {
            loadDoctors();
            loadPaymentRequests();
        }
    }, [address]);

    const loadDoctors = async () => {
        try {
            const { doctors: data } = await getAllDoctors();
            setDoctors(data || []);
        } catch (err) {
            console.error('Failed to load doctors:', err);
        }
    };

    const loadPaymentRequests = async () => {
        try {
            const { requests } = await getPatientPaymentRequests(address);
            setPaymentRequests(requests || []);
        } catch (err) {
            console.error('Failed to load payment requests:', err);
        }
    };

    const loadPayments = async () => {
        setIsLoadingHistory(true);
        try {
            const events = await getPaymentEvents(viewType, address);
            setPayments(events.sort((a: PaymentEvent, b: PaymentEvent) => b.timestamp - a.timestamp));
        } catch (err) {
            console.error('Failed to load payments:', err);
        } finally {
            setIsLoadingHistory(false);
        }
    };

    const handlePay = async () => {
        if (!selectedDoctor || !amount) return;
        setIsPaying(true);
        setError('');
        setTxResult(null);
        try {
            const { tx } = await payDoctor(selectedDoctor.wallet_address, amount);
            setTxResult({ hash: tx.hash, success: true });
            setSelectedDoctor(null);
            setSearchQuery('');
            setAmount('');
            await loadPayments();
        } catch (err: any) {
            if (err.message?.includes('user rejected')) {
                setError('Transaction rejected in MetaMask.');
            } else if (err.message?.includes('Recipient is not a doctor')) {
                setError('That address is not registered as a doctor on the blockchain.');
            } else {
                setError(err.message || 'Payment failed. Please try again.');
            }
        } finally {
            setIsPaying(false);
        }
    };

    const handleApproveRequest = async (req: PaymentRequest) => {
        setApprovingId(req.id);
        setError('');
        try {
            const { tx } = await payDoctor(req.doctor_wallet, req.amount);
            await updatePaymentRequest(req.id, { status: 'paid', tx_hash: tx.hash });
            await loadPaymentRequests();
            await loadPayments();
        } catch (err: any) {
            if (err.message?.includes('user rejected')) {
                setError('Transaction rejected in MetaMask.');
            } else {
                setError(err.message || 'Payment failed.');
            }
        } finally {
            setApprovingId(null);
        }
    };

    const handleDeclineRequest = async (req: PaymentRequest) => {
        try {
            await updatePaymentRequest(req.id, { status: 'declined' });
            await loadPaymentRequests();
        } catch (err: any) {
            console.error('Failed to decline:', err);
        }
    };

    const filteredDoctors = doctors.filter(d =>
        d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.specialty.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const pendingRequests = paymentRequests.filter(r => r.status === 'pending');

    const totalAmount = payments.reduce((sum, p) => {
        try { return sum + Number(formatEther(p.amount)); } catch { return sum; }
    }, 0);

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Stats Row */}
            <div className="grid grid-cols-2 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-5 border border-blue-100">
                    <p className="text-[10px] font-bold text-blue-500 uppercase tracking-widest mb-1">
                        {viewType === 'patient' ? 'Total Paid' : 'Total Earned'}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 tracking-tight">
                        {totalAmount.toFixed(4)} <span className="text-sm font-medium text-gray-400">ETH</span>
                    </p>
                </div>
                <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-2xl p-5 border border-green-100">
                    <p className="text-[10px] font-bold text-green-600 uppercase tracking-widest mb-1">Transactions</p>
                    <p className="text-2xl font-bold text-gray-900 tracking-tight">{payments.length}</p>
                </div>
            </div>

            {/* Payment Form — only for patients */}
            {viewType === 'patient' && (
                <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-5">
                        <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                        </div>
                        <div>
                            <h3 className="text-base font-semibold text-gray-900">Pay a Doctor</h3>
                            <p className="text-xs text-gray-500">Select a doctor by name — no wallet address needed</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        {/* Doctor Selector */}
                        <div className="relative">
                            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-1.5 block">
                                Select Doctor
                            </label>
                            {selectedDoctor ? (
                                <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-xl px-4 py-3">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold">
                                            {selectedDoctor.name.charAt(0).toUpperCase()}
                                        </div>
                                        <div>
                                            <p className="text-sm font-semibold text-gray-900">{selectedDoctor.name}</p>
                                            <p className="text-[11px] text-gray-500">{selectedDoctor.specialty}</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => { setSelectedDoctor(null); setSearchQuery(''); }}
                                        className="text-gray-400 hover:text-red-500 transition-colors p-1"
                                    >
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                                    </button>
                                </div>
                            ) : (
                                <div>
                                    <input
                                        type="text"
                                        value={searchQuery}
                                        onChange={e => { setSearchQuery(e.target.value); setShowDropdown(true); }}
                                        onFocus={() => setShowDropdown(true)}
                                        placeholder="Search by doctor name or specialty..."
                                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                                    />
                                    {showDropdown && (
                                        <div className="absolute z-50 top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-xl max-h-60 overflow-y-auto">
                                            {filteredDoctors.length === 0 ? (
                                                <div className="px-4 py-6 text-center text-sm text-gray-400">
                                                    No doctors found
                                                </div>
                                            ) : (
                                                filteredDoctors.map(doc => (
                                                    <button
                                                        key={doc.id}
                                                        onClick={() => {
                                                            setSelectedDoctor(doc);
                                                            setSearchQuery('');
                                                            setShowDropdown(false);
                                                        }}
                                                        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-blue-50 transition-colors text-left border-b border-gray-50 last:border-0"
                                                    >
                                                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 text-blue-600 flex items-center justify-center text-sm font-bold shrink-0">
                                                            {doc.name.charAt(0).toUpperCase()}
                                                        </div>
                                                        <div className="flex-1 min-w-0">
                                                            <p className="text-sm font-semibold text-gray-900 truncate">{doc.name}</p>
                                                            <p className="text-[11px] text-gray-500">{doc.specialty}</p>
                                                        </div>
                                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-300 shrink-0"><polyline points="9 18 15 12 9 6"></polyline></svg>
                                                    </button>
                                                ))
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        <div>
                            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-1.5 block">
                                Amount (ETH)
                            </label>
                            <input
                                type="number"
                                step="0.001"
                                min="0"
                                value={amount}
                                onChange={e => setAmount(e.target.value)}
                                placeholder="0.01"
                                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                            />
                        </div>

                        <button
                            onClick={handlePay}
                            disabled={isPaying || !selectedDoctor || !amount}
                            className="w-full bg-blue-600 text-white rounded-xl px-6 py-3.5 font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm flex items-center justify-center gap-2"
                        >
                            {isPaying ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                    Confirm in MetaMask...
                                </>
                            ) : (
                                <>
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                                    Send Payment
                                </>
                            )}
                        </button>
                    </div>

                    {/* Success */}
                    {txResult?.success && (
                        <div className="mt-4 px-4 py-3 rounded-xl bg-green-50 border border-green-200 text-sm text-green-700">
                            <p className="font-semibold mb-1">✅ Payment sent successfully!</p>
                            <p className="text-xs font-mono break-all text-green-600">Tx: {txResult.hash}</p>
                        </div>
                    )}

                    {/* Error */}
                    {error && (
                        <div className="mt-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-600">
                            {error}
                        </div>
                    )}
                </div>
            )}

            {/* ──── Payment Requests Section (Patient only) ──── */}
            {viewType === 'patient' && pendingRequests.length > 0 && (
                <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                    <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-100 px-6 py-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"></path></svg>
                            </div>
                            <h3 className="font-semibold text-gray-900 text-sm tracking-wide">Payment Requests</h3>
                        </div>
                        <span className="bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full text-xs font-bold">
                            {pendingRequests.length} pending
                        </span>
                    </div>

                    <div className="divide-y divide-gray-100">
                        {pendingRequests.map(req => (
                            <div key={req.id} className="px-6 py-5">
                                <div className="flex items-start justify-between gap-4 mb-3">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-100 to-indigo-100 text-purple-600 flex items-center justify-center text-sm font-bold shrink-0">
                                            {(req.doctor_name || 'D').charAt(0).toUpperCase()}
                                        </div>
                                        <div>
                                            <p className="text-sm font-semibold text-gray-900">{req.doctor_name || 'Doctor'}</p>
                                            <p className="text-[11px] text-gray-500">{req.reason}</p>
                                        </div>
                                    </div>
                                    <div className="text-right shrink-0">
                                        <p className="text-lg font-bold text-gray-900">{req.amount} <span className="text-xs text-gray-400">ETH</span></p>
                                        <p className="text-[10px] text-gray-400">{new Date(req.created_at).toLocaleDateString()}</p>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => handleApproveRequest(req)}
                                        disabled={approvingId === req.id}
                                        className="flex-1 px-4 py-2.5 rounded-xl bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                                    >
                                        {approvingId === req.id ? (
                                            <>
                                                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                                Paying...
                                            </>
                                        ) : (
                                            <>✓ Approve & Pay</>
                                        )}
                                    </button>
                                    <button
                                        onClick={() => handleDeclineRequest(req)}
                                        className="px-4 py-2.5 rounded-xl bg-gray-50 border border-gray-200 text-gray-600 text-sm font-semibold hover:bg-red-50 hover:border-red-200 hover:text-red-600 transition-all"
                                    >
                                        Decline
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Transaction History */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="bg-gray-50/50 border-b border-gray-100 px-6 py-4 flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900 text-sm tracking-wide">
                        {viewType === 'patient' ? 'Payment History' : 'Earnings History'}
                    </h3>
                    <div className="text-xs font-medium text-gray-500 bg-white border border-gray-200 px-2 py-0.5 rounded-full">
                        {payments.length} txns
                    </div>
                </div>

                <div className="divide-y divide-gray-100">
                    {isLoadingHistory ? (
                        <div className="py-12 flex flex-col items-center justify-center">
                            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
                            <p className="text-sm text-gray-500">Loading transactions from blockchain...</p>
                        </div>
                    ) : payments.length === 0 ? (
                        <div className="py-12 flex flex-col items-center justify-center">
                            <div className="w-14 h-14 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center mb-3">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-gray-300"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                            </div>
                            <p className="text-sm font-medium text-gray-500">No transactions yet</p>
                            <p className="text-xs text-gray-400 mt-1">
                                {viewType === 'patient' ? 'Payments to doctors will appear here' : 'Payments from patients will appear here'}
                            </p>
                        </div>
                    ) : (
                        payments.map((p, i) => (
                            <div key={i} className="px-6 py-4 flex items-center gap-4 hover:bg-gray-50 transition-colors">
                                {/* Icon */}
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${viewType === 'patient'
                                        ? 'bg-red-50 text-red-500 border border-red-100'
                                        : 'bg-green-50 text-green-500 border border-green-100'
                                    }`}>
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        {viewType === 'patient'
                                            ? <><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></>
                                            : <><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></>
                                        }
                                    </svg>
                                </div>

                                {/* Details */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-0.5">
                                        <p className="text-sm font-semibold text-gray-900">
                                            {viewType === 'patient' ? 'Paid to' : 'Received from'}
                                        </p>
                                        <span className="text-xs font-mono text-gray-500 bg-gray-50 px-1.5 py-0.5 rounded border border-gray-200 truncate max-w-[180px]">
                                            {viewType === 'patient'
                                                ? `${p.doctor.slice(0, 6)}...${p.doctor.slice(-4)}`
                                                : `${p.patient.slice(0, 6)}...${p.patient.slice(-4)}`
                                            }
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2 text-[11px] text-gray-400">
                                        <span>{new Date(p.timestamp * 1000).toLocaleString()}</span>
                                        <span className="w-1 h-1 bg-gray-300 rounded-full"></span>
                                        <span className="font-mono truncate max-w-[120px]">{p.txHash.slice(0, 10)}...</span>
                                    </div>
                                </div>

                                {/* Amount */}
                                <div className="text-right shrink-0">
                                    <p className={`text-base font-bold tracking-tight ${viewType === 'patient' ? 'text-red-600' : 'text-green-600'}`}>
                                        {viewType === 'patient' ? '-' : '+'}{Number(formatEther(p.amount)).toFixed(4)}
                                    </p>
                                    <p className="text-[10px] text-gray-400 font-medium">ETH</p>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
