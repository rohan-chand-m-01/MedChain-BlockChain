import { expect } from "chai";
import { ethers } from "hardhat";
import { ConsentRegistry } from "../typechain-types";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { time } from "@nomicfoundation/hardhat-network-helpers";

describe("ConsentRegistry", function () {
    let consentRegistry: ConsentRegistry;
    let patient: SignerWithAddress;
    let clinic: SignerWithAddress;
    let otherClinic: SignerWithAddress;

    const patientId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("patient-123"));
    const consentType = "Blood report access";
    const durationDays = 30;

    beforeEach(async function () {
        [patient, clinic, otherClinic] = await ethers.getSigners();
        
        const ConsentRegistry = await ethers.getContractFactory("ConsentRegistry");
        consentRegistry = await ConsentRegistry.deploy();
        await consentRegistry.deployed();
    });

    describe("grantConsent", function () {
        it("Should grant consent successfully", async function () {
            await expect(
                consentRegistry.grantConsent(
                    patientId,
                    clinic.address,
                    consentType,
                    durationDays
                )
            ).to.emit(consentRegistry, "ConsentGranted");
            
            expect(await consentRegistry.hasConsent(patientId, clinic.address)).to.be.true;
        });

        it("Should set correct expiry time", async function () {
            const tx = await consentRegistry.grantConsent(
                patientId,
                clinic.address,
                consentType,
                durationDays
            );
            
            const receipt = await tx.wait();
            const event = receipt.events?.find(e => e.event === "ConsentGranted");
            const expiresAt = event!.args!.expiresAt;
            
            const currentTime = await time.latest();
            const expectedExpiry = currentTime + (durationDays * 24 * 3600);
            
            expect(expiresAt).to.be.closeTo(expectedExpiry, 5);
        });

        it("Should allow multiple consents for same patient", async function () {
            await consentRegistry.grantConsent(
                patientId,
                clinic.address,
                consentType,
                durationDays
            );
            
            await consentRegistry.grantConsent(
                patientId,
                otherClinic.address,
                "X-ray access",
                durationDays
            );
            
            expect(await consentRegistry.hasConsent(patientId, clinic.address)).to.be.true;
            expect(await consentRegistry.hasConsent(patientId, otherClinic.address)).to.be.true;
        });
    });

    describe("revokeConsent", function () {
        beforeEach(async function () {
            await consentRegistry.grantConsent(
                patientId,
                clinic.address,
                consentType,
                durationDays
            );
        });

        it("Should revoke consent successfully", async function () {
            await expect(
                consentRegistry.revokeConsent(patientId, clinic.address)
            ).to.emit(consentRegistry, "ConsentRevoked");
            
            expect(await consentRegistry.hasConsent(patientId, clinic.address)).to.be.false;
        });

        it("Should handle revoking already revoked consent", async function () {
            await consentRegistry.revokeConsent(patientId, clinic.address);
            
            // Revoking again should not revert
            await expect(
                consentRegistry.revokeConsent(patientId, clinic.address)
            ).to.not.be.reverted;
        });

        it("Should only revoke specific clinic consent", async function () {
            await consentRegistry.grantConsent(
                patientId,
                otherClinic.address,
                "X-ray access",
                durationDays
            );
            
            await consentRegistry.revokeConsent(patientId, clinic.address);
            
            expect(await consentRegistry.hasConsent(patientId, clinic.address)).to.be.false;
            expect(await consentRegistry.hasConsent(patientId, otherClinic.address)).to.be.true;
        });
    });

    describe("hasConsent", function () {
        it("Should return true for active consent", async function () {
            await consentRegistry.grantConsent(
                patientId,
                clinic.address,
                consentType,
                durationDays
            );
            
            expect(await consentRegistry.hasConsent(patientId, clinic.address)).to.be.true;
        });

        it("Should return false for expired consent", async function () {
            await consentRegistry.grantConsent(
                patientId,
                clinic.address,
                consentType,
                1 // 1 day
            );
            
            // Fast forward time by 2 days
            await time.increase(2 * 24 * 3600);
            
            expect(await consentRegistry.hasConsent(patientId, clinic.address)).to.be.false;
        });

        it("Should return false for revoked consent", async function () {
            await consentRegistry.grantConsent(
                patientId,
                clinic.address,
                consentType,
                durationDays
            );
            
            await consentRegistry.revokeConsent(patientId, clinic.address);
            
            expect(await consentRegistry.hasConsent(patientId, clinic.address)).to.be.false;
        });

        it("Should return false for non-existent consent", async function () {
            expect(await consentRegistry.hasConsent(patientId, clinic.address)).to.be.false;
        });
    });

    describe("getPatientConsents", function () {
        it("Should return all consents for a patient", async function () {
            await consentRegistry.grantConsent(
                patientId,
                clinic.address,
                consentType,
                durationDays
            );
            
            await consentRegistry.grantConsent(
                patientId,
                otherClinic.address,
                "X-ray access",
                durationDays
            );
            
            const consents = await consentRegistry.getPatientConsents(patientId);
            expect(consents.length).to.equal(2);
            expect(consents[0].clinic).to.equal(clinic.address);
            expect(consents[1].clinic).to.equal(otherClinic.address);
        });

        it("Should return empty array for patient with no consents", async function () {
            const consents = await consentRegistry.getPatientConsents(patientId);
            expect(consents.length).to.equal(0);
        });
    });
});
