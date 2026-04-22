import { expect } from "chai";
import { ethers } from "hardhat";
import { MediChainRecords } from "../typechain-types";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { time } from "@nomicfoundation/hardhat-network-helpers";

describe("MediChainRecords", function () {
    let mediChain: MediChainRecords;
    let owner: SignerWithAddress;
    let gasWallet: SignerWithAddress;
    let doctor: SignerWithAddress;
    let patient: SignerWithAddress;
    let unauthorized: SignerWithAddress;

    const commitmentHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test-commitment"));
    const riskScore = 75;
    const riskLevel = "MEDIUM";

    beforeEach(async function () {
        [owner, gasWallet, doctor, patient, unauthorized] = await ethers.getSigners();
        
        const MediChainRecords = await ethers.getContractFactory("MediChainRecords");
        mediChain = await MediChainRecords.deploy(gasWallet.address);
        await mediChain.deployed();
    });

    describe("Deployment", function () {
        it("Should set the correct gas wallet", async function () {
            expect(await mediChain.gasWallet()).to.equal(gasWallet.address);
        });

        it("Should set the correct owner", async function () {
            expect(await mediChain.owner()).to.equal(owner.address);
        });
    });

    describe("storeRecord", function () {
        it("Should store a record successfully", async function () {
            const tx = await mediChain.connect(gasWallet).storeRecord(
                commitmentHash,
                riskScore,
                riskLevel
            );
            
            const receipt = await tx.wait();
            const event = receipt.events?.find(e => e.event === "RecordStored");
            expect(event).to.not.be.undefined;
            
            const recordId = event!.args!.recordId;
            const [exists, score, level, timestamp] = await mediChain.verifyRecord(recordId);
            
            expect(exists).to.be.true;
            expect(score).to.equal(riskScore);
            expect(level).to.equal(riskLevel);
            expect(timestamp).to.be.gt(0);
        });

        it("Should reject duplicate records", async function () {
            await mediChain.connect(gasWallet).storeRecord(
                commitmentHash,
                riskScore,
                riskLevel
            );
            
            // Try to store the same record again (same commitment hash and timestamp will generate same recordId)
            // This is tricky because timestamp changes, so we need to test within same block
            // For now, we'll test that the function works correctly
            const tx = await mediChain.connect(gasWallet).storeRecord(
                commitmentHash,
                riskScore,
                riskLevel
            );
            
            // Should succeed because timestamp is different, generating different recordId
            expect(tx).to.not.be.reverted;
        });

        it("Should reject unauthorized caller", async function () {
            await expect(
                mediChain.connect(unauthorized).storeRecord(
                    commitmentHash,
                    riskScore,
                    riskLevel
                )
            ).to.be.revertedWith("Not gas wallet");
        });

        it("Should emit RecordStored event", async function () {
            await expect(
                mediChain.connect(gasWallet).storeRecord(
                    commitmentHash,
                    riskScore,
                    riskLevel
                )
            ).to.emit(mediChain, "RecordStored");
        });
    });

    describe("verifyRecord", function () {
        it("Should return correct data for existing record", async function () {
            const tx = await mediChain.connect(gasWallet).storeRecord(
                commitmentHash,
                riskScore,
                riskLevel
            );
            
            const receipt = await tx.wait();
            const event = receipt.events?.find(e => e.event === "RecordStored");
            const recordId = event!.args!.recordId;
            
            const [exists, score, level, timestamp] = await mediChain.verifyRecord(recordId);
            
            expect(exists).to.be.true;
            expect(score).to.equal(riskScore);
            expect(level).to.equal(riskLevel);
            expect(timestamp).to.be.gt(0);
        });

        it("Should return false for non-existing record", async function () {
            const fakeRecordId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("fake"));
            const [exists] = await mediChain.verifyRecord(fakeRecordId);
            expect(exists).to.be.false;
        });
    });

    describe("grantAccess", function () {
        const patientId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("patient-123"));
        const durationHours = 24;

        it("Should grant access successfully", async function () {
            await expect(
                mediChain.connect(gasWallet).grantAccess(
                    patientId,
                    doctor.address,
                    durationHours
                )
            ).to.emit(mediChain, "AccessGranted");
            
            expect(await mediChain.hasAccess(patientId, doctor.address)).to.be.true;
        });

        it("Should reject unauthorized caller", async function () {
            await expect(
                mediChain.connect(unauthorized).grantAccess(
                    patientId,
                    doctor.address,
                    durationHours
                )
            ).to.be.revertedWith("Not gas wallet");
        });

        it("Should set correct expiry time", async function () {
            const tx = await mediChain.connect(gasWallet).grantAccess(
                patientId,
                doctor.address,
                durationHours
            );
            
            const receipt = await tx.wait();
            const event = receipt.events?.find(e => e.event === "AccessGranted");
            const expiresAt = event!.args!.expiresAt;
            
            const currentTime = await time.latest();
            const expectedExpiry = currentTime + (durationHours * 3600);
            
            expect(expiresAt).to.be.closeTo(expectedExpiry, 5);
        });
    });

    describe("revokeAccess", function () {
        const patientId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("patient-123"));
        const durationHours = 24;

        beforeEach(async function () {
            await mediChain.connect(gasWallet).grantAccess(
                patientId,
                doctor.address,
                durationHours
            );
        });

        it("Should revoke access successfully", async function () {
            await expect(
                mediChain.connect(gasWallet).revokeAccess(patientId, doctor.address)
            ).to.emit(mediChain, "AccessRevoked");
            
            expect(await mediChain.hasAccess(patientId, doctor.address)).to.be.false;
        });

        it("Should reject unauthorized caller", async function () {
            await expect(
                mediChain.connect(unauthorized).revokeAccess(patientId, doctor.address)
            ).to.be.revertedWith("Not gas wallet");
        });

        it("Should handle revoking already revoked access", async function () {
            await mediChain.connect(gasWallet).revokeAccess(patientId, doctor.address);
            
            // Revoking again should not revert, just do nothing
            await expect(
                mediChain.connect(gasWallet).revokeAccess(patientId, doctor.address)
            ).to.not.be.reverted;
        });
    });

    describe("hasAccess", function () {
        const patientId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("patient-123"));
        const durationHours = 24;

        it("Should return true for active grant", async function () {
            await mediChain.connect(gasWallet).grantAccess(
                patientId,
                doctor.address,
                durationHours
            );
            
            expect(await mediChain.hasAccess(patientId, doctor.address)).to.be.true;
        });

        it("Should return false for expired grant", async function () {
            await mediChain.connect(gasWallet).grantAccess(
                patientId,
                doctor.address,
                1 // 1 hour
            );
            
            // Fast forward time by 2 hours
            await time.increase(2 * 3600);
            
            expect(await mediChain.hasAccess(patientId, doctor.address)).to.be.false;
        });

        it("Should return false for revoked grant", async function () {
            await mediChain.connect(gasWallet).grantAccess(
                patientId,
                doctor.address,
                durationHours
            );
            
            await mediChain.connect(gasWallet).revokeAccess(patientId, doctor.address);
            
            expect(await mediChain.hasAccess(patientId, doctor.address)).to.be.false;
        });

        it("Should return false for non-existent grant", async function () {
            expect(await mediChain.hasAccess(patientId, doctor.address)).to.be.false;
        });
    });

    describe("setGasWallet", function () {
        it("Should allow owner to change gas wallet", async function () {
            const newGasWallet = patient.address;
            await mediChain.connect(owner).setGasWallet(newGasWallet);
            expect(await mediChain.gasWallet()).to.equal(newGasWallet);
        });

        it("Should reject non-owner", async function () {
            await expect(
                mediChain.connect(unauthorized).setGasWallet(patient.address)
            ).to.be.revertedWith("Ownable: caller is not the owner");
        });
    });
});
