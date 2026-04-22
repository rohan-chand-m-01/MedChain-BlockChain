'use client';

import { usePrivyAuth } from '@/hooks/usePrivyAuth';
import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function ClaimWalletPage() {
  const { ready, authenticated, user, walletAddress, login, getAccessToken } = usePrivyAuth();
  const [custodialWallet, setCustodialWallet] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  // Get custodial wallet from URL if provided
  useEffect(() => {
    const wallet = searchParams.get('wallet');
    if (wallet) {
      setCustodialWallet(wallet);
    }
  }, [searchParams]);

  const handleClaimWallet = async () => {
    if (!custodialWallet || !user?.id || !walletAddress) {
      setError('Missing required information');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Get Privy access token
      const token = await getAccessToken();
      
      if (!token) {
        throw new Error('Failed to get authentication token');
      }

      // Link Privy account to custodial wallet
      const response = await fetch('/api/privy/link-patient', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          privy_id: user.id,
          patient_wallet: custodialWallet
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to link wallet');
      }

      const data = await response.json();
      
      if (data.success) {
        setSuccess(true);
        
        // Redirect to patient dashboard after 2 seconds
        setTimeout(() => {
          router.push('/patient');
        }, 2000);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to claim wallet');
    } finally {
      setLoading(false);
    }
  };

  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🔐 Claim Your Wallet
          </h1>
          <p className="text-lg text-gray-600">
            Upgrade from WhatsApp to full Web3 sovereignty
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {!authenticated ? (
            // Step 1: Login with Privy
            <div className="text-center">
              <div className="mb-6">
                <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-4xl">👤</span>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Sign In to Claim Your Records
                </h2>
                <p className="text-gray-600">
                  Use your email or Google account to create a secure MPC wallet
                </p>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-blue-900 mb-2">What is MPC?</h3>
                <p className="text-sm text-blue-800">
                  Multi-Party Computation splits your wallet key between your device and Privy's servers. 
                  Neither party alone can access your funds. You can export to MetaMask anytime for full self-custody.
                </p>
              </div>

              <button
                onClick={login}
                className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-lg shadow-md hover:shadow-lg"
              >
                Sign In with Privy
              </button>

              <p className="text-xs text-gray-500 mt-4">
                By signing in, you agree to our Terms of Service and Privacy Policy
              </p>
            </div>
          ) : success ? (
            // Step 3: Success
            <div className="text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-4xl">✅</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Wallet Claimed Successfully!
              </h2>
              <p className="text-gray-600 mb-4">
                Your medical records are now secured with your Privy MPC wallet
              </p>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-green-800">
                  <strong>Your Wallet:</strong><br />
                  <code className="text-xs">{walletAddress}</code>
                </p>
              </div>
              <p className="text-sm text-gray-600">
                Redirecting to your dashboard...
              </p>
            </div>
          ) : (
            // Step 2: Link Custodial Wallet
            <div>
              <div className="mb-6">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-4xl">🔗</span>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">
                  Link Your WhatsApp Records
                </h2>
                <p className="text-gray-600 text-center">
                  Enter your custodial wallet address to import all your WhatsApp reports
                </p>
              </div>

              {/* User Info */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Signed in as:</span>
                  <span className="text-sm font-medium">{user?.email || 'Authenticated'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Your MPC Wallet:</span>
                  <code className="text-xs font-mono bg-white px-2 py-1 rounded">
                    {walletAddress?.slice(0, 6)}...{walletAddress?.slice(-4)}
                  </code>
                </div>
              </div>

              {/* Input Form */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Custodial Wallet Address (from WhatsApp)
                </label>
                <input
                  type="text"
                  value={custodialWallet}
                  onChange={(e) => setCustodialWallet(e.target.value)}
                  placeholder="0x..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-2">
                  This is the wallet address you received via WhatsApp when you first uploaded a report
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <p className="text-sm text-red-800">❌ {error}</p>
                </div>
              )}

              {/* Action Button */}
              <button
                onClick={handleClaimWallet}
                disabled={loading || !custodialWallet}
                className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-lg shadow-md hover:shadow-lg disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {loading ? 'Claiming Wallet...' : 'Claim My Wallet'}
              </button>

              {/* Info Box */}
              <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">What happens next?</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>✓ All your WhatsApp reports will be linked to your MPC wallet</li>
                  <li>✓ You'll have full control over your medical records</li>
                  <li>✓ You can export your wallet to MetaMask anytime</li>
                  <li>✓ Your data remains encrypted and on IPFS</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-sm text-gray-600">
            Need help? <a href="/support" className="text-blue-600 hover:underline">Contact Support</a>
          </p>
        </div>
      </div>
    </div>
  );
}
