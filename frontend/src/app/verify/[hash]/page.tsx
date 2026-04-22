'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';

interface VerificationData {
  verified: boolean;
  risk_level: string;
  risk_score: number;
  timestamp: string;
  ipfs_cid: string;
  commitment_hash: string;
  record_id: string;
  blockchain_verified: boolean;
  blockchain_risk_score?: number;
  blockchain_risk_level?: string;
  blockchain_timestamp?: number;
}

export default function VerifyPage() {
  const params = useParams();
  const hash = params.hash as string;
  
  const [data, setData] = useState<VerificationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    const fetchVerification = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/verify/${hash}`);
        
        if (!response.ok) {
          if (response.status === 404) {
            setError('Record not found');
          } else {
            setError('Verification failed');
          }
          setLoading(false);
          return;
        }
        
        const result = await response.json();
        setData(result);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch verification data');
        setLoading(false);
      }
    };

    if (hash) {
      fetchVerification();
    }
  }, [hash]);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
  };

  const getRiskEmoji = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low': return '🟢';
      case 'medium': return '🟡';
      case 'high': return '🔴';
      default: return '⚪';
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Verifying record...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 text-center">
          <div className="text-6xl mb-4">❌</div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Verification Failed
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {error || 'Record not found'}
          </p>
          <a
            href="/"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Return Home
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
            🔐 Blockchain Verification
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Medical Report Authenticity Proof
          </p>
        </div>

        {/* Verification Status Banner */}
        <div className={`rounded-2xl p-6 ${
          data.verified && data.blockchain_verified
            ? 'bg-green-50 dark:bg-green-900/20 border-2 border-green-500'
            : 'bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-500'
        }`}>
          <div className="flex items-center gap-4">
            <div className="text-4xl">
              {data.verified && data.blockchain_verified ? '✅' : '⚠️'}
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                {data.verified && data.blockchain_verified
                  ? 'Verified on Blockchain'
                  : 'Database Verified'}
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                {data.blockchain_verified
                  ? 'This record exists on the Ethereum blockchain and cannot be tampered with'
                  : 'Record found in database. Blockchain verification unavailable.'}
              </p>
            </div>
          </div>
        </div>

        {/* Record Details Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            📋 Record Details
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Risk Level</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {getRiskEmoji(data.risk_level)} {data.risk_level.toUpperCase()}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600 dark:text-gray-400">Risk Score</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {data.risk_score}%
                </p>
              </div>
            </div>
            
            {data.blockchain_verified && data.blockchain_risk_score !== undefined && (
              <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <p className="text-sm font-medium text-green-900 dark:text-green-200 mb-2">
                  ✅ Blockchain Verified Data
                </p>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-green-800 dark:text-green-300">On-Chain Risk Level</p>
                    <p className="text-lg font-semibold text-green-900 dark:text-green-100">
                      {getRiskEmoji(data.blockchain_risk_level || '')} {data.blockchain_risk_level}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-green-800 dark:text-green-300">On-Chain Risk Score</p>
                    <p className="text-lg font-semibold text-green-900 dark:text-green-100">
                      {data.blockchain_risk_score}%
                    </p>
                  </div>
                </div>
                {data.blockchain_timestamp && (
                  <p className="text-xs text-green-700 dark:text-green-400 mt-2">
                    Blockchain Timestamp: {new Date(data.blockchain_timestamp * 1000).toLocaleString()}
                  </p>
                )}
              </div>
            )}
            
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Timestamp</p>
              <p className="text-gray-900 dark:text-white font-mono">
                {formatDate(data.timestamp)}
              </p>
            </div>
          </div>
        </div>

        {/* Blockchain Proof Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            🔗 Blockchain Proof
          </h3>
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600 dark:text-gray-400">Record ID</p>
                <button
                  onClick={() => copyToClipboard(data.record_id, 'record')}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  {copied === 'record' ? '✓ Copied' : '📋 Copy'}
                </button>
              </div>
              <p className="text-gray-900 dark:text-white font-mono text-sm break-all">
                {data.record_id}
              </p>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600 dark:text-gray-400">Commitment Hash</p>
                <button
                  onClick={() => copyToClipboard(data.commitment_hash, 'commitment')}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  {copied === 'commitment' ? '✓ Copied' : '📋 Copy'}
                </button>
              </div>
              <p className="text-gray-900 dark:text-white font-mono text-sm break-all">
                {data.commitment_hash}
              </p>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600 dark:text-gray-400">IPFS CID</p>
                <button
                  onClick={() => copyToClipboard(data.ipfs_cid, 'ipfs')}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  {copied === 'ipfs' ? '✓ Copied' : '📋 Copy'}
                </button>
              </div>
              <p className="text-gray-900 dark:text-white font-mono text-sm break-all">
                {data.ipfs_cid}
              </p>
            </div>

            <a
              href={`https://sepolia.etherscan.io/address/${process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || ''}`}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full text-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              🔍 View Contract on Etherscan
            </a>
          </div>
        </div>

        {/* Insurance Verification Instructions */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            🏥 For Insurance Providers
          </h3>
          <div className="space-y-4 text-gray-600 dark:text-gray-400">
            <p className="font-medium text-gray-900 dark:text-white">
              How to verify this record:
            </p>
            <ol className="list-decimal list-inside space-y-2 ml-2">
              <li>Copy the Record ID or Commitment Hash above</li>
              <li>Visit the Ethereum blockchain explorer (Etherscan)</li>
              <li>Navigate to the MediChainRecords contract address</li>
              <li>Call <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">verifyRecord(recordId)</code> to confirm it exists on-chain</li>
            </ol>
            
            <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
              <p className="text-sm font-medium text-yellow-900 dark:text-yellow-200">
                ⚠️ Important Disclaimer
              </p>
              <p className="text-sm text-yellow-800 dark:text-yellow-300 mt-2">
                This verification proves the <strong>existence and timestamp</strong> of a medical report on the blockchain.
                It does NOT provide access to the medical content itself, which is encrypted and stored on IPFS.
                Only the patient can decrypt and share the full report.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500 dark:text-gray-400 pt-4">
          <p>Powered by MediChain • Ethereum Blockchain • IPFS</p>
          <p className="mt-2">🔒 Privacy-Preserved • 🔐 Tamper-Proof • ✅ Verifiable</p>
        </div>
      </div>
    </div>
  );
}
