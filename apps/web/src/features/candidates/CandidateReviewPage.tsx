import React from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Mail,
  Phone,
  Linkedin,
  Github,
  AlertCircle,
  Scale,
  Sparkles,
  BookmarkCheck,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Star,
  Download,
} from "lucide-react";
import { api } from "../../services/api";
import { useScreeningStore } from "../../store/screeningStore";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Spinner } from "../../components/ui/Spinner";

export const CandidateReviewPage: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const activeRun = useScreeningStore((s) => s.activeRun);
  const setActiveRun = useScreeningStore((s) => s.setActiveRun);
  
  const selectedCandidateId = useScreeningStore((s) => s.selectedCandidateId);
  const setSelectedCandidateId = useScreeningStore((s) => s.setSelectedCandidateId);
  
  const comparisonIds = useScreeningStore((s) => s.comparisonIds);
  const toggleComparisonId = useScreeningStore((s) => s.toggleComparisonId);

  // Fallback to fetch if page reloaded
  const { isLoading, error } = useQuery({
    queryKey: ["run", runId],
    queryFn: () => api.getRunDetails(runId || ""),
    enabled: !activeRun && !!runId,
    meta: {
      onSuccess: (data: any) => {
        setActiveRun(data);
      },
    },
  });

  const run = activeRun;

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white">
        <Spinner />
      </div>
    );
  }

  if (error || !run) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-10 text-center space-y-4">
        <AlertCircle className="w-12 h-12 text-zinc-300" />
        <h2 className="text-lg font-semibold text-zinc-950">Campaign details missing</h2>
        <Link to="/">
          <Button variant="secondary">Back to workspace</Button>
        </Link>
      </div>
    );
  }

  const selectedCandidate = run.candidates.find((c) => c.id === selectedCandidateId) || run.candidates[0];

  const getScoreColor = (score: number) => {
    if (score >= 80) return "success";
    if (score >= 60) return "warning";
    return "error";
  };

  const getConfidenceColor = (conf: string) => {
    if (conf === "High") return "success";
    if (conf === "Medium") return "warning";
    return "neutral";
  };

  // ── Export utilities ────────────────────────────────────────────────────────

  const exportJSON = () => {
    const payload = {
      run_id:        run.run_id,
      role_title:    run.role_title,
      exported_at:   new Date().toISOString(),
      candidates:    run.candidates.map((c: any) => ({
        rank:            c.rank ?? run.candidates.indexOf(c) + 1,
        name:            c.name,
        email:           c.email,
        overall_score:   c.overall_score,
        match_status:    c.match_status,
        experience_years: c.experience_years,
        education_degree: c.education_degree,
        matched_skills:  c.matched_skills,
        missing_skills:  c.missing_skills,
        scores:          c.scores,
        recruiter_brief: c.recruiter_brief,
      })),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `ScreenIT_${run.role_title.replace(/\s+/g, "_")}_${run.run_id.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportCSV = () => {
    const headers = [
      "Rank", "Name", "Email", "Overall Score", "Match Status",
      "Experience (yrs)", "Education", "Matched Skills", "Missing Skills",
      "Semantic Score", "Skills Score", "Experience Score", "Education Score",
      "Recruiter Brief",
    ];
    const escape = (v: any) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const rows = run.candidates.map((c: any, i: number) => [
      escape(i + 1),
      escape(c.name),
      escape(c.email),
      escape(c.overall_score),
      escape(c.match_status),
      escape(c.experience_years),
      escape(c.education_degree),
      escape((c.matched_skills ?? []).join("; ")),
      escape((c.missing_skills ?? []).join("; ")),
      escape(c.scores?.semantic ?? ""),
      escape(c.scores?.skills ?? ""),
      escape(c.scores?.experience ?? ""),
      escape(c.scores?.education ?? ""),
      escape(c.recruiter_brief ?? ""),
    ]);
    const csv  = [headers.join(","), ...rows.map((r: string[]) => r.join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `ScreenIT_${run.role_title.replace(/\s+/g, "_")}_${run.run_id.slice(0, 8)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportPDF = () => {
    // Build a styled HTML page and print it as PDF via the browser's print dialog
    const rows = run.candidates.map((c: any, i: number) => `
      <tr style="border-bottom:1px solid #e5e7eb;">
        <td style="padding:8px 12px;font-weight:600;">${i + 1}</td>
        <td style="padding:8px 12px;">${c.name ?? ""}</td>
        <td style="padding:8px 12px;">${c.email ?? ""}</td>
        <td style="padding:8px 12px;font-weight:700;">${c.overall_score}</td>
        <td style="padding:8px 12px;">${c.match_status ?? ""}</td>
        <td style="padding:8px 12px;">${c.experience_years ?? 0} yrs</td>
        <td style="padding:8px 12px;">${(c.matched_skills ?? []).slice(0, 4).join(", ")}</td>
        <td style="padding:8px 12px;font-size:11px;color:#6b7280;">${(c.recruiter_brief ?? "").slice(0, 120)}${(c.recruiter_brief ?? "").length > 120 ? "..." : ""}</td>
      </tr>
    `).join("");

    const html = `
      <!DOCTYPE html><html><head><meta charset="utf-8">
      <title>ScreenIT – ${run.role_title}</title>
      <style>
        body { font-family: -apple-system, sans-serif; padding: 32px; color: #111; }
        h1   { font-size: 22px; margin-bottom: 4px; }
        p    { color: #6b7280; font-size: 13px; margin-bottom: 24px; }
        table{ width: 100%; border-collapse: collapse; font-size: 12px; }
        th   { background: #f4f4f5; text-align: left; padding: 8px 12px;
               font-size: 11px; text-transform: uppercase; letter-spacing: .05em; }
        @media print { body { padding: 16px; } }
      </style></head><body>
      <h1>ScreenIT — ${run.role_title} Shortlist</h1>
      <p>Run ID: ${run.run_id} &nbsp;|&nbsp; Exported: ${new Date().toLocaleString()}</p>
      <table><thead><tr>
        <th>#</th><th>Name</th><th>Email</th><th>Score</th><th>Match</th>
        <th>Experience</th><th>Matched Skills</th><th>AI Summary</th>
      </tr></thead><tbody>${rows}</tbody></table>
      <script>window.onload=()=>{ window.print(); }<\/script>
      </body></html>
    `;
    const win = window.open("", "_blank");
    if (win) { win.document.write(html); win.document.close(); }
  };

  const exportHandlers: Record<string, () => void> = {
    PDF:  exportPDF,
    CSV:  exportCSV,
    JSON: exportJSON,
  };

  return (
    <div className="flex-1 flex h-screen overflow-hidden">
      {/* 1. Left List Pane (Recruiter list column) */}
      <div className="w-80 border-r border-zinc-200 flex flex-col h-full bg-zinc-50/50 shrink-0">
        <div className="p-4 border-b border-zinc-200 bg-white space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-[10px] text-zinc-400 font-mono uppercase tracking-wider">
              Shortlist Candidates
            </span>
            {comparisonIds.length > 0 && (
              <Link to={`/screen/${run.run_id}/compare`}>
                <Button variant="primary" size="sm" className="gap-1.5 py-1 px-2.5 rounded-md text-xs">
                  <Scale className="w-3.5 h-3.5" />
                  <span>Compare ({comparisonIds.length})</span>
                </Button>
              </Link>
            )}
          </div>
          <div>
            <h2 className="text-sm font-semibold text-zinc-900 truncate">{run.role_title}</h2>
            <p className="text-xs text-zinc-500 mt-0.5">{run.candidates.length} candidates ranked</p>
          </div>
        </div>

        {/* Candidate Scroll list */}
        <div className="flex-1 overflow-y-auto divide-y divide-zinc-200/60">
          {run.candidates.map((cand, idx) => {
            const isSelected = cand.id === selectedCandidateId;
            const inCompare = comparisonIds.includes(cand.id);
            
            return (
              <div
                key={cand.id}
                onClick={() => setSelectedCandidateId(cand.id)}
                className={`p-4 cursor-pointer transition-colors relative flex items-start gap-3 group ${
                  isSelected ? "bg-white border-l-2 border-zinc-950 pl-3.5" : "hover:bg-zinc-100/50"
                }`}
              >
                {/* Compare Checkbox */}
                <input
                  type="checkbox"
                  checked={inCompare}
                  onClick={(e) => e.stopPropagation()}
                  onChange={() => toggleComparisonId(cand.id)}
                  className="mt-1 h-3.5 w-3.5 rounded border-zinc-300 text-zinc-950 focus:ring-zinc-950 shrink-0"
                />

                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex justify-between items-baseline gap-2">
                    <h3 className="text-xs font-semibold text-zinc-900 truncate">{cand.name}</h3>
                    <span className="text-xs font-mono font-bold text-zinc-950">
                      {cand.overall_score}
                    </span>
                  </div>

                  <p className="text-[11px] text-zinc-500 truncate">{cand.education_degree} degree</p>

                  {cand.matched_skills && cand.matched_skills.length > 0 && (
                    <p className="text-[10px] text-emerald-600 font-medium truncate mt-0.5">
                      ✓ {cand.matched_skills.slice(0, 3).join(", ")}
                    </p>
                  )}

                  <div className="flex items-center gap-2 pt-1">
                    <Badge variant={getScoreColor(cand.overall_score)}>
                      Rank #{idx + 1}
                    </Badge>
                    <Badge variant={getConfidenceColor(cand.confidence)}>
                      {cand.match_status}
                    </Badge>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Right Detail Pane (Document View) */}
      <div className="flex-1 flex flex-col h-full bg-white overflow-hidden">
        {selectedCandidate ? (
          <div className="flex-1 flex flex-col h-full overflow-hidden">
            {/* Candidate Identity Header */}
            <div className="p-6 border-b border-zinc-200 bg-white shrink-0 flex justify-between items-start">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <h1 className="text-xl font-bold tracking-tight text-zinc-900">
                    {selectedCandidate.name}
                  </h1>
                </div>
                
                {/* Contact Coordinates */}
                <div className="flex items-center gap-4 text-xs text-zinc-500 font-mono">
                  {selectedCandidate.email && (
                    <span className="flex items-center gap-1.5">
                      <Mail className="w-3.5 h-3.5 stroke-[1.5]" />
                      {selectedCandidate.email}
                    </span>
                  )}
                  {selectedCandidate.phone && (
                    <span className="flex items-center gap-1.5">
                      <Phone className="w-3.5 h-3.5 stroke-[1.5]" />
                      {selectedCandidate.phone}
                    </span>
                  )}
                  {selectedCandidate.linkedin && (
                    <a
                      href={selectedCandidate.linkedin}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1.5 hover:text-zinc-900"
                    >
                      <Linkedin className="w-3.5 h-3.5 stroke-[1.5]" />
                      LinkedIn
                    </a>
                  )}
                  {selectedCandidate.github && (
                    <a
                      href={selectedCandidate.github}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1.5 hover:text-zinc-900"
                    >
                      <Github className="w-3.5 h-3.5 stroke-[1.5]" />
                      GitHub
                    </a>
                  )}
                </div>

                {/* Export Options */}
                <div className="flex gap-2 pt-1">
                  <span className="text-[10px] uppercase font-mono tracking-wider text-zinc-400 font-bold self-center mr-2">Export</span>
                  {(["PDF", "CSV", "JSON"] as const).map(format => (
                    <button
                      key={format}
                      onClick={exportHandlers[format]}
                      className="flex items-center gap-1 px-2 py-1 bg-zinc-100 hover:bg-zinc-200 active:bg-zinc-300 text-zinc-600 rounded text-[10px] font-mono font-semibold transition-colors cursor-pointer"
                    >
                      <Download className="w-3 h-3" />
                      {format}
                    </button>
                  ))}
                </div>
              </div>

              {/* Scoring Meter Circular indicator */}
              <div className="flex flex-col gap-3 bg-zinc-50 border border-zinc-200/80 px-5 py-4 rounded-xl min-w-[200px]">
                <div className="flex justify-between items-start">
                  <div className="text-left">
                    <h2 className="text-3xl font-bold text-zinc-950 font-mono leading-none">
                      {selectedCandidate.overall_score}
                    </h2>
                    <div className="flex items-center gap-0.5 mt-1.5">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className={`w-3.5 h-3.5 ${i < (selectedCandidate.overall_score >= 80 ? 5 : selectedCandidate.overall_score >= 60 ? 4 : 3) ? "fill-zinc-900 text-zinc-900" : "fill-zinc-200 text-zinc-200"}`} />
                      ))}
                    </div>
                  </div>
                  <Badge variant={getConfidenceColor(selectedCandidate.confidence)} className="text-[10px]">
                    {selectedCandidate.match_status}
                  </Badge>
                </div>
                
                <div className="w-full h-px bg-zinc-200 my-1" />
                
                <div className="text-left space-y-1.5">
                  <div className="flex justify-between items-center text-[10px] text-zinc-500 font-mono">
                    <span>AI Confidence</span>
                    <span className="font-bold text-zinc-700">{selectedCandidate.confidence === "High" ? "94%" : selectedCandidate.confidence === "Medium" ? "72%" : "45%"}</span>
                  </div>
                  <div className="w-full bg-zinc-200 rounded-full h-1.5 overflow-hidden">
                    <div
                      className={`h-full ${selectedCandidate.confidence === "High" ? "bg-emerald-500" : selectedCandidate.confidence === "Medium" ? "bg-amber-400" : "bg-zinc-400"}`}
                      style={{ width: selectedCandidate.confidence === "High" ? "94%" : selectedCandidate.confidence === "Medium" ? "72%" : "45%" }}
                    />
                  </div>
                </div>

                {/* Model routing telemetry */}
                <div className="w-full h-px bg-zinc-200 my-1" />
                <div className="text-left space-y-1 text-[10px] font-mono text-zinc-400">
                  <div className="flex justify-between">
                    <span>AI Model:</span>
                    <span className="font-bold text-zinc-600">{selectedCandidate.model_used || "Offline Fallback"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Latency:</span>
                    <span className="font-bold text-zinc-600">{selectedCandidate.latency ? `${selectedCandidate.latency}s` : "0.0s"}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Notion Scrollable Profile Document */}
            <div className="flex-1 overflow-y-auto p-8 space-y-10 max-w-3xl">
              {/* AI Recruiter Brief */}
              <section className="space-y-3">
                <h3 className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold border-b border-zinc-100 pb-2">
                  <Sparkles className="w-4 h-4 text-zinc-950 stroke-[1.5]" />
                  <span>AI Recruiter Brief</span>
                </h3>
                <p className="text-sm text-zinc-800 leading-relaxed font-sans bg-zinc-50/50 p-4 border border-zinc-150 rounded-xl italic">
                  "{selectedCandidate.recruiter_brief || "No summary provided."}"
                </p>
              </section>

              {/* Match Reasoning (Why Ranked) */}
              <section className="space-y-3">
                <h3 className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold border-b border-zinc-100 pb-2">
                  <BookmarkCheck className="w-4 h-4 text-emerald-600 stroke-[2]" />
                  <span className="text-zinc-900">Why Ranked #{run.candidates.findIndex(c => c.id === selectedCandidate.id) + 1}</span>
                </h3>
                <ul className="space-y-2.5 bg-zinc-50/50 p-4 rounded-xl border border-zinc-100">
                  {selectedCandidate.why_reasoning.map((reason, idx) => (
                    <li key={idx} className="flex gap-3 items-start text-[13px] text-zinc-800 font-medium">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                      <span className="leading-relaxed">{reason}</span>
                    </li>
                  ))}
                </ul>
              </section>


              {/* Risk Factors */}
              {selectedCandidate.risk_factors && selectedCandidate.risk_factors.length > 0 && (
                <section className="space-y-3">
                  <h3 className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold border-b border-zinc-100 pb-2">
                    <ShieldAlert className="w-4 h-4 text-amber-500 stroke-[1.5]" />
                    <span>Risk Signals</span>
                  </h3>
                  <ul className="space-y-2">
                    {selectedCandidate.risk_factors.map((risk, idx) => (
                      <li key={idx} className="flex gap-2.5 items-start text-xs text-amber-700 bg-amber-50/60 border border-amber-100 rounded-lg px-3 py-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                        <span>{risk}</span>
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              {/* Skills Analysis */}
              <section className="space-y-4">
                <h3 className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold border-b border-zinc-100 pb-2">
                  Skill Alignment Matrix
                </h3>
                <div className="grid grid-cols-2 gap-6">
                  {/* Matched */}
                  <div className="space-y-2.5">
                    <h4 className="text-xs font-semibold text-zinc-900">
                      Matched Skills ({selectedCandidate.matched_skills.length})
                    </h4>
                    {selectedCandidate.matched_skills.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {selectedCandidate.matched_skills.map((skill) => (
                          <Badge key={skill} variant="success">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-zinc-400">None detected</p>
                    )}
                  </div>
                  {/* Missing */}
                  <div className="space-y-2.5">
                    <h4 className="text-xs font-semibold text-zinc-900">
                      Critical Gaps ({selectedCandidate.missing_skills.length})
                    </h4>
                    {selectedCandidate.missing_skills.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {selectedCandidate.missing_skills.map((skill) => (
                          <Badge key={skill} variant="error">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-zinc-400">No skill gaps identified</p>
                    )}
                  </div>
                </div>
              </section>

              {/* Strengths & Weaknesses */}
              {(selectedCandidate.strengths?.length || selectedCandidate.weaknesses?.length) ? (
                <section className="space-y-4">
                  <h3 className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold border-b border-zinc-100 pb-2">
                    AI Strengths & Weaknesses
                  </h3>
                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <h4 className="text-xs font-semibold text-zinc-900 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                        Strengths
                      </h4>
                      <ul className="space-y-1.5">
                        {selectedCandidate.strengths?.map((s, i) => (
                          <li key={i} className="text-xs text-zinc-700 flex gap-2 items-start">
                            <div className="w-1 h-1 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-xs font-semibold text-zinc-900 flex items-center gap-1.5">
                        <XCircle className="w-3.5 h-3.5 text-rose-400" />
                        Development Areas
                      </h4>
                      <ul className="space-y-1.5">
                        {selectedCandidate.weaknesses?.map((w, i) => (
                          <li key={i} className="text-xs text-zinc-700 flex gap-2 items-start">
                            <div className="w-1 h-1 rounded-full bg-rose-300 mt-1.5 shrink-0" />
                            {w}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </section>
              ) : null}

              {/* Targeted Interview Questions */}
              {selectedCandidate.interview_questions && selectedCandidate.interview_questions.length > 0 && (
                <section className="space-y-3">
                  <h3 className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold border-b border-zinc-100 pb-2">
                    Custom Interview Questions
                  </h3>
                  <div className="space-y-3">
                    {selectedCandidate.interview_questions.map((q, idx) => (
                      <div key={idx} className="p-3.5 border border-zinc-200/80 rounded-xl bg-zinc-50/20 flex gap-3">
                        <span className="font-mono text-xs text-zinc-400 mt-0.5 font-bold">
                          Q{idx + 1}
                        </span>
                        <p className="text-xs text-zinc-700 font-medium leading-relaxed">
                          {q}
                        </p>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Decision Section */}
              <section className="pt-6 border-t border-zinc-200 mt-8 mb-4">
                <h3 className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold mb-4">
                  Final Recommendation
                </h3>
                <div className={`p-5 rounded-xl border flex gap-4 ${selectedCandidate.overall_score >= 80 ? "bg-emerald-50/50 border-emerald-200" : selectedCandidate.overall_score >= 60 ? "bg-amber-50/50 border-amber-200" : "bg-rose-50/50 border-rose-200"}`}>
                  <div className={`w-3 h-3 mt-1 rounded-full shrink-0 ${selectedCandidate.overall_score >= 80 ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : selectedCandidate.overall_score >= 60 ? "bg-amber-500" : "bg-rose-500"}`} />
                  <div className="space-y-1.5">
                    <h4 className={`text-sm font-bold ${selectedCandidate.overall_score >= 80 ? "text-emerald-900" : selectedCandidate.overall_score >= 60 ? "text-amber-900" : "text-rose-900"}`}>
                      {selectedCandidate.overall_score >= 80 ? "Recommend Interview" : selectedCandidate.overall_score >= 60 ? "Hold for Review" : "Reject"}
                    </h4>
                    <p className={`text-xs leading-relaxed ${selectedCandidate.overall_score >= 80 ? "text-emerald-800" : selectedCandidate.overall_score >= 60 ? "text-amber-800" : "text-rose-800"}`}>
                      {selectedCandidate.overall_score >= 80 
                        ? `Strong semantic match (${selectedCandidate.scores.semantic}%), excellent skills alignment (${selectedCandidate.scores.skills}%), meets experience requirement. Minimal onboarding effort.`
                        : selectedCandidate.overall_score >= 60
                        ? `Partial skills alignment. Missing some core requirements. Might require significant onboarding time.`
                        : `Poor match for the role requirements. Lacks necessary core skills and experience.`
                      }
                    </p>
                  </div>
                </div>
              </section>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-zinc-400">
            No candidate selected.
          </div>
        )}
      </div>
    </div>
  );
};
