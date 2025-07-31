import { ResearchRequest, ResearchResult, ResearchModeInfo } from '../types/api'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  async conductResearch(request: ResearchRequest): Promise<ResearchResult> {
    return this.request<ResearchResult>('/research', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getResearchModes(): Promise<{ modes: Record<string, ResearchModeInfo> }> {
    return this.request<{ modes: Record<string, ResearchModeInfo> }>('/research-modes')
  }

  async getApiInfo(): Promise<any> {
    return this.request<any>('/')
  }

  async clarifyIntent(query: string): Promise<any> {
    return this.request<any>('/clarify', {
      method: 'POST',
      body: JSON.stringify({ query }),
    })
  }

  async rewritePrompt(originalQuery: string, clarifiedIntent: string = ''): Promise<any> {
    return this.request<any>('/rewrite-prompt', {
      method: 'POST',
      body: JSON.stringify({ 
        original_query: originalQuery,
        clarified_intent: clarifiedIntent 
      }),
    })
  }

  async rewritePromptWithAnswers(originalQuery: string, clarificationWithAnswers: any): Promise<any> {
    return this.request<any>('/rewrite-prompt', {
      method: 'POST',
      body: JSON.stringify({ 
        original_query: originalQuery,
        clarification_with_answers: clarificationWithAnswers 
      }),
    })
  }

  async conductAnalysisOnly(request: any): Promise<any> {
    return this.request<any>('/research-analysis', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getAvailableTools(): Promise<any> {
    return this.request<any>('/tools')
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/healthz')
  }
}

export const apiClient = new ApiClient()
