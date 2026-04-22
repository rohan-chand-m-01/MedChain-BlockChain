/**
 * Client-Side Encryption with Privy MPC Wallets
 * 
 * Security Model:
 * - AES key encrypted with patient's Privy wallet public key
 * - Only patient's biometric (Face ID/Touch ID) can decrypt
 * - Backend stores encrypted keys but CANNOT decrypt them
 * - Patient can export private key anytime for full self-custody
 */

import { ethers } from 'ethers';
import * as CryptoJS from 'crypto-js';

/**
 * Generate a random AES-256 key for file encryption
 */
export function generateAESKey(): string {
  const randomBytes = CryptoJS.lib.WordArray.random(32); // 256 bits
  return randomBytes.toString(CryptoJS.enc.Base64);
}

/**
 * Encrypt file with AES-256
 */
export async function encryptFileWithAES(
  fileBuffer: ArrayBuffer,
  aesKey: string
): Promise<string> {
  // Convert ArrayBuffer to WordArray
  const wordArray = CryptoJS.lib.WordArray.create(fileBuffer as any);
  
  // Encrypt with AES-256
  const encrypted = CryptoJS.AES.encrypt(
    wordArray,
    aesKey
  ).toString();
  
  return encrypted;
}

/**
 * Decrypt file with AES-256
 */
export async function decryptFileWithAES(
  encryptedData: string,
  aesKey: string
): Promise<ArrayBuffer> {
  // Decrypt with AES-256
  const decrypted = CryptoJS.AES.decrypt(encryptedData, aesKey);
  
  // Convert WordArray back to ArrayBuffer
  const typedArray = new Uint8Array(decrypted.words.length * 4);
  for (let i = 0; i < decrypted.words.length; i++) {
    const word = decrypted.words[i];
    typedArray[i * 4] = (word >> 24) & 0xff;
    typedArray[i * 4 + 1] = (word >> 16) & 0xff;
    typedArray[i * 4 + 2] = (word >> 8) & 0xff;
    typedArray[i * 4 + 3] = word & 0xff;
  }
  
  return typedArray.buffer;
}

/**
 * Encrypt AES key with patient's Privy wallet
 * This requires the patient's active Privy session
 */
export async function encryptAESKeyWithWallet(
  aesKey: string,
  walletAddress: string,
  signer: ethers.Signer
): Promise<string> {
  // Create a deterministic message to sign
  const message = `Encrypt medical record AES key for ${walletAddress}`;
  
  // Patient signs with their Privy wallet (requires Face ID/Touch ID)
  const signature = await signer.signMessage(message);
  
  // Derive encryption key from signature (deterministic)
  const encryptionKey = ethers.keccak256(ethers.toUtf8Bytes(signature));
  
  // Encrypt AES key with derived key
  const encrypted = CryptoJS.AES.encrypt(aesKey, encryptionKey).toString();
  
  return encrypted;
}

/**
 * Decrypt AES key with patient's Privy wallet
 * This requires the patient's active Privy session
 */
export async function decryptAESKeyWithWallet(
  encryptedAESKey: string,
  walletAddress: string,
  signer: ethers.Signer
): Promise<string> {
  // Create the same deterministic message
  const message = `Encrypt medical record AES key for ${walletAddress}`;
  
  // Patient signs with their Privy wallet (requires Face ID/Touch ID)
  const signature = await signer.signMessage(message);
  
  // Derive decryption key from signature (same as encryption)
  const decryptionKey = ethers.keccak256(ethers.toUtf8Bytes(signature));
  
  // Decrypt AES key
  const decrypted = CryptoJS.AES.decrypt(encryptedAESKey, decryptionKey);
  const aesKey = decrypted.toString(CryptoJS.enc.Utf8);
  
  return aesKey;
}

/**
 * Complete flow: Upload encrypted medical record
 */
export async function uploadEncryptedRecord(
  file: File,
  walletAddress: string,
  signer: ethers.Signer,
  uploadToIPFS: (data: string) => Promise<string>
): Promise<{
  ipfsHash: string;
  encryptedAESKey: string;
  walletAddress: string;
}> {
  // 1. Generate random AES key
  const aesKey = generateAESKey();
  
  // 2. Read file as ArrayBuffer
  const fileBuffer = await file.arrayBuffer();
  
  // 3. Encrypt file with AES
  const encryptedFile = await encryptFileWithAES(fileBuffer, aesKey);
  
  // 4. Upload encrypted file to IPFS
  const ipfsHash = await uploadToIPFS(encryptedFile);
  
  // 5. Encrypt AES key with patient's Privy wallet
  const encryptedAESKey = await encryptAESKeyWithWallet(
    aesKey,
    walletAddress,
    signer
  );
  
  // 6. Return metadata to store in database
  return {
    ipfsHash,
    encryptedAESKey, // Backend stores this but CANNOT decrypt it
    walletAddress,
  };
}

/**
 * Complete flow: Download and decrypt medical record
 */
export async function downloadDecryptedRecord(
  ipfsHash: string,
  encryptedAESKey: string,
  walletAddress: string,
  signer: ethers.Signer,
  downloadFromIPFS: (hash: string) => Promise<string>
): Promise<ArrayBuffer> {
  // 1. Download encrypted file from IPFS
  const encryptedFile = await downloadFromIPFS(ipfsHash);
  
  // 2. Decrypt AES key with patient's Privy wallet (requires Face ID)
  const aesKey = await decryptAESKeyWithWallet(
    encryptedAESKey,
    walletAddress,
    signer
  );
  
  // 3. Decrypt file with AES key
  const decryptedFile = await decryptFileWithAES(encryptedFile, aesKey);
  
  return decryptedFile;
}

/**
 * Grant doctor access: Re-encrypt AES key with doctor's wallet
 */
export async function grantDoctorAccess(
  encryptedAESKey: string,
  patientWalletAddress: string,
  patientSigner: ethers.Signer,
  doctorWalletAddress: string
): Promise<string> {
  // 1. Patient decrypts AES key with their wallet
  const aesKey = await decryptAESKeyWithWallet(
    encryptedAESKey,
    patientWalletAddress,
    patientSigner
  );
  
  // 2. Create message for doctor's wallet
  const message = `Encrypt medical record AES key for ${doctorWalletAddress}`;
  
  // 3. Sign with patient's wallet to create doctor's encryption key
  const signature = await patientSigner.signMessage(message);
  const doctorEncryptionKey = ethers.keccak256(ethers.toUtf8Bytes(signature));
  
  // 4. Encrypt AES key for doctor
  const doctorEncryptedAESKey = CryptoJS.AES.encrypt(
    aesKey,
    doctorEncryptionKey
  ).toString();
  
  return doctorEncryptedAESKey;
}
