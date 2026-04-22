'use client';

import { usePrivy } from '@privy-io/react-auth';
import { useAuth } from '@/contexts/AuthContext';
import AuthMethodIndicator from './AuthMethodIndicator';

export default function EditorialTopNav() {
  const { user } = usePrivy();
  const { userId, authMethod } = useAuth();

  // Get user display info from Privy
  const userEmail = user?.email?.address || user?.wallet?.address || '';
  const userInitial = userEmail.charAt(0).toUpperCase() || 'U';

  return (
    <header className="flex justify-between items-center h-16 w-full pl-72 pr-8 z-30 bg-white/80 dark:bg-slate-950/80 backdrop-blur-lg shadow-sm dark:shadow-none fixed top-0">
      {/* Search Bar */}
      <div className="flex-1 max-w-xl">
        <div className="relative group">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-600 transition-colors">
            search
          </span>
          <input
            className="w-full bg-slate-100 border-none rounded-full py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-blue-600/20 placeholder:text-slate-500/60"
            placeholder="Search appointments, patients..."
            type="text"
          />
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-4 ml-8">
        <div className="flex items-center gap-1">
          <button className="p-2 text-slate-500 hover:text-blue-600 transition-all scale-95 duration-150 active:scale-90">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="p-2 text-slate-500 hover:text-blue-600 transition-all scale-95 duration-150 active:scale-90">
            <span className="material-symbols-outlined">mail</span>
          </button>
          <button className="p-2 text-slate-500 hover:text-blue-600 transition-all scale-95 duration-150 active:scale-90">
            <span className="material-symbols-outlined">chat</span>
          </button>
        </div>

        <div className="h-8 w-[1px] bg-slate-300/30"></div>

        {/* Auth Method Indicator */}
        {userId && authMethod && (
          <>
            <AuthMethodIndicator 
              authMethod={authMethod} 
              userId={userId}
              className="mr-2"
            />
            <div className="h-8 w-[1px] bg-slate-300/30"></div>
          </>
        )}

        {/* User Info */}
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-slate-900">
            {userEmail}
          </span>
          <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs ring-2 ring-blue-600">
            {userInitial}
          </div>
        </div>
      </div>
    </header>
  );
}
