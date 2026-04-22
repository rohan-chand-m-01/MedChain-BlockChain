/**
 * Lab Report Encryption Hook
 * 
 * Provides easy-to-use interface for encrypting/decrypting lab reports
 * using Privy's embedded wallet for key management.
 * 
 * Usage:
 * ```tsx
 * const { encryptReport, decryptReport, grantAccess } = useLabReportEncryption();
 * 
 * // Upload encrypted report
 * const encrypted = await encryptReport(reportData);
 * await uploadToIPFS(encrypted);
 * 
 * // View report
 * const decrypted = await decryptReport(encryptedData, iv);
 * 
 * // Grant doctor access
 * await grantAccess(doctorAddress, 7); // 7 days
 * ```
 */

import { useState } from 'react';
import { usePrivy, useWallets } from '@privy-io/react-auth';
import { usePrivyKeyManager, EncryptedReportMetadata } from '@/services/privyKeyManager';

export function useLabReportEncryption() {
  const { ready, authenticated, user } = usePrivy();
  const { wallets } = useWallets();
  const keyManager = usePrivyKeyManager();

  const [isEncrypting, setIsEncrypting] = useState(false);
  const [isDecrypting, setIsDecrypting] = useState(false);

  const embeddedWallet = wallets.find((w) => w.walletClientType === 'privy');
  const walletAddress = embeddedWallet?.address;

  /**
   * Encrypt lab report for secure storage
   */
  const encryptReport = async (
    reportData: string,
    reportType: string = 'lab_report'
  ): Promise<EncryptedReportMetadata> => {
    if (!keyManager || !walletAddress) {
      throw new Error('Please login with Privy to encrypt reports');
    }

    setIsEncrypting(true);
    try {
      const { encrypted, iv } = await keyManager.encryptLabReport(
        reportData,
        walletAddress
      );

      // Create metadata for on-chain storage
      const metadata: EncryptedReportMetadata = {
        patientId: walletAddress,
        reportHash: '', // Will be set after IPFS upload
        encryptedData: encrypted,
        iv,
        timestamp: Date.now(),
        reportType,
        accessGrants: [],
      };

      return metadata;
    } finally {
      setIsEncrypting(false);
    }
  };

  /**
   * Decrypt lab report for viewing
   */
  const decryptReport = async (
    encryptedData: string,
    iv: string,
    patientId?: string
  ): Promise<string> => {
    if (!keyManager || !walletAddress) {
      throw new Error('Please login with Privy to decrypt reports');
    }

    setIsDecrypting(true);
    try {
      // Use provided patientId or current user's address
      const targetPatientId = patientId || walletAddress;

      const decrypted = await keyManager.decryptLabReport(
        encryptedData,
        iv,
        targetPatientId
      );

      return decrypted;
    } finally {
      setIsDecrypting(false);
    }
  };

  /**
   * Grant doctor access to encrypted report
   */
  const grantAccess = async (
    doctorWalletAddress: string,
    durationDays: number = 7
  ): Promise<{ encryptedKey: string; expiresAt: number }> => {
    if (!keyManager || !walletAddress) {
      throw new Error('Please login with Privy to grant access');
    }

    const expiresIn = durationDays * 24 * 60 * 60 * 1000;
    return await keyManager.grantDoctorAccess(
      walletAddress,
      doctorWalletAddress,
      expiresIn
    );
  };

  /**
   * Revoke doctor access
   */
  const revokeAccess = async (doctorWalletAddress: string): Promise<void> => {
    if (!keyManager || !walletAddress) {
      throw new Error('Please login with Privy to revoke access');
    }

    await keyManager.revokeDoctorAccess(walletAddress, doctorWalletAddress);
  };

  /**
   * Check if current user can access a report
   */
  const canAccess = (metadata: EncryptedReportMetadata): boolean => {
    if (!walletAddress) return false;

    // Patient always has access
    if (metadata.patientId === walletAddress) {
      return true;
    }

    // Check doctor access grants
    const grant = metadata.accessGrants.find(
      (g) => g.doctorAddress === walletAddress && g.expiresAt > Date.now()
    );

    return !!grant;
  };

  return {
    // State
    isEncrypting,
    isDecrypting,
    isReady: ready && authenticated && !!keyManager,
    walletAddress,

    // Methods
    encryptReport,
    decryptReport,
    grantAccess,
    revokeAccess,
    canAccess,
  };
}
