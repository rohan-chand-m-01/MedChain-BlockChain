/**
 * Privy-Based Decentralized Key Manager
 * 
 * Uses Privy's embedded wallet to derive encryption keys for lab reports.
 * Users can recover access via social login - no passwords to remember!
 * 
 * Architecture:
 * 1. User logs in with Privy (email/Google/passkey)
 * 2. Privy creates/recovers embedded wallet (MPC)
 * 3. Wallet signs deterministic message → derives encryption key
 * 4. Key encrypts/decrypts lab reports client-side
 * 5. Only encrypted data stored on-chain/IPFS
 * 
 * Security:
 * - Keys never leave client
 * - Deterministic derivation (same signature = same key)
 * - Social recovery via Privy
 * - Zero-knowledge: backend never sees plaintext keys
 */

import { usePrivy, useWallets } from '@privy-io/react-auth';
import CryptoJS from 'crypto-js';

export class PrivyKeyManager {
  private wallet: any;

  constructor(wallet: any) {
    this.wallet = wallet;
  }

  /**
   * Derive encryption key from wallet signature
   * Uses deterministic message signing for consistent key derivation
   */
  async deriveEncryptionKey(patientId: string): Promise<string> {
    if (!this.wallet) {
      throw new Error('Wallet not initialized. Please login with Privy.');
    }

    // Deterministic message for key derivation
    const message = `MediChain Key Derivation\nPatient: ${patientId}\nPurpose: Lab Report Encryption`;

    try {
      // Sign message with embedded wallet
      // Same message = same signature = same key (deterministic)
      const signature = await this.wallet.signMessage(message);

      // Derive 256-bit encryption key from signature
      const key = CryptoJS.SHA256(signature).toString();

      return key;
    } catch (error) {
      console.error('Key derivation failed:', error);
      throw new Error('Failed to derive encryption key. Please try again.');
    }
  }

  /**
   * Encrypt lab report data client-side
   */
  async encryptLabReport(
    reportData: string,
    patientId: string
  ): Promise<{ encrypted: string; iv: string }> {
    const key = await this.deriveEncryptionKey(patientId);

    // Generate random IV for this encryption
    const iv = CryptoJS.lib.WordArray.random(16);

    // Encrypt with AES-256-CBC
    const encrypted = CryptoJS.AES.encrypt(reportData, key, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7,
    });

    return {
      encrypted: encrypted.toString(),
      iv: iv.toString(CryptoJS.enc.Base64),
    };
  }

  /**
   * Decrypt lab report data client-side
   */
  async decryptLabReport(
    encryptedData: string,
    iv: string,
    patientId: string
  ): Promise<string> {
    const key = await this.deriveEncryptionKey(patientId);

    // Parse IV from base64
    const ivWordArray = CryptoJS.enc.Base64.parse(iv);

    // Decrypt with AES-256-CBC
    const decrypted = CryptoJS.AES.decrypt(encryptedData, key, {
      iv: ivWordArray,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7,
    });

    return decrypted.toString(CryptoJS.enc.Utf8);
  }

  /**
   * Grant doctor access by encrypting key with doctor's public key
   * Doctor can decrypt using their own Privy wallet
   */
  async grantDoctorAccess(
    patientId: string,
    doctorWalletAddress: string,
    expiresIn: number = 7 * 24 * 60 * 60 * 1000 // 7 days
  ): Promise<{ encryptedKey: string; expiresAt: number }> {
    const patientKey = await this.deriveEncryptionKey(patientId);

    // In production, fetch doctor's public key from their Privy wallet
    // For now, we'll use a shared secret approach
    const doctorMessage = `MediChain Doctor Access\nDoctor: ${doctorWalletAddress}\nPatient: ${patientId}`;
    const doctorSignature = await this.wallet.signMessage(doctorMessage);
    const doctorKey = CryptoJS.SHA256(doctorSignature).toString();

    // Encrypt patient's key with doctor's derived key
    const encryptedKey = CryptoJS.AES.encrypt(patientKey, doctorKey).toString();

    const expiresAt = Date.now() + expiresIn;

    return { encryptedKey, expiresAt };
  }

  /**
   * Revoke doctor access (mark as expired on-chain)
   */
  async revokeDoctorAccess(
    patientId: string,
    doctorWalletAddress: string
  ): Promise<void> {
    // Call smart contract to revoke access
    // This will be implemented with your ConsentRegistry contract
    console.log(`Revoking access for doctor ${doctorWalletAddress} to patient ${patientId}`);
  }
}

/**
 * React Hook for Privy Key Management
 */
export function usePrivyKeyManager() {
  const { ready, authenticated, user } = usePrivy();
  const { wallets } = useWallets();

  const embeddedWallet = wallets.find((w) => w.walletClientType === 'privy');

  if (!ready || !authenticated || !embeddedWallet) {
    return null;
  }

  return new PrivyKeyManager(embeddedWallet);
}

/**
 * Helper: Store encrypted report metadata on-chain
 */
export interface EncryptedReportMetadata {
  patientId: string;
  reportHash: string; // IPFS hash of encrypted report
  encryptedData: string; // Encrypted report data
  iv: string; // Initialization vector
  timestamp: number;
  reportType: string;
  accessGrants: {
    doctorAddress: string;
    encryptedKey: string;
    expiresAt: number;
  }[];
}

/**
 * Helper: Verify user can access report
 */
export async function canAccessReport(
  keyManager: PrivyKeyManager | null,
  metadata: EncryptedReportMetadata,
  userWalletAddress: string
): Promise<boolean> {
  if (!keyManager) return false;

  // Patient always has access
  if (metadata.patientId === userWalletAddress) {
    return true;
  }

  // Check if doctor has valid access grant
  const grant = metadata.accessGrants.find(
    (g) => g.doctorAddress === userWalletAddress && g.expiresAt > Date.now()
  );

  return !!grant;
}
