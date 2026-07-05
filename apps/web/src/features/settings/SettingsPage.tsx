import React, { useState, useEffect } from "react";
import { Sliders, Server, Activity, ShieldCheck, Play } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Spinner } from "../../components/ui/Spinner";

export const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"general" | "providers" | "routing" | "health">("general");
  const [loading, setLoading] = useState(false);
  const [keys, setKeys] = useState<Record<string, string>>({
    openai: "",
    openrouter: "",
    anthropic: "",
    gemini: ""
  });
  const [keyStatus, setKeyStatus] = useState<Record<string, string>>({});
  const [testingStatus, setTestingStatus] = useState<Record<string, string>>({});
  const [routing, setRouting] = useState<Record<string, string[]>>({
    parsing: [],
    summary: [],
    questions: [],
    default: []
  });
  const [health, setHealth] = useState<any>(null);
  const [models, setModels] = useState<{ id: string; name: string; free: boolean }[]>([]);

  // Fetch all preferences on mount
  useEffect(() => {
    const initSettings = async () => {
      setLoading(true);
      try {
        const keyStats = await api.getKeys();
        setKeyStatus(keyStats);
        
        const routeData = await api.getRouting();
        setRouting(routeData);
        
        const healthData = await api.getHealth();
        setHealth(healthData);

        const modelsData = await api.getModels();
        setModels(modelsData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    initSettings();
  }, []);

  const handleSaveKey = async (provider: string) => {
    const keyVal = keys[provider];
    if (!keyVal) return;
    try {
      await api.saveKey(provider, keyVal);
      setKeyStatus(prev => ({ ...prev, [provider]: "configured" }));
      setKeys(prev => ({ ...prev, [provider]: "" }));
    } catch (err) {
      alert("Failed to save API key");
    }
  };

  const handleTestKey = async (provider: string) => {
    const keyVal = keys[provider];
    if (!keyVal) return;
    setTestingStatus(prev => ({ ...prev, [provider]: "testing" }));
    try {
      const res = await api.testKey(provider, keyVal);
      setTestingStatus(prev => ({ ...prev, [provider]: res.valid ? "valid" : "invalid" }));
    } catch (err) {
      setTestingStatus(prev => ({ ...prev, [provider]: "invalid" }));
    }
  };

  const handleRoutingChange = (task: string, idx: number, val: string) => {
    setRouting(prev => {
      const updated = { ...prev };
      const current = [...(updated[task] || [])];
      current[idx] = val;
      updated[task] = current;
      return updated;
    });
  };

  const handleSaveRouting = async () => {
    try {
      await api.saveRouting(routing);
      alert("Model routing matrix saved successfully.");
    } catch (err) {
      alert("Failed to save routing settings");
    }
  };

  const tabs = [
    { id: "general", label: "Scoring Weight", icon: Sliders },
    { id: "providers", label: "AI Providers", icon: Server },
    { id: "routing", label: "Model Routing Matrix", icon: Play },
    { id: "health", label: "System Health", icon: Activity }
  ] as const;



  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="p-10 max-w-4xl w-full mx-auto space-y-8"
    >
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
          Platform Settings & Configurations
        </h1>
        <p className="text-zinc-500 text-sm mt-1">
          Review core metrics weighting, model routing defaults, and local data directories.
        </p>
      </div>

      {/* Tabs list */}
      <div className="flex border-b border-zinc-200 gap-1 overflow-x-auto pb-px">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold border-b-2 transition-all shrink-0 ${
                isActive
                  ? "border-zinc-950 text-zinc-950 font-bold"
                  : "border-transparent text-zinc-500 hover:text-zinc-900"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="p-12 flex justify-center">
          <Spinner />
        </div>
      ) : (
        <div className="mt-4">
          <AnimatePresence mode="wait">
            {activeTab === "general" && (
              <motion.div
                key="general"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.15 }}
                className="border border-zinc-200 rounded-xl p-6 bg-white space-y-4 shadow-sm"
              >
                <h3 className="text-sm font-semibold text-zinc-950 flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-zinc-950 stroke-[1.5]" />
                  <span>Scoring Weight Breakdown</span>
                </h3>
                <p className="text-xs text-zinc-500 leading-normal">
                  ScreenIt scoring weights are set inside the Python ranking modules:
                </p>
                <div className="space-y-4 pt-2">
                  {[
                    { label: "Semantic Similarity Match", pct: 50, desc: "SentenceTransformer all-MiniLM-L6-v2 vector match" },
                    { label: "Role Required Skills", pct: 25, desc: "Direct keyword matrix intersection match" },
                    { label: "Minimum Experience Years", pct: 15, desc: "Normalized experience duration check" },
                    { label: "Education Level Requirements", pct: 10, desc: "Degree hierarchy validation match" },
                  ].map((wt) => (
                    <div key={wt.label} className="space-y-1.5">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-semibold text-zinc-800">{wt.label}</span>
                        <span className="font-mono text-zinc-500 font-bold">{wt.pct}%</span>
                      </div>
                      <div className="w-full bg-zinc-100 rounded-full h-1.5">
                        <div className="bg-zinc-950 h-1.5 rounded-full" style={{ width: `${wt.pct}%` }} />
                      </div>
                      <p className="text-[10px] text-zinc-400">{wt.desc}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === "providers" && (
              <motion.div
                key="providers"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.15 }}
                className="space-y-6"
              >
                <div className="border border-zinc-200 rounded-xl p-6 bg-white space-y-4 shadow-sm">
                  <h3 className="text-sm font-semibold text-zinc-950 flex items-center gap-2">
                    <Server className="w-4 h-4 text-zinc-950 stroke-[1.5]" />
                    <span>AI Provider API Keys</span>
                  </h3>
                  <p className="text-xs text-zinc-500 leading-normal">
                    Secrets are managed securely via backend configuration mutations writing directly to `.env`.
                  </p>

                  <div className="space-y-5 pt-2">
                    {["openai", "openrouter", "anthropic", "gemini"].map((provider) => {
                      const isConfigured = keyStatus[provider] === "configured";
                      const testState = testingStatus[provider];
                      return (
                        <div key={provider} className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl border border-zinc-200 bg-zinc-50/50">
                          <div className="space-y-1">
                            <span className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold">{provider}</span>
                            <div className="flex items-center gap-2">
                              <h4 className="text-sm font-bold text-zinc-850 capitalize">{provider} API</h4>
                              {isConfigured ? (
                                <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-150">
                                  <ShieldCheck className="w-3 h-3" /> Configured
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-zinc-500 bg-zinc-150 px-2 py-0.5 rounded">
                                  Missing
                                </span>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <input
                              type="password"
                              placeholder={isConfigured ? "••••••••••••••••" : "Paste your API key"}
                              value={keys[provider] || ""}
                              onChange={(e) => setKeys(prev => ({ ...prev, [provider]: e.target.value }))}
                              className="px-3 py-1.5 text-xs rounded border border-zinc-200 focus:outline-none focus:ring-1 focus:ring-zinc-950 bg-white min-w-[200px]"
                            />
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => handleTestKey(provider)}
                              disabled={!keys[provider]}
                              className="text-xs"
                            >
                              {testState === "testing" ? <Spinner className="w-3.5 h-3.5" /> : testState === "valid" ? "Verified" : "Test Key"}
                            </Button>
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => handleSaveKey(provider)}
                              disabled={!keys[provider]}
                              className="text-xs"
                            >
                              Save
                            </Button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === "routing" && (
              <motion.div
                key="routing"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.15 }}
                className="border border-zinc-200 rounded-xl p-6 bg-white space-y-6 shadow-sm"
              >
                <div className="flex justify-between items-center border-b border-zinc-200 pb-4">
                  <div className="space-y-1">
                    <h3 className="text-sm font-semibold text-zinc-950">AI Orchestrator routing cascades</h3>
                    <p className="text-xs text-zinc-500 leading-normal">
                      Customize task routing execution priorities. Cascades cascade down to the next model in case of failures.
                    </p>
                  </div>
                  <Button variant="primary" size="sm" onClick={handleSaveRouting}>
                    Save Matrix
                  </Button>
                </div>

                <div className="space-y-6 divide-y divide-zinc-150">
                  {["parsing", "summary", "questions", "default"].map((task) => {
                    const taskPrefs = routing[task] || [];
                    return (
                      <div key={task} className="pt-4 first:pt-0 space-y-3">
                        <span className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold">{task} Task Cascade</span>
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                          {[0, 1, 2, 3, 4].map((cascadeIdx) => (
                            <div key={cascadeIdx} className="space-y-1">
                              <span className="text-[10px] text-zinc-400 font-semibold font-mono">Priority #{cascadeIdx + 1}</span>
                              <select
                                value={taskPrefs[cascadeIdx] || "offline"}
                                onChange={(e) => handleRoutingChange(task, cascadeIdx, e.target.value)}
                                className="w-full text-xs p-2 border border-zinc-200 rounded bg-zinc-50 focus:outline-none focus:ring-1 focus:ring-zinc-950"
                              >
                                {models.length === 0 ? (
                                  <>
                                    <option value="openai">OPENAI</option>
                                    <option value="qwen">QWEN</option>
                                    <option value="anthropic">ANTHROPIC</option>
                                    <option value="gemini">GEMINI</option>
                                    <option value="offline">Offline Fallback</option>
                                  </>
                                ) : (
                                  <>
                                    <optgroup label="Free Tier Models">
                                      {models.filter(m => m.free).map((m) => (
                                        <option key={m.id} value={m.id}>
                                          {m.name}
                                        </option>
                                      ))}
                                    </optgroup>
                                    <optgroup label="Paid Models">
                                      {models.filter(m => !m.free).map((m) => (
                                        <option key={m.id} value={m.id}>
                                          {m.name}
                                        </option>
                                      ))}
                                    </optgroup>
                                  </>
                                )}
                              </select>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {activeTab === "health" && (
              <motion.div
                key="health"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.15 }}
                className="border border-zinc-200 rounded-xl p-6 bg-white space-y-4 shadow-sm"
              >
                <h3 className="text-sm font-semibold text-zinc-950 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-zinc-950 stroke-[1.5]" />
                  <span>Platform Diagnostics</span>
                </h3>
                
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { name: "Backend API Connection", status: health?.status === "offline" ? "Offline" : "Online", ok: health?.status !== "offline" },
                    { name: "Embedding Model Loading", status: health?.embeddings === "loaded" ? "Loaded" : "Failed", ok: health?.embeddings === "loaded" },
                    { name: "SQLite DB Status", status: health?.database === "connected" ? "Connected" : "Disconnected", ok: health?.database === "connected" },
                  ].map((sys) => (
                    <div key={sys.name} className="flex justify-between items-center bg-zinc-50 border border-zinc-100 p-3.5 rounded-lg">
                      <span className="text-xs font-semibold text-zinc-700">{sys.name}</span>
                      <span className={`flex items-center gap-1.5 text-[11px] font-mono font-bold ${sys.ok ? "text-emerald-700" : "text-rose-700"}`}>
                        <div className={`w-2 h-2 rounded-full ${sys.ok ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`} />
                        {sys.status}
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
};

