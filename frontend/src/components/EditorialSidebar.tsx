'use client';

import { usePrivy } from '@privy-io/react-auth';
import { useState, useEffect } from 'react';

interface Record {
  id: string;
  file_name: string;
  created_at: string;
  risk_score?: number;
}

interface EditorialSidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  records?: Record[];
  selectedRecordId?: string | null;
  onRecordSelect?: (recordId: string) => void;
  onRecordDelete?: (recordId: string) => void;
}

export default function EditorialSidebar({ activeTab, onTabChange, records = [], selectedRecordId, onRecordSelect, onRecordDelete }: EditorialSidebarProps) {
  const { user } = usePrivy();
  const [userName, setUserName] = useState<string | null>(null);

  // Get user display info from Privy
  const userEmail = user?.email?.address || user?.wallet?.address || '';
  const userInitial = userName?.charAt(0).toUpperCase() || userEmail.charAt(0).toUpperCase() || 'U';

  // Fetch user profile name
  useEffect(() => {
    const fetchUserName = async () => {
      if (!user) return;
      
      const walletAddress = user?.wallet?.address || user?.id;
      if (!walletAddress) return;

      try {
        const userRole = typeof window !== 'undefined' ? localStorage.getItem('userRole') : null;
        const endpoint = userRole === 'patient' 
          ? `/api/profiles/patient/${walletAddress}`
          : `/api/profiles/doctor/${walletAddress}`;
        
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`);
        if (response.ok) {
          const data = await response.json();
          if (data.exists) {
            setUserName(data.full_name || data.name);
          }
        }
      } catch (error) {
        console.error('Failed to fetch user name:', error);
      }
    };

    fetchUserName();
  }, [user]);

  const navItems = [
    { id: 'analysis', icon: 'description', label: 'Analysis' },
    { id: 'twin', icon: 'view_in_ar', label: '3D Anatomy' },
    { id: 'chat', icon: 'chat', label: 'AI Chat' },
    { id: 'avatar', icon: 'videocam', label: 'Video Consult' },
    { id: 'access', icon: 'lock', label: 'Data Access' },
    { id: 'appointments', icon: 'calendar_today', label: 'Appointments' },
    { id: 'profile', icon: 'person', label: 'My Profile' },
  ];

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getRiskColor = (score?: number) => {
    if (!score) return 'bg-gray-100 text-gray-600';
    if (score < 30) return 'bg-green-100 text-green-700';
    if (score < 60) return 'bg-yellow-100 text-yellow-700';
    if (score < 80) return 'bg-orange-100 text-orange-700';
    return 'bg-red-100 text-red-700';
  };

  return (
    <aside className="fixed left-0 top-0 h-full z-40 flex flex-col p-4 bg-slate-50/80 dark:bg-slate-900/80 backdrop-blur-xl w-64 border-r border-slate-200/50">
      {/* Logo */}
      <div className="mb-6 px-4 flex items-center gap-3">
        <div className="w-10 h-10 bg-[#2563eb] rounded-xl flex items-center justify-center text-white">
          <span className="material-symbols-outlined">medical_services</span>
        </div>
        <div>
          <h1 className="text-xl font-bold text-[#2c3434] dark:text-slate-100">
            MediChain AI
          </h1>
          <p className="text-[10px] text-[#737686] tracking-wider uppercase font-semibold">
            Clinical Intelligence
          </p>
        </div>
      </div>

      {/* Medical Records List */}
      {records && records.length > 0 && (
        <div className="mb-4 px-2">
          <h3 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2 px-2">
            Medical Records ({records.length})
          </h3>
          <div className="space-y-1 max-h-48 overflow-y-auto custom-scrollbar">
            {records.map((record) => (
              <div
                key={record.id}
                className={`group relative w-full text-left px-3 py-2 rounded-lg transition-all ${
                  selectedRecordId === record.id
                    ? 'bg-[#2563eb] text-white shadow-md'
                    : 'bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300'
                }`}
              >
                <button
                  onClick={() => onRecordSelect?.(record.id)}
                  className="w-full text-left"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-semibold truncate">
                        {record.file_name}
                      </p>
                      <p className={`text-[10px] mt-0.5 ${selectedRecordId === record.id ? 'text-blue-100' : 'text-slate-500 dark:text-slate-400'}`}>
                        {formatDate(record.created_at)}
                      </p>
                    </div>
                    {record.risk_score !== undefined && (
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${selectedRecordId === record.id ? 'bg-white/20 text-white' : getRiskColor(record.risk_score)}`}>
                        {record.risk_score}%
                      </span>
                    )}
                  </div>
                </button>
                {onRecordDelete && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm(`Delete "${record.file_name}"? This action cannot be undone.`)) {
                        onRecordDelete(record.id);
                      }
                    }}
                    className={`absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-500 hover:text-white ${
                      selectedRecordId === record.id ? 'text-white hover:bg-red-600' : 'text-slate-400 hover:text-white'
                    }`}
                    title="Delete record"
                  >
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto custom-scrollbar">
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-2 rounded-full font-semibold transition-all ${
                isActive
                  ? 'bg-[#adedf6] dark:bg-[#0f5a62] text-[#0f5a62] dark:text-[#adedf6] opacity-90'
                  : 'text-slate-500 dark:text-slate-400 hover:text-[#246870] hover:bg-slate-200/50 dark:hover:bg-slate-800/50'
              }`}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span className="font-sans">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* User Profile */}
      <div className="mt-auto p-4 bg-[#f2f4f6] rounded-2xl flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-[#2563eb] flex items-center justify-center text-white font-bold">
          {userInitial}
        </div>
        <div className="overflow-hidden flex-1">
          <p className="text-sm font-bold truncate">
            {userName || userEmail}
          </p>
          <p className="text-xs text-[#737686] truncate">
            {typeof window !== 'undefined' && localStorage.getItem('userRole') === 'doctor' ? 'Doctor' : 'Patient'}
          </p>
        </div>
      </div>
    </aside>
  );
}
