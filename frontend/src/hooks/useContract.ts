'use client';

import { useCallback } from 'react';
import { Contract, parseEther } from 'ethers';
import { useWallet } from './useWallet';
import { MEDICHAIN_ABI, CONTRACT_ADDRESS } from '@/lib/contract';

export function useContract() {
    const { signer, address, provider } = useWallet();

    const getContract = useCallback(() => {
        if (!signer) throw new Error('Please connect your MetaMask wallet first.');
        try {
            return new Contract(CONTRACT_ADDRESS, MEDICHAIN_ABI, signer);
        } catch (err: any) {
            throw new Error('Unable to connect to the blockchain. Please check your network in MetaMask.');
        }
    }, [signer]);

    const registerUser = useCallback(async (role: 1 | 2) => {
        const contract = getContract();
        const tx = await contract.registerUser(role);
        await tx.wait();
        return tx;
    }, [getContract]);

    const storeRecord = useCallback(async (recordHash: string, metadataCID: string) => {
        const contract = getContract();
        const tx = await contract.storeRecord(recordHash, metadataCID);
        const receipt = await tx.wait();

        let recordId: number | undefined;
        if (receipt && receipt.logs) {
            for (const log of receipt.logs) {
                try {
                    const parsedLog = contract.interface.parseLog(log);
                    if (parsedLog && parsedLog.name === 'RecordStored') {
                        recordId = Number(parsedLog.args.recordId);
                        break;
                    }
                } catch (e) {
                    // Ignore logs that don't match our ABI
                }
            }
        }

        return { tx, receipt, recordId };
    }, [getContract]);

    const grantAccess = useCallback(async (doctorAddress: string, recordId: number) => {
        const contract = getContract();
        const tx = await contract.grantAccess(doctorAddress, recordId);
        await tx.wait();
        return tx;
    }, [getContract]);

    const revokeAccess = useCallback(async (doctorAddress: string, recordId: number) => {
        const contract = getContract();
        const tx = await contract.revokeAccess(doctorAddress, recordId);
        await tx.wait();
        return tx;
    }, [getContract]);

    const hasAccess = useCallback(async (doctorAddress: string, recordId: number): Promise<boolean> => {
        const contract = getContract();
        return await contract.hasAccess(doctorAddress, recordId);
    }, [getContract]);

    const getUserRole = useCallback(async (userAddress?: string): Promise<number> => {
        const contract = getContract();
        return Number(await contract.getUserRole(userAddress || address));
    }, [getContract, address]);

    const getRecord = useCallback(async (recordId: number) => {
        const contract = getContract();
        const [recordHash, metadataCID, patient, timestamp] = await contract.getRecord(recordId);
        return { recordHash, metadataCID, patient, timestamp: Number(timestamp) };
    }, [getContract]);

    const payDoctor = useCallback(async (doctorAddress: string, amountInEth: string) => {
        const contract = getContract();
        const tx = await contract.payDoctor(doctorAddress, {
            value: parseEther(amountInEth),
        });
        const receipt = await tx.wait();
        return { tx, receipt };
    }, [getContract]);

    const getPaymentEvents = useCallback(async (filterType: 'patient' | 'doctor', walletAddress: string) => {
        if (!provider) return [];
        const contract = new Contract(CONTRACT_ADDRESS, MEDICHAIN_ABI, provider);
        try {
            // Fetch all events and filter client-side to avoid issues with `null` indexed filters in ethers v6
            const filter = contract.filters.DoctorPaid();
            const events = await contract.queryFilter(filter);
            
            const lowerWallet = walletAddress.toLowerCase();
            
            const mappedEvents = events.map((e: any) => ({
                patient: e.args.patient,
                doctor: e.args.doctor,
                amount: e.args.amount,
                timestamp: Number(e.args.timestamp),
                txHash: e.transactionHash,
            }));

            return mappedEvents.filter((ev: any) => 
                filterType === 'patient' 
                    ? ev.patient.toLowerCase() === lowerWallet 
                    : ev.doctor.toLowerCase() === lowerWallet
            );
        } catch (err) {
            console.error('Failed to query payment events:', err);
            return [];
        }
    }, [provider]);

    return {
        registerUser,
        storeRecord,
        grantAccess,
        revokeAccess,
        hasAccess,
        getUserRole,
        getRecord,
        payDoctor,
        getPaymentEvents,
    };
}

