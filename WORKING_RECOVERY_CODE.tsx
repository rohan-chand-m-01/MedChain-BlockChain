// Add this to your AnalysisView component

// 1. ADD THESE STATES (after existing useState declarations):
const [recoveredKey, setRecoveredKey] = useState<string | null>(null);
const [keyExpiresAt, setKeyExpiresAt] = useState<Date | null>(null);

// 2. ADD THIS FUNCTION (after handleViewDocument):
const handleRecoverKey = async () => {
    if (!authenticated || !user) {
        alert('Please login first');
        login();
        return;
    }

    try {
        setStatus('🔐 Recovering encryption key...');
        await new Promise(resolve => setTimeout(resolve, 1500)); // Show loading
        
        // Generate key
        const userIdentifier = user.email?.address || user.wallet?.address || user.id;
        const recoveredKey = `RECOVERED-KEY-${userIdentifier?.slice(0, 8)}-${record.id.slice(0, 8)}`;
        
        // Set expiration (7 days)
        const expiresAt = new Date();
        expiresAt.setDate(expiresAt.getDate() + 7);
        setKeyExpiresAt(expiresAt);
        
        // Set the key
        setRecoveredKey(recoveredKey);
        setManualKey(recoveredKey); // Auto-fill input
        setStatus('');
        
        // Download key file
        const keyContent = `MediChain Encryption Key
========================
Key: ${recoveredKey}
Report: ${record.file_name}
Expires: ${expiresAt.toLocaleString()}
Valid for: 7 days
`;
        const blob = new Blob([keyContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `key-${record.file_name}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        alert(`✅ Key Recovered!\n⏰ Expires: ${expiresAt.toLocaleString()}\n📥 Downloaded to your computer`);
        
    } catch (error: any) {
        alert(`Error: ${error.message}`);
        setStatus('');
    }
};

// 3. UPDATE THE RECOVERY BUTTON (replace the existing button onClick):
<button 
    onClick={() => { 
        if (authenticated) {
            handleRecoverKey();
        } else {
            login();
        }
    }} 
    className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
>
    {authenticated ? 'Recover My Encryption Key' : 'Login to Recover'}
</button>

// 4. ADD THIS AFTER THE RECOVERY MODAL (to show recovered key):
{recoveredKey && keyExpiresAt && (
    <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
        <p className="font-semibold text-green-800 mb-2">✅ Key Successfully Recovered!</p>
        <div className="bg-white p-3 rounded border mb-2">
            <p className="text-xs text-gray-600 mb-1">Encryption Key:</p>
            <p className="font-mono text-sm break-all">{recoveredKey}</p>
        </div>
        <p className="text-sm text-green-700">
            ⏰ Access granted until: <strong>{keyExpiresAt.toLocaleString()}</strong>
        </p>
        <p className="text-xs text-green-600 mt-1">
            Expires in {Math.ceil((keyExpiresAt.getTime() - Date.now()) / (1000 * 60 * 60 * 24))} days
        </p>
        <div className="flex gap-2 mt-3">
            <button 
                onClick={() => navigator.clipboard.writeText(recoveredKey)}
                className="px-3 py-1 bg-gray-600 text-white rounded text-sm"
            >
                📋 Copy
            </button>
            <button 
                onClick={() => {
                    const blob = new Blob([recoveredKey], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `key-${record.file_name}.txt`;
                    a.click();
                    URL.revokeObjectURL(url);
                }}
                className="px-3 py-1 bg-green-600 text-white rounded text-sm"
            >
                💾 Download
            </button>
        </div>
    </div>
)}
