'use client';

import { usePrivy, useWallets } from '@privy-io/react-auth';
import { useEffect, useState } from 'react';

export interface PrivyUser {
  id: string;
  email?: string;
  wallet?: {
    address: string;
    chainId: string;
  };
  createdAt: Date;
}

export function usePrivyAuth() {
  const {
    ready,
    authenticated,
    user,
    login,
    logout,
    linkEmail,
    linkWallet,
    unlinkEmail,
    unlinkWallet,
    exportWallet,
    getAccessToken,
  } = usePrivy();

  const { wallets } = useWallets();
  const [embeddedWallet, setEmbeddedWallet] = useState<any>(null);

  // Get the embedded (MPC) wallet
  useEffect(() => {
    if (wallets && wallets.length > 0) {
      // Find the embedded wallet (created by Privy)
      const embedded = wallets.find((w) => w.walletClientType === 'privy');
      setEmbeddedWallet(embedded);
    }
  }, [wallets]);

  // Format user data
  const privyUser: PrivyUser | null = user
    ? {
        id: user.id,
        email: user.email?.address,
        wallet: embeddedWallet
          ? {
              address: embeddedWallet.address,
              chainId: embeddedWallet.chainId,
            }
          : undefined,
        createdAt: user.createdAt,
      }
    : null;

  return {
    // Status
    ready,
    authenticated,
    user: privyUser,
    
    // Wallet info
    walletAddress: embeddedWallet?.address,
    walletChainId: embeddedWallet?.chainId,
    
    // Authentication methods
    login,
    logout,
    getAccessToken, // Get JWT token for backend verification
    
    // Account management
    linkEmail,
    linkWallet,
    unlinkEmail,
    unlinkWallet,
    
    // Export wallet (for self-custody)
    exportWallet,
    
    // Raw Privy objects (for advanced use)
    rawUser: user,
    rawWallets: wallets,
    embeddedWallet,
  };
}
