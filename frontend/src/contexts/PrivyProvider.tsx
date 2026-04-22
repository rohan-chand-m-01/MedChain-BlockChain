'use client';

import { PrivyProvider as PrivyProviderBase } from '@privy-io/react-auth';
import { sepolia, mainnet, polygon, arbitrum } from 'viem/chains';

export function PrivyProvider({ children }: { children: React.ReactNode }) {
  const privyAppId = process.env.NEXT_PUBLIC_PRIVY_APP_ID;

  if (!privyAppId) {
    console.warn('NEXT_PUBLIC_PRIVY_APP_ID not configured - Privy authentication disabled');
    return <>{children}</>;
  }

  return (
    <PrivyProviderBase
      appId={privyAppId}
      config={{
        // Appearance customization
        appearance: {
          theme: 'light',
          accentColor: '#1a56db',
          logo: 'https://medichain.app/logo.png',
        },
        // Login methods (passkey = Face ID / Touch ID / Windows Hello)
        loginMethods: ['email', 'google', 'wallet', 'passkey'],
        // Embedded wallet configuration (MPC)
        embeddedWallets: {
          createOnLogin: 'users-without-wallets', // Auto-create MPC wallet
          requireUserPasswordOnCreate: false, // Seamless UX
        },
        // Default chain
        defaultChain: sepolia,
        // Supported chains
        supportedChains: [sepolia, mainnet],
        // Legal links
        legal: {
          termsAndConditionsUrl: 'https://medichain.app/terms',
          privacyPolicyUrl: 'https://medichain.app/privacy',
        },
      }}
    >
      {children}
    </PrivyProviderBase>
  );
}
