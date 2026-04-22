'use client';

import { PrivySecureUpload } from '@/components/PrivySecureUpload';

export default function SecureUploadPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            True Privacy with Privy
          </h1>
          <p className="text-xl text-gray-600">
            Client-side encryption with biometric keys
          </p>
        </div>

        {/* Demo Component */}
        <PrivySecureUpload />

        {/* Architecture Explanation */}
        <div className="mt-12 bg-white rounded-xl p-8 shadow-lg">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Architecture: Zero-Knowledge Healthcare
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Before */}
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <h3 className="font-bold text-red-900 mb-3">
                ❌ Traditional Approach
              </h3>
              <ul className="text-sm text-red-800 space-y-2">
                <li>• Backend holds encryption keys</li>
                <li>• Company can decrypt files</li>
                <li>• "Trust us" security model</li>
                <li>• Single point of failure</li>
                <li>• No true self-custody</li>
              </ul>
            </div>

            {/* After */}
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="font-bold text-green-900 mb-3">
                ✅ Privy MPC Approach
              </h3>
              <ul className="text-sm text-green-800 space-y-2">
                <li>• Patient's wallet holds keys</li>
                <li>• Backend CANNOT decrypt</li>
                <li>• "Cryptographically impossible" model</li>
                <li>• Distributed security (MPC)</li>
                <li>• Export key anytime</li>
              </ul>
            </div>
          </div>

          {/* Flow Diagram */}
          <div className="mt-8 p-6 bg-gray-50 rounded-lg">
            <h3 className="font-bold text-gray-900 mb-4">
              Encryption Flow:
            </h3>
            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  1
                </span>
                <p>Patient uploads file → AES-256 encryption in browser</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  2
                </span>
                <p>Encrypted file → IPFS (public but unreadable)</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  3
                </span>
                <p>AES key → encrypted with Privy wallet signature</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  4
                </span>
                <p>Encrypted AES key → stored in database</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
                  ✓
                </span>
                <p>
                  <strong>Result:</strong> Backend has encrypted key but cannot
                  decrypt without patient's Face ID
                </p>
              </div>
            </div>
          </div>

          {/* Pitch Points */}
          <div className="mt-8 p-6 bg-blue-900 text-white rounded-lg">
            <h3 className="font-bold text-xl mb-4">For Your Pitch:</h3>
            <p className="mb-4">
              "We use Privy MPC wallets for client-side encryption. When a
              patient uploads a medical record, it's encrypted with AES-256 in
              their browser. The AES key is then encrypted with their Privy
              wallet, which requires Face ID or Touch ID to unlock."
            </p>
            <p className="mb-4">
              "Our backend stores the encrypted AES keys, but we are
              <strong> physically incapable</strong> of decrypting them without
              the patient's active biometric consent. This isn't a 'trust us'
              promise - it's cryptographically enforced."
            </p>
            <p>
              "Patients can export their private keys anytime for full
              self-custody. We've built genuine Web3 sovereignty with zero
              crypto UX."
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
