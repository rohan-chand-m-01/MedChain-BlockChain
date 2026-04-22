/**
 * Stellar Service - Frontend Integration
 * 
 * Handles Stellar wallet operations for MediChain.
 * Works with Privy for identity management.
 * 
 * Architecture:
 * - Privy: Who you are (phone number → user identity)
 * - Stellar: What you do (transactions, proofs, payments)
 * - Backend: Bridge between Privy user ID and Stellar keypair
 */

import * as StellarSdk from '@stellar/stellar-sdk';

export interface StellarAccount {
  publicKey: string;
  encryptedSecret: string;
}

export interface RecordProof {
  ipfsHash: string;
  riskScore: number;
  riskLevel: string;
}

export class StellarService {
  private server: StellarSdk.Horizon.Server;
  private networkPassphrase: string;
  private network: 'testnet' | 'public';

  constructor(network: 'testnet' | 'public' = 'testnet') {
    this.network = network;
    
    if (network === 'testnet') {
      this.server = new StellarSdk.Horizon.Server('https://horizon-testnet.stellar.org');
      this.networkPassphrase = StellarSdk.Networks.TESTNET;
    } else {
      this.server = new StellarSdk.Horizon.Server('https://horizon.stellar.org');
      this.networkPassphrase = StellarSdk.Networks.PUBLIC;
    }
  }

  /**
   * Create Stellar account for new Privy user
   * Called automatically on user registration
   */
  async createAccountForUser(privyUserId: string): Promise<StellarAccount> {
    // Generate new keypair
    const keypair = StellarSdk.Keypair.random();

    // Fund testnet account via Friendbot
    if (this.network === 'testnet') {
      try {
        await fetch(`https://friendbot.stellar.org?addr=${keypair.publicKey()}`);
        console.log('✅ Funded testnet account:', keypair.publicKey());
      } catch (error) {
        console.error('Failed to fund testnet account:', error);
      }
    }

    // Return account details (backend will encrypt and store secret)
    return {
      publicKey: keypair.publicKey(),
      encryptedSecret: keypair.secret(), // Backend encrypts this
    };
  }

  /**
   * Store medical record proof on Stellar
   * Called after IPFS upload completes
   */
  async storeProofOnStellar(
    ipfsHash: string,
    riskScore: number,
    riskLevel: string
  ): Promise<string> {
    try {
      // Call backend API to store proof
      // Backend handles signing with gas wallet
      const response = await fetch('/api/stellar/store-proof', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ipfsHash,
          riskScore,
          riskLevel,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to store proof on Stellar');
      }

      const data = await response.json();
      console.log('✅ Stored proof on Stellar:', data.txHash);
      
      return data.txHash;
    } catch (error) {
      console.error('Error storing proof on Stellar:', error);
      throw error;
    }
  }

  /**
   * Grant doctor access to medical record
   * Patient signs this transaction
   */
  async grantAccess(
    doctorPublicKey: string,
    recordId: string,
    durationHours: number
  ): Promise<string> {
    try {
      // Call backend API to grant access
      // Backend handles patient keypair and signing
      const response = await fetch('/api/stellar/grant-access', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doctorPublicKey,
          recordId,
          durationHours,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to grant access');
      }

      const data = await response.json();
      console.log('✅ Access granted:', data.txHash);
      
      return data.txHash;
    } catch (error) {
      console.error('Error granting access:', error);
      throw error;
    }
  }

  /**
   * Verify doctor has access to patient record
   * Called before showing medical data
   */
  async verifyAccess(
    patientPublicKey: string,
    doctorPublicKey: string,
    recordId: string
  ): Promise<boolean> {
    try {
      const response = await fetch('/api/stellar/verify-access', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientPublicKey,
          doctorPublicKey,
          recordId,
        }),
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      return data.hasAccess;
    } catch (error) {
      console.error('Error verifying access:', error);
      return false;
    }
  }

  /**
   * Pay doctor for consultation
   * Patient signs payment transaction
   */
  async payDoctor(
    doctorPublicKey: string,
    amount: string = '0.5'
  ): Promise<string> {
    try {
      const response = await fetch('/api/stellar/pay-doctor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doctorPublicKey,
          amount,
        }),
      });

      if (!response.ok) {
        throw new Error('Payment failed');
      }

      const data = await response.json();
      console.log('✅ Payment processed:', data.txHash);
      
      return data.txHash;
    } catch (error) {
      console.error('Payment error:', error);
      throw error;
    }
  }

  /**
   * Get record proof from Stellar
   */
  async getRecordProof(
    patientPublicKey: string,
    recordId: string
  ): Promise<RecordProof | null> {
    try {
      const account = await this.server.loadAccount(patientPublicKey);
      
      const ipfsKey = `ipfs_${recordId}`;
      const riskKey = `risk_${recordId}`;
      
      if (account.data_attr[ipfsKey] && account.data_attr[riskKey]) {
        const ipfsHash = Buffer.from(account.data_attr[ipfsKey], 'base64').toString();
        const riskData = Buffer.from(account.data_attr[riskKey], 'base64').toString();
        const [riskScore, riskLevel] = riskData.split(':');
        
        return {
          ipfsHash,
          riskScore: parseInt(riskScore),
          riskLevel,
        };
      }
      
      return null;
    } catch (error) {
      console.error('Error getting record proof:', error);
      return null;
    }
  }

  /**
   * Check account balance
   */
  async getBalance(publicKey: string): Promise<string> {
    try {
      const account = await this.server.loadAccount(publicKey);
      const balance = account.balances.find(
        (b: any) => b.asset_type === 'native'
      );
      return balance ? balance.balance : '0';
    } catch (error) {
      console.error('Error getting balance:', error);
      return '0';
    }
  }

  /**
   * Get transaction history
   */
  async getTransactionHistory(publicKey: string, limit: number = 10) {
    try {
      const transactions = await this.server
        .transactions()
        .forAccount(publicKey)
        .limit(limit)
        .order('desc')
        .call();
      
      return transactions.records;
    } catch (error) {
      console.error('Error getting transaction history:', error);
      return [];
    }
  }

  /**
   * View transaction on Stellar Expert
   */
  getExplorerUrl(txHash: string): string {
    const network = this.network === 'testnet' ? 'testnet' : 'public';
    return `https://stellar.expert/explorer/${network}/tx/${txHash}`;
  }
}

// Export singleton instance
export const stellarService = new StellarService(
  process.env.NEXT_PUBLIC_STELLAR_NETWORK as 'testnet' | 'public' || 'testnet'
);
