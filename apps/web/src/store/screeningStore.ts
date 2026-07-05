import { create } from "zustand";
import { RunDetails } from "../types";

interface ScreeningState {
  activeRun: RunDetails | null;
  selectedCandidateId: string | null;
  comparisonIds: string[];
  
  setActiveRun: (run: RunDetails | null) => void;
  setSelectedCandidateId: (id: string | null) => void;
  toggleComparisonId: (id: string) => void;
  clearComparison: () => void;
}

export const useScreeningStore = create<ScreeningState>((set) => ({
  activeRun: null,
  selectedCandidateId: null,
  comparisonIds: [],

  setActiveRun: (run) => {
    const nextCandId = run && run.candidates.length > 0 ? run.candidates[0].id : null;
    set({
      activeRun: run,
      selectedCandidateId: nextCandId,
      comparisonIds: [],
    });
  },

  setSelectedCandidateId: (id) => set({ selectedCandidateId: id }),

  toggleComparisonId: (id) =>
    set((state) => {
      const exists = state.comparisonIds.includes(id);
      return {
        comparisonIds: exists
          ? state.comparisonIds.filter((cid) => cid !== id)
          : [...state.comparisonIds, id],
      };
    }),

  clearComparison: () => set({ comparisonIds: [] }),
}));
