/**
 * Placeholder component for blockchain features that are temporarily disabled
 * during the MetaMask to Clerk migration
 */

export default function BlockchainFeatureDisabled({ featureName }: { featureName: string }) {
    return (
        <div className="min-h-screen flex items-center justify-center px-6 pt-20">
            <div className="glass-card p-8 max-w-md text-center">
                <div className="w-16 h-16 rounded-full bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center mx-auto mb-4">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#eab308" strokeWidth="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                        <line x1="12" y1="9" x2="12" y2="13" />
                        <line x1="12" y1="17" x2="12.01" y2="17" />
                    </svg>
                </div>
                <h2 className="text-xl font-semibold text-black mb-2">Feature Temporarily Unavailable</h2>
                <p className="text-sm text-gray-600 mb-4">
                    {featureName} is currently being updated to work with our new authentication system.
                </p>
                <p className="text-xs text-gray-500">
                    This feature will be available again soon. Thank you for your patience!
                </p>
            </div>
        </div>
    );
}
