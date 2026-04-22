'use client';

import { Wallet, Mail } from 'lucide-react';

interface AuthMethodIndicatorProps {
  authMethod: 'privy' | 'metamask' | null;
  userId: string | null;
  className?: string;
}

export default function AuthMethodIndicator({ 
  authMethod, 
  userId, 
  className = '' 
}: AuthMethodIndicatorProps) {
  if (!authMethod || !userId) {
    return null;
  }

  const isMetaMask = authMethod === 'metamask';
  
  // Truncate wallet address for display (0x1234...5678)
  const displayId = isMetaMask && userId.startsWith('0x')
    ? `${userId.slice(0, 6)}...${userId.slice(-4)}`
    : userId.slice(0, 20) + (userId.length > 20 ? '...' : '');

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div
        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${
          isMetaMask
            ? 'bg-orange-50 border-orange-200 text-orange-700'
            : 'bg-blue-50 border-blue-200 text-blue-700'
        }`}
      >
        {isMetaMask ? (
          <Wallet className="w-4 h-4" />
        ) : (
          <Mail className="w-4 h-4" />
        )}
        <span className="text-xs font-semibold">
          {isMetaMask ? 'MetaMask' : 'Privy'}
        </span>
      </div>
      
      <div className="flex items-center gap-1.5 px-2.5 py-1 bg-gray-50 border border-gray-200 rounded-lg">
        <span className="text-xs font-mono text-gray-600">
          {displayId}
        </span>
      </div>
    </div>
  );
}
