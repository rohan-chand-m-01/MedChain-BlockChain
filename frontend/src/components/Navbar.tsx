'use client';

import Link from 'next/link';
import { usePrivy } from '@privy-io/react-auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import LanguageSelector from '@/components/LanguageSelector';
import { useLanguage } from '@/contexts/LanguageContext';

export default function Navbar() {
    const { authenticated, user, login, logout } = usePrivy();
    const router = useRouter();
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [userName, setUserName] = useState<string | null>(null);
    const { t } = useLanguage();

    // Get user role from localStorage
    const userRole = typeof window !== 'undefined' ? localStorage.getItem('userRole') : null;

    // Fetch user profile name
    useEffect(() => {
        const fetchUserName = async () => {
            if (!authenticated || !user) return;
            
            const walletAddress = user?.wallet?.address || user?.id;
            if (!walletAddress) return;

            try {
                const endpoint = userRole === 'patient' 
                    ? `/api/profiles/patient/${walletAddress}`
                    : `/api/profiles/doctor/${walletAddress}`;
                
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`);
                if (response.ok) {
                    const data = await response.json();
                    if (data.exists) {
                        setUserName(data.full_name || data.name);
                    }
                }
            } catch (error) {
                console.error('Failed to fetch user name:', error);
            }
        };

        fetchUserName();
    }, [authenticated, user, userRole]);

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-0 border-b border-[rgba(99,102,241,0.1)]" style={{ borderRadius: 0 }}>
            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
                        </svg>
                    </div>
                    <span className="text-xl font-bold gradient-text">MediChain AI</span>
                </Link>

                <div className="flex items-center gap-5">
                    {authenticated ? (
                        <>
                            {/* Dashboard Links */}
                            {userRole === 'patient' && (
                                <Link href="/patient" className="text-sm text-gray-400 hover:text-white transition-colors">
                                    Dashboard
                                </Link>
                            )}
                            {userRole === 'doctor' && (
                                <Link href="/doctor" className="text-sm text-gray-400 hover:text-white transition-colors">
                                    Dashboard
                                </Link>
                            )}

                            <div className="flex items-center gap-3">
                                <LanguageSelector />
                                
                                {/* User Menu */}
                                <div className="relative">
                                    <button
                                        onClick={() => setShowUserMenu(!showUserMenu)}
                                        className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold text-sm hover:shadow-lg transition-all"
                                    >
                                        {userName?.charAt(0).toUpperCase() || user?.email?.address?.charAt(0).toUpperCase() || user?.wallet?.address?.slice(0, 2) || 'U'}
                                    </button>

                                    {showUserMenu && (
                                        <>
                                            <div className="fixed inset-0 z-40" onClick={() => setShowUserMenu(false)} />
                                            <div className="absolute top-full right-0 mt-2 w-64 bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden z-50">
                                                <div className="p-4 border-b border-gray-100">
                                                    <p className="text-base font-bold text-gray-900 mb-1">
                                                        {userName || user?.email?.address || 'User'}
                                                    </p>
                                                    {userRole && (
                                                        <p className="text-xs text-gray-500 capitalize">
                                                            {userRole === 'patient' ? '🏥 Patient' : '🩺 Doctor'}
                                                        </p>
                                                    )}
                                                </div>
                                                <div className="p-2">
                                                    <Link
                                                        href="/profile"
                                                        onClick={() => setShowUserMenu(false)}
                                                        className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-all"
                                                    >
                                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                                        </svg>
                                                        My Profile
                                                    </Link>
                                                    <Link
                                                        href="/register"
                                                        onClick={() => setShowUserMenu(false)}
                                                        className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-all"
                                                    >
                                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                                                        </svg>
                                                        Change Role
                                                    </Link>
                                                    <button
                                                        onClick={() => {
                                                            logout();
                                                            setShowUserMenu(false);
                                                            localStorage.removeItem('userRole');
                                                            router.push('/');
                                                        }}
                                                        className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50 transition-all"
                                                    >
                                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                                        </svg>
                                                        Sign Out
                                                    </button>
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>
                        </>
                    ) : (
                        <>
                            <LanguageSelector />
                            <button 
                                onClick={() => login()}
                                className="text-sm text-gray-400 hover:text-white transition-colors"
                            >
                                {t('nav.signIn')}
                            </button>
                            <button 
                                onClick={() => login()}
                                className="btn-primary text-sm !px-5 !py-2.5"
                            >
                                {t('landing.getStarted')}
                            </button>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}
