export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type UserMe = {
  id: number;
  email: string;
  full_name: string;
  tenant_id: number;
  tenant_name: string;
  role: string;
  skills: string;
  seniority: string;
  target_role: string;
};

export type Job = {
  id: number;
  tenant_id: number;
  title: string;
  title_original?: string;
  company: string;
  description: string;
  description_original?: string;
  requirements: string;
  location: string;
  url: string;
  source: string;
  external_id: string;
  seniority: string;
  employment_type: string;
  salary_min: number;
  salary_max: number;
  remote: boolean;
  created_at: string;
};

export type Application = {
  id: number;
  tenant_id: number;
  user_id: number;
  job_id: number;
  status: ApplicationStatus;
  notes: string;
  next_action: string;
  created_at: string;
  updated_at: string;
};

export type ApplicationStatus = "saved" | "applied" | "screening" | "interview" | "technical_test" | "offer" | "rejected" | "withdrawn";

export type MatchScore = {
  id: number;
  tenant_id: number;
  user_id: number;
  job_id: number;
  score: number;
  skill_score: number;
  seniority_score: number;
  keyword_score: number;
  matched_skills: string[];
  missing_skills: string[];
  explanation: string;
  created_at: string;
};

export type RankItem = {
  job_id: number;
  title: string;
  company: string;
  score: number;
  explanation: string;
};

export type Resume = {
  id: number;
  tenant_id: number;
  user_id: number;
  job_id: number;
  content_md: string;
  version: number;
  created_at: string;
};

export type InterviewPrep = {
  job_id: number;
  role_pitch: string;
  questions: string[];
  weak_points: string[];
  study_plan: string[];
  salary_talk: string;
};


export type StrategyPriority = "HIGH_PRIORITY" | "MEDIUM_PRIORITY" | "LOW_PRIORITY";

export type StrategyFactors = {
  match_score: number;
  recency_score: number;
  competition_score: number;
  location_score: number;
  remote_score: number;
  seniority_score: number;
};

export type StrategyRecommendation = {
  job_id: number;
  title: string;
  company: string;
  location: string;
  remote: boolean;
  strategy_score: number;
  priority: StrategyPriority;
  explanation: string;
  factors: StrategyFactors;
};


export type ApplicationQueueStatus = "queued" | "approved" | "skipped" | "applied" | "failed";

export type ApplicationQueueItem = {
  id: number;
  tenant_id: number;
  user_id: number;
  job_id: number;
  strategy_score: number;
  evaluation_grade: string;
  generated_cv: string;
  cover_message: string;
  status: ApplicationQueueStatus;
  failure_reason: string;
  created_at: string;
  updated_at: string;
  job_title?: string | null;
  company?: string | null;
  location?: string | null;
  remote?: boolean | null;
  job_url?: string | null;
};

export type QueueBuildResponse = {
  created: number;
  skipped: number;
  blocked_low_priority: number;
  daily_limit_remaining: number;
  items: ApplicationQueueItem[];
};

export type UserSkill = { id: number; name: string; level: string; category: string };
export type UserExperience = { id: number; company: string; role: string; start_date: string; end_date: string; description: string; achievements: string };
export type UserProject = { id: number; name: string; description: string; technologies: string; url: string };
export type UserEducation = { id: number; institution: string; course: string; start_date: string; end_date: string; description: string };
export type UserProfile = {
  id: number | null; tenant_id: number; user_id: number; full_name: string; professional_title: string;
  summary: string; location: string; work_preferences: string;
  job_country: string; job_state: string; job_state_code: string; job_cities: string[]; job_all_cities: boolean; job_remote_preference: string; job_city_code: string;
  education_level: string; english_level: string; spanish_level: string;
  salary_expectation: number; phone: string; email: string;
  resume_text: string; completeness: number; skills: UserSkill[]; experiences: UserExperience[]; projects: UserProject[]; education: UserEducation[];
};


export type AtsSuggestion = {
  priority: "alta" | "média" | "baixa" | string;
  title: string;
  description: string;
};

export type AtsAnalysis = {
  ats_score: number;
  rh_score: number;
  match_score: number;
  keyword_score: number;
  experience_score: number;
  clarity_score: number;
  seniority_score: number;
  final_score: number;
  grade: string;
  probability: string;
  strengths: string[];
  weaknesses: string[];
  missing_keywords: string[];
  suggestions: AtsSuggestion[];
  warnings: string[];
  compared_job_id?: number | null;
};


export type NotificationSettings = {
  enabled: boolean;
  max_per_run: number;
  min_priority: string;
  telegram: { configured: boolean };
  whatsapp_evolution: { configured: boolean };
  auto_send: boolean;
  responsible_use: string;
};

export type NotificationResult = {
  enabled: boolean;
  sent: number;
  skipped: number;
  selected?: number | null;
  max_per_run?: number | null;
  results: Array<Record<string, unknown>>;
};


export type WhatsAppSessionStatus = {
  configured: boolean;
  instance_id: string;
  instance_name?: string;
  session_id?: number | null;
  target_number_configured: boolean;
  phone_number?: string;
  status: string;
  message: string;
  connected: boolean;
  qrcode?: string;
  qrcode_type?: "base64_image" | "text" | "none" | string;
  qr_code?: string;
  qr_type?: string;
  last_error?: string;
  sent?: boolean;
  cached?: boolean;
  last_checked_at?: string | null;
  connected_at?: string | null;
};


export type AnalyticsOverview = {
  jobs_total: number;
  jobs_analyzed: number;
  applications_total: number;
  response_rate: number;
  status_counts: Record<string, number>;
  top_sources: Array<{ source: string; count: number }>;
  top_roles: Array<{ role: string; count: number }>;
  average_match_score: number;
  active_applications?: number;
  high_match_jobs?: number;
  source_diversity?: number;
  career_efficiency?: number;
  career_score?: number;
  score_trend?: Array<{ date: string; career_score: number; average_match_score: number; applications_total: number; high_match_jobs: number }>;
  decision_history?: Array<{ id: number; type: string; title: string; detail: string; score: number; job_id?: number | null; application_id?: number | null; created_at: string }>;
  warnings: string[];
};

export type SkillGapRoadmap = {
  jobs_analyzed: number;
  strong_skills: Array<{ skill: string; count: number }>;
  missing_skills: Array<{ skill: string; count: number }>;
  roadmap: Array<{ skill: string; priority: string; count: number; action: string }>;
  warnings: string[];
};

export type RadarRun = {
  id: number;
  provider: string;
  total_ingested: number;
  high_priority_count: number;
  notified_count: number;
  status: string;
  message: string;
  created_at?: string;
};

export type AutomationMode = "interval" | "fixed" | "window";

export type AutomationStatus = {
  enabled: boolean;
  mode: AutomationMode;
  interval_minutes: number | null;
  times: string[] | null;
  window_start: string | null;
  window_end: string | null;
  last_run: string | null;
  next_run_estimate: string | null;
  total_notifications_sent: number;
  scheduler_enabled: boolean;
};

export type AutomationSettingsPayload = {
  enabled: boolean;
  mode: AutomationMode;
  interval_minutes: number | null;
  times: string[] | null;
  window_start: string | null;
  window_end: string | null;
};
