import React from "react";
import { Sliders, Server, Activity } from "lucide-react";
import { motion } from "framer-motion";

export const SettingsPage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="p-10 max-w-3xl w-full mx-auto space-y-8"
    >
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
          Platform Settings & Configurations
        </h1>
        <p className="text-zinc-500 text-sm mt-1">
          Review core metrics weighting, model routing defaults, and local data directories.
        </p>
      </div>

      <div className="space-y-6">
        {/* System Status */}
        <div className="border border-zinc-200 rounded-xl p-6 bg-white space-y-4 shadow-sm">
          <h3 className="text-sm font-semibold text-zinc-950 flex items-center gap-2">
            <Activity className="w-4 h-4 text-zinc-950 stroke-[1.5]" />
            <span>System Status</span>
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { name: "Backend API", status: "Online" },
              { name: "Embedding Model", status: "Loaded" },
              { name: "SQLite DB", status: "Connected" },
              { name: "OpenRouter API", status: "Connected" },
            ].map((sys) => (
              <div key={sys.name} className="flex justify-between items-center bg-zinc-50 border border-zinc-100 p-3 rounded-lg">
                <span className="text-xs font-semibold text-zinc-700">{sys.name}</span>
                <span className="flex items-center gap-1.5 text-[11px] font-mono font-bold text-emerald-700">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse" />
                  {sys.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Providers list */}
        <div className="border border-zinc-200 rounded-xl p-6 bg-white space-y-4 shadow-sm">
          <h3 className="text-sm font-semibold text-zinc-950 flex items-center gap-2">
            <Server className="w-4 h-4 text-zinc-950 stroke-[1.5]" />
            <span>AI Providers & Router Transparency</span>
          </h3>
          <p className="text-xs text-zinc-500 leading-normal">
            The hybrid routing engine dynamically fails over across multiple AI models based on task requirements.
          </p>

          <div className="grid grid-cols-2 gap-4 pt-2">
            {[
              { name: "GPT-OSS 120B", status: "Active", dot: "bg-emerald-500" },
              { name: "Qwen3 Next 80B", status: "Standby", dot: "bg-amber-400" },
              { name: "Llama 3.3 70B", status: "Standby", dot: "bg-amber-400" },
              { name: "Gemma 3 27B", status: "Standby", dot: "bg-amber-400" },
              { name: "Offline Rule Engine", status: "Ready", dot: "bg-emerald-500" },
            ].map((provider) => (
              <div key={provider.name} className="flex flex-col gap-1.5 p-4 rounded-xl border border-zinc-200 bg-zinc-50">
                <span className="text-sm font-bold text-zinc-900">{provider.name}</span>
                <span className="flex items-center gap-1.5 text-xs text-zinc-500 font-mono">
                  <div className={`w-1.5 h-1.5 rounded-full ${provider.dot}`} />
                  {provider.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Core Algorithm scoring weights */}
        <div className="border border-zinc-200 rounded-xl p-6 bg-white space-y-4 shadow-sm">
          <h3 className="text-sm font-semibold text-zinc-950 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-zinc-950 stroke-[1.5]" />
            <span>Scoring Weight Breakdown</span>
          </h3>
          <p className="text-xs text-zinc-500 leading-normal">
            ScreenIt scoring weights are set inside the Python ranking modules:
          </p>
          <div className="space-y-3 pt-2">
            {[
              { label: "Semantic Similarity Match", pct: 40, desc: "SentenceTransformer all-MiniLM-L6-v2 vector match" },
              { label: "Role Required Skills", pct: 30, desc: "Direct keyword matrix intersection match" },
              { label: "Minimum Experience Years", pct: 20, desc: "Normalized experience duration check" },
              { label: "Education Level Requirements", pct: 10, desc: "Degree hierarchy validation match" },
            ].map((wt) => (
              <div key={wt.label} className="space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-zinc-800">{wt.label}</span>
                  <span className="font-mono text-zinc-500">{wt.pct}%</span>
                </div>
                <div className="w-full bg-zinc-100 rounded-full h-1.5">
                  <div className="bg-zinc-950 h-1.5 rounded-full" style={{ width: `${wt.pct}%` }} />
                </div>
                <p className="text-[10px] text-zinc-400">{wt.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};
