'use client';

import { PasskeyLoginDemo } from '@/components/PasskeyLoginDemo';

export default function PasskeyDemoPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Passkey Authentication Demo
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Web3 Onboarding with Zero Crypto UX
          </p>
          <p className="text-gray-500">
            Face ID / Touch ID / Windows Hello → MPC Wallet Created
          </p>
        </div>

        {/* Demo Component */}
        <PasskeyLoginDemo />

        {/* Explanation Section */}
        <div className="mt-12 grid md:grid-cols-2 gap-6">
          {/* What is Passkey */}
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              🔑 What is a Passkey?
            </h3>
            <div className="space-y-3 text-gray-700">
              <p>
                Passkeys are a modern authentication standard that uses your device's biometric sensors (Face ID, Touch ID, Windows Hello) instead of passwords.
              </p>
              <p className="text-sm">
                <strong>Key Benefits:</strong>
              </p>
              <ul className="text-sm space-y-1 ml-4">
                <li>• No passwords to remember or type</li>
                <li>• Phishing-resistant (can't be stolen)</li>
                <li>• Works across all your devices</li>
                <li>• Instant authentication (1-2 seconds)</li>
              </ul>
            </div>
          </div>

          {/* How MPC Works */}
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              🔐 MPC Wallet Security
            </h3>
            <div className="space-y-3 text-gray-700">
              <p>
                Multi-Party Computation (MPC) splits your private key between your device and Privy's servers using advanced cryptography.
              </p>
              <p className="text-sm">
                <strong>Security Model:</strong>
              </p>
              <ul className="text-sm space-y-1 ml-4">
                <li>• Your device holds 50% of the key</li>
                <li>• Privy's servers hold 50% of the key</li>
                <li>• Neither party alone can access funds</li>
                <li>• You can export to MetaMask anytime</li>
              </ul>
            </div>
          </div>

          {/* Comparison */}
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              📊 vs Traditional Web3
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center pb-2 border-b">
                <span className="text-gray-700">Onboarding Time</span>
                <div className="text-right">
                  <p className="text-sm text-gray-500 line-through">5 minutes</p>
                  <p className="text-green-600 font-bold">2 seconds</p>
                </div>
              </div>
              <div className="flex justify-between items-center pb-2 border-b">
                <span className="text-gray-700">Drop-off Rate</span>
                <div className="text-right">
                  <p className="text-sm text-gray-500 line-through">50%</p>
                  <p className="text-green-600 font-bold">5%</p>
                </div>
              </div>
              <div className="flex justify-between items-center pb-2 border-b">
                <span className="text-gray-700">Seed Phrases</span>
                <div className="text-right">
                  <p className="text-sm text-gray-500 line-through">12 words</p>
                  <p className="text-green-600 font-bold">0 words</p>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">User Experience</span>
                <div className="text-right">
                  <p className="text-sm text-gray-500 line-through">Complex</p>
                  <p className="text-green-600 font-bold">Simple</p>
                </div>
              </div>
            </div>
          </div>

          {/* Use Cases */}
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              🎯 Perfect For
            </h3>
            <div className="space-y-3 text-gray-700">
              <div className="flex items-start gap-3">
                <span className="text-2xl">🏥</span>
                <div>
                  <p className="font-medium">Healthcare</p>
                  <p className="text-sm text-gray-600">Patients need simple, secure access to medical records</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">👴</span>
                <div>
                  <p className="font-medium">Elderly Users</p>
                  <p className="text-sm text-gray-600">No technical knowledge required - just use your face</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">🌍</span>
                <div>
                  <p className="font-medium">Mainstream Adoption</p>
                  <p className="text-sm text-gray-600">530M WhatsApp users can access Web3</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Technical Details */}
        <div className="mt-12 bg-gray-900 text-white rounded-xl p-8">
          <h3 className="text-2xl font-bold mb-6">Technical Implementation</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-bold text-blue-400 mb-3">Frontend (React)</h4>
              <pre className="bg-gray-800 p-4 rounded-lg text-sm overflow-x-auto">
{`// PrivyProvider config
loginMethods: [
  'email',
  'google', 
  'wallet',
  'passkey' // ← Enables passkeys
]

// Usage
const { login } = usePrivyAuth();
<button onClick={login}>
  Sign In
</button>`}
              </pre>
            </div>

            <div>
              <h4 className="font-bold text-green-400 mb-3">What Happens</h4>
              <div className="space-y-2 text-sm">
                <p>1. User clicks "Sign In"</p>
                <p>2. Privy shows passkey prompt</p>
                <p>3. User uses Face ID/Touch ID</p>
                <p>4. Privy creates MPC wallet</p>
                <p>5. Wallet address returned</p>
                <p>6. User can sign transactions</p>
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-blue-900 rounded-lg">
            <p className="text-sm">
              <strong>Security Note:</strong> Passkeys use WebAuthn standard with public-key cryptography. 
              The private key never leaves your device. Privy only receives a signed challenge, 
              proving you own the passkey without exposing the key itself.
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <a
            href="/"
            className="inline-block px-8 py-4 bg-white text-blue-600 rounded-xl hover:bg-gray-50 transition-colors font-bold text-lg shadow-lg"
          >
            ← Back to Home
          </a>
        </div>
      </div>
    </div>
  );
}
