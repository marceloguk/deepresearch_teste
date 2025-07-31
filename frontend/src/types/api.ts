export interface ResearchRequest {
  query: string
  mode: ResearchMode
  max_tokens?: number
  temperature?: number
  include_clarification: boolean
  include_prompt_rewriting: boolean
}

export enum ResearchMode {
  DEEP_RESEARCH_O3 = "o3-deep-research",
  DEEP_RESEARCH_O4_MINI = "o4-mini-deep-research", 
  WEBSEARCH_MCP = "websearch-mcp",
  WEBSEARCH_ONLY = "websearch-only",
  MCP_ONLY = "mcp-only"
}

export interface ClarificationQuestion {
  question: string
  context: string
}

export interface ClarificationResponse {
  questions: ClarificationQuestion[]
  clarified_intent: string
}

export interface ClarificationAnswer {
  question_index: number
  answer: string
}

export interface ClarificationWithAnswers {
  questions: ClarificationQuestion[]
  answers: ClarificationAnswer[]
  clarified_intent: string
}

export interface PromptRewriteResponse {
  original_query: string
  rewritten_prompt: string
  reasoning: string
}

export interface SearchResult {
  id: string
  title: string
  url: string
  snippet: string
  relevance_score?: number
}

export interface FetchResult {
  id: string
  content: string
  metadata: Record<string, any>
}

export interface ResearchStep {
  step_type: "clarification" | "prompt_rewriting" | "search" | "fetch" | "analysis"
  input_data: Record<string, any>
  output_data: Record<string, any>
  timestamp: string
  duration_ms: number
}

export interface ResearchResult {
  query: string
  mode: ResearchMode
  clarification?: ClarificationResponse
  prompt_rewrite?: PromptRewriteResponse
  search_results: SearchResult[]
  fetch_results: FetchResult[]
  final_analysis: string
  steps: ResearchStep[]
  total_duration_ms: number
  success: boolean
  error_message?: string
}

export interface ResearchModeInfo {
  name: string
  description: string
  capabilities: string[]
  workflow: string
}
