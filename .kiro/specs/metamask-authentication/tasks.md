# Implementation Tasks: MetaMask Authentication Integration

## Phase 1: Component Creation and Updates

### 1.1 Create AuthMethodIndicator Component
- [x] 1.1.1 Create `frontend/src/components/AuthMethodIndicator.tsx` file
- [x] 1.1.2 Implement component interface accepting authMethod, userId, and className props
- [x] 1.1.3 Add badge display logic for 'clerk' and 'metamask' auth methods
- [x] 1.1.4 Implement wallet address truncation (0x1234...5678 format)
- [x] 1.1.5 Add distinct styling for each auth method (colors, icons)
- [ ] 1.1.6 Add optional auth method switching buttons
- [x] 1.1.7 Export component for use in dashboards

### 1.2 Update HeroSection Component
- [x] 1.2.1 Import MetaMaskButton component (already exists)
- [x] 1.2.2 Import useAuth hook from AuthContext
- [x] 1.2.3 Import useRouter from next/navigation
- [x] 1.2.4 Add handleMetaMaskSuccess callback function
- [x] 1.2.5 Implement redirect logic to /register?role=patient after MetaMask connection
- [x] 1.2.6 Add MetaMaskButton component to UI alongside Clerk buttons
- [x] 1.2.7 Style MetaMask button to match design system
- [x] 1.2.8 Add visual separation between auth methods
- [ ] 1.2.9 Test both auth flows work correctly

### 1.3 Update Patient Dashboard
- [x] 1.3.1 Replace Clerk's useAuth import with AuthContext useAuth
- [x] 1.3.2 Update userId extraction to use AuthContext userId
- [x] 1.3.3 Add authMethod extraction from AuthContext
- [x] 1.3.4 Update authentication check to use AuthContext isAuthenticated
- [x] 1.3.5 Add AuthMethodIndicator component to dashboard header
- [ ] 1.3.6 Update API calls to pass authMethod parameter
- [ ] 1.3.7 Update patient_wallet parameter to use unified userId
- [ ] 1.3.8 Add blockchain feature enablement logic based on authMethod
- [ ] 1.3.9 Test dashboard with both Clerk and MetaMask auth
- [ ] 1.3.10 Verify all existing functionality works with both auth methods

### 1.4 Update Doctor Dashboard
- [x] 1.4.1 Replace Clerk's useAuth import with AuthContext useAuth
- [x] 1.4.2 Update userId extraction to use AuthContext userId
- [x] 1.4.3 Add authMethod extraction from AuthContext
- [x] 1.4.4 Update authentication check to use AuthContext isAuthenticated
- [x] 1.4.5 Add AuthMethodIndicator component to dashboard header
- [ ] 1.4.6 Update API calls to pass authMethod parameter
- [ ] 1.4.7 Update doctor_wallet parameter to use unified userId
- [ ] 1.4.8 Add blockchain feature enablement logic based on authMethod
- [ ] 1.4.9 Test dashboard with both Clerk and MetaMask auth
- [ ] 1.4.10 Verify all existing functionality works with both auth methods

## Phase 2: API Integration Updates

### 2.1 Update API Utility Functions
- [ ] 2.1.1 Open `frontend/src/lib/api.ts` file
- [ ] 2.1.2 Add authMethod parameter to getPatientRecords function
- [ ] 2.1.3 Add authMethod parameter to analyzeReport function
- [ ] 2.1.4 Add authMethod parameter to getAppointments function
- [ ] 2.1.5 Add authMethod parameter to getDoctorGrants function
- [ ] 2.1.6 Add authMethod parameter to getDoctorAppointments function
- [ ] 2.1.7 Update request payloads to include authMethod field
- [ ] 2.1.8 Update request headers based on authMethod
- [ ] 2.1.9 Add TypeScript types for authMethod parameter
- [ ] 2.1.10 Test API functions with both auth methods

### 2.2 Backend Endpoint Updates
- [ ] 2.2.1 Update `/analyze` endpoint to accept authMethod parameter
- [ ] 2.2.2 Update `/records` endpoint to accept authMethod parameter
- [ ] 2.2.3 Update `/appointments` endpoint to accept authMethod parameter
- [ ] 2.2.4 Update `/access-control` endpoints to accept authMethod parameter
- [ ] 2.2.5 Add validation for authMethod parameter (must be 'clerk' or 'metamask')
- [ ] 2.2.6 Add validation that userId format matches authMethod
- [ ] 2.2.7 Update database queries to handle both Clerk IDs and wallet addresses
- [ ] 2.2.8 Test endpoints with both identifier types
- [ ] 2.2.9 Add error handling for mismatched authMethod and userId
- [ ] 2.2.10 Update API documentation with authMethod parameter

## Phase 3: Blockchain Feature Integration

### 3.1 Conditional Blockchain Features
- [ ] 3.1.1 Create utility function to check if blockchain features should be enabled
- [ ] 3.1.2 Update IPFS upload logic to check authMethod
- [ ] 3.1.3 Update blockchain storage logic to check authMethod
- [ ] 3.1.4 Show BlockchainFeatureDisabled component for Clerk users
- [ ] 3.1.5 Enable full blockchain features for MetaMask users
- [ ] 3.1.6 Update transaction signing to use connected wallet
- [ ] 3.1.7 Add wallet connection validation before blockchain operations
- [ ] 3.1.8 Test blockchain features with MetaMask auth
- [ ] 3.1.9 Test disabled state with Clerk auth
- [ ] 3.1.10 Add user feedback for blockchain feature availability

### 3.2 Smart Contract Interactions
- [ ] 3.2.1 Update contract interaction code to use wallet from useWallet hook
- [ ] 3.2.2 Add signer validation before contract calls
- [ ] 3.2.3 Update transaction submission to use connected wallet
- [ ] 3.2.4 Add gas estimation for MetaMask users
- [ ] 3.2.5 Add transaction confirmation UI
- [ ] 3.2.6 Handle transaction errors gracefully
- [ ] 3.2.7 Test contract interactions with MetaMask
- [ ] 3.2.8 Verify transactions are signed correctly

## Phase 4: Error Handling and User Feedback

### 4.1 MetaMask Error Handling
- [ ] 4.1.1 Add error handling for MetaMask not installed
- [ ] 4.1.2 Display error message with MetaMask download link
- [ ] 4.1.3 Add error handling for user rejection of connection
- [ ] 4.1.4 Display retry option for rejected connections
- [ ] 4.1.5 Add error handling for network mismatch
- [ ] 4.1.6 Display network switching instructions
- [ ] 4.1.7 Add error handling for wallet disconnection during session
- [ ] 4.1.8 Redirect to landing page on wallet disconnection
- [ ] 4.1.9 Test all error scenarios
- [ ] 4.1.10 Verify error messages are user-friendly

### 4.2 Loading States and Feedback
- [ ] 4.2.1 Add loading state during MetaMask connection
- [ ] 4.2.2 Display spinner or progress indicator
- [ ] 4.2.3 Add success feedback after successful connection
- [ ] 4.2.4 Add loading state during auth method switching
- [ ] 4.2.5 Add loading state during dashboard data fetching
- [ ] 4.2.6 Ensure loading states are consistent across components
- [ ] 4.2.7 Test loading states with slow network
- [ ] 4.2.8 Verify success feedback is clear and timely

### 4.3 Validation and Security
- [ ] 4.3.1 Add Ethereum address format validation function
- [ ] 4.3.2 Validate wallet addresses before using as userId
- [ ] 4.3.3 Add validation for authMethod parameter
- [ ] 4.3.4 Ensure no private keys are stored or logged
- [ ] 4.3.5 Clear auth state on logout/disconnect
- [ ] 4.3.6 Validate HTTPS in production environment
- [ ] 4.3.7 Add CSRF protection for auth endpoints
- [ ] 4.3.8 Test security validations
- [ ] 4.3.9 Perform security audit of auth flow
- [ ] 4.3.10 Document security considerations

## Phase 5: Testing and Quality Assurance

### 5.1 Unit Tests
- [ ] 5.1.1 Write tests for AuthMethodIndicator component
- [ ] 5.1.2 Write tests for updated HeroSection component
- [ ] 5.1.3 Write tests for updated Patient Dashboard
- [ ] 5.1.4 Write tests for updated Doctor Dashboard
- [ ] 5.1.5 Write tests for API utility functions with authMethod
- [ ] 5.1.6 Write tests for wallet address validation
- [ ] 5.1.7 Write tests for auth method switching
- [ ] 5.1.8 Write tests for error handling scenarios
- [ ] 5.1.9 Ensure all tests pass
- [ ] 5.1.10 Achieve >80% code coverage for new code

### 5.2 Integration Tests
- [ ] 5.2.1 Test complete MetaMask login flow (landing → dashboard)
- [ ] 5.2.2 Test complete Clerk login flow (landing → dashboard)
- [ ] 5.2.3 Test auth method switching (Clerk → MetaMask)
- [ ] 5.2.4 Test auth method switching (MetaMask → Clerk)
- [ ] 5.2.5 Test API calls with MetaMask auth
- [ ] 5.2.6 Test API calls with Clerk auth
- [ ] 5.2.7 Test blockchain features with MetaMask
- [ ] 5.2.8 Test blockchain features disabled with Clerk
- [ ] 5.2.9 Test wallet disconnection handling
- [ ] 5.2.10 Test network switching in MetaMask

### 5.3 End-to-End Tests
- [ ] 5.3.1 Test patient registration with MetaMask
- [ ] 5.3.2 Test doctor registration with MetaMask
- [ ] 5.3.3 Test patient dashboard full workflow with MetaMask
- [ ] 5.3.4 Test doctor dashboard full workflow with MetaMask
- [ ] 5.3.5 Test file upload and analysis with MetaMask
- [ ] 5.3.6 Test appointment booking with MetaMask
- [ ] 5.3.7 Test access control with MetaMask
- [ ] 5.3.8 Test chatbot with MetaMask
- [ ] 5.3.9 Test all features work with Clerk (regression)
- [ ] 5.3.10 Test cross-browser compatibility (Chrome, Firefox, Brave, Edge)

### 5.4 Property-Based Tests
- [ ] 5.4.1 Write property test for authentication state consistency
- [ ] 5.4.2 Write property test for wallet address format validation
- [ ] 5.4.3 Write property test for authMethod matching userId source
- [ ] 5.4.4 Write property test for API request parameter consistency
- [ ] 5.4.5 Run property tests with fast-check library
- [ ] 5.4.6 Verify no edge cases cause failures
- [ ] 5.4.7 Document property test results

## Phase 6: Documentation and Deployment

### 6.1 Code Documentation
- [ ] 6.1.1 Add JSDoc comments to AuthMethodIndicator component
- [ ] 6.1.2 Add JSDoc comments to updated API functions
- [ ] 6.1.3 Add inline comments for complex auth logic
- [ ] 6.1.4 Update component prop types with descriptions
- [ ] 6.1.5 Document auth method switching behavior
- [ ] 6.1.6 Document blockchain feature enablement logic
- [ ] 6.1.7 Review and update existing comments

### 6.2 User Documentation
- [ ] 6.2.1 Create user guide for MetaMask authentication
- [ ] 6.2.2 Document how to install MetaMask
- [ ] 6.2.3 Document how to connect wallet
- [ ] 6.2.4 Document how to switch networks
- [ ] 6.2.5 Document blockchain feature requirements
- [ ] 6.2.6 Create FAQ for common issues
- [ ] 6.2.7 Add troubleshooting guide

### 6.3 Developer Documentation
- [ ] 6.3.1 Update README with MetaMask setup instructions
- [ ] 6.3.2 Document AuthContext usage
- [ ] 6.3.3 Document API parameter changes
- [ ] 6.3.4 Document testing procedures
- [ ] 6.3.5 Document deployment requirements
- [ ] 6.3.6 Update architecture diagrams
- [ ] 6.3.7 Document security considerations

### 6.4 Deployment Preparation
- [ ] 6.4.1 Verify all environment variables are set
- [ ] 6.4.2 Test on staging environment
- [ ] 6.4.3 Verify HTTPS is enabled
- [ ] 6.4.4 Test with Sepolia testnet
- [ ] 6.4.5 Verify Clerk configuration
- [ ] 6.4.6 Verify MetaMask compatibility
- [ ] 6.4.7 Run performance tests
- [ ] 6.4.8 Run security audit
- [ ] 6.4.9 Create deployment checklist
- [ ] 6.4.10 Plan rollback strategy

### 6.5 Production Deployment
- [ ] 6.5.1 Deploy backend changes
- [ ] 6.5.2 Deploy frontend changes
- [ ] 6.5.3 Verify deployment successful
- [ ] 6.5.4 Test MetaMask auth in production
- [ ] 6.5.5 Test Clerk auth in production (regression)
- [ ] 6.5.6 Monitor error logs
- [ ] 6.5.7 Monitor performance metrics
- [ ] 6.5.8 Verify blockchain features work
- [ ] 6.5.9 Test on multiple browsers
- [ ] 6.5.10 Announce feature to users

## Phase 7: Post-Deployment Monitoring

### 7.1 Monitoring and Analytics
- [ ] 7.1.1 Set up monitoring for MetaMask connection success rate
- [ ] 7.1.2 Set up monitoring for auth method distribution
- [ ] 7.1.3 Set up monitoring for error rates by auth method
- [ ] 7.1.4 Set up monitoring for API response times by auth method
- [ ] 7.1.5 Set up alerts for authentication failures
- [ ] 7.1.6 Track user adoption of MetaMask auth
- [ ] 7.1.7 Monitor blockchain feature usage
- [ ] 7.1.8 Collect user feedback
- [ ] 7.1.9 Analyze performance metrics
- [ ] 7.1.10 Create monitoring dashboard

### 7.2 Bug Fixes and Improvements
- [ ] 7.2.1 Monitor for reported issues
- [ ] 7.2.2 Prioritize and fix critical bugs
- [ ] 7.2.3 Address user feedback
- [ ] 7.2.4 Optimize performance bottlenecks
- [ ] 7.2.5 Improve error messages based on user feedback
- [ ] 7.2.6 Enhance UI/UX based on usage patterns
- [ ] 7.2.7 Update documentation based on common questions
- [ ] 7.2.8 Plan future enhancements
- [ ] 7.2.9 Conduct retrospective meeting
- [ ] 7.2.10 Document lessons learned

## Task Dependencies

### Critical Path
1. Phase 1.1 (AuthMethodIndicator) → Phase 1.3 & 1.4 (Dashboard updates)
2. Phase 1.2 (HeroSection) → Phase 5.2 (Integration tests)
3. Phase 2.1 (API updates) → Phase 2.2 (Backend updates)
4. Phase 2.2 (Backend) → Phase 5.2 (Integration tests)
5. Phase 3.1 (Blockchain features) → Phase 5.3 (E2E tests)
6. Phase 5 (All testing) → Phase 6.4 (Deployment prep)
7. Phase 6.4 (Deployment prep) → Phase 6.5 (Production deployment)
8. Phase 6.5 (Deployment) → Phase 7 (Monitoring)

### Parallel Work Streams
- Phase 1.1, 1.2, 1.3, 1.4 can be worked on in parallel
- Phase 2.1 and 2.2 can be worked on in parallel
- Phase 4.1, 4.2, 4.3 can be worked on in parallel
- Phase 5.1, 5.2, 5.3, 5.4 can be worked on in parallel
- Phase 6.1, 6.2, 6.3 can be worked on in parallel

## Estimated Effort

### Phase 1: Component Creation and Updates
- Estimated time: 8-12 hours
- Complexity: Medium
- Risk: Low

### Phase 2: API Integration Updates
- Estimated time: 6-8 hours
- Complexity: Medium
- Risk: Medium

### Phase 3: Blockchain Feature Integration
- Estimated time: 4-6 hours
- Complexity: Medium
- Risk: Low

### Phase 4: Error Handling and User Feedback
- Estimated time: 4-6 hours
- Complexity: Low
- Risk: Low

### Phase 5: Testing and Quality Assurance
- Estimated time: 12-16 hours
- Complexity: High
- Risk: Medium

### Phase 6: Documentation and Deployment
- Estimated time: 6-8 hours
- Complexity: Low
- Risk: Low

### Phase 7: Post-Deployment Monitoring
- Estimated time: Ongoing (2-4 hours/week for first month)
- Complexity: Low
- Risk: Low

### Total Estimated Effort
- Total time: 40-56 hours
- Recommended timeline: 2-3 weeks
- Team size: 1-2 developers

## Success Metrics

### Functional Metrics
- [ ] 100% of existing Clerk auth flows continue to work
- [ ] MetaMask auth flow has >95% success rate
- [ ] All dashboard features work with both auth methods
- [ ] Blockchain features are enabled for MetaMask users
- [ ] API calls work correctly with both auth methods

### Quality Metrics
- [ ] >80% code coverage for new code
- [ ] Zero critical bugs in production
- [ ] <5 minor bugs in first week
- [ ] All tests passing
- [ ] Code review approved

### Performance Metrics
- [ ] MetaMask connection completes in <5 seconds
- [ ] Dashboard load time within 10% of Clerk auth
- [ ] API response times unchanged
- [ ] No performance regressions

### User Experience Metrics
- [ ] >80% user satisfaction with MetaMask auth
- [ ] <10% error rate for MetaMask connections
- [ ] Clear and helpful error messages
- [ ] Smooth authentication flow
- [ ] Positive user feedback

## Risk Mitigation

### Risk 1: Breaking Existing Clerk Authentication
- **Mitigation**: Comprehensive regression testing, feature flags, gradual rollout
- **Contingency**: Quick rollback plan, maintain backward compatibility

### Risk 2: MetaMask Compatibility Issues
- **Mitigation**: Test on multiple browsers, handle edge cases, clear error messages
- **Contingency**: Provide fallback to Clerk auth, document known issues

### Risk 3: Backend Performance Impact
- **Mitigation**: Load testing, database indexing, caching strategy
- **Contingency**: Scale backend resources, optimize queries

### Risk 4: User Confusion with Dual Auth
- **Mitigation**: Clear UI, user documentation, onboarding flow
- **Contingency**: User support, FAQ, video tutorials

### Risk 5: Security Vulnerabilities
- **Mitigation**: Security audit, validation, HTTPS enforcement
- **Contingency**: Security patches, incident response plan
