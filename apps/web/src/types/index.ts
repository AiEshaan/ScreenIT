export interface CandidateScores {
  semantic: number;
  skills: number;
  experience: number;
  education: number;
}

export interface Candidate {
  id: string;
  run_id: string;
  name: string;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
  overall_score: number;
  confidence: "High" | "Medium" | "Low";
  match_status: "Strong Match" | "Good Match" | "Weak Match";
  scores: CandidateScores;
  experience_years: number;
  education_degree: string;
  matched_skills: string[];
  missing_skills: string[];
  why_reasoning: string[];
  risk_factors?: string[];
  recruiter_brief?: string;
  strengths?: string[];
  weaknesses?: string[];
  interview_questions?: string[];
  raw_profile?: any;
}

export interface ScreeningRun {
  run_id: string;
  role_title: string;
  job_description: string;
  processing_time?: number;
  status: string;
  created_at: string;
  candidate_count: number;
}

export interface RunDetails extends ScreeningRun {
  candidates: Candidate[];
}
