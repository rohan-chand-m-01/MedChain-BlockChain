'use client';

import { useState } from 'react';
import { usePrivyAuth } from '@/hooks/usePrivyAuth';
import { ethers } from 'ethers';
import {
  uploadEncryptedRecord,
  downloadDecryptedRecord,
} from '@/lib/privyEncryption';

export function PrivySecureUpload() {
  const { authenticated, walletAddress, embeddedWallet } = usePrivyAuth();
  const [uploading, setUploading] = useState(false);
  const [uploadedRecord, setUploadedRecord] = useState<any>(null);

  const handleSecureUpload = async (file: File) => {
    if (!authenticated || !walletAddress || !embeddedWallet) {
      alert('Please sign in with Privy first');
      return;
    }

    setUploading(true);

    try {
      // Get Privy wallet signer
      const provider = await embeddedWallet.getEthereumProvider();
      const ethersProvider = new ethers.BrowserProvider(provider);
      const signer = await ethersProvider.getSigner();

      // Mock IPFS upload function (replace with real implementation)
      const uploadToIPFS = async (data: string): Promise<string> => {
        const response = await fetch('/api/ipfs/upload', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ data }),
        });
        const result = await response.json();
        return result.ipfsHash;
      };

      // Upload encrypted record
      const result = await uploadEncryptedRecord(
        file,
        walletAddress,
        signer,
        uploadToIPFS
      );

      // Store metadata in database
      const response = await fetch('/api/records/store', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ipfsHash: result.ipfsHash,
          encryptedAESKey: result.encryptedAESKey,
          walletAddress: result.walletAddress,
          fileName: file.name,
          fileSize: file.size,
          uploadedAt: new Date().toISOString(),
        }),
      });

      const record = await response.json();
      setUploadedRecord(record);

      alert('✅ File encrypted and uploaded securely!');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed: ' + (error as Error).message);
    } finally {
      setUploading(false);
    }
  };

  const handleSecureDownload = async (recordId: string) => {
    if (!authenticated || !walletAddress || !embeddedWallet) {
      alert('Please sign in with Privy first');
      return;
    }

    try {
      // Get record metadata from database
      const response = await fetch(`/api/records/${recordId}`);
      const record = await response.json();

      // Get Privy wallet signer
      const provider = await embeddedWallet.getEthereumProvider();
      const ethersProvider = new ethers.BrowserProvider(provider);
      const signer = await ethersProvider.getSigner();

      // Mock IPFS download function (replace with real implementation)
      const downloadFromIPFS = async (hash: string): Promise<string> => {
        const response = await fetch(`/api/ipfs/download/${hash}`);
        const result = await response.json();
        return result.data;
      };

      // Download and decrypt record
      const decryptedFile = await downloadDecryptedRecord(
        record.ipfsHash,
        record.encryptedAESKey,
        walletAddress,
        signer,
        downloadFromIPFS
      );

      // Create download link
      const blob = new Blob([decryptedFile]);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = record.fileName;
      a.click();

      alert('✅ File decrypted and downloaded!');
    } catch (error) {
      console.error('Download error:', error);
      alert('Download failed: ' + (error as Error).message);
    }
  };

  if (!authenticated) {
    return (
      <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-800">
          Please sign in with Privy to use secure file encryption
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          🔐 Privy Secure Upload
        </h2>
        <p className="text-gray-600">
          Files encrypted with your biometric - only you can decrypt
        </p>
      </div>

      {/* Security Explanation */}
      <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
        <h3 className="font-bold text-green-900 mb-2">
          How This Works:
        </h3>
        <ul className="text-sm text-green-800 space-y-1">
          <li>✓ File encrypted with AES-256 in your browser</li>
          <li>✓ AES key encrypted with your Privy wallet</li>
          <li>✓ Requires Face ID/Touch ID to decrypt</li>
          <li>✓ Backend stores encrypted keys but CANNOT decrypt</li>
          <li>✓ You can export private key anytime for full custody</li>
        </ul>
      </div>

      {/* Upload Section */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload Medical Record
        </label>
        <input
          type="file"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleSecureUpload(file);
          }}
          disabled={uploading}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
        />
        {uploading && (
          <p className="mt-2 text-sm text-blue-600">
            Encrypting and uploading...
          </p>
        )}
      </div>

      {/* Uploaded Record */}
      {uploadedRecord && (
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="font-bold text-gray-900 mb-2">
            ✅ Upload Complete
          </h3>
          <div className="text-sm text-gray-700 space-y-1">
            <p>File: {uploadedRecord.fileName}</p>
            <p>IPFS: {uploadedRecord.ipfsHash.slice(0, 20)}...</p>
            <p>Encrypted with: {walletAddress?.slice(0, 10)}...</p>
          </div>
          <button
            onClick={() => handleSecureDownload(uploadedRecord.id)}
            className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            Download & Decrypt
          </button>
        </div>
      )}

      {/* Privacy Guarantee */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900">
          <strong>Privacy Guarantee:</strong> Your medical records are encrypted
          with your Privy MPC wallet. Our backend stores encrypted keys but is
          physically incapable of decrypting your files without your active
          biometric consent (Face ID/Touch ID). You maintain full sovereignty
          and can export your private key anytime.
        </p>
      </div>
    </div>
  );
}
