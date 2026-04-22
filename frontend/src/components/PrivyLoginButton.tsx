'use client';

import { usePrivyAuth } from '@/hooks/usePrivyAuth';
import { useState } from 'react';

export function PrivyLoginButton() {
  const { ready, authenticated, user, login, logout, walletAddress, exportWallet } = usePrivyAuth();
  const [showExportModal, setShowExportModal] = useState(false);

  if (!ready) {
    return (
      <button
        disabled
        className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed"
      >
        Loading...
      </button>
    );
  }

  if (!authenticated) {
    return (
      <button
        onClick={login}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md hover:shadow-lg"
      >
        Sign In with Privy
      </button>
    );
  }

  return (
    <div className="flex items-center gap-4">
      {/* User Info */}
      <div className="flex flex-col items-end">
        <span className="text-sm text-gray-600">
          {user?.email || 'Authenticated'}
        </span>
        {walletAddress && (
          <span className="text-xs text-gray-500 font-mono">
            {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
          </span>
        )}
      </div>

      {/* Export Wallet Button */}
      {walletAddress && (
        <button
          onClick={() => setShowExportModal(true)}
          className="px-3 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
          title="Export wallet for self-custody"
        >
          🔑 Export Wallet
        </button>
      )}

      {/* Logout Button */}
      <button
        onClick={logout}
        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
      >
        Sign Out
      </button>

      {/* Export Wallet Modal */}
      {showExportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Export Your Wallet</h3>
            <p className="text-gray-600 mb-4">
              Export your wallet's private key to take full self-custody. You can import this into MetaMask or any other wallet.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-yellow-800">
                ⚠️ <strong>Warning:</strong> Never share your private key with anyone. Store it securely.
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  exportWallet();
                  setShowExportModal(false);
                }}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Export Now
              </button>
              <button
                onClick={() => setShowExportModal(false)}
                className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
