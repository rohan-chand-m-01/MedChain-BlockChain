'use client';

import { useState } from 'react';
import { useWallet } from '@/hooks/useWallet';
import { Wallet, Loader2, AlertCircle } from 'lucide-react';

interface MetaMaskButtonProps {
    onSuccess?: () => void;
    className?: string;
    variant?: 'primary' | 'secondary' | 'outline';
}

export default function MetaMaskButton({ onSuccess, className = '', variant = 'primary' }: MetaMaskButtonProps) {
    const { address, isConnecting, isConnected, connect, disconnect, error } = useWallet();
    const [showError, setShowError] = useState(false);

    const handleConnect = async () => {
        try {
            setShowError(false);
            await connect();
            if (onSuccess) {
                onSuccess();
            }
        } catch (err) {
            setShowError(true);
        }
    };

    const variantStyles = {
        primary: 'bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-lg',
        secondary: 'bg-gray-800 hover:bg-gray-900 text-white',
        outline: 'border-2 border-orange-500 text-orange-600 hover:bg-orange-50',
    };

    if (isConnected && address) {
        return (
            <div className={`flex items-center gap-3 ${className}`}>
                <div className="flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-lg">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-green-700">
                        {address.slice(0, 6)}...{address.slice(-4)}
                    </span>
                </div>
                <button
                    onClick={disconnect}
                    className="text-sm text-gray-600 hover:text-gray-900 underline"
                >
                    Disconnect
                </button>
            </div>
        );
    }

    return (
        <div className={className}>
            <button
                onClick={handleConnect}
                disabled={isConnecting}
                className={`
                    flex items-center gap-2 px-6 py-3 rounded-lg font-semibold
                    transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                    ${variantStyles[variant]}
                `}
            >
                {isConnecting ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Connecting...</span>
                    </>
                ) : (
                    <>
                        <Wallet className="w-5 h-5" />
                        <span>Connect MetaMask</span>
                    </>
                )}
            </button>

            {(showError || error) && (
                <div className="mt-3 flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                        <p className="text-sm font-medium text-red-900">Connection Failed</p>
                        <p className="text-sm text-red-700 mt-1">
                            {error || 'Please make sure MetaMask is installed and try again.'}
                        </p>
                        {!error?.includes('MetaMask is not installed') && (
                            <a
                                href="https://metamask.io/download/"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-red-600 hover:text-red-800 underline mt-2 inline-block"
                            >
                                Install MetaMask
                            </a>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
