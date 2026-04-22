'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth, useUser } from '@clerk/nextjs';
import { getUserId, isPatient } from '@/lib/auth';
import { getPatientRecords, getAppointments } from '@/lib/api';
import EditorialSidebar from '@/components/EditorialSidebar';
import EditorialTopNav from '@/components/EditorialTopNav';

interface Analysis {
  id: string;
  file_name: string;
  file_url: string;
  summary: string;
  risk_score: number;
  conditions: string[];
  specialist: string;
  urgency: string;
  created_at: string;
}

interface Appointment {
  id: string;
  date: string;
  time: string;
  status: string;
  reason: string;
  doctor_name?: string;
  doctor_specialty?: string;
}

export default function EditorialPatientDashboard() {
  const router = useRouter();
  const { isSignedIn, userId } = useAuth();
  const { user } = useUser();
  const [records, setRecords] = useState<Analysis[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [activeTab, setActiveTab] = useState<string>('analysis');
  const [stats, setStats] = useState({
    totalRecords: 0,
    avgRiskScore: 0,
    upcomingAppointments: 0,
    lastVisit: 'N/A',
  });

  useEffect(() => {
    if (!isSignedIn) {
      router.push('/');
      return;
    }
    if (!isPatient(user)) {
      router.push('/register');
      return;
    }
    if (userId) {
      loadData();
    }
  }, [isSignedIn, userId, user, router]);

  const loadData = async () => {
    if (!userId) return;
    try {
      const { records: data } = await getPatientRecords(userId);
      const { appointments: appts } = await getAppointments(userId);

      if (data) {
        setRecords(data as Analysis[]);
        const avgRisk =
          data.length > 0
            ? data.reduce((sum: number, r: any) => sum + (r.risk_score || 0), 0) / data.length
            : 0;

        const upcoming = (appts as Appointment[]).filter(
          (a) => a.status === 'confirmed' || a.status === 'pending'
        ).length;

        setStats({
          totalRecords: data.length,
          avgRiskScore: Math.round(avgRisk),
          upcomingAppointments: upcoming,
          lastVisit: data.length > 0 ? new Date(data[0].created_at).toLocaleDateString() : 'N/A',
        });
      }

      if (appts) {
        setAppointments(appts as Appointment[]);
      }
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };

  if (!isSignedIn || !userId) return null;

  return (
    <div className="flex min-h-screen bg-[#f7f9fb]">
      <EditorialSidebar activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="flex-1 flex flex-col min-w-0">
        <EditorialTopNav />

        {/* Main Content */}
        <main className="pl-72 pr-8 py-8 flex flex-col gap-8 flex-1">
          {/* Header */}
          <div className="flex justify-between items-end">
            <div>
              <h2 className="text-3xl font-bold text-[#191c1e]">Hospital Dashboard</h2>
              <p className="text-[#434655] font-medium">
                Overview of your health records for {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
              </p>
            </div>
            <div className="flex gap-2">
              <button className="bg-[#e0e3e5] px-4 py-2 rounded-xl text-sm font-semibold text-[#2563eb] hover:bg-[#d8dadc] transition-colors">
                Export Report
              </button>
              <Link
                href="/patient/book"
                className="bg-[#2563eb] text-white px-4 py-2 rounded-xl text-sm font-semibold shadow-sm hover:bg-[#125c63] transition-colors"
              >
                + New Appointment
              </Link>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Metric Card 1 */}
            <div className="bg-white p-6 rounded-xl shadow-[0_12px_32px_-4px_rgba(44,52,52,0.06)] flex flex-col gap-2">
              <div className="flex justify-between items-start">
                <div className="w-12 h-12 rounded-full bg-[#2563eb]/10 flex items-center justify-center text-[#2563eb]">
                  <span className="material-symbols-outlined">description</span>
                </div>
                <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg">
                  +12%
                </span>
              </div>
              <p className="text-3xl font-bold font-body mt-2">{stats.totalRecords}</p>
              <p className="text-sm font-medium text-[#434655]">Medical Records</p>
            </div>

            {/* Metric Card 2 */}
            <div className="bg-white p-6 rounded-xl shadow-[0_12px_32px_-4px_rgba(44,52,52,0.06)] flex flex-col gap-2">
              <div className="flex justify-between items-start">
                <div className="w-12 h-12 rounded-full bg-[#565e74]/10 flex items-center justify-center text-[#565e74]">
                  <span className="material-symbols-outlined">favorite</span>
                </div>
                <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg">
                  Good
                </span>
              </div>
              <p className="text-3xl font-bold font-body mt-2">{stats.avgRiskScore}%</p>
              <p className="text-sm font-medium text-[#434655]">Avg Health Score</p>
            </div>

            {/* Metric Card 3 */}
            <div className="bg-white p-6 rounded-xl shadow-[0_12px_32px_-4px_rgba(44,52,52,0.06)] flex flex-col gap-2">
              <div className="flex justify-between items-start">
                <div className="w-12 h-12 rounded-full bg-[#006242]/10 flex items-center justify-center text-[#006242]">
                  <span className="material-symbols-outlined">calendar_today</span>
                </div>
                <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg">
                  Active
                </span>
              </div>
              <p className="text-3xl font-bold font-body mt-2">{stats.upcomingAppointments}</p>
              <p className="text-sm font-medium text-[#434655]">Appointments</p>
            </div>

            {/* Metric Card 4 */}
            <div className="bg-white p-6 rounded-xl shadow-[0_12px_32px_-4px_rgba(44,52,52,0.06)] flex flex-col gap-2">
              <div className="flex justify-between items-start">
                <div className="w-12 h-12 rounded-full bg-[#2563eb]/10 flex items-center justify-center text-[#125c63]">
                  <span className="material-symbols-outlined">schedule</span>
                </div>
                <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded-lg">
                  Recent
                </span>
              </div>
              <p className="text-xl font-bold font-body mt-2">{stats.lastVisit}</p>
              <p className="text-sm font-medium text-[#434655]">Last Visit</p>
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Chart Section */}
            <div className="lg:col-span-2 bg-white p-8 rounded-xl shadow-[0_12px_32px_-4px_rgba(44,52,52,0.06)]">
              <div className="flex justify-between items-center mb-8">
                <h3 className="text-2xl font-bold">Health Overview</h3>
                <select className="bg-[#eceef0] border-none rounded-lg text-xs font-bold px-3 py-1 focus:ring-0">
                  <option>Daily</option>
                  <option>Weekly</option>
                  <option>Monthly</option>
                </select>
              </div>

              {/* Simple Bar Chart Visualization */}
              <div className="h-64 relative w-full overflow-hidden">
                <div className="absolute inset-0 flex items-end gap-[12%] pb-8">
                  {[40, 60, 55, 75, 65, 85].map((height, i) => (
                    <div
                      key={i}
                      className={`flex-1 rounded-t-lg relative group transition-all hover:opacity-80 ${
                        i === 3 ? 'bg-[#2563eb]' : 'bg-[#2563eb]/40'
                      }`}
                      style={{ height: `${height}%` }}
                    >
                      <div className="absolute -top-10 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 bg-[#191c1e] text-white text-[10px] px-2 py-1 rounded">
                        {height * 10}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="absolute bottom-0 left-0 right-0 flex justify-between text-[10px] text-[#737686] font-bold uppercase tracking-widest pt-4 border-t border-[#c3c6d7]/10">
                  <span>Mon</span>
                  <span>Tue</span>
                  <span>Wed</span>
                  <span>Thu</span>
                  <span>Fri</span>
                  <span>Sat</span>
                </div>
              </div>
            </div>

            {/* Calendar Widget */}
            <div className="bg-white p-6 rounded-xl shadow-[0_12px_32px_-4px_rgba(44,52,52,0.06)]">
              <div className="flex justify-between items-center mb-6">
                <h3 className="font-bold text-xl">Calendar</h3>
                <div className="flex gap-1">
                  <button className="p-1 hover:bg-[#eceef0] rounded-lg transition-colors">
                    <span className="material-symbols-outlined text-sm">chevron_left</span>
                  </button>
                  <button className="p-1 hover:bg-[#eceef0] rounded-lg transition-colors">
                    <span className="material-symbols-outlined text-sm">chevron_right</span>
                  </button>
                </div>
              </div>

              <div className="mb-4 text-center">
                <span className="font-bold text-[#2563eb]">
                  {new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </span>
              </div>

              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-1 text-center mb-2">
                {['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'].map((day) => (
                  <span key={day} className="text-[10px] font-bold text-[#737686] uppercase">
                    {day}
                  </span>
                ))}
              </div>

              <div className="grid grid-cols-7 gap-1 text-center">
                {Array.from({ length: 35 }, (_, i) => {
                  const day = i - 2;
                  const isToday = day === new Date().getDate();
                  const isCurrentMonth = day > 0 && day <= 31;

                  return (
                    <span
                      key={i}
                      className={`p-2 text-xs font-bold rounded-lg cursor-pointer transition-colors ${
                        isToday
                          ? 'bg-[#2563eb] text-white ring-4 ring-[#2563eb]/20'
                          : isCurrentMonth
                          ? 'hover:bg-[#2563eb]/20'
                          : 'text-[#737686]/30'
                      }`}
                    >
                      {isCurrentMonth ? day : ''}
                    </span>
                  );
                })}
              </div>

              {/* Upcoming Events */}
              <div className="mt-6 pt-6 border-t border-[#c3c6d7]/10">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-2 h-10 bg-[#2563eb] rounded-full"></div>
                  <div>
                    <p className="text-xs font-bold">Health Checkup</p>
                    <p className="text-[10px] text-[#737686]">09:00 AM - 10:30 AM</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-10 bg-[#565e74] rounded-full"></div>
                  <div>
                    <p className="text-xs font-bold">Lab Results</p>
                    <p className="text-[10px] text-[#737686]">11:00 AM - 12:00 PM</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Records Table */}
          <div className="bg-white rounded-xl shadow-[0_12px_32px_-4px_rgba(44,52,52,0.06)] overflow-hidden">
            <div className="p-6 flex justify-between items-center bg-[#eceef0]/50">
              <h3 className="text-2xl font-bold">Recent Records</h3>
              <div className="flex gap-2">
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#737686] text-sm">
                    filter_list
                  </span>
                  <input
                    className="bg-white border-none rounded-lg py-1.5 pl-8 pr-4 text-xs font-semibold focus:ring-1 focus:ring-[#2563eb]"
                    placeholder="Filter"
                    type="text"
                  />
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-[11px] font-bold text-[#737686] uppercase tracking-widest border-b border-[#c3c6d7]/10">
                    <th className="px-6 py-4">No</th>
                    <th className="px-6 py-4">File Name</th>
                    <th className="px-6 py-4">Date</th>
                    <th className="px-6 py-4">Risk Score</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Specialist</th>
                    <th className="px-6 py-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#c3c6d7]/5">
                  {records.slice(0, 5).map((record, idx) => (
                    <tr key={record.id} className="hover:bg-[#eceef0] transition-colors group">
                      <td className="px-6 py-5 text-sm font-bold">{String(idx + 1).padStart(2, '0')}</td>
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center font-bold text-[10px]">
                            {record.file_name.substring(0, 2).toUpperCase()}
                          </div>
                          <span className="text-sm font-bold">{record.file_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-5 text-sm">
                        {new Date(record.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-5 text-sm">{record.risk_score}%</td>
                      <td className="px-6 py-5">
                        <span
                          className={`px-3 py-1 rounded-full text-[10px] font-bold ${
                            record.urgency === 'critical'
                              ? 'bg-red-50 text-red-600'
                              : record.urgency === 'high'
                              ? 'bg-orange-50 text-orange-600'
                              : record.urgency === 'medium'
                              ? 'bg-yellow-50 text-yellow-600'
                              : 'bg-green-50 text-green-600'
                          }`}
                        >
                          {record.urgency}
                        </span>
                      </td>
                      <td className="px-6 py-5 text-sm text-[#737686]">{record.specialist}</td>
                      <td className="px-6 py-5 text-right">
                        <button className="text-[#737686] hover:text-[#2563eb] transition-colors">
                          <span className="material-symbols-outlined text-lg">more_vert</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="p-6 bg-white border-t border-[#c3c6d7]/5 flex justify-between items-center">
              <p className="text-xs text-[#737686]">
                Showing 1-{Math.min(5, records.length)} of {records.length} records
              </p>
              <div className="flex gap-2">
                <button className="px-3 py-1 rounded border border-[#c3c6d7]/20 text-xs font-bold hover:bg-[#eceef0]">
                  Previous
                </button>
                <button className="px-3 py-1 rounded bg-[#2563eb] text-white text-xs font-bold">
                  1
                </button>
                <button className="px-3 py-1 rounded border border-[#c3c6d7]/20 text-xs font-bold hover:bg-[#eceef0]">
                  2
                </button>
                <button className="px-3 py-1 rounded border border-[#c3c6d7]/20 text-xs font-bold hover:bg-[#eceef0]">
                  Next
                </button>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="flex flex-col md:flex-row justify-between items-center py-8 pl-72 pr-8 mt-auto w-full bg-slate-50 dark:bg-slate-900 border-t border-slate-200/10">
          <p className="text-xs text-slate-400 dark:text-slate-500">
            © 2024 MediChain AI. All rights reserved.
          </p>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a
              className="text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity"
              href="#"
            >
              Privacy Policy
            </a>
            <a
              className="text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity"
              href="#"
            >
              Terms of Service
            </a>
            <a
              className="text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity"
              href="#"
            >
              HIPAA Compliance
            </a>
            <a
              className="text-xs text-slate-400 dark:text-slate-500 hover:text-[#246870] dark:hover:text-slate-300 opacity-80 hover:opacity-100 transition-opacity"
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
