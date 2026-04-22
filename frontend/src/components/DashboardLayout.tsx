'use client';

import { ReactNode } from 'react';
import EditorialSidebar from './EditorialSidebar';
import EditorialTopNav from './EditorialTopNav';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex min-h-screen bg-[#f7f9fb]">
      <EditorialSidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <EditorialTopNav />
        <main className="pl-72 pr-8 py-8 pt-24 flex flex-col gap-8 flex-1">
          {children}
        </main>
        {/* Footer */}
        <footer className="flex flex-col md:flex-row justify-between items-center py-8 pl-72 pr-8 mt-auto w-full bg-slate-50 dark:bg-slate-900 border-t border-slate-200/10">
          <p className="font-sans text-xs text-slate-400 dark:text-slate-500">
            © 2026 MediChain AI. All rights reserved.
          </p>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a
              className="font-sans text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity"
              href="#"
            >
              Privacy Policy
            </a>
            <a
              className="font-sans text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity"
              href="#"
            >
              Terms of Service
            </a>
            <a
              className="font-sans text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity"
              href="#"
            >
              HIPAA Compliance
            </a>
            <a
              className="font-sans text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity"
              href="#"
            >
              Support
            </a>
          </div>
        </footer>
      </div>
    </div>
  );
}
