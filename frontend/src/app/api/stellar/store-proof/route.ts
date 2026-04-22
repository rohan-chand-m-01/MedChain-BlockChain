/**
 * API Route: Store Proof on Stellar Blockchain
 * 
 * Proxies request to FastAPI backend to store medical record proof on Stellar.
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { ipfs_hash, risk_score, risk_level } = body;

    console.log('Stellar store-proof request:', { ipfs_hash, risk_score, risk_level });

    // Validate required fields
    if (!ipfs_hash) {
      console.error('Missing ipfs_hash in request');
      return NextResponse.json(
        { error: 'Missing ipfs_hash' },
        { status: 400 }
      );
    }

    // Call FastAPI backend
    console.log(`Calling backend: ${BACKEND_URL}/api/stellar/store-proof`);
    const response = await fetch(`${BACKEND_URL}/api/stellar/store-proof`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ipfs_hash,
        risk_score: risk_score || 50,
        risk_level: risk_level || 'MEDIUM',
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch {
        errorData = { detail: errorText };
      }
      throw new Error(errorData.detail || 'Stellar storage failed');
    }

    const data = await response.json();
    console.log('Stellar transaction successful:', data);

    return NextResponse.json({
      success: data.success,
      tx_hash: data.tx_hash,
      message: data.message,
    });
  } catch (error: any) {
    console.error('Stellar storage error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to store proof on Stellar' },
      { status: 500 }
    );
  }
}
