import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Scale, ChevronLeft } from "lucide-react";
import { useScreeningStore } from "../../store/screeningStore";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { motion } from "framer-motion";

export const ComparisonPage: React.FC = () => {
  const navigate = useNavigate();
  const activeRun = useScreeningStore((s) => s.activeRun);
  const comparisonIds = useScreeningStore((s) => s.comparisonIds);
  const clearComparison = useScreeningStore((s) => s.clearComparison);

  if (!activeRun) {
    return (
      <div className="p-10 text-center space-y-4">
                <p className="text-zinc-500">No active campaign loaded.</p>
        <Link to="/">
          <Button variant="secondary">Go back</Button>
        </Link>
      </div>
    );
  }

  const selectedCandidates = activeRun.candidates.filter((c) =>
    comparisonIds.includes(c.id)
  );

  if (selectedCandidates.length === 0) {
    return (
      <div className="p-10 max-w-2xl mx-auto text-center space-y-4 mt-20">
        <Scale className="w-12 h-12 text-zinc-300 mx-auto" />
        <h2 className="text-lg font-semibold text-zinc-950">No candidates queued</h2>
        <p className="text-zinc-500 text-sm">
          Go back to the review panel and check the boxes next to the candidates you wish to compare side-by-side.
        </p>
        <Button variant="secondary" onClick={() => navigate(-1)}>
          Back to Candidate Review
        </Button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex-1 flex flex-col h-screen overflow-hidden bg-white"
    >
      {/* Sub Header */}
      <div className="p-6 border-b border-zinc-200 bg-white flex justify-between items-center shrink-0">
        <div className="space-y-1">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-900 transition-colors font-medium"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Back to Candidate Review</span>
          </button>
          <h1 className="text-xl font-bold tracking-tight text-zinc-900 flex items-center gap-2">
            <Scale className="w-5 h-5 text-zinc-950" />
            <span>Candidate Comparison Matrix</span>
          </h1>
        </div>

        <Button
          variant="secondary"
          size="sm"
          onClick={clearComparison}
          className="text-xs h-9 rounded-lg"
        >
          Clear Selection
        </Button>
      </div>

      {/* Grid Comparison Matrix container */}
      <div className="flex-1 overflow-x-auto overflow-y-auto p-8">
        <div className="min-w-[800px] max-w-6xl mx-auto border border-zinc-200 rounded-xl overflow-hidden divide-y divide-zinc-200 shadow-sm bg-white">
          {/* Header Row */}
          <div className="grid grid-flow-col auto-cols-fr bg-zinc-50/50 font-mono text-[10px] text-zinc-400 font-bold uppercase tracking-wider divide-x divide-zinc-200">
            <div className="p-4 bg-zinc-50/80">Parameter</div>
            {selectedCandidates.map((cand) => (
              <div key={cand.id} className="p-4 flex flex-col justify-between">
                <span className="text-zinc-950 text-xs font-sans font-bold capitalize normal-case truncate">
                  {cand.name}
                </span>
                <span className="mt-1 font-mono text-[10px] text-zinc-500">
                  Overall Score: {cand.overall_score}
                </span>
              </div>
            ))}
          </div>

          {/* Score Bars */}
          <div className="grid grid-flow-col auto-cols-fr divide-x divide-zinc-200 text-xs bg-zinc-50/30">
            <div className="p-4 font-semibold text-zinc-900 bg-zinc-50/20">Score Breakdown</div>
            {selectedCandidates.map((cand) => (
              <div key={cand.id} className="p-4 space-y-2">
                {([
                  { label: "Semantic", value: cand.scores.semantic },
                  { label: "Skills", value: cand.scores.skills },
                  { label: "Experience", value: cand.scores.experience },
                  { label: "Education", value: cand.scores.education },
                ] as const).map((dim) => (
                  <div key={dim.label}>
                    <div className="flex justify-between items-center mb-0.5">
                      <span className="text-[10px] text-zinc-500 font-mono">{dim.label}</span>
                      <span className="text-[10px] text-zinc-700 font-mono font-bold">{dim.value}</span>
                    </div>
                    <div className="w-full bg-zinc-100 rounded-full h-1">
                      <div
                        className={`h-1 rounded-full ${
                          dim.value >= 80 ? "bg-emerald-500" : dim.value >= 60 ? "bg-amber-400" : "bg-rose-400"
                        }`}
                        style={{ width: `${dim.value}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>

          {/* Fit Status */}
          <div className="grid grid-flow-col auto-cols-fr divide-x divide-zinc-200 text-xs">
            <div className="p-4 font-semibold text-zinc-900 bg-zinc-50/20">Fit Analysis</div>
            {selectedCandidates.map((cand) => (
              <div key={cand.id} className="p-4 space-y-1">
                <Badge variant={cand.overall_score >= 80 ? "success" : "warning"}>
                  {cand.match_status}
                </Badge>
                <div className="text-[10px] text-zinc-400 font-mono">
                  Confidence: {cand.confidence}
                </div>
              </div>
            ))}
          </div>

          {/* Recruiter brief */}
          <div className="grid grid-flow-col auto-cols-fr divide-x divide-zinc-200 text-xs">
            <div className="p-4 font-semibold text-zinc-900 bg-zinc-50/20">Recruiter Brief</div>
            {selectedCandidates.map((cand) => (
              <div key={cand.id} className="p-4 text-zinc-600 leading-relaxed italic">
                "{cand.recruiter_brief}"
              </div>
            ))}
          </div>

          {/* Education & Exp */}
          <div className="grid grid-flow-col auto-cols-fr divide-x divide-zinc-200 text-xs">
            <div className="p-4 font-semibold text-zinc-900 bg-zinc-50/20">Background</div>
            {selectedCandidates.map((cand) => (
              <div key={cand.id} className="p-4 space-y-1">
                <div>
                  <span className="font-semibold text-zinc-800">Experience:</span>{" "}
                  {cand.experience_years} years
                </div>
                <div>
                  <span className="font-semibold text-zinc-800">Education:</span>{" "}
                  {cand.education_degree} degree
                </div>
              </div>
            ))}
          </div>

          {/* Matched Skills */}
          <div className="grid grid-flow-col auto-cols-fr divide-x divide-zinc-200 text-xs">
            <div className="p-4 font-semibold text-zinc-900 bg-zinc-50/20">Matched Skills</div>
            {selectedCandidates.map((cand) => (
              <div key={cand.id} className="p-4">
                <div className="flex flex-wrap gap-1">
                  {cand.matched_skills.slice(0, 8).map((skill) => (
                    <Badge key={skill} variant="success" className="text-[10px] py-0">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Missing Skills */}
          <div className="grid grid-flow-col auto-cols-fr divide-x divide-zinc-200 text-xs">
            <div className="p-4 font-semibold text-zinc-900 bg-zinc-50/20">Missing Skills</div>
            {selectedCandidates.map((cand) => (
              <div key={cand.id} className="p-4">
                <div className="flex flex-wrap gap-1">
                  {cand.missing_skills.length > 0 ? (
                    cand.missing_skills.slice(0, 8).map((skill) => (
                      <Badge key={skill} variant="error" className="text-[10px] py-0">
                        {skill}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-[10px] text-zinc-400 font-mono">None missing</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Interview questions */}
          <div className="grid grid-flow-col auto-cols-fr divide-x divide-zinc-200 text-xs">
            <div className="p-4 font-semibold text-zinc-900 bg-zinc-50/20">Targeted Qs</div>
            {selectedCandidates.map((cand) => (
              <div key={cand.id} className="p-4 space-y-2">
                {cand.interview_questions?.slice(0, 2).map((q, idx) => (
                  <div key={idx} className="text-[11px] text-zinc-700 leading-normal pl-2 border-l border-zinc-200">
                    {q}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};
