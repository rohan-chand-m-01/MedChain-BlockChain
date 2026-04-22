'use client';

import { usePrivyAuth } from '@/hooks/usePrivyAuth';

export function PasskeyLoginDemo() {
  const { ready, authenticated, user, walletAddress, login, logout } = usePrivyAuth();

  if (!ready) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!authenticated) {
    return (
      <div className="max-w-md mx-auto p-6 bg-white rounded-2xl shadow-xl">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">🔐</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Sign In with Passkey
          </h2>
          <p className="text-gray-600">
            Use Face ID, Touch ID, or Windows Hello
          </p>
        </div>

        {/* Features */}
        <div className="space-y-3 mb-6">
          <div className="flex items-start gap-3">
            <span className="text-green-600 mt-1">✓</span>
            <div>
              <p className="font-medium text-gray-900">Instant Login</p>
              <p className="text-sm text-gray-600">No passwords, no OTP codes</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-green-600 mt-1">✓</span>
            <div>
              <p className="font-medium text-gray-900">MPC Wallet Created</p>
              <p className="text-sm text-gray-600">Real Ethereum wallet, split key security</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-green-600 mt-1">✓</span>
            <div>
              <p className="font-medium text-gray-900">Phishing Resistant</p>
              <p className="text-sm text-gray-600">Biometric authentication, can't be stolen</p>
            </div>
          </div>
        </div>

        {/* Login Button */}
        <button
          onClick={login}
          className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all font-medium text-lg shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          🔑 Sign In with Passkey
        </button>

        {/* Info */}
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <p className="text-xs text-blue-800">
            <strong>How it works:</strong> Privy will prompt you to use your device's biometric authentication (Face ID, Touch ID, or Windows Hello). Your passkey is stored securely on your device and creates a real MPC wallet.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-2xl shadow-xl">
      {/* Success Header */}
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-3xl">✅</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Signed In Successfully!
        </h2>
        <p className="text-gray-600">
          Your MPC wallet is ready
        </p>
      </div>

      {/* User Info */}
      <div className="space-y-4 mb-6">
        <div className="p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Email</p>
          <p className="font-medium text-gray-900">{user?.email || 'Authenticated'}</p>
        </div>

        <div className="p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Wallet Address</p>
          <p className="font-mono text-sm text-gray-900 break-all">
            {walletAddress || 'Creating wallet...'}
          </p>
        </div>

        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm font-medium text-green-900 mb-2">
            🔐 MPC Security Active
          </p>
          <p className="text-xs text-green-800">
            Your private key is split between your device and Privy's servers. Neither party alone can access your funds.
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-3">
        <button
          onClick={() => window.location.href = '/patient'}
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Go to Dashboard
        </button>
        
        <button
          onClick={logout}
          className="w-full px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
        >
          Sign Out
        </button>
      </div>

      {/* Demo Stats */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center mb-3">
          Demo Performance Metrics
        </p>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div>
            <p className="text-2xl font-bold text-blue-600">2s</p>
            <p className="text-xs text-gray-600">Login Time</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-600">0</p>
            <p className="text-xs text-gray-600">Passwords</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-purple-600">100%</p>
            <p className="text-xs text-gray-600">Secure</p>
          </div>
        </div>
      </div>
    </div>
  );
}
