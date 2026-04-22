/**
 * API Route: Upload Encrypted Lab Report
 * 
 * Uses InsForge SDK to store encrypted report metadata.
 * Encrypted data stored in InsForge database (not IPFS for simplicity).
 * 
 * Note: Backend never sees plaintext - only encrypted data!
 */

import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@insforge/sdk';

const client = createClient({
  baseUrl: process.env.NEXT_PUBLIC_INSFORGE_BASE_URL!,
  anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY!,
});

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { encryptedData, iv, patientId, reportType, timestamp } = body;

    // Validate required fields
    if (!encryptedData || !iv || !patientId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Store encrypted report in InsForge database
    const { data, error } = await client.database
      .from('encrypted_reports')
      .insert([{
        patient_id: patientId,
        ipfs_hash: encryptedData, // Store encrypted data directly
        iv,
        report_type: reportType,
        timestamp,
      }])
      .select();

    if (error) {
      throw new Error(error.message);
    }

    // Return data needed for Stellar blockchain proof
    return NextResponse.json({
      success: true,
      reportId: data[0].id,
      ipfsHash: encryptedData, // Return encrypted data hash for Stellar
      txHash: data[0].id, // Use report ID as transaction reference
      riskScore: 50, // Default risk score
      riskLevel: 'MEDIUM', // Default risk level
      message: 'Report encrypted and uploaded successfully',
    });
  } catch (error: any) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: error.message || 'Upload failed' },
      { status: 500 }
    );
  }
}
