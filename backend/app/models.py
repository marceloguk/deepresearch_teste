from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class ResearchMode(str, Enum):
    DEEP_RESEARCH_O3 = "o3-deep-research"
    DEEP_RESEARCH_O4_MINI = "o4-mini-deep-research"
    WEBSEARCH_MCP = "websearch-mcp"
    WEBSEARCH_ONLY = "websearch-only"
    MCP_ONLY = "mcp-only"


class ResearchRequest(BaseModel):
    query: str
    mode: ResearchMode
    max_tokens: Optional[int] = 4000
    temperature: Optional[float] = 0.7
    include_clarification: bool = True
    include_prompt_rewriting: bool = True


class ClarificationQuestion(BaseModel):
    question: str
    context: str


class ClarificationResponse(BaseModel):
    questions: List[ClarificationQuestion]
    clarified_intent: str


class ClarificationAnswer(BaseModel):
    question_index: int
    answer: str


class ClarificationWithAnswers(BaseModel):
    questions: List[ClarificationQuestion]
    answers: List[ClarificationAnswer]
    clarified_intent: str


class PromptRewriteResponse(BaseModel):
    original_query: str
    rewritten_prompt: str
    reasoning: str


class SearchResult(BaseModel):
    id: str
    title: str
    url: str
    snippet: str
    relevance_score: Optional[float] = None


class FetchResult(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]


class ResearchStep(BaseModel):
    step_type: Literal["clarification", "prompt_rewriting", "search", "fetch", "analysis"]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    timestamp: str
    duration_ms: int


class ResearchResult(BaseModel):
    query: str
    mode: ResearchMode
    clarification: Optional[ClarificationResponse] = None
    prompt_rewrite: Optional[PromptRewriteResponse] = None
    search_results: List[SearchResult] = []
    fetch_results: List[FetchResult] = []
    final_analysis: str
    steps: List[ResearchStep] = []
    total_duration_ms: int
    success: bool
    error_message: Optional[str] = None


class MCPSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10


class MCPFetchRequest(BaseModel):
    id: str


class WebSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10
    include_citations: bool = True
