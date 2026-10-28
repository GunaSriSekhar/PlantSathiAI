export interface PlantCandidate {
  label: string;
  score: number;
  rank: number;
}

export interface PlantResult {
  common_name?: string | null;
  scientific_name?: string | null;
  confidence?: number | null;
  confidence_level?: string;
  reliable: boolean;
  supported: boolean;
  candidates: PlantCandidate[];
  warning?: string | null;
}

export interface DiseaseResult {
  status: string;
  label?: string | null;
  crop?: string | null;
  disease_name?: string | null;
  is_healthy?: boolean | null;
  confidence?: number | null;
  confidence_level?: string;
  supported: boolean;
  warning?: string | null;
}

export interface Recommendation {
  category: string;
  title: string;
  description: string;
  urgency: 'high' | 'medium' | 'low';
}

export interface ModelsUsed {
  identification?: string | null;
  diagnosis?: string | null;
}

export interface AnalysisResult {
  scan_id: string;
  created_at: string;
  plant: PlantResult;
  disease: DiseaseResult;
  recommendations: Recommendation[];
  warnings: string[];
  models: ModelsUsed;
  analysis_duration_ms?: number | null;
  image_filename?: string | null;
}

export interface ScanSummary {
  id: string;
  created_at: string;
  plant_common_name?: string | null;
  plant_scientific_name?: string | null;
  disease_label?: string | null;
  disease_status: string;
  plant_confidence?: number | null;
  disease_confidence?: number | null;
  image_filename?: string | null;
}

export interface ScanDetail {
  id: string;
  created_at: string;
  updated_at: string;
  plant_common_name?: string | null;
  plant_scientific_name?: string | null;
  plant_confidence?: number | null;
  plant_confidence_level?: string | null;
  plant_model?: string | null;
  plant_supported: boolean;
  plant_top_candidates?: PlantCandidate[] | null;
  disease_label?: string | null;
  disease_crop?: string | null;
  disease_name?: string | null;
  disease_confidence?: number | null;
  disease_confidence_level?: string | null;
  disease_status: string;
  disease_model?: string | null;
  disease_supported: boolean;
  disease_is_healthy?: boolean | null;
  warnings: string[];
  recommendations: Recommendation[];
  analysis_duration_ms?: number | null;
  image_filename?: string | null;
  image_stored: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  message: string;
  suggestions: string[];
  related_topics: string[];
  is_llm: boolean;
  disclaimer: string;
}

export interface ModelStatus {
  name: string;
  task: string;
  status: string;
  device: string;
  class_count?: number | null;
  loaded_at?: string | null;
  error?: string | null;
}

export interface SavedPlant {
  id: string;
  created_at: string;
  common_name: string;
  scientific_name?: string | null;
  notes?: string | null;
  scan_id?: string | null;
}
