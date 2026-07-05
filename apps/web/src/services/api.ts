import { RunDetails, ScreeningRun } from "../types";

export const api = {
  getHealth: async (): Promise<any> => {
    try {
      const res = await fetch("/api/settings/health");
      if (!res.ok) throw new Error();
      return await res.json();
    } catch (err) {
      return { status: "offline", database: "disconnected", embeddings: "failed", providers: {} };
    }
  },

  getRuns: async (): Promise<ScreeningRun[]> => {
    const res = await fetch("/api/runs");
    if (!res.ok) throw new Error("Failed to fetch runs");
    return res.json();
  },

  getRunDetails: async (id: string): Promise<RunDetails> => {
    const res = await fetch(`/api/runs/${id}`);
    if (!res.ok) throw new Error("Failed to fetch screening details");
    return res.json();
  },

  screenResumes: async (formData: FormData): Promise<RunDetails> => {
    const res = await fetch("/api/screen", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Screening failed. Please verify files and try again.");
    return res.json();
  },

  getAnalytics: async (): Promise<any> => {
    const res = await fetch("/api/analytics");
    if (!res.ok) throw new Error("Failed to fetch analytics");
    return res.json();
  },

  getKeys: async (): Promise<any> => {
    const res = await fetch("/api/settings/keys");
    if (!res.ok) throw new Error("Failed to fetch API keys");
    return res.json();
  },

  saveKey: async (provider: string, key: string): Promise<any> => {
    const res = await fetch("/api/settings/keys", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, key }),
    });
    if (!res.ok) throw new Error("Failed to save key");
    return res.json();
  },

  getModels: async (): Promise<any> => {
    const res = await fetch("/api/settings/models");
    if (!res.ok) throw new Error("Failed to fetch available models");
    return res.json();
  },

  getRouting: async (): Promise<any> => {
    const res = await fetch("/api/settings/routing");
    if (!res.ok) throw new Error("Failed to fetch routing cascades");
    return res.json();
  },

  saveRouting: async (prefs: any): Promise<any> => {
    const res = await fetch("/api/settings/routing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prefs }),
    });
    if (!res.ok) throw new Error("Failed to save routing matrix");
    return res.json();
  },

  testKey: async (provider: string, key: string): Promise<any> => {
    const res = await fetch("/api/settings/test-key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, key }),
    });
    if (!res.ok) throw new Error("Key validation test failed");
    return res.json();
  },

  deleteRun: async (runId: string): Promise<any> => {
    const res = await fetch(`/api/runs/${runId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete campaign run");
    return res.json();
  },

  deleteCandidate: async (candidateId: string): Promise<any> => {
    const res = await fetch(`/api/candidates/${candidateId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete candidate");
    return res.json();
  },

  updateCandidate: async (candidateId: string, updates: any): Promise<any> => {
    const res = await fetch(`/api/candidates/${candidateId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error("Failed to update candidate assessment");
    return res.json();
  }
};



