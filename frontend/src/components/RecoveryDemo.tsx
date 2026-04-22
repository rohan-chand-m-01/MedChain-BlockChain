/**
 * Recovery Demo Component
 * 
 * Demonstrates how Privy's social recovery works.
 * Shows users they can recover access from any device.
 */

'use client';

import { useState } from 'react';
import { usePrivy, useWallets } from '@privy-io/react-auth';

export function RecoveryDemo() {
  const { login, logout, authenticated, user } = usePrivy();
  const { wallets } = useWallets();
  const [showDemo, setShowDemo] = useState(false);

  const embeddedWallet = wallets.find((w) => w.walletClientType === 'privy');

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>

        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            🔐 Social Recovery Enabled
          </h3>
          <p className="text-sm text-gray-700 mb-4">
            Your encryption keys are automatically recoverable. No passwords to remember!
          </p>

          {authenticated && embeddedWallet ? (
            <div className="space-y-3">
              <div className="p-3 bg-white rounded border border-green-200">
                <p className="text-xs text-gray-600 mb-1">Your Wallet Address:</p>
                <p className="text-sm font-mono text-green-700">
                  {embeddedWallet.address}
                </p>
              </div>

              <div className="p-3 bg-white rounded border border-blue-200">
                <p className="text-xs text-gray-600 mb-1">Logged in with:</p>
                <p className="text-sm font-semibold text-blue-700">
                  {user?.email?.address || user?.google?.email || user?.wallet?.address || 'Wallet'}
                </p>
              </div>

              <button
                onClick={() => setShowDemo(!showDemo)}
                className="text-sm text-blue-600 hover:text-blue-700 underline"
              >
                {showDemo ? 'Hide' : 'Show'} Recovery Instructions
              </button>

              {showDemo && (
                <div className="mt-4 p-4 bg-white rounded border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-3">
                    How to Recover Access on a New Device:
                  </h4>
                  <ol className="space-y-2 text-sm text-gray-700">
                    <li className="flex gap-2">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">1</span>
                      <span>Open MediChain on your new device</span>
                    </li>
                    <li className="flex gap-2">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">2</span>
                      <span>Click "Login" and choose the same method you used before</span>
                    </li>
                    <li className="flex gap-2">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">3</span>
                      <span>Login with: <strong>{user?.email?.address || user?.google?.email || 'your account'}</strong></span>
                    </li>
                    <li className="flex gap-2">
                      <span className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-xs font-bold">✓</span>
                      <span>Privy automatically recovers your wallet and encryption keys!</span>
                    </li>
                  </ol>

                  <div className="mt-4 p-3 bg-yellow-50 rounded border border-yellow-200">
                    <p className="text-xs text-yellow-800">
                      <strong>Important:</strong> You must use the same login method (email/Google/etc.) 
                      to recover your wallet. Different login methods create different wallets.
                    </p>
                  </div>

                  <div className="mt-4">
                    <button
                      onClick={() => {
                        if (confirm('This will log you out to simulate recovery. Ready to test?')) {
                          logout();
                        }
                      }}
                      className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
                    >
                      Test Recovery (Logout & Login Again)
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-sm text-gray-600">
                Login to see your recovery options
              </p>
              <button
                onClick={login}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                Login with Privy
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Recovery Methods Info */}
      <div className="mt-6 pt-6 border-t border-blue-200">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">
          Available Recovery Methods:
        </h4>
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-white rounded border border-gray-200">
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
              <span className="text-sm font-medium text-gray-900">Email</span>
            </div>
            <p className="text-xs text-gray-600">Login with same email</p>
          </div>

          <div className="p-3 bg-white rounded border border-gray-200">
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-medium text-gray-900">Google</span>
            </div>
            <p className="text-xs text-gray-600">Login with Google account</p>
          </div>

          <div className="p-3 bg-white rounded border border-gray-200">
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <span className="text-sm font-medium text-gray-900">Passkey</span>
            </div>
            <p className="text-xs text-gray-600">Face ID / Touch ID / Windows Hello</p>
          </div>

          <div className="p-3 bg-white rounded border border-gray-200">
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
              <span className="text-sm font-medium text-gray-900">Wallet</span>
            </div>
            <p className="text-xs text-gray-600">MetaMask / WalletConnect</p>
          </div>
        </div>
      </div>
    </div>
  );
}
