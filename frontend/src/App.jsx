import React, { useEffect, useState } from 'react';
import SystemStatus from './components/SystemStatus';
import RouteSelector from './components/RouteSelector';
import Dashboard from './components/Dashboard';
import { Moon, ShieldCheck, Sun, Train } from 'lucide-react';

export default function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [latestBookedTicket, setLatestBookedTicket] = useState(null);
  const [isSystemUnlocked, setIsSystemUnlocked] = useState(false);
  const [theme, setTheme] = useState(() => {
    const themeParam = new URLSearchParams(window.location.search).get('theme');
    return themeParam === 'dark' || themeParam === 'light'
      ? themeParam
      : localStorage.getItem('metro-theme') || 'light';
  });

  useEffect(() => {
    localStorage.setItem('metro-theme', theme);
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const handleTicketBooked = (ticket) => {
    setLatestBookedTicket(ticket);
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleStatusVerified = (unlocked) => {
    setIsSystemUnlocked(unlocked);
  };

  return (
    <div className={`min-h-screen text-slate-800 flex flex-col font-sans bg-slate-50 overflow-x-hidden transition-colors duration-300 ${theme === 'dark' ? 'theme-dark' : 'theme-light'}`}>
      <div className="h-1.5 w-full flex">
        <div className="bg-[#FF9933] w-1/3 h-full" />
        <div className="bg-white w-1/3 h-full" />
        <div className="bg-[#128807] w-1/3 h-full" />
      </div>

      <div className="bg-slate-100 border-b border-slate-200 py-1.5 px-4 text-[11px] text-slate-600 font-medium hidden sm:block">
        <div className="max-w-7xl mx-auto flex justify-between items-center gap-4">
          <div className="flex gap-4 min-w-0">
            <span className="truncate">Technical Assessment Demo</span>
            <span className="text-slate-300">|</span>
            <span className="truncate">Fictional Kolkata Metro Management System</span>
          </div>
          <div className="flex gap-4 items-center shrink-0">
            <span>React + FastAPI + PostgreSQL + SQLite</span>
            <span>|</span>
            <span className="font-semibold text-slate-700">Route planning, booking, diagnostics</span>
          </div>
        </div>
      </div>

      <header className="bg-white border-b-2 border-slate-200 shadow-sm sticky top-0 z-50 py-4 px-3 sm:px-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3.5 min-w-0 w-full md:w-auto overflow-hidden">
            <span className="p-2.5 bg-gradient-to-tr from-[#0F2C59] to-[#1E3A8A] rounded-lg shadow-md flex items-center justify-center shrink-0">
              <Train className="w-7 h-7 text-white" />
            </span>
            <div className="min-w-0">
              <div className="flex items-center gap-2 min-w-0">
                <h1 className="text-lg md:text-xl font-extrabold tracking-tight text-[#0F2C59] truncate">
                  Kolkata Metro Planner
                </h1>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-600 uppercase shrink-0">
                  Demo
                </span>
              </div>
              <h2 className="text-xs md:text-sm font-semibold text-slate-500 mt-0.5 truncate">
                Route finder, fare estimator, and QR ticket workflow
              </h2>
              <p className="hidden sm:block text-[9px] font-bold text-[#128807] uppercase tracking-wider mt-0.5 truncate">
                Fictional assessment project - not affiliated with any transit authority
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={() => setTheme((current) => current === 'dark' ? 'light' : 'dark')}
              className="h-11 w-11 rounded-lg border border-slate-200 bg-slate-50 text-slate-600 shadow-inner flex items-center justify-center transition hover:-translate-y-0.5 hover:shadow-md"
              aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
              title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>

            <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 shadow-inner">
              <span className="relative flex h-2.5 w-2.5">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    isSystemUnlocked ? 'bg-emerald-500' : 'bg-rose-500'
                  }`}
                />
                <span
                  className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                    isSystemUnlocked ? 'bg-emerald-600' : 'bg-rose-600'
                  }`}
                />
              </span>
              <div className="text-left">
                <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block">Assessment Gateway</span>
                <span className="text-xs font-bold text-slate-700">
                  {isSystemUnlocked ? 'Verification Active' : 'Offline Mode'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <SystemStatus mode="compact" onStatusVerified={handleStatusVerified} />

      <main className="flex-1 max-w-7xl w-full min-w-0 mx-auto px-3 sm:px-4 py-6 pb-12 overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(300px,0.85fr)_minmax(0,2.15fr)] gap-6 min-w-0">
          <div className="min-w-0 motion-enter">
            <RouteSelector onTicketBooked={handleTicketBooked} />
          </div>

          <div className="min-w-0 motion-enter motion-delay-1">
            <Dashboard refreshTrigger={refreshTrigger} latestBookedTicket={latestBookedTicket} />
          </div>
        </div>
      </main>

      <SystemStatus mode="details" onStatusVerified={handleStatusVerified} />

      <footer className="bg-[#0F2C59] text-white border-t border-slate-300 mt-auto">
        <div className="h-1 w-full flex">
          <div className="bg-[#FF9933] w-1/3 h-full" />
          <div className="bg-white w-1/3 h-full" />
          <div className="bg-[#128807] w-1/3 h-full" />
        </div>

        <div className="max-w-7xl mx-auto py-8 px-6 grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-slate-300">
          <div>
            <h4 className="font-bold text-sm text-white mb-2 uppercase">Kolkata Metro Management System</h4>
            <p className="leading-relaxed">
              Fictional technical assessment application for station discovery, shortest-route planning,
              QR ticket booking, and system diagnostics.
            </p>
          </div>
          <div className="md:text-right flex flex-col justify-between">
            <p className="leading-relaxed">
              Built with a React/Vite frontend, FastAPI backend, PostgreSQL ticket storage,
              and SQLite metro route graph.
              <br />
              Page last updated: {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}.
            </p>
            <p className="text-[10px] text-slate-400 mt-4 flex items-center gap-1.5 md:justify-end">
              <ShieldCheck className="w-3.5 h-3.5" />
              Not affiliated with Kolkata Metro Rail Corporation or any real transit authority.
            </p>
          </div>
        </div>

        <div className="bg-[#0b1d3a] py-3 text-center text-[10px] text-slate-400 border-t border-slate-800">
          <p>(c) 2026 Kolkata Metro Management System Demo. Technical assessment submission.</p>
        </div>
      </footer>
    </div>
  );
}
