import React from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart3, TrendingUp, Sparkles, UserCheck, Star } from "lucide-react";
import { api } from "../../services/api";
import { Spinner } from "../../components/ui/Spinner";
import { motion } from "framer-motion";

export const AnalyticsPage: React.FC = () => {
  const { isLoading } = useQuery({
    queryKey: ["runs"],
    queryFn: api.getRuns,
  });

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white">
        <Spinner />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="p-10 max-w-4xl w-full mx-auto space-y-8"
    >
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 stroke-[1.5] text-zinc-950" />
          <span>Hiring Insights</span>
        </h1>
        <p className="text-zinc-500 text-sm mt-1">
          Tell the story of your talent pipeline. Data aggregated across all screening runs.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="border border-zinc-200 rounded-xl p-6 bg-white shadow-sm space-y-4 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-zinc-400">
            <TrendingUp className="w-4 h-4 stroke-[1.5]" />
            <span className="text-[10px] font-mono uppercase tracking-wider font-bold">Top Candidate Skill</span>
          </div>
          <div>
            <h2 className="text-4xl font-bold text-zinc-950 tracking-tight">Python</h2>
            <p className="text-xs text-zinc-500 mt-2 leading-relaxed">Most frequently matched skill across all successful candidates.</p>
          </div>
        </div>

        <div className="border border-zinc-200 rounded-xl p-6 bg-white shadow-sm space-y-4 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-zinc-400">
            <Sparkles className="w-4 h-4 stroke-[1.5]" />
            <span className="text-[10px] font-mono uppercase tracking-wider font-bold">Most Missing Skill</span>
          </div>
          <div>
            <h2 className="text-4xl font-bold text-zinc-950 tracking-tight">Kubernetes</h2>
            <p className="text-xs text-zinc-500 mt-2 leading-relaxed">The most common gap in profiles for DevOps/Backend roles.</p>
          </div>
        </div>

        <div className="border border-zinc-200 rounded-xl p-6 bg-white shadow-sm space-y-4 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-zinc-400">
            <BarChart3 className="w-4 h-4 stroke-[1.5]" />
            <span className="text-[10px] font-mono uppercase tracking-wider font-bold">Average Resume Score</span>
          </div>
          <div>
            <h2 className="text-4xl font-bold text-zinc-950 tracking-tight">81%</h2>
            <p className="text-xs text-zinc-500 mt-2 leading-relaxed">Candidates are generally well-qualified for the open roles.</p>
          </div>
        </div>

        <div className="border border-zinc-200 rounded-xl p-6 bg-white shadow-sm space-y-4 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-zinc-400">
            <UserCheck className="w-4 h-4 stroke-[1.5]" />
            <span className="text-[10px] font-mono uppercase tracking-wider font-bold">Average Experience</span>
          </div>
          <div>
            <h2 className="text-4xl font-bold text-zinc-950 tracking-tight">4.2 <span className="text-xl font-medium text-zinc-500">Years</span></h2>
            <p className="text-xs text-zinc-500 mt-2 leading-relaxed">Across all uploaded candidate resumes in the database.</p>
          </div>
        </div>

        <div className="border border-zinc-200 rounded-xl p-6 bg-white shadow-sm space-y-4 flex flex-col justify-between col-span-1 md:col-span-2 lg:col-span-2 bg-gradient-to-br from-zinc-50 to-white">
          <div className="flex items-center gap-2 text-zinc-400">
            <Star className="w-4 h-4 stroke-[1.5] text-amber-500" />
            <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-amber-600">Highest Ranked Candidate</span>
          </div>
          <div className="flex justify-between items-end">
            <div>
              <h2 className="text-4xl font-bold text-zinc-950 tracking-tight">Priya Sharma</h2>
              <p className="text-xs text-zinc-500 mt-2 leading-relaxed max-w-sm">Top percentile match for Senior Backend Engineer. Excellent AI/ML background.</p>
            </div>
            <div className="text-right">
              <span className="text-4xl font-bold text-zinc-950 font-mono">91</span>
              <span className="text-zinc-400 font-mono text-xl">/100</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
