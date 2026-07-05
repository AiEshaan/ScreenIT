import { RunDetails, ScreeningRun } from "../types";

// Demo data fallback for offline exploration
const demoRunList: ScreeningRun[] = [
  {
    run_id: "demo_123",
    role_title: "Senior Backend Engineer",
    candidate_count: 4,
    created_at: new Date().toISOString(),
    processing_time: 1.8,
    job_description: "Senior Backend Engineer JD",
    status: "completed",
  }
];

const demoRunDetails: RunDetails = {
  run_id: "demo_123",
  role_title: "Senior Backend Engineer",
  created_at: new Date().toISOString(),
  job_description: "Senior Backend Engineer JD",
  status: "completed",
  candidate_count: 2,
  processing_time: 1.8,
  candidates: [
    {
      id: "c1",
      run_id: "demo_123",
      name: "Priya Sharma",
      email: "priya@example.com",
      phone: null,
      linkedin: null,
      github: null,
      education_degree: "Master's",
      experience_years: 5,
      overall_score: 91,
      match_status: "Strong Match",
      confidence: "High",
      why_reasoning: [
        "Highest semantic similarity to role requirements",
        "Matches 18/20 required skills including AWS, FastAPI, and Kubernetes",
        "Exceeds experience requirement with 5 years in backend engineering"
      ],
      scores: { semantic: 94, skills: 90, experience: 85, education: 100 },
      matched_skills: ["Python", "FastAPI", "AWS", "Kubernetes", "PostgreSQL"],
      missing_skills: ["GraphQL"],
      strengths: ["Excellent scalable architecture background", "Strong Python proficiency"],
      weaknesses: ["No direct experience with GraphQL APIs"],
      interview_questions: [
        "Can you describe a time you optimized a slow FastAPI endpoint?",
        "How do you handle zero-downtime deployments with Kubernetes?"
      ],
      recruiter_brief: "Priya is an exceptionally strong candidate with deep expertise in Python and AWS, making her a top percentile match for this role.",
      raw_profile: { experience: [{ role: "Backend Developer", company: "TechCorp", duration: "2019-2024" }] }
    },
    {
      id: "c2",
      run_id: "demo_123",
      name: "Arjun Desai",
      email: "arjun@example.com",
      phone: null,
      linkedin: null,
      github: null,
      education_degree: "Bachelor's",
      experience_years: 2,
      overall_score: 74,
      match_status: "Good Match",
      confidence: "Medium",
      why_reasoning: [
        "Good core Python skills",
        "Lacks cloud infrastructure experience",
      ],
      scores: { semantic: 70, skills: 75, experience: 80, education: 80 },
      matched_skills: ["Python", "Django", "SQL"],
      missing_skills: ["AWS", "Kubernetes", "FastAPI"],
      strengths: ["Solid database design knowledge"],
      weaknesses: ["Missing modern cloud-native stack experience"],
      interview_questions: [
        "How would you approach learning Kubernetes if required for this role?"
      ],
      recruiter_brief: "Arjun has solid fundamentals but would require onboarding time for our cloud stack.",
      raw_profile: { experience: [] }
    }
  ]
};

export const api = {
  getRuns: async (): Promise<ScreeningRun[]> => {
    try {
      const res = await fetch("/api/runs");
      if (!res.ok) throw new Error();
      return res.json();
    } catch (err) {
      console.warn("Backend offline. Loading Demo Data.");
      return demoRunList;
    }
  },

  getRunDetails: async (id: string): Promise<RunDetails> => {
    try {
      const res = await fetch(`/api/runs/${id}`);
      if (!res.ok) throw new Error();
      return res.json();
    } catch (err) {
      if (id === "demo_123") return demoRunDetails;
      throw new Error("Failed to fetch screening details");
    }
  },

  screenResumes: async (formData: FormData): Promise<RunDetails> => {
    const res = await fetch("/api/screen", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Screening failed. Please verify files and try again.");
    return res.json();
  },
};
