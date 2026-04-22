// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MediChainRecords is ReentrancyGuard, Ownable(msg.sender) {
    
    struct MedicalRecord {
        bytes32 commitmentHash;  // keccak256(cid+score+timestamp+patientId)
        uint256 riskScore;       // Readable by anyone — insurer can verify
        string riskLevel;        // HIGH / MEDIUM / LOW
        uint256 timestamp;
        bool exists;
    }
    
    struct AccessGrant {
        address doctor;
        uint256 grantedAt;
        uint256 expiresAt;
        bool revoked;
    }
    
    mapping(bytes32 => MedicalRecord) public records;
    mapping(bytes32 => AccessGrant[]) public accessGrants;
    
    // Gas wallet — low balance, rotated regularly
    address public gasWallet;
    uint256 public constant MAX_GAS_WALLET_BALANCE = 0.05 ether;
    
    event RecordStored(
        bytes32 indexed recordId,
        uint256 riskScore,
        string riskLevel,
        uint256 timestamp
    );
    
    event AccessGranted(
        bytes32 indexed patientId,
        address indexed doctor,
        uint256 expiresAt
    );
    
    event AccessRevoked(
        bytes32 indexed patientId,
        address indexed doctor,
        uint256 revokedAt
    );
    
    modifier onlyGasWallet() {
        require(msg.sender == gasWallet, "Not gas wallet");
        _;
    }
    
    constructor(address _gasWallet) {
        gasWallet = _gasWallet;
    }
    
    function setGasWallet(address _newGasWallet) external onlyOwner {
        gasWallet = _newGasWallet;
    }
    
    function storeRecord(
        bytes32 commitmentHash,
        uint256 riskScore,
        string calldata riskLevel
    ) external onlyGasWallet nonReentrant returns (bytes32 recordId) {
        recordId = keccak256(
            abi.encodePacked(commitmentHash, block.timestamp, msg.sender)
        );
        require(!records[recordId].exists, "Record exists");
        records[recordId] = MedicalRecord({
            commitmentHash: commitmentHash,
            riskScore: riskScore,
            riskLevel: riskLevel,
            timestamp: block.timestamp,
            exists: true
        });
        emit RecordStored(recordId, riskScore, riskLevel, block.timestamp);
    }
    
    function verifyRecord(bytes32 recordId)
        external view
        returns (bool exists, uint256 riskScore, string memory riskLevel, uint256 timestamp)
    {
        MedicalRecord memory r = records[recordId];
        return (r.exists, r.riskScore, r.riskLevel, r.timestamp);
    }
    
    function grantAccess(
        bytes32 patientId,
        address doctor,
        uint256 durationHours
    ) external onlyGasWallet nonReentrant {
        accessGrants[patientId].push(AccessGrant({
            doctor: doctor,
            grantedAt: block.timestamp,
            expiresAt: block.timestamp + (durationHours * 1 hours),
            revoked: false
        }));
        emit AccessGranted(patientId, doctor, block.timestamp + (durationHours * 1 hours));
    }
    
    function revokeAccess(bytes32 patientId, address doctor)
        external onlyGasWallet nonReentrant
    {
        AccessGrant[] storage grants = accessGrants[patientId];
        for (uint i = 0; i < grants.length; i++) {
            if (grants[i].doctor == doctor && !grants[i].revoked) {
                grants[i].revoked = true;
                emit AccessRevoked(patientId, doctor, block.timestamp);
            }
        }
    }
    
    function hasAccess(bytes32 patientId, address doctor)
        external view returns (bool)
    {
        AccessGrant[] memory grants = accessGrants[patientId];
        for (uint i = 0; i < grants.length; i++) {
            if (
                grants[i].doctor == doctor &&
                !grants[i].revoked &&
                block.timestamp < grants[i].expiresAt
            ) {
                return true;
            }
        }
        return false;
    }
}
