'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import { useWallet } from '@/hooks/useWallet';

type AuthMethod = 'privy' | 'metamask' | null;

interface AuthContextType {
    userId: string | null;
    authMethod: AuthMethod;
    isAuthenticated: boolean;
    isLoading: boolean;
    walletAddress: string | null;
    privyUser: any;
    switchToMetaMask: () => Promise<void>;
    switchToPrivy: () => void;
}

const AuthContext = createContext<AuthContextType>({
    userId: null,
    authMethod: null,
    isAuthenticated: false,
    isLoading: true,
    walletAddress: null,
    privyUser: null,
    switchToMetaMask: async () => {},
    switchToPrivy: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
    const { user: privyUser, authenticated, ready } = usePrivy();
    const { address: walletAddress, isConnected: walletConnected, connect: connectWallet } = useWallet();
    
    const [authMethod, setAuthMethod] = useState<AuthMethod>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Determine authentication method and user ID
    useEffect(() => {
        if (!ready) {
            setIsLoading(true);
            return;
        }

        // Check localStorage for preferred auth method
        const savedAuthMethod = localStorage.getItem('authMethod') as AuthMethod;

        if (savedAuthMethod === 'metamask' && walletConnected && walletAddress) {
            // User prefers MetaMask and wallet is connected
            setAuthMethod('metamask');
            setIsLoading(false);
        } else if (authenticated && privyUser) {
            // Privy user is signed in
            setAuthMethod('privy');
            setIsLoading(false);
        } else if (walletConnected && walletAddress) {
            // Wallet is connected but no preference set
            setAuthMethod('metamask');
            localStorage.setItem('authMethod', 'metamask');
            setIsLoading(false);
        } else {
            // No authentication
            setAuthMethod(null);
            setIsLoading(false);
        }
    }, [privyUser, authenticated, ready, walletAddress, walletConnected]);

    const switchToMetaMask = async () => {
        try {
            await connectWallet();
            localStorage.setItem('authMethod', 'metamask');
            setAuthMethod('metamask');
        } catch (error) {
            console.error('Failed to switch to MetaMask:', error);
            throw error;
        }
    };

    const switchToPrivy = () => {
        localStorage.setItem('authMethod', 'privy');
        setAuthMethod('privy');
    };

    // Determine user ID based on auth method
    const userId = authMethod === 'metamask' 
        ? walletAddress 
        : authMethod === 'privy' && privyUser 
            ? privyUser.id 
            : null;

    const isAuthenticated = !!userId;

    return (
        <AuthContext.Provider
            value={{
                userId,
                authMethod,
                isAuthenticated,
                isLoading,
                walletAddress,
                privyUser,
                switchToMetaMask,
                switchToPrivy,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
