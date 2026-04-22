'use client';

import { usePrivy } from '@privy-io/react-auth';

export default function TestPrivyPage() {
  const { login, authenticated, user, ready, logout } = usePrivy();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6">Privy Test Page</h1>
        
        <div className="space-y-4 mb-8">
          <div className="p-4 bg-gray-100 rounded">
            <p className="font-semibold">Status:</p>
            <p>Ready: {ready ? '✅ Yes' : '❌ No'}</p>
            <p>Authenticated: {authenticated ? '✅ Yes' : '❌ No'}</p>
            <p>App ID: {process.env.NEXT_PUBLIC_PRIVY_APP_ID || '❌ Not configured'}</p>
          </div>

          {user && (
            <div className="p-4 bg-green-100 rounded">
              <p className="font-semibold">User Info:</p>
              <pre className="text-xs mt-2 overflow-auto">
                {JSON.stringify(user, null, 2)}
              </pre>
            </div>
          )}
        </div>

        <div className="space-x-4">
          {!authenticated ? (
            <button
              onClick={() => {
                console.log('Login button clicked');
                login();
              }}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
            >
              🔐 Login with Privy
            </button>
          ) : (
            <button
              onClick={() => logout()}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold"
            >
              Logout
            </button>
          )}
        </div>

        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-yellow-800">
            <strong>Debug:</strong> Open browser console (F12) to see any errors
          </p>
        </div>
      </div>
    </div>
  );
}
