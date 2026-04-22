'use client';

import { useState } from 'react';
import { useUser, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';

export default function ChangeRolePage() {
    const { user } = useUser();
    const { isSignedIn } = useAuth();
    const router = useRouter();
    const [isChanging, setIsChanging] = useState(false);
    const [message, setMessage] = useState('');

    const currentRole = user?.unsafeMetadata?.role as string | undefined;

    const changeRole = async (newRole: 'patient' | 'doctor') => {
        if (!user) return;
        
        setIsChanging(true);
        setMessage('');
        
        try {
            await user.update({
                unsafeMetadata: {
                    role: newRole,
                    walletAddress: user.id
                }
            });
            
            await user.reload();
            
            setMessage(`✅ Role changed to ${newRole}! Redirecting...`);
            
            setTimeout(() => {
                router.push(newRole === 'patient' ? '/patient' : '/doctor');
            }, 1500);
        } catch (err) {
            console.error('Failed to change role:', err);
            setMessage('❌ Failed to change role. Please try again.');
        } finally {
            setIsChanging(false);
        }
    };

    const clearRole = async () => {
        if (!user) return;
        
        setIsChanging(true);
        setMessage('');
        
        try {
            await user.update({
                unsafeMetadata: {
                    role: undefined,
                    walletAddress: user.id
                }
            });
            
            await user.reload();
            
            setMessage('✅ Role cleared! Redirecting to registration...');
            
            setTimeout(() => {
                router.push('/register');
            }, 1500);
        } catch (err) {
            console.error('Failed to clear role:', err);
            setMessage('❌ Failed to clear role. Please try again.');
        } finally {
            setIsChanging(false);
        }
    };

    if (!isSignedIn) {
        return (
            <>
                <Navbar />
                <div className="min-h-screen pt-32 flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
                    <div className="text-center">
                        <h1 className="text-2xl font-bold text-gray-900 mb-4">Please sign in first</h1>
                        <p className="text-gray-600">You need to be signed in to change your role.</p>
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
            <Navbar />
            <div className="min-h-screen pt-32 pb-12 px-6 bg-gradient-to-br from-slate-50 to-blue-50">
                <div className="max-w-2xl mx-auto">
                    <div className="bg-white rounded-3xl shadow-xl border border-gray-200 p-8">
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">Change Your Role</h1>
                        <p className="text-gray-600 mb-8">Switch between patient and doctor accounts</p>

                        {/* Current Role */}
                        <div className="mb-8 p-4 bg-blue-50 border-2 border-blue-200 rounded-xl">
                            <p className="text-sm font-semibold text-blue-900 mb-1">Current Role</p>
                            <p className="text-2xl font-bold text-blue-700 capitalize">
                                {currentRole || 'No role set'}
                            </p>
                        </div>

                        {/* User Info */}
                        <div className="mb-8 p-4 bg-gray-50 rounded-xl">
                            <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Account Info</p>
                            <p className="text-sm font-medium text-gray-900">{user?.primaryEmailAddress?.emailAddress}</p>
                            <p className="text-xs text-gray-500 font-mono mt-1">ID: {user?.id}</p>
                        </div>

                        {/* Action Buttons */}
                        <div className="space-y-4">
                            <button
                                onClick={() => changeRole('patient')}
                                disabled={isChanging || currentRole === 'patient'}
                                className="w-full py-4 px-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:cursor-not-allowed flex items-center justify-center gap-3"
                            >
                                <span className="text-2xl">🏥</span>
                                <span>Switch to Patient</span>
                            </button>

                            <button
                                onClick={() => changeRole('doctor')}
                                disabled={isChanging || currentRole === 'doctor'}
                                className="w-full py-4 px-6 bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:cursor-not-allowed flex items-center justify-center gap-3"
                            >
                                <span className="text-2xl">🩺</span>
                                <span>Switch to Doctor</span>
                            </button>

                            <button
                                onClick={clearRole}
                                disabled={isChanging}
                                className="w-full py-3 px-6 bg-white hover:bg-gray-50 border-2 border-gray-300 hover:border-gray-400 text-gray-700 font-semibold rounded-xl transition-all disabled:cursor-not-allowed"
                            >
                                Clear Role (Go to Registration)
                            </button>
                        </div>

                        {/* Status Message */}
                        {message && (
                            <div className={`mt-6 p-4 rounded-xl text-center font-semibold ${
                                message.includes('✅') 
                                    ? 'bg-green-50 text-green-700 border-2 border-green-200' 
                                    : 'bg-red-50 text-red-700 border-2 border-red-200'
                            }`}>
                                {message}
                            </div>
                        )}

                        {isChanging && (
                            <div className="mt-6 flex items-center justify-center gap-3">
                                <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                                <span className="text-sm text-gray-600">Updating your role...</span>
                            </div>
                        )}
                    </div>

                    {/* Info Box */}
                    <div className="mt-8 p-6 bg-yellow-50 border-2 border-yellow-200 rounded-2xl">
                        <div className="flex items-start gap-3">
                            <span className="text-2xl">💡</span>
                            <div>
                                <h3 className="font-bold text-yellow-900 mb-2">Testing Tip</h3>
                                <p className="text-sm text-yellow-800 leading-relaxed">
                                    Use this page to switch between patient and doctor roles for testing. 
                                    In production, users would only register once and keep their role.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
