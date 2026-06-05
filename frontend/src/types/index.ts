export interface User {
  id: string
  email: string
  full_name: string
  role: "candidate" | "recruiter" | "admin"
  status: string
  preferred_language: string
  is_verified: boolean
}

export interface ATSFeedback {
  score: number
  grade: string
  issues: string[]
  suggestions: string[]
  keyword_match_rate: number
  section_scores: Record<string, number>
}

export interface ParsedCVData {
  contact: Record<string, string | null>
  skills: string[]
  education: Array<Record<string, string | null>>
  experience: Array<Record<string, string | null>>
  languages: string[]
  summary: string | null
}

export interface CVDocument {
  id: string
  original_filename: string
  status: "uploaded" | "processing" | "parsed" | "failed"
  detected_language: string | null
  ats_score: number | null
  ats_feedback: ATSFeedback | null
  parsed_data: ParsedCVData | null
  created_at: string
}

export interface Job {
  id: string
  title: string
  description: string
  requirements: string | null
  location: string | null
  job_type: string
  status: string
  required_skills: string[]
  required_languages: string[]
  experience_years_min: number | null
  is_remote: boolean
  language: string
  created_at: string
}

export interface CandidateMatchResult {
  candidate_id: string
  full_name: string
  email: string
  similarity_score: number
  ranking_score: number
  rank_position: number
  skills_matched: string[]
  skills_missing: string[]
  experience_years: number | null
  detected_language: string | null
  explanation: string
}

export interface MatchResponse {
  job_id: string
  job_title: string
  total_candidates: number
  matches: CandidateMatchResult[]
}

export interface JobFairnessReport {
  job_id: string
  job_title: string
  total_applications: number
  flagged_applications: number
  overall_fair: boolean
  disparate_impact_ratio: number
  language_distribution: Record<string, number>
  bias_summary: Record<string, number>
  recommendations: string[]
  per_language_scores: Record<string, number>
}