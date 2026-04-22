// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MediChainPayments is ReentrancyGuard {
    
    IERC20 public mediToken;
    
    struct Consultation {
        address patient;
        address doctor;
        uint256 amount;
        bool completed;
        bool refunded;
        uint256 createdAt;
        uint256 expiresAt;
    }
    
    mapping(bytes32 => Consultation) public consultations;
    
    event ConsultationRequested(bytes32 id, address patient, address doctor, uint256 amount);
    event ConsultationCompleted(bytes32 id, uint256 amount);
    event RefundIssued(bytes32 id, address patient, uint256 amount);
    
    constructor(address _mediToken) {
        mediToken = IERC20(_mediToken);
    }
    
    function requestConsultation(
        address doctor,
        uint256 amount,
        uint256 durationHours
    ) external nonReentrant returns (bytes32 id) {
        require(mediToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        id = keccak256(abi.encodePacked(msg.sender, doctor, block.timestamp));
        consultations[id] = Consultation({
            patient: msg.sender,
            doctor: doctor,
            amount: amount,
            completed: false,
            refunded: false,
            createdAt: block.timestamp,
            expiresAt: block.timestamp + (durationHours * 1 hours)
        });
        emit ConsultationRequested(id, msg.sender, doctor, amount);
    }
    
    function completeConsultation(bytes32 id) external nonReentrant {
        Consultation storage c = consultations[id];
        require(msg.sender == c.doctor, "Not doctor");
        require(!c.completed && !c.refunded, "Already settled");
        require(block.timestamp < c.expiresAt, "Expired");
        c.completed = true;
        require(mediToken.transfer(c.doctor, c.amount), "Transfer failed");
        emit ConsultationCompleted(id, c.amount);
    }
    
    function claimRefund(bytes32 id) external nonReentrant {
        Consultation storage c = consultations[id];
        require(msg.sender == c.patient, "Not patient");
        require(!c.completed && !c.refunded, "Already settled");
        require(block.timestamp > c.expiresAt, "Not expired");
        c.refunded = true;
        require(mediToken.transfer(c.patient, c.amount), "Transfer failed");
        emit RefundIssued(id, c.patient, c.amount);
    }
}
