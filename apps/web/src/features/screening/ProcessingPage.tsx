import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { useScreeningStore } from "../../store/screeningStore";

export const ProcessingPage: React.FC = () => {
  const navigate = useNavigate();
  const activeRun = useScreeningStore((s) => s.activeRun);
  const [stage, setStage] = useState(0);

  const stages = [
    "Uploading",
    "Parsing",
    "Embedding",
    "Ranking",
    "Generating AI Brief",
    "Completed"
  ];

  // Auto-transition UI stages
  useEffect(() => {
    const interval = setInterval(() => {
      setStage((prev) => {
        if (prev < stages.length - 2) {
          return prev + 1;
        }
        return prev;
      });
    }, 1200);
    
    return () => clearInterval(interval);
  }, [stages.length]);

  // Navigate to review once activeRun is set
  useEffect(() => {
    if (activeRun) {
      setStage(stages.length - 1);
      const timeout = setTimeout(() => {
        navigate(`/screen/${activeRun.run_id}/review`);
      }, 800);
      return () => clearTimeout(timeout);
    }
  }, [activeRun, navigate, stages.length]);

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-10 bg-white">
      <div className="max-w-md w-full text-center space-y-8">
        <div className="relative flex justify-center">
          <div className="absolute w-20 h-20 bg-zinc-100 rounded-full animate-ping opacity-75" />
          <div className="relative w-20 h-20 bg-zinc-950 text-white rounded-full flex items-center justify-center shadow-lg">
            <Sparkles className="w-8 h-8 animate-pulse stroke-[1.5]" />
          </div>
        </div>

        <div className="space-y-2">
          <h2 className="text-xl font-semibold tracking-tight text-zinc-950">
            Processing Candidates
          </h2>
          <p className="text-sm text-zinc-500 max-w-sm mx-auto leading-relaxed">
            Running hybrid AI + semantic search pipeline
          </p>
        </div>

        <div className="border border-zinc-200 rounded-xl p-8 bg-zinc-50/50 text-left space-y-5 max-w-sm mx-auto shadow-inner">
          {stages.map((stg, idx) => {
            const isActive = stage === idx;
            const isCompleted = stage > idx;
            
            return (
              <div
                key={idx}
                className={`transition-opacity duration-300 space-y-1.5 ${
                  isActive ? "opacity-100" : isCompleted ? "opacity-40" : "opacity-20"
                }`}
              >
                <div className="flex justify-between items-center text-xs font-mono font-bold tracking-wider uppercase">
                  <span className={`${isActive ? "text-zinc-950" : "text-zinc-500"}`}>{stg}</span>
                  {isCompleted && <span className="text-emerald-500 font-bold">Done</span>}
                </div>
                <div className="flex gap-1">
                  {[...Array(10)].map((_, i) => (
                    <div 
                      key={i} 
                      className={`h-1.5 flex-1 rounded-full ${
                        isCompleted 
                          ? "bg-zinc-900" 
                          : isActive && i < 6 
                            ? "bg-zinc-900 animate-pulse" 
                            : "bg-zinc-200"
                      }`} 
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

