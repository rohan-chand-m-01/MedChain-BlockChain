/**
 * Lab Report Upload Component with Privy Encryption
 * 
 * Demonstrates decentralized encryption:
 * 1. User uploads report
 * 2. Encrypted client-side with Privy wallet signature
 * 3. Encrypted data stored on IPFS
 * 4. Metadata stored on blockchain
 * 5. User can recover access via social login (no password!)
 */

'use client';

import { useState } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import { useLabReportEncryption } from '@/hooks/useLabReportEncryption';

export function LabReportUpload() {
  const { login, authenticated } = usePrivy();
  const {
    encryptReport,
    isEncrypting,
    isReady,
    walletAddress,
  } = useLabReportEncryption();

  const [file, setFile] = useState<File | null>(null);
  const [reportType, setReportType] = useState('blood_test');
  const [uploadStatus, setUploadStatus] = useState<string>('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !isReady) return;

    setUploadStatus('Reading file...');

    try {
      // Read file content
      const fileContent = await file.text();

      setUploadStatus('Encrypting with your Privy wallet...');

      // Encrypt with Privy wallet signature
      const encrypted = await encryptReport(fileContent, reportType);

      setUploadStatus('Uploading to IPFS...');

      // Upload encrypted data to IPFS
      const response = await fetch('/api/upload-encrypted-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          encryptedData: encrypted.encryptedData,
          iv: encrypted.iv,
          patientId: encrypted.patientId,
          reportType: encrypted.reportType,
          timestamp: encrypted.timestamp,
        }),
      });

      if (!response.ok) throw new Error('Upload failed');

      const { ipfsHash, txHash, riskScore, riskLevel } = await response.json();

      setUploadStatus('Storing proof on Stellar blockchain...');

      // Store proof on Stellar
      try {
        const stellarResponse = await fetch('/api/stellar/store-proof', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ipfs_hash: ipfsHash,
            risk_score: riskScore || 50,
            risk_level: riskLevel || 'MEDIUM',
          }),
        });

        const stellarData = await stellarResponse.json();
        const stellarTxHash = stellarData.tx_hash;

        setUploadStatus(
          `✅ Report encrypted and uploaded!\n` +
          `IPFS: ${ipfsHash}\n` +
          `Blockchain Tx: ${txHash}\n` +
          `Stellar Proof: ${stellarTxHash}\n` +
          `View on Stellar: https://stellar.expert/explorer/testnet/tx/${stellarTxHash}`
        );
      } catch (stellarError) {
        console.warn('Stellar proof storage failed:', stellarError);
        setUploadStatus(
          `✅ Report encrypted and uploaded!\n` +
          `IPFS: ${ipfsHash}\n` +
          `Blockchain Tx: ${txHash}\n` +
          `⚠️ Stellar proof pending...`
        );
      }

      setFile(null);
    } catch (error: any) {
      setUploadStatus(`❌ Error: ${error.message}`);
    }
  };

  if (!authenticated) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Upload Lab Report</h3>
        <p className="text-gray-600 mb-4">
          Login with Privy to securely encrypt and upload your lab reports.
          No passwords needed - recover access anytime with social login!
        </p>
        <button
          onClick={login}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Login with Privy
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Upload Lab Report</h3>

      <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
        <p className="text-sm text-blue-800">
          🔐 Your report will be encrypted with your Privy wallet signature.
          Only you (and doctors you grant access to) can decrypt it.
        </p>
        <p className="text-xs text-blue-600 mt-1">
          Wallet: {walletAddress?.slice(0, 6)}...{walletAddress?.slice(-4)}
        </p>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Report Type</label>
        <select
          value={reportType}
          onChange={(e) => setReportType(e.target.value)}
          className="w-full p-2 border rounded"
        >
          <option value="blood_test">Blood Test</option>
          <option value="urine_test">Urine Test</option>
          <option value="xray">X-Ray</option>
          <option value="mri">MRI</option>
          <option value="ct_scan">CT Scan</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Select File</label>
        <input
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.txt,.jpg,.png"
          className="w-full p-2 border rounded"
        />
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || isEncrypting || !isReady}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
      >
        {isEncrypting ? 'Encrypting...' : 'Encrypt & Upload'}
      </button>

      {uploadStatus && (
        <div className="mt-4 p-3 bg-gray-50 rounded border">
          <pre className="text-xs whitespace-pre-wrap">{uploadStatus}</pre>
        </div>
      )}

      <div className="mt-6 p-4 bg-green-50 rounded border border-green-200">
        <h4 className="font-semibold text-green-800 mb-2">
          🎉 Decentralized Security Benefits:
        </h4>
        <ul className="text-sm text-green-700 space-y-1">
          <li>✅ No passwords to remember</li>
          <li>✅ Recover access via social login (Google, email, passkey)</li>
          <li>✅ Keys derived from your Privy wallet signature</li>
          <li>✅ Encrypted client-side (backend never sees plaintext)</li>
          <li>✅ Stored on IPFS (decentralized storage)</li>
          <li>✅ Access control on blockchain</li>
        </ul>
      </div>
    </div>
  );
}
