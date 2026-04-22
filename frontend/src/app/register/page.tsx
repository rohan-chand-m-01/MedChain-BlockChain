'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { usePrivy } from '@privy-io/react-auth';
import Navbar from '@/components/Navbar';

export default function RegisterPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { authenticated, user, login } = usePrivy();

    // Read role from URL (?role=patient or ?role=doctor)
    const urlRole = searchParams.get('role');
    const [selectedRole, setSelectedRole] = useState<'patient' | 'doctor' | null>(
        urlRole === 'patient' ? 'patient' : urlRole === 'doctor' ? 'doctor' : null
    );
    const [isRegistering, setIsRegistering] = useState(false);

    // If authenticated and role selected, proceed to dashboard
    useEffect(() => {
        if (authenticated && selectedRole) {
            console.log('[Registration] User authenticated with role:', selectedRole);
            // Store role in localStorage for now (you can use a backend API later)
            localStorage.setItem('userRole', selectedRole);
            localStorage.setItem('userId', user?.id || '');
            
            // Redirect to appropriate dashboard
            router.push(selectedRole === 'patient' ? '/patient' : '/doctor');
        }
    }, [authenticated, selectedRole, router, user]);

    const handleContinue = () => {
        if (!selectedRole) return;
        
        if (!authenticated) {
            // Trigger Privy login
            console.log('[Register] Triggering Privy login...');
            try {
                login();
            } catch (error) {
                console.error('[Register] Login error:', error);
            }
        } else {
            // Already authenticated, just redirect
            console.log('[Register] Already authenticated, redirecting...');
            localStorage.setItem('userRole', selectedRole);
            router.push(selectedRole === 'patient' ? '/patient' : '/doctor');
        }
    };

    return (
        <>
            <Navbar />
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 relative overflow-hidden">
                {/* Animated Background Elements */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute top-20 left-10 w-72 h-72 bg-blue-200/30 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute bottom-20 right-10 w-96 h-96 bg-indigo-200/30 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
                </div>

                <div className="relative z-10 min-h-screen flex items-center justify-center px-6 py-20">
                    <div className="w-full max-w-5xl">
                        <div className="grid lg:grid-cols-2 gap-12 items-center">
                            
                            {/* Left Side - Branding */}
                            <div className="hidden lg:block space-y-8">
                                <h1 className="text-5xl font-bold text-gray-900 leading-tight">
                                    Welcome to the Future of
                                    <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                                        Healthcare
                                    </span>
                                </h1>
                                
                                <p className="text-lg text-gray-600">
                                    Join thousands of healthcare professionals and patients using AI-powered medical analysis.
                                </p>

                                <div className="space-y-4">
                                    {[
                                        { icon: '🤖', title: 'AI-Powered Analysis', desc: 'Advanced medical report interpretation' },
                                        { icon: '🔒', title: 'Secure & Private', desc: 'HIPAA-compliant data protection' },
                                        { icon: '⚡', title: 'Instant Results', desc: 'Get insights in seconds, not days' },
                                    ].map((feature, i) => (
                                        <div key={i} className="flex items-start gap-4 bg-white/60 backdrop-blur-sm p-4 rounded-2xl border border-white/60">
                                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center text-2xl">
                                                {feature.icon}
                                            </div>
                                            <div>
                                                <h3 className="font-semibold text-gray-900">{feature.title}</h3>
                                                <p className="text-sm text-gray-600">{feature.desc}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Right Side - Registration */}
                            <div className="w-full">
                                <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/60 p-8 lg:p-10">
                                    
                                    <div className="text-center mb-8">
                                        <h2 className="text-3xl font-bold text-gray-900 mb-2">
                                            {selectedRole ? `Join as ${selectedRole === 'patient' ? 'Patient' : 'Doctor'}` : 'Complete Your Profile'}
                                        </h2>
                                        <p className="text-sm text-gray-600">
                                            {authenticated ? 'Select your role to continue' : 'Choose your role and sign in'}
                                        </p>
                                    </div>

                                    {/* Authenticated User Info */}
                                    {authenticated && user && (
                                        <div className="mb-6 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl p-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                                                    <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                                                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                                    </svg>
                                                </div>
                                                <div className="flex-1">
                                                    <p className="text-sm font-semibold text-green-900">Signed In Successfully</p>
                                                    <p className="text-xs text-green-700">{user.email?.address || user.wallet?.address}</p>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Role Selection */}
                                    {!selectedRole ? (
                                        <div className="space-y-6">
                                            <p className="text-center text-sm font-medium text-gray-500 mb-4">I am a...</p>
                                            
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                                <button
                                                    onClick={() => setSelectedRole('patient')}
                                                    className="group bg-gradient-to-br from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 p-6 rounded-2xl border-2 border-blue-200 hover:border-blue-400 transition-all text-left"
                                                >
                                                    <div className="w-14 h-14 rounded-xl bg-white shadow-lg flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform">
                                                        🏥
                                                    </div>
                                                    <h3 className="text-xl font-bold text-gray-900 mb-2">Patient</h3>
                                                    <p className="text-sm text-gray-600">Upload medical reports and get AI analysis</p>
                                                </button>

                                                <button
                                                    onClick={() => setSelectedRole('doctor')}
                                                    className="group bg-gradient-to-br from-cyan-50 to-teal-50 hover:from-cyan-100 hover:to-teal-100 p-6 rounded-2xl border-2 border-cyan-200 hover:border-cyan-400 transition-all text-left"
                                                >
                                                    <div className="w-14 h-14 rounded-xl bg-white shadow-lg flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform">
                                                        🩺
                                                    </div>
                                                    <h3 className="text-xl font-bold text-gray-900 mb-2">Doctor</h3>
                                                    <p className="text-sm text-gray-600">Review patient records and provide care</p>
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="space-y-6">
                                            {/* Role Confirmation */}
                                            <div className={`${selectedRole === 'patient' ? 'bg-blue-50 border-blue-200' : 'bg-cyan-50 border-cyan-200'} border-2 rounded-2xl p-6`}>
                                                <div className="flex items-start gap-4">
                                                    <div className="w-12 h-12 rounded-xl bg-white shadow-md flex items-center justify-center text-2xl">
                                                        {selectedRole === 'patient' ? '🏥' : '🩺'}
                                                    </div>
                                                    <div className="flex-1">
                                                        <div className="flex items-center justify-between mb-2">
                                                            <h3 className="text-lg font-bold text-gray-900">
                                                                {selectedRole === 'patient' ? 'Patient Account' : 'Doctor Account'}
                                                            </h3>
                                                            <button 
                                                                onClick={() => setSelectedRole(null)} 
                                                                className="text-xs font-medium text-gray-500 hover:text-gray-700 underline"
                                                            >
                                                                Change
                                                            </button>
                                                        </div>
                                                        <p className="text-sm text-gray-700">
                                                            {selectedRole === 'patient'
                                                                ? 'Upload medical reports, get AI analysis, and manage your health data.'
                                                                : 'Review patient records and provide expert medical care.'}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Continue Button */}
                                            <button
                                                onClick={handleContinue}
                                                disabled={isRegistering}
                                                className={`w-full py-4 rounded-xl font-semibold text-white text-base shadow-lg transition-all ${
                                                    selectedRole === 'patient'
                                                        ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
                                                        : 'bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700'
                                                } hover:-translate-y-0.5`}
                                            >
                                                <span className="flex items-center justify-center gap-2">
                                                    {authenticated ? 'Continue' : 'Sign In with Privy'} 🔐
                                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                                                        <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                                    </svg>
                                                </span>
                                            </button>
                                        </div>
                                    )}

                                    <Link href="/" className="block text-center text-sm text-gray-500 hover:text-gray-700 transition-colors mt-6">
                                        <span className="inline-flex items-center gap-2">
                                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                                            </svg>
                                            Back to Home
                                        </span>
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
