import React, { useState, useEffect } from 'react';
import { getSystemStatus } from '../services/api';
import { CheckCircle2, XCircle, RefreshCw, Key, Database, Activity, ShieldAlert } from 'lucide-react';

export default function SystemStatus({ onStatusVerified, mode = 'details' }) {
  const [statusData, setStatusData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);

  const checkStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getSystemStatus();
      setStatusData(response.data);
      if (response.data.status === 'fully_operational') {
        onStatusVerified(true, response.data.secret_code);
      } else {
        onStatusVerified(false, null);
      }
    } catch (err) {
      console.error(err);
      setError('System Error - Verification Offline');
      setStatusData(null);
      onStatusVerified(false, null);
    } finally {
      setLoading(false);
      setLastChecked(new Date().toLocaleTimeString());
    }
  };

  useEffect(() => {
    checkStatus();
    // Poll system status every 15 seconds to track heartbeat and updates
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const isOperational = statusData && statusData.status === 'fully_operational';

  if (mode === 'compact') {
    return (
      <div className="w-full border-b border-slate-200 bg-white/95">
        <div className="max-w-7xl mx-auto px-4 py-2.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            {isOperational ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            ) : (
              <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0" />
            )}
            <span className={`text-xs font-extrabold uppercase tracking-wider ${isOperational ? 'text-emerald-700' : 'text-rose-700'}`}>
              {isOperational ? 'System verified' : loading ? 'Checking gateway' : 'Verification offline'}
            </span>
            <span className="hidden md:inline text-[11px] text-slate-400 truncate">
              PostgreSQL, SQLite, and heartbeat checks
            </span>
          </div>
          {isOperational && statusData.secret_code && (
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Clearance Code</span>
              <code className="px-2 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-[11px] sm:text-xs font-mono font-extrabold text-emerald-800 select-all">
                {statusData.secret_code}
              </code>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 pb-10">
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#0F2C59]" />
            <div>
              <h3 className="font-bold text-slate-800 text-sm">System Diagnostics</h3>
              <p className="text-[10px] text-slate-400 mt-0.5">
                Verification details kept below the main workflow.
              </p>
            </div>
          </div>
          <button 
            onClick={checkStatus} 
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Run Checks
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Key A Check */}
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/80 flex items-start gap-2.5">
            <Key className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-slate-700">PostgreSQL Config</span>
                {statusData?.checks?.key_a_present ? (
                  <span className="text-[10px] font-extrabold text-emerald-600 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Passed
                  </span>
                ) : (
                  <span className="text-[10px] font-extrabold text-red-600 flex items-center gap-1">
                    <XCircle className="w-3.5 h-3.5" /> Failed
                  </span>
                )}
              </div>
              <p className="text-[10px] text-slate-500 mt-1">Key A read successfully from system_config.</p>
            </div>
          </div>

          {/* Key B Check */}
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/80 flex items-start gap-2.5">
            <Database className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-slate-700">SQLite Vault Key</span>
                {statusData?.checks?.key_b_present ? (
                  <span className="text-[10px] font-extrabold text-emerald-600 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Passed
                  </span>
                ) : (
                  <span className="text-[10px] font-extrabold text-red-600 flex items-center gap-1">
                    <XCircle className="w-3.5 h-3.5" /> Failed
                  </span>
                )}
              </div>
              <p className="text-[10px] text-slate-500 mt-1">Key B fragment resolved from vault_keys.</p>
            </div>
          </div>

          {/* Heartbeat Check */}
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/80 flex items-start gap-2.5">
            <Activity className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-slate-700">Scheduler Heartbeat</span>
                {statusData?.checks?.heartbeat_fresh ? (
                  <span className="text-[10px] font-extrabold text-emerald-600 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Active
                  </span>
                ) : (
                  <span className="text-[10px] font-extrabold text-red-600 flex items-center gap-1">
                    <XCircle className="w-3.5 h-3.5" /> Inactive
                  </span>
                )}
              </div>
              <p className="text-[10px] text-slate-500 mt-1">
                {statusData?.time_diff_seconds !== null && statusData?.time_diff_seconds !== undefined
                  ? `Last heartbeat tick: ${Math.round(statusData.time_diff_seconds)} seconds ago.`
                  : "Worker heartbeat timestamp stale or offline."}
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row justify-between gap-2 mt-3 text-[9px] text-slate-400 border-t border-slate-100 pt-3">
          <span>AES-256-CBC verification using SHA-256 key derivation</span>
          <span>Last Diagnostic Sync: {lastChecked || 'None'}</span>
        </div>
      </div>
    </div>
  );
}
