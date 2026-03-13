export interface TopicResult {
  topic_id: number;
  label: string;
  description: string;
  category: string;
  count: number;
  percentage: number;
  keywords: string[];
  sample_responses: string[];
}

export interface Assignment {
  id: number;
  text: string;
  topic_id: number;
  topic_label: string;
  probability: number;
}

export interface Summary {
  total_responses: number;
  num_topics: number;
}

export interface AnalysisResponse {
  analysis_id: string;
  summary: Summary;
  topics: TopicResult[];
  assignments: Assignment[];
}

export interface LibraryItem {
  id: string;
  filename: string;
  title: string | null;
  created_at: string;
  total_responses: number;
  num_topics: number;
}

export interface SaveRequest {
  title?: string | null;
}
