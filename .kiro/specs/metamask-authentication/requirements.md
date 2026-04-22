# Requirements Document: MetaMask Authentication Integration

## 1. Functional Requirements

### 1.1 Landing Page Authentication Options

The landing page HeroSection SHALL provide dual authentication options allowing users to choose between Clerk (email/password) and MetaMask (Web3 wallet) authentication methods.

**Acceptance Criteria:**
- 1.1.1 The HeroSection displays a "Connect MetaMask" button alongside existing Clerk sign-in buttons
- 1.1.2 The MetaMask button uses the existing MetaMaskButton component with appropriate styling
- 1.1.3 Clicking the MetaMask button initiates wallet connection flow
- 1.1.4 Successful MetaMask connection redirects user to role selection page (/register?role=patient or /register?role=doctor)
- 1.1.5 The UI clearly distinguishes between the two authentication methods
- 1.1.6 Both authentication methods are equally prominent in the UI

### 1.2 MetaMask Authentication Flow

The system SHALL support complete MetaMask wallet authentication as an alternative to Clerk authentication.

**Acceptance Criteria:**
- 1.2.1 User can connect MetaMask wallet from landing page
- 1.2.2 System validates wallet connection and retrieves wallet address
- 1.2.3 Wallet address is stored as userId in AuthContext
- 1.2.4 authMethod is set to 'metamask' in AuthContext
- 1.2.5 Authentication preference is persisted in localStorage
- 1.2.6 User is redirected to appropriate dashboard after successful connection
- 1.2.7 System handles MetaMask connection errors gracefully

### 1.3 Unified Authentication Context

The patient and doctor dashboards SHALL use the unified AuthContext instead of Clerk-specific authentication hooks.

**Acceptance Criteria:**
- 1.3.1 Patient dashboard imports and uses `useAuth()` from '@/contexts/AuthContext'
- 1.3.2 Doctor dashboard imports and uses `useAuth()` from '@/contexts/AuthContext'
- 1.3.3 Dashboards retrieve userId from AuthContext (works for both Clerk ID and wallet address)
- 1.3.4 Dashboards retrieve authMethod from AuthContext
- 1.3.5 Dashboards check isAuthenticated from AuthContext before rendering
- 1.3.6 Unauthenticated users are redirected to landing page
- 1.3.7 Existing Clerk authentication continues to work without breaking changes

### 1.4 API Integration with Auth Method

All API calls from dashboards SHALL include the authentication method and use the correct user identifier.

**Acceptance Criteria:**
- 1.4.1 API calls pass userId as patient_wallet or doctor_wallet parameter
- 1.4.2 API calls include authMethod parameter ('clerk' or 'metamask')
- 1.4.3 When authMethod is 'metamask', userId is the wallet address
- 1.4.4 When authMethod is 'clerk', userId is the Clerk user ID
- 1.4.5 Backend endpoints accept both Clerk IDs and wallet addresses
- 1.4.6 API responses are correctly processed regardless of auth method

### 1.5 Blockchain Features Enablement

Blockchain features SHALL be enabled when user authenticates via MetaMask.

**Acceptance Criteria:**
- 1.5.1 When authMethod is 'metamask', blockchain features are enabled
- 1.5.2 When authMethod is 'clerk', blockchain features show disabled state
- 1.5.3 BlockchainFeatureDisabled component is shown for Clerk users
- 1.5.4 MetaMask users can access full blockchain functionality (IPFS upload, on-chain storage)
- 1.5.5 Blockchain transaction signing uses connected wallet
- 1.5.6 System validates wallet connection before blockchain operations

### 1.6 Authentication Method Indicator

The dashboards SHALL display a visual indicator showing which authentication method is active.

**Acceptance Criteria:**
- 1.6.1 A new AuthMethodIndicator component is created
- 1.6.2 The indicator displays "Clerk" badge when authMethod is 'clerk'
- 1.6.3 The indicator displays "MetaMask" badge when authMethod is 'metamask'
- 1.6.4 The indicator shows the user identifier (Clerk ID or wallet address)
- 1.6.5 Wallet addresses are truncated for display (e.g., 0x1234...5678)
- 1.6.6 The indicator is prominently placed in dashboard header or sidebar
- 1.6.7 The indicator uses distinct styling for each auth method

### 1.7 Role-Based Access Control

The system SHALL maintain role-based access control (patient/doctor) regardless of authentication method.

**Acceptance Criteria:**
- 1.7.1 Users can select patient or doctor role after MetaMask connection
- 1.7.2 Role selection works identically for both Clerk and MetaMask auth
- 1.7.3 Patient dashboard is accessible only to users with patient role
- 1.7.4 Doctor dashboard is accessible only to users with doctor role
- 1.7.5 Role information is stored and retrieved correctly for MetaMask users
- 1.7.6 Users without roles are redirected to role selection page

## 2. Non-Functional Requirements

### 2.1 Performance

**2.1.1** MetaMask connection SHALL complete within 5 seconds under normal network conditions

**2.1.2** Dashboard loading with MetaMask auth SHALL have similar performance to Clerk auth (within 10% difference)

**2.1.3** Auth method switching SHALL update UI within 1 second

**2.1.4** Wallet address validation SHALL complete in less than 100ms

### 2.2 Security

**2.2.1** The system SHALL never store or request private keys from users

**2.2.2** Wallet addresses SHALL be validated using Ethereum address format regex before use

**2.2.3** Authentication state SHALL be cleared on logout/disconnect

**2.2.4** MetaMask authentication SHALL only work over HTTPS in production

**2.2.5** Backend SHALL validate that authMethod matches the request source

**2.2.6** Session tokens SHALL be invalidated when user switches auth methods

### 2.3 Usability

**2.3.1** Error messages SHALL be clear and actionable for users

**2.3.2** MetaMask not installed error SHALL include link to download page

**2.3.3** Network mismatch error SHALL guide user to switch networks

**2.3.4** Loading states SHALL be shown during wallet connection

**2.3.5** Success feedback SHALL be provided after successful authentication

**2.3.6** The UI SHALL clearly indicate which auth method is currently active

### 2.4 Compatibility

**2.4.1** The system SHALL support MetaMask browser extension on Chrome, Firefox, Brave, and Edge

**2.4.2** The system SHALL work with MetaMask mobile browser

**2.4.3** The system SHALL maintain backward compatibility with existing Clerk authentication

**2.4.4** The system SHALL support Ethereum Sepolia testnet and Hardhat local network

**2.4.5** The system SHALL gracefully degrade if MetaMask is not available

### 2.5 Maintainability

**2.5.1** Authentication logic SHALL be centralized in AuthContext

**2.5.2** Components SHALL use the unified useAuth() hook consistently

**2.5.3** Auth method switching logic SHALL be reusable across components

**2.5.4** Code SHALL follow existing TypeScript and React best practices

**2.5.5** Components SHALL have clear separation of concerns

### 2.6 Reliability

**2.6.1** The system SHALL handle MetaMask connection failures gracefully without crashing

**2.6.2** The system SHALL recover from wallet disconnection during active session

**2.6.3** Authentication state SHALL persist across page refreshes using localStorage

**2.6.4** The system SHALL handle network switching in MetaMask

**2.6.5** API calls SHALL retry with exponential backoff on failure

## 3. Technical Requirements

### 3.1 Frontend Components

**3.1.1** Update `frontend/src/components/landing/HeroSection.tsx` to include MetaMask authentication option

**3.1.2** Create `frontend/src/components/AuthMethodIndicator.tsx` component

**3.1.3** Update `frontend/src/app/patient/page.tsx` to use unified AuthContext

**3.1.4** Update `frontend/src/app/doctor/page.tsx` to use unified AuthContext

**3.1.5** Ensure all dashboard sub-components use unified auth

### 3.2 Authentication Context

**3.2.1** The existing `frontend/src/contexts/AuthContext.tsx` SHALL be used without modifications

**3.2.2** Components SHALL import `useAuth` from '@/contexts/AuthContext' instead of '@clerk/nextjs'

**3.2.3** AuthContext SHALL provide userId, authMethod, isAuthenticated, walletAddress, and clerkUser

### 3.3 API Integration

**3.3.1** Update `frontend/src/lib/api.ts` functions to accept authMethod parameter

**3.3.2** API functions SHALL pass authMethod in request payload or headers

**3.3.3** Backend endpoints SHALL be updated to handle both Clerk IDs and wallet addresses

**3.3.4** Backend SHALL validate authMethod matches the provided userId format

### 3.4 Blockchain Integration

**3.4.1** Blockchain operations SHALL use wallet from useWallet() hook when authMethod is 'metamask'

**3.4.2** IPFS uploads SHALL be enabled only for MetaMask authenticated users

**3.4.3** Smart contract interactions SHALL use connected wallet signer

**3.4.4** Transaction signing SHALL prompt MetaMask for user approval

### 3.5 State Management

**3.5.1** Authentication preference SHALL be stored in localStorage with key 'authMethod'

**3.5.2** AuthContext SHALL read localStorage on initialization

**3.5.3** Auth state SHALL be cleared from localStorage on logout

**3.5.4** Wallet disconnection SHALL clear MetaMask auth state

### 3.6 Error Handling

**3.6.1** MetaMask not installed error SHALL display with download link

**3.6.2** User rejection of connection SHALL display retry option

**3.6.3** Network mismatch SHALL display network switching instructions

**3.6.4** API errors SHALL be caught and displayed to user

**3.6.5** Wallet disconnection during session SHALL redirect to landing page

## 4. Constraints

### 4.1 Technical Constraints

**4.1.1** Must use existing AuthContext implementation without breaking changes

**4.1.2** Must maintain compatibility with existing Clerk authentication

**4.1.3** Must use ethers.js v6 for Web3 interactions

**4.1.4** Must work with Next.js 14 App Router

**4.1.5** Must support TypeScript strict mode

### 4.2 Business Constraints

**4.2.1** Cannot remove or disable existing Clerk authentication

**4.2.2** Must provide equal user experience for both auth methods

**4.2.3** Must not require users to have both Clerk account and MetaMask wallet

**4.2.4** Must allow users to choose their preferred authentication method

### 4.3 Security Constraints

**4.3.1** Cannot store private keys or seed phrases

**4.3.2** Cannot bypass MetaMask security prompts

**4.3.3** Must validate all wallet addresses before use

**4.3.4** Must use HTTPS in production environment

### 4.4 User Experience Constraints

**4.4.1** Authentication flow must be simple and intuitive

**4.4.2** Error messages must be user-friendly and actionable

**4.4.3** Loading states must be clearly indicated

**4.4.4** Must not confuse users with technical jargon

## 5. Assumptions

### 5.1 User Assumptions

**5.1.1** Users choosing MetaMask authentication have MetaMask installed

**5.1.2** Users understand basic Web3 wallet concepts

**5.1.3** Users have ETH for gas fees (when using blockchain features)

**5.1.4** Users are on supported Ethereum network (Sepolia or Hardhat)

### 5.2 Technical Assumptions

**5.2.1** MetaMask extension API remains stable

**5.2.2** Ethers.js v6 API remains compatible

**5.2.3** Browser supports window.ethereum API

**5.2.4** LocalStorage is available and enabled

**5.2.5** Backend can handle both Clerk IDs and wallet addresses as identifiers

### 5.3 Infrastructure Assumptions

**5.3.1** Ethereum network (Sepolia/Hardhat) is accessible

**5.3.2** IPFS service is available for blockchain features

**5.3.3** Backend API endpoints are available and responsive

**5.3.4** Clerk service is available and operational

## 6. Dependencies

### 6.1 Existing Components

- `frontend/src/contexts/AuthContext.tsx` (already implemented)
- `frontend/src/components/MetaMaskButton.tsx` (already implemented)
- `frontend/src/hooks/useWallet.tsx` (already implemented)
- `frontend/src/app/layout.tsx` (already configured with providers)

### 6.2 External Libraries

- `@clerk/nextjs`: ^4.x (Clerk authentication)
- `ethers`: ^6.x (Web3 library)
- `next`: ^14.x (Next.js framework)
- `react`: ^18.x (React library)

### 6.3 Backend Dependencies

- FastAPI backend with updated endpoints
- Database schema supporting both identifier types
- Blockchain client for on-chain operations

### 6.4 External Services

- Clerk authentication service
- Ethereum network (Sepolia testnet or Hardhat local)
- IPFS service (for blockchain features)

## 7. Success Criteria

### 7.1 Functional Success

**7.1.1** Users can successfully authenticate using MetaMask from landing page

**7.1.2** Users can successfully authenticate using Clerk (existing flow)

**7.1.3** Patient dashboard works correctly with both auth methods

**7.1.4** Doctor dashboard works correctly with both auth methods

**7.1.5** Blockchain features are enabled for MetaMask users

**7.1.6** API calls work correctly with both auth methods

**7.1.7** Auth method indicator displays correctly

### 7.2 Quality Success

**7.2.1** Zero breaking changes to existing Clerk authentication

**7.2.2** All existing tests continue to pass

**7.2.3** New tests cover MetaMask authentication flows

**7.2.4** Code review approval from team

**7.2.5** No console errors or warnings in browser

### 7.3 User Experience Success

**7.3.1** Users can easily understand and choose between auth methods

**7.3.2** Error messages are clear and helpful

**7.3.3** Loading states provide appropriate feedback

**7.3.4** Authentication flow feels smooth and responsive

**7.3.5** Users can successfully complete their tasks with either auth method

## 8. Out of Scope

### 8.1 Not Included in This Feature

**8.1.1** Support for other Web3 wallets (WalletConnect, Coinbase Wallet, etc.)

**8.1.2** Multi-wallet support (connecting multiple wallets simultaneously)

**8.1.3** Wallet switching UI (users must disconnect and reconnect)

**8.1.4** Social login integration (Google, Facebook, etc.)

**8.1.5** Two-factor authentication for MetaMask

**8.1.6** Account linking (connecting Clerk account to MetaMask wallet)

**8.1.7** Migration tool for existing users to switch auth methods

**8.1.8** Admin dashboard for managing auth methods

### 8.2 Future Enhancements

**8.2.1** Support for additional Web3 wallets

**8.2.2** Account linking between Clerk and MetaMask

**8.2.3** Multi-signature wallet support

**8.2.4** Hardware wallet support (Ledger, Trezor)

**8.2.5** Gasless transactions for MetaMask users

**8.2.6** ENS (Ethereum Name Service) resolution

**8.2.7** Wallet-based role verification using on-chain credentials
