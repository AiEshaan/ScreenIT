import React from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Users, ChevronRight, FileSpreadsheet } from "lucide-react";
import { api } from "../../services/api";
import { useScreeningStore } from "../../store/screeningStore";
import { Spinner } from "../../components/ui/Spinner";
import { motion } from "framer-motion";

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const setActiveRun = useScreeningStore((s) => s.setActiveRun);

  const { data: runs, isLoading } = useQuery({
    queryKey: ["runs"],
    queryFn: api.getRuns,
  });

  const loadRun = async (runId: string) => {
    try {
      const details = await api.getRunDetails(runId);
      setActiveRun(details);
      navigate(`/screen/${runId}/review`);
    } catch (err) {
      console.error(err);
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const normalized = dateStr.includes(" ") && !dateStr.includes("T")
        ? dateStr.replace(" ", "T") + "Z"
        : dateStr;
      const d = new Date(normalized);
      return isNaN(d.getTime()) ? dateStr : d.toLocaleDateString();
    } catch (e) {
      return dateStr;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="p-10 max-w-4xl w-full mx-auto space-y-8"
    >
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
          Campaign History Log
        </h1>
        <p className="text-zinc-500 text-sm mt-1">
          Review and audit past candidate shortlists stored inside the local SQLite database.
        </p>
      </div>

      {isLoading ? (
        <div className="h-64 border border-zinc-200 rounded-xl flex items-center justify-center bg-zinc-50/20">
          <Spinner />
        </div>
      ) : !runs || runs.length === 0 ? (
        <div className="border border-dashed border-zinc-200 rounded-xl p-16 text-center bg-zinc-50/10">
          <FileSpreadsheet className="w-12 h-12 text-zinc-300 mx-auto stroke-[1.5] mb-4" />
          <h3 className="text-sm font-semibold text-zinc-900">No campaigns found</h3>
          <p className="text-zinc-500 text-xs mt-1">
            Your screening runs will appear here as soon as you create them.
          </p>
        </div>
      ) : (
        <div className="border border-zinc-200 rounded-xl overflow-hidden bg-white shadow-sm">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-zinc-200 bg-zinc-50/50 font-mono text-[10px] text-zinc-400 font-bold uppercase tracking-wider">
                <th className="p-4 pl-6">Campaign Role</th>
                <th className="p-4">Candidates</th>
                <th className="p-4">Created Date</th>
                <th className="p-4 pr-6 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-150">
              {runs.map((run) => (
                <tr
                  key={run.run_id}
                  onClick={() => loadRun(run.run_id)}
                  className="hover:bg-zinc-50 cursor-pointer group text-sm"
                >
                  <td className="p-4 pl-6">
                    <span className="font-semibold text-zinc-900 group-hover:text-zinc-950 transition-colors">
                      {run.role_title}
                    </span>
                  </td>
                  <td className="p-4 text-zinc-500">
                    <span className="inline-flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-zinc-400" />
                      {run.candidate_count} Candidates
                    </span>
                  </td>
                  <td className="p-4 text-zinc-500 font-mono text-xs">
                    {formatDate(run.created_at)}
                  </td>
                  <td className="p-4 pr-6 text-right">
                    <button className="inline-flex items-center gap-1.5 text-xs text-zinc-500 font-medium group-hover:text-zinc-950 transition-colors">
                      <span>View Shortlist</span>
                      <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
};
