// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract ConsentRegistry is ReentrancyGuard {
    
    struct Consent {
        bytes32 patientId;
        address clinic;
        string consentType;
        uint256 grantedAt;
        uint256 expiresAt;
        bool revoked;
    }
    
    mapping(bytes32 => Consent[]) public patientConsents;
    
    event ConsentGranted(bytes32 indexed patientId, address indexed clinic, string consentType, uint256 expiresAt);
    event ConsentRevoked(bytes32 indexed patientId, address indexed clinic, uint256 revokedAt);
    
    function grantConsent(
        bytes32 patientId,
        address clinic,
        string calldata consentType,
        uint256 durationDays
    ) external nonReentrant {
        patientConsents[patientId].push(Consent({
            patientId: patientId,
            clinic: clinic,
            consentType: consentType,
            grantedAt: block.timestamp,
            expiresAt: block.timestamp + (durationDays * 1 days),
            revoked: false
        }));
        emit ConsentGranted(patientId, clinic, consentType, block.timestamp + (durationDays * 1 days));
    }
    
    function revokeConsent(bytes32 patientId, address clinic)
        external nonReentrant
    {
        Consent[] storage consents = patientConsents[patientId];
        for (uint i = 0; i < consents.length; i++) {
            if (consents[i].clinic == clinic && !consents[i].revoked) {
                consents[i].revoked = true;
                emit ConsentRevoked(patientId, clinic, block.timestamp);
            }
        }
    }
    
    function hasConsent(bytes32 patientId, address clinic)
        external view returns (bool)
    {
        Consent[] memory consents = patientConsents[patientId];
        for (uint i = 0; i < consents.length; i++) {
            if (
                consents[i].clinic == clinic &&
                !consents[i].revoked &&
                block.timestamp < consents[i].expiresAt
            ) {
                return true;
            }
        }
        return false;
    }
    
    function getPatientConsents(bytes32 patientId)
        external view returns (Consent[] memory)
    {
        return patientConsents[patientId];
    }
}
