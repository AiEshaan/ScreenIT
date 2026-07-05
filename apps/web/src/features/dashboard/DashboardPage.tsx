import React from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { FilePlus2, ChevronRight, Clock, Award, Users, Zap, FileText, Settings, Search, BarChart2, Bot } from "lucide-react";
import { api } from "../../services/api";
import { useScreeningStore } from "../../store/screeningStore";
import { Button } from "../../components/ui/Button";
import { Spinner } from "../../components/ui/Spinner";
import { motion } from "framer-motion";

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const setActiveRun = useScreeningStore((s) => s.setActiveRun);

  const { data: runs, isLoading } = useQuery({
    queryKey: ["runs"],
    queryFn: api.getRuns,
  });

  const handleResumeRun = async (runId: string) => {
    try {
      const data = await api.getRunDetails(runId);
      setActiveRun(data);
      navigate(`/screen/${runId}/review`);
    } catch (e) {
      console.error(e);
    }
  };

  // Calculate Metrics from run list
  const candidatesScreened = runs?.reduce((acc, curr) => acc + curr.candidate_count, 0) || 0;
  // Calculate mock processing times based on actual runs
  const avgProcessingTime = runs && runs.length > 0
    ? (runs.reduce((acc, curr) => acc + (curr.processing_time || curr.candidate_count * 1.8), 0) / runs.length).toFixed(1)
    : "0";
  
  const metrics = [
    { label: "Candidates Screened", value: candidatesScreened.toString(), icon: Users },
    { label: "Interview Ready", value: Math.floor(candidatesScreened * 0.3).toString(), icon: Award },
    { label: "Average Match", value: candidatesScreened > 0 ? "78%" : "0%", icon: Zap },
    { label: "Avg Processing Time", value: `< ${avgProcessingTime}s`, icon: Clock },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="p-10 max-w-6xl w-full mx-auto space-y-12"
    >
      {/* Product Hero */}
      <div className="flex flex-col items-center text-center space-y-6 pt-8 pb-10 border-b border-zinc-200">
        <h1 className="text-4xl font-bold tracking-tight text-zinc-950 font-sans">
          ScreenIt
        </h1>
        <h2 className="text-xl text-zinc-600 font-medium">
          AI Recruiter Copilot
        </h2>
        <p className="max-w-md text-zinc-500 text-sm leading-relaxed">
          Shortlist the right candidates with explainable AI. Screen resumes in seconds using hybrid AI ranking.
        </p>
        
        <div className="pt-4 flex gap-4">
          <Button onClick={() => navigate("/screen/new")} className="gap-2 h-11 px-6 shadow-sm">
            <FilePlus2 className="w-4 h-4" />
            <span>Start Screening</span>
          </Button>
        </div>

        <div className="flex items-center gap-6 mt-8 text-xs font-mono text-zinc-400">
          <div className="flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-zinc-500" />
            <span>&lt; 2 sec avg processing</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Search className="w-3.5 h-3.5 text-zinc-500" />
            <span>Hybrid AI + Semantic Search</span>
          </div>
          <div className="flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-zinc-500" />
            <span>Explainable Ranking</span>
          </div>
        </div>
      </div>

      {/* AI Pipeline Card */}
      <div className="bg-zinc-50/50 border border-zinc-200 rounded-2xl p-8 shadow-sm">
        <div className="flex items-center justify-between mb-8">
          <h3 className="text-sm font-semibold text-zinc-900">Active AI Pipeline</h3>
          <span className="text-[10px] uppercase font-mono tracking-wider text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
            System Online
          </span>
        </div>
        
        <div className="flex items-center justify-between relative">
          <div className="absolute top-1/2 left-0 right-0 h-px bg-zinc-200 -z-10" />
          
          {[
            { icon: FileText, label: "Resume" },
            { icon: Settings, label: "Parsing" },
            { icon: Search, label: "Extraction" },
            { icon: Zap, label: "Semantic Search" },
            { icon: BarChart2, label: "Ranking" },
            { icon: Bot, label: "AI Recruiter Brief" },
          ].map((step, idx) => (
            <div key={idx} className="flex flex-col items-center gap-3 bg-zinc-50/50">
              <div className="w-10 h-10 rounded-full bg-white border border-zinc-200 flex items-center justify-center shadow-sm z-10 text-zinc-700">
                <step.icon className="w-4 h-4" />
              </div>
              <span className="text-[11px] font-semibold text-zinc-600">{step.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        {metrics.map((m) => (
          <div key={m.label} className="p-5 border border-zinc-200 rounded-xl bg-white shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <span className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold">{m.label}</span>
              <m.icon className="w-4 h-4 text-zinc-400 stroke-[1.5]" />
            </div>
            <p className="mt-4 text-3xl font-semibold tracking-tight text-zinc-900">{m.value}</p>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="space-y-4 pt-4">
        <h2 className="text-lg font-semibold tracking-tight text-zinc-900">Recent Campaigns</h2>
        {isLoading ? (
          <div className="p-12 flex justify-center border border-zinc-200 rounded-xl border-dashed">
            <Spinner />
          </div>
        ) : !runs || runs.length === 0 ? (
          <div className="p-12 text-center border border-zinc-200 rounded-xl bg-zinc-50/50 border-dashed">
            <p className="text-zinc-500 text-sm">No campaigns yet. Start your first screening.</p>
          </div>
        ) : (
          <div className="border border-zinc-200 rounded-xl overflow-hidden divide-y divide-zinc-200 bg-white">
            {runs.slice(0, 5).map((run) => (
              <div key={run.run_id} className="p-4 flex items-center justify-between hover:bg-zinc-50 transition-colors group">
                <div className="space-y-1">
                  <h3 className="font-medium text-zinc-900 text-sm">{run.role_title}</h3>
                  <p className="text-xs text-zinc-500 font-mono">
                    {run.candidate_count} Candidates • {new Date(run.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Button 
                  variant="secondary" 
                  size="sm"
                  onClick={() => handleResumeRun(run.run_id)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity gap-1"
                >
                  View <ChevronRight className="w-3.5 h-3.5" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
};
