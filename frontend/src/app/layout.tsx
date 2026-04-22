import type { Metadata } from 'next';
import './globals.css';
import { LanguageProvider } from '@/contexts/LanguageContext';
import { WalletProvider } from '@/hooks/useWallet';
import { AuthProvider } from '@/contexts/AuthContext';
import { PrivyProvider } from '@/contexts/PrivyProvider';

export const metadata: Metadata = {
  title: 'MediChain AI — Clinical Intelligence Platform',
  description: 'AI-powered blockchain-secured medical record platform with intelligent analysis, chatbot, and AI doctor avatar.',
  keywords: ['medical records', 'blockchain', 'AI analysis', 'healthcare', 'decentralized', 'Web3'],
  openGraph: {
    title: 'MediChain AI — Clinical Intelligence Platform',
    description: 'Upload medical reports, get AI analysis, and secure records on blockchain.',
    type: 'website',
  },
  robots: 'index, follow',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="light">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700&family=Inter:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[#f7f9fb] text-[#191c1e]">
        <PrivyProvider>
          <LanguageProvider>
            <WalletProvider>
              <AuthProvider>
                {children}
              </AuthProvider>
            </WalletProvider>
          </LanguageProvider>
        </PrivyProvider>
      </body>
    </html>
  );
}
