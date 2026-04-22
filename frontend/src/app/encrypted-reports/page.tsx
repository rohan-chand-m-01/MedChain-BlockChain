/**
 * Encrypted Lab Reports Demo Page
 * 
 * Demonstrates Privy-based decentralized encryption:
 * - No passwords to remember
 * - Social recovery (Google, email, passkey)
 * - Client-side encryption
 * - Zero-knowledge backend
 * - Blockchain access control
 */

'use client';

import { useState, useEffect } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import { useLabReportEncryption } from '@/hooks/useLabReportEncryption';
import { LabReportUpload } from '@/components/LabReportUpload';
import { RecoveryDemo } from '@/components/RecoveryDemo';
import { RecoverAccessButton } from '@/components/RecoverAccessButton';

export default function EncryptedReportsPage() {
  const { login, logout, authenticated, user } = usePrivy();
  const {
    decryptReport,
    grantAccess,
    revokeAccess,
    canAccess,
    isReady,
    walletAddress,
  } = useLabReportEncryption();

  const [reports, setReports] = useState<any[]>([]);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [decryptedContent, setDecryptedContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [showGrantModal, setShowGrantModal] = useState(false);
  const [grantingReportId, setGrantingReportId] = useState<string>('');
  const [doctorAddress, setDoctorAddress] = useState('');
  const [selectedDuration, setSelectedDuration] = useState<number | 'custom'>(12);
  const [customHours, setCustomHours] = useState('');
  const [isGranting, setIsGranting] = useState(false);

  // Load patient's reports
  useEffect(() => {
    if (isReady && walletAddress) {
      loadReports();
    }
  }, [isReady, walletAddress]);

  const loadReports = async () => {
    if (!walletAddress) return;

    setIsLoading(true);
    try {
      // Use InsForge SDK to fetch reports
      const { createClient } = await import('@insforge/sdk');
      const client = createClient({
        baseUrl: process.env.NEXT_PUBLIC_INSFORGE_BASE_URL!,
        anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY!,
      });

      const { data, error } = await client.database
        .from('encrypted_reports')
        .select('*, access_grants:report_access_grants(*)')
        .eq('patient_id', walletAddress)
        .order('timestamp', { ascending: false });

      if (error) throw error;
      setReports(data || []);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDecrypt = async (report: any) => {
    setSelectedReport(report);
    setDecryptedContent('Decrypting...');

    try {
      // Decrypt with Privy wallet (data stored directly in ipfs_hash field)
      const decrypted = await decryptReport(
        report.ipfs_hash,
        report.iv,
        report.patient_id
      );

      setDecryptedContent(decrypted);
    } catch (error: any) {
      setDecryptedContent(`Error: ${error.message}`);
    }
  };

  const openGrantModal = (reportId: string) => {
    setGrantingReportId(reportId);
    setShowGrantModal(true);
    setDoctorAddress('');
    setSelectedDuration(12);
    setCustomHours('');
  };

  const closeGrantModal = () => {
    setShowGrantModal(false);
    setGrantingReportId('');
    setDoctorAddress('');
    setIsGranting(false);
  };

  const handleGrantAccess = async () => {
    if (!doctorAddress.trim()) {
      alert('Please enter doctor wallet address');
      return;
    }

    // Calculate duration in hours
    let durationHours: number;
    if (selectedDuration === 'custom') {
      const parsed = parseFloat(customHours);
      if (isNaN(parsed) || parsed <= 0) {
        alert('Please enter a valid number of hours');
        return;
      }
      durationHours = parsed;
    } else {
      durationHours = selectedDuration;
    }

    setIsGranting(true);
    try {
      // Convert hours to days for the grantAccess function
      const durationDays = durationHours / 24;
      
      const { encryptedKey, expiresAt } = await grantAccess(
        doctorAddress,
        durationDays
      );

      // Store grant in InsForge database
      const { createClient } = await import('@insforge/sdk');
      const client = createClient({
        baseUrl: process.env.NEXT_PUBLIC_INSFORGE_BASE_URL!,
        anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY!,
      });

      const { error } = await client.database
        .from('report_access_grants')
        .insert([{
          report_id: grantingReportId,
          patient_id: walletAddress,
          doctor_address: doctorAddress,
          encrypted_key: encryptedKey,
          expires_at: expiresAt,
        }]);

      if (error) throw error;

      alert(`Access granted for ${durationHours} hour(s)!`);
      closeGrantModal();
      loadReports();
    } catch (error: any) {
      alert(`Error: ${error.message}`);
    } finally {
      setIsGranting(false);
    }
  };

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-2xl font-bold mb-4">Encrypted Lab Reports</h1>
          <p className="text-gray-600 mb-6">
            Secure your medical records with decentralized encryption.
            No passwords to remember - recover access anytime with social login!
          </p>

          <div className="mb-6 p-4 bg-blue-50 rounded border border-blue-200">
            <h3 className="font-semibold text-blue-800 mb-2">How it works:</h3>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>✅ Login with Google, email, or passkey</li>
              <li>✅ Privy creates your encrypted wallet</li>
              <li>✅ Reports encrypted with your wallet signature</li>
              <li>✅ Recover access via social login (no password!)</li>
              <li>✅ Grant/revoke doctor access anytime</li>
            </ul>
          </div>

          <button
            onClick={login}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold mb-4"
          >
            Login with Privy
          </button>

          <div className="flex justify-center">
            <RecoverAccessButton />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">Encrypted Lab Reports</h1>
              <p className="text-sm text-gray-600 mt-1">
                Wallet: {walletAddress?.slice(0, 6)}...{walletAddress?.slice(-4)}
              </p>
            </div>
            <button
              onClick={logout}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Logout
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Section */}
          <div>
            <LabReportUpload />
          </div>

          {/* Reports List */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Your Reports</h3>

            {isLoading ? (
              <p className="text-gray-500">Loading...</p>
            ) : reports.length === 0 ? (
              <p className="text-gray-500">No reports yet. Upload your first report!</p>
            ) : (
              <div className="space-y-3">
                {reports.map((report) => (
                  <div
                    key={report.id}
                    className="p-4 border rounded hover:bg-gray-50"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-semibold">{report.report_type}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(report.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                        🔐 Encrypted
                      </span>
                    </div>

                    <div className="flex gap-2 mt-3">
                      <button
                        onClick={() => handleDecrypt(report)}
                        className="text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        View
                      </button>
                      <button
                        onClick={() => openGrantModal(report.id)}
                        className="text-sm px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                      >
                        Grant Access
                      </button>
                    </div>

                    {report.access_grants?.length > 0 && (
                      <div className="mt-2 text-xs text-gray-600">
                        Shared with {report.access_grants.length} doctor(s)
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recovery Demo Section */}
        <div className="mt-6">
          <RecoveryDemo />
        </div>

        {/* Grant Access Modal */}
        {showGrantModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold">Grant Doctor Access</h3>
                <button
                  onClick={closeGrantModal}
                  className="text-gray-500 hover:text-gray-700"
                  disabled={isGranting}
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                {/* Doctor Address Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Doctor Wallet Address
                  </label>
                  <input
                    type="text"
                    value={doctorAddress}
                    onChange={(e) => setDoctorAddress(e.target.value)}
                    placeholder="0x..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isGranting}
                  />
                </div>

                {/* Duration Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Access Duration
                  </label>
                  <div className="grid grid-cols-2 gap-2 mb-2">
                    {[
                      { value: 1, label: '1 hour' },
                      { value: 4, label: '4 hours' },
                      { value: 12, label: '12 hours' },
                      { value: 24, label: '24 hours' },
                    ].map((option) => (
                      <button
                        key={option.value}
                        onClick={() => setSelectedDuration(option.value)}
                        className={`px-4 py-2 rounded-lg border-2 transition-colors ${
                          selectedDuration === option.value
                            ? 'border-blue-600 bg-blue-50 text-blue-700'
                            : 'border-gray-300 hover:border-gray-400'
                        }`}
                        disabled={isGranting}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                  
                  {/* Custom Duration */}
                  <button
                    onClick={() => setSelectedDuration('custom')}
                    className={`w-full px-4 py-2 rounded-lg border-2 transition-colors ${
                      selectedDuration === 'custom'
                        ? 'border-blue-600 bg-blue-50 text-blue-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    disabled={isGranting}
                  >
                    Custom Duration
                  </button>

                  {selectedDuration === 'custom' && (
                    <div className="mt-2">
                      <input
                        type="number"
                        value={customHours}
                        onChange={(e) => setCustomHours(e.target.value)}
                        placeholder="Enter hours"
                        min="0.5"
                        step="0.5"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={isGranting}
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Enter duration in hours (e.g., 0.5 for 30 minutes, 48 for 2 days)
                      </p>
                    </div>
                  )}
                </div>

                {/* Info Box */}
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-800">
                    🔐 The doctor will be able to decrypt and view this report until the access expires.
                    You can revoke access anytime.
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={closeGrantModal}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    disabled={isGranting}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleGrantAccess}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                    disabled={isGranting}
                  >
                    {isGranting ? 'Granting...' : 'Grant Access'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Decrypted Content Modal */}
        {selectedReport && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-auto p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">
                    {selectedReport.report_type}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {new Date(selectedReport.timestamp).toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setSelectedReport(null);
                    setDecryptedContent('');
                  }}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>

              <div className="p-4 bg-gray-50 rounded border">
                <pre className="text-sm whitespace-pre-wrap">
                  {decryptedContent}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
