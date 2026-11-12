import React, { useState } from 'react';
import { axiomApi } from '../api/client';
import {
  CheckCircle2,
  Cpu,
  Database,
  HardDrive,
  Lock,
  Play,
  RefreshCw,
  Server,
  ShieldCheck,
  Sparkles,
  Terminal,
  Trash2,
  Workflow,
} from 'lucide-react';

interface SettingsAndAutomationViewProps {
  aiStatus: any;
  memories: any[];
  obsidianConfig: any;
  automationStatus: any;
  backups: any[];
  onRefreshStatus: () => Promise<void>;
  onUpdateProvider: (payload: any) => Promise<void>;
  onAddMemory: (category: string, key: string, statement: string) => Promise<void>;
  onDeleteMemory: (id: number) => Promise<void>;
  onUpdateObsidian: (payload: any) => Promise<void>;
  onRunWorkflow: (workflowKey: string) => Promise<any>;
  onCreateBackup: () => Promise<void>;
}

export const SettingsAndAutomationView: React.FC<SettingsAndAutomationViewProps> = ({
  aiStatus,
  memories,
  obsidianConfig,
  automationStatus,
  backups,
  onRefreshStatus,
  onUpdateProvider,
  onAddMemory,
  onDeleteMemory,
  onUpdateObsidian,
  onRunWorkflow,
  onCreateBackup,
}) => {
  const [geminiKey, setGeminiKey] = useState('');
  const [enableGemini, setEnableGemini] = useState(false);
  const [vaultName, setVaultName] = useState(obsidianConfig?.vault_name || 'Learning OS');
  const [vaultPath, setVaultPath] = useState(obsidianConfig?.vault_local_path || '');
  const [memCat, setMemCat] = useState('learner');
  const [memKey, setMemKey] = useState('');
  const [memStatement, setMemStatement] = useState('');
  const [workflowOutput, setWorkflowOutput] = useState<string>('');
  const [testPrompt, setTestPrompt] = useState('Explain how CPU privilege rings enforce memory isolation in 2 sentences.');
  const [testResult, setTestResult] = useState<any | null>(null);
  const [testingPrompt, setTestingPrompt] = useState(false);
  const [busy, setBusy] = useState(false);

  const hw = aiStatus?.hardware;
  const ollama = aiStatus?.ollama;

  return (
    <div className="space-y-6">
      {/* 1. Hardware & Local Ollama Intelligence Panel */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
              Hardware-Aware Local AI Architecture
            </span>
            <h2 className="text-xl font-bold text-white">Local Ollama Primary Provider & Hardware Telemetry</h2>
          </div>
          <button
            type="button"
            onClick={onRefreshStatus}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800"
          >
            <RefreshCw className="h-3.5 w-3.5 text-indigo-400" /> Re-Inspect Hardware & Models
          </button>
        </div>

        {hw && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5 space-y-1">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
                <Cpu className="h-4 w-4 text-indigo-400" /> Host Processor
              </div>
              <div className="text-base font-bold text-white">{hw.cpu_name}</div>
              <div className="text-xs text-slate-400 font-medium">
                {hw.cpu_physical_cores} Physical / {hw.cpu_logical_cores} Logical Cores ({hw.os_name})
              </div>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5 space-y-1">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
                <Server className="h-4 w-4 text-emerald-400" /> Dedicated GPU & VRAM
              </div>
              <div className="text-base font-bold text-emerald-300">{hw.gpu_name}</div>
              <div className="text-xs text-slate-400 font-medium">
                {hw.gpu_vram_total_gb} GB Total VRAM ({hw.gpu_vram_free_gb} GB Free)
              </div>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5 space-y-1">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
                <HardDrive className="h-4 w-4 text-amber-400" /> System Memory & Disk
              </div>
              <div className="text-base font-bold text-white">{hw.ram_total_gb} GB System RAM</div>
              <div className="text-xs text-slate-400 font-medium">
                {hw.ram_available_gb} GB Free RAM · {hw.disk_free_gb} GB Free SSD
              </div>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5 space-y-1">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
                <ShieldCheck className="h-4 w-4 text-indigo-400" /> Local Ollama Engine
              </div>
              <div className="text-base font-bold text-white">
                {ollama?.health?.online ? 'ONLINE (127.0.0.1:11434)' : 'Standby / Local Synthesis'}
              </div>
              <div className="text-xs text-slate-400 font-medium">{hw.ollama_version}</div>
            </div>
          </div>
        )}

        {/* Hardware-Aware Model Recommendations & License Table */}
        {hw?.recommendations && (
          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950 text-slate-400 text-xs font-bold uppercase tracking-wider">
                <tr>
                  <th className="p-4">Model Tag</th>
                  <th className="p-4">Download / VRAM</th>
                  <th className="p-4">Hardware Suitability Assessment</th>
                  <th className="p-4">License & Restrictions</th>
                  <th className="p-4">Action / Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-slate-900/50">
                {hw.recommendations.map((rec: any) => (
                  <tr key={rec.model_tag}>
                    <td className="p-4 font-mono font-bold text-indigo-300">{rec.model_tag}</td>
                    <td className="p-4 text-slate-200">
                      {rec.download_size_gb} GB DL / ~{rec.estimated_vram_gb} GB VRAM
                    </td>
                    <td className="p-4 text-slate-300">{rec.suitability_reason}</td>
                    <td className="p-4 text-slate-300">
                      <strong className="text-slate-100">{rec.license_name}:</strong> {rec.license_notes}
                    </td>
                    <td className="p-4">
                      {rec.is_currently_installed ? (
                        <button
                          type="button"
                          onClick={() =>
                            onUpdateProvider({ provider_name: 'ollama', default_model: rec.model_tag, is_default: true })
                          }
                          className={`rounded-xl px-3.5 py-1.5 font-bold text-xs transition-colors ${
                            ollama?.config?.default_model === rec.model_tag
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                              : 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-sm'
                          }`}
                        >
                          {ollama?.config?.default_model === rec.model_tag ? 'Active Default' : 'Select Model'}
                        </button>
                      ) : (
                        <code className="rounded bg-slate-950 px-2.5 py-1 font-mono text-xs text-amber-300">
                          {rec.pull_command}
                        </code>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Live Ollama Verification Playground */}
        <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950 p-5 space-y-3.5">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-indigo-400">
              <Terminal className="h-4 w-4" /> Live Local AI Model Execution Test
            </span>
            <span className="font-mono text-xs text-slate-400">
              Target: {ollama?.config?.default_model || 'qwen3.5:9b'}
            </span>
          </div>
          <div className="flex gap-3">
            <input
              type="text"
              value={testPrompt}
              onChange={(e) => setTestPrompt(e.target.value)}
              placeholder="Enter a prompt to test your local model..."
              className="flex-1 rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
            />
            <button
              type="button"
              disabled={!testPrompt.trim() || testingPrompt}
              onClick={async () => {
                setTestingPrompt(true);
                try {
                  const res = await axiomApi.testAiGeneration({ prompt: testPrompt });
                  setTestResult(res);
                } catch (err: any) {
                  setTestResult({ content: err.message, status: 'error', latency_ms: 0 });
                } finally {
                  setTestingPrompt(false);
                }
              }}
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 text-sm font-bold text-white hover:bg-indigo-500 disabled:opacity-50 shadow-md transition-colors"
            >
              <Play className="h-4 w-4" />
              {testingPrompt ? 'Generating...' : 'Run Live Test'}
            </button>
          </div>

          {testResult && (
            <div className={`rounded-xl border p-4 text-sm space-y-2 ${
              testResult.status === 'error' ? 'border-rose-900/40 bg-rose-950/20 text-rose-300' : 'border-slate-800 bg-slate-900/80 text-slate-200'
            }`}>
              <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                <span>Model: <strong className="text-indigo-300">{testResult.model}</strong></span>
                <span className="font-mono text-emerald-400 font-bold">{testResult.latency_ms} ms</span>
              </div>
              <p className="font-serif text-[15px] leading-relaxed whitespace-pre-wrap">{testResult.content}</p>
            </div>
          )}
        </div>
      </div>

      {/* 2. Optional Cloud Provider (Google Gemini) with Explicit Opt-In & Privacy Warning */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 space-y-3">
        <div className="flex items-center gap-2 text-amber-300">
          <Lock className="h-4 w-4" />
          <h3 className="text-base font-bold">Optional Cloud Provider: Google Gemini Developer API (Explicit Opt-In)</h3>
        </div>
        <p className="text-xs text-slate-400">
          <strong>Privacy Disclosure:</strong> By default, Axiom OS runs 100% locally via Ollama. If you explicitly
          enable Gemini below, note that free-tier API prompts may be reviewed by Google. Axiom OS never transmits your
          Obsidian vault or local project source code to cloud providers without explicit authorization.
        </p>
        <div className="flex flex-wrap items-center gap-3.5">
          <input
            type="password"
            value={geminiKey}
            onChange={(e) => setGeminiKey(e.target.value)}
            placeholder="Optional: Enter GEMINI_API_KEY..."
            className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
          />
          <label className="flex items-center gap-2 text-sm text-slate-200 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={enableGemini}
              onChange={(e) => setEnableGemini(e.target.checked)}
              className="h-4 w-4 rounded border-slate-700 text-indigo-600 focus:ring-0"
            />
            <span>Explicitly Enable Cloud AI Fallback</span>
          </label>
          <button
            type="button"
            onClick={() =>
              onUpdateProvider({
                provider_name: 'gemini',
                is_enabled: enableGemini,
                api_key: geminiKey || undefined,
                allow_cloud_ai: enableGemini,
              })
            }
            className="rounded-xl bg-slate-800 px-5 py-3 text-sm font-bold text-slate-200 hover:bg-slate-700 transition-colors"
          >
            Save Cloud Policy
          </button>
        </div>
      </div>

      {/* 3. Obsidian Configuration & n8n Local Automation Center */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Obsidian Config */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 sm:p-7 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white">Obsidian Knowledge Vault Sync</h3>
            <span
              className={`rounded-full px-3 py-1 text-xs font-bold ${
                obsidianConfig?.is_enabled ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {obsidianConfig?.is_enabled ? 'Connected' : 'Disabled'}
            </span>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">
            Export Markdown notes with YAML frontmatter and bidirectional wikilinks to your local Obsidian vault.
          </p>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-slate-200 mb-1.5">Obsidian Vault Name</label>
              <input
                type="text"
                value={vaultName}
                onChange={(e) => setVaultName(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-200 mb-1.5">Vault Local Absolute Path</label>
              <input
                type="text"
                value={vaultPath}
                onChange={(e) => setVaultPath(e.target.value)}
                placeholder="e.g. C:/Users/YourName/Documents/MyVault"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <button
              type="button"
              onClick={() =>
                onUpdateObsidian({
                  is_enabled: true,
                  vault_name: vaultName,
                  vault_local_path: vaultPath,
                  read_permission: true,
                  write_permission: true,
                })
              }
              className="w-full rounded-xl bg-indigo-600 py-3 text-sm font-bold text-white hover:bg-indigo-500 shadow-md transition-colors"
            >
              Save Obsidian Vault Settings
            </button>
          </div>
        </div>

        {/* n8n Local Automation Center */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 sm:p-7 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Workflow className="h-5 w-5 text-indigo-400" />
              <h3 className="text-lg font-bold text-white">n8n Local Workflow Automation</h3>
            </div>
            <span
              className={`rounded-full px-3 py-1 text-xs font-bold ${
                automationStatus?.is_online ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {automationStatus?.is_online ? 'n8n Active' : 'Standby Mode'}
            </span>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">
            Automate daily digest synthesis, spaced-repetition notifications, and automated research sync.
          </p>

          <div className="space-y-2.5">
            {[
              { key: 'daily_learning_digest', label: 'Trigger Daily Learning Digest Workflow' },
              { key: 'spaced_repetition_sync', label: 'Sync Spaced Repetition Due Queue' },
              { key: 'weekly_research_digest', label: 'Generate Weekly Research Synthesis' },
            ].map((wf) => (
              <button
                key={wf.key}
                type="button"
                disabled={busy}
                onClick={async () => {
                  setBusy(true);
                  try {
                    const res = await onRunWorkflow(wf.key);
                    setWorkflowOutput(`[Executed ${wf.key}]: ${JSON.stringify(res)}`);
                  } catch (e: any) {
                    setWorkflowOutput(`[Error running ${wf.key}]: ${e.message}`);
                  } finally {
                    setBusy(false);
                  }
                }}
                className="flex w-full items-center justify-between rounded-xl border border-slate-700 bg-slate-950 p-3.5 text-sm font-medium text-slate-200 hover:border-indigo-500 hover:bg-slate-900 transition-colors"
              >
                <span>{wf.label}</span>
                <Play className="h-4 w-4 text-indigo-400" />
              </button>
            ))}
          </div>

          {workflowOutput && (
            <div className="mt-2 rounded-xl bg-slate-950 p-3.5 font-mono text-xs text-slate-300 overflow-x-auto">
              {workflowOutput}
            </div>
          )}
        </div>
      </div>

      {/* 4. Database Backups & 5-Tier Persistent Memory Store */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Backups */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 sm:p-7 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white">Database Snapshot & Backups</h3>
            <button
              type="button"
              onClick={onCreateBackup}
              className="rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-500 shadow-sm transition-colors"
            >
              Create Snapshot Now
            </button>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">
            Zero-loss local SQLite snapshots preserving all journeys, notes, experiments, and memory.
          </p>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {backups.map((b) => (
              <div key={b.id} className="flex items-center justify-between rounded-xl bg-slate-950 p-3 text-xs">
                <span className="font-mono text-slate-200 font-semibold">{b.backup_type} ({b.size_kb} KB)</span>
                <span className="text-slate-400 font-mono">{b.created_at?.slice(0, 19).replace('T', ' ')}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 5-Tier Persistent Memory Store */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 sm:p-7 space-y-4 shadow-sm">
          <h3 className="text-lg font-bold text-white">5-Tier Persistent AI Memory Store</h3>
          <p className="text-sm text-slate-300 leading-relaxed">
            Facts and preferences stored locally so your AI mentor remembers your background across weeks.
          </p>

          <div className="flex gap-2.5">
            <select
              value={memCat}
              onChange={(e) => setMemCat(e.target.value)}
              className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs font-semibold text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="learner">Learner Profile</option>
              <option value="journey">Journey Fact</option>
              <option value="project">Project Fact</option>
              <option value="research">Research Fact</option>
            </select>
            <input
              type="text"
              value={memKey}
              onChange={(e) => setMemKey(e.target.value)}
              placeholder="Key (e.g. math_background)..."
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div className="flex gap-2.5">
            <input
              type="text"
              value={memStatement}
              onChange={(e) => setMemStatement(e.target.value)}
              placeholder="Statement: e.g. Familiar with linear algebra and Python..."
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="button"
              disabled={!memKey || !memStatement}
              onClick={async () => {
                await onAddMemory(memCat, memKey, memStatement);
                setMemKey('');
                setMemStatement('');
              }}
              className="rounded-xl bg-indigo-600 px-5 py-2 text-xs font-bold text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors shadow-sm"
            >
              Add Fact
            </button>
          </div>

          <div className="space-y-2 max-h-40 overflow-y-auto">
            {memories.map((m) => (
              <div key={m.id} className="flex items-center justify-between rounded-xl bg-slate-950 p-3 text-xs">
                <div>
                  <span className="font-bold text-indigo-300">[{m.memory_category}] </span>
                  <span className="text-slate-200">{m.fact_statement}</span>
                </div>
                <button
                  type="button"
                  onClick={() => onDeleteMemory(m.id)}
                  className="text-slate-400 hover:text-rose-400 p-1"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
