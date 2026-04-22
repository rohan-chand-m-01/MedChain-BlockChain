import { expect } from "chai";
import { ethers } from "hardhat";
import { MediChainPayments, MediToken } from "../typechain-types";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { time } from "@nomicfoundation/hardhat-network-helpers";

describe("MediChainPayments", function () {
    let payments: MediChainPayments;
    let mediToken: MediToken;
    let owner: SignerWithAddress;
    let patient: SignerWithAddress;
    let doctor: SignerWithAddress;

    const consultationAmount = ethers.utils.parseEther("100");
    const durationHours = 24;

    beforeEach(async function () {
        [owner, patient, doctor] = await ethers.getSigners();
        
        // Deploy MediToken
        const MediToken = await ethers.getContractFactory("MediToken");
        mediToken = await MediToken.deploy();
        await mediToken.deployed();
        
        // Deploy MediChainPayments
        const MediChainPayments = await ethers.getContractFactory("MediChainPayments");
        payments = await MediChainPayments.deploy(mediToken.address);
        await payments.deployed();
        
        // Transfer tokens to patient
        await mediToken.transfer(patient.address, ethers.utils.parseEther("1000"));
        
        // Approve payments contract to spend patient's tokens
        await mediToken.connect(patient).approve(payments.address, ethers.utils.parseEther("10000"));
    });

    describe("Deployment", function () {
        it("Should set the correct MediToken address", async function () {
            expect(await payments.mediToken()).to.equal(mediToken.address);
        });
    });

    describe("requestConsultation", function () {
        it("Should create consultation successfully", async function () {
            const tx = await payments.connect(patient).requestConsultation(
                doctor.address,
                consultationAmount,
                durationHours
            );
            
            const receipt = await tx.wait();
            const event = receipt.events?.find(e => e.event === "ConsultationRequested");
            expect(event).to.not.be.undefined;
            
            const consultationId = event!.args!.id;
            const consultation = await payments.consultations(consultationId);
            
            expect(consultation.patient).to.equal(patient.address);
            expect(consultation.doctor).to.equal(doctor.address);
            expect(consultation.amount).to.equal(consultationAmount);
            expect(consultation.completed).to.be.false;
            expect(consultation.refunded).to.be.false;
        });

        it("Should transfer tokens to contract", async function () {
            const balanceBefore = await mediToken.balanceOf(payments.address);
            
            await payments.connect(patient).requestConsultation(
                doctor.address,
                consultationAmount,
                durationHours
            );
            
            const balanceAfter = await mediToken.balanceOf(payments.address);
            expect(balanceAfter.sub(balanceBefore)).to.equal(consultationAmount);
        });

        it("Should emit ConsultationRequested event", async function () {
            await expect(
                payments.connect(patient).requestConsultation(
                    doctor.address,
                    consultationAmount,
                    durationHours
                )
            ).to.emit(payments, "ConsultationRequested");
        });

        it("Should fail if insufficient allowance", async function () {
            await mediToken.connect(patient).approve(payments.address, 0);
            
            await expect(
                payments.connect(patient).requestConsultation(
                    doctor.address,
                    consultationAmount,
                    durationHours
                )
            ).to.be.reverted;
        });
    });

    describe("completeConsultation", function () {
        let consultationId: string;

        beforeEach(async function () {
            const tx = await payments.connect(patient).requestConsultation(
                doctor.address,
                consultationAmount,
                durationHours
            );
            const receipt = await tx.wait();
            const event = receipt.events?.find(e => e.event === "ConsultationRequested");
            consultationId = event!.args!.id;
        });

        it("Should complete consultation successfully", async function () {
            const doctorBalanceBefore = await mediToken.balanceOf(doctor.address);
            
            await payments.connect(doctor).completeConsultation(consultationId);
            
            const doctorBalanceAfter = await mediToken.balanceOf(doctor.address);
            expect(doctorBalanceAfter.sub(doctorBalanceBefore)).to.equal(consultationAmount);
            
            const consultation = await payments.consultations(consultationId);
            expect(consultation.completed).to.be.true;
        });

        it("Should reject non-doctor caller", async function () {
            await expect(
                payments.connect(patient).completeConsultation(consultationId)
            ).to.be.revertedWith("Not doctor");
        });

        it("Should reject if already completed", async function () {
            await payments.connect(doctor).completeConsultation(consultationId);
            
            await expect(
                payments.connect(doctor).completeConsultation(consultationId)
            ).to.be.revertedWith("Already settled");
        });

        it("Should reject if expired", async function () {
            // Fast forward time beyond expiry
            await time.increase((durationHours + 1) * 3600);
            
            await expect(
                payments.connect(doctor).completeConsultation(consultationId)
            ).to.be.revertedWith("Expired");
        });

        it("Should emit ConsultationCompleted event", async function () {
            await expect(
                payments.connect(doctor).completeConsultation(consultationId)
            ).to.emit(payments, "ConsultationCompleted");
        });
    });

    describe("claimRefund", function () {
        let consultationId: string;

        beforeEach(async function () {
            const tx = await payments.connect(patient).requestConsultation(
                doctor.address,
                consultationAmount,
                durationHours
            );
            const receipt = await tx.wait();
            const event = receipt.events?.find(e => e.event === "ConsultationRequested");
            consultationId = event!.args!.id;
        });

        it("Should refund successfully after expiry", async function () {
            // Fast forward time beyond expiry
            await time.increase((durationHours + 1) * 3600);
            
            const patientBalanceBefore = await mediToken.balanceOf(patient.address);
            
            await payments.connect(patient).claimRefund(consultationId);
            
            const patientBalanceAfter = await mediToken.balanceOf(patient.address);
            expect(patientBalanceAfter.sub(patientBalanceBefore)).to.equal(consultationAmount);
            
            const consultation = await payments.consultations(consultationId);
            expect(consultation.refunded).to.be.true;
        });

        it("Should reject non-patient caller", async function () {
            await time.increase((durationHours + 1) * 3600);
            
            await expect(
                payments.connect(doctor).claimRefund(consultationId)
            ).to.be.revertedWith("Not patient");
        });

        it("Should reject if not expired yet", async function () {
            await expect(
                payments.connect(patient).claimRefund(consultationId)
            ).to.be.revertedWith("Not expired");
        });

        it("Should reject if already completed", async function () {
            await payments.connect(doctor).completeConsultation(consultationId);
            
            await time.increase((durationHours + 1) * 3600);
            
            await expect(
                payments.connect(patient).claimRefund(consultationId)
            ).to.be.revertedWith("Already settled");
        });

        it("Should emit RefundIssued event", async function () {
            await time.increase((durationHours + 1) * 3600);
            
            await expect(
                payments.connect(patient).claimRefund(consultationId)
            ).to.emit(payments, "RefundIssued");
        });
    });
});
