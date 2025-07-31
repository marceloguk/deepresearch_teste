from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import psycopg

from .models import (
    ResearchRequest, ResearchResult, ResearchMode,
    ClarificationResponse, PromptRewriteResponse,
    SearchResult, FetchResult, MCPSearchRequest, MCPFetchRequest,
    WebSearchRequest, ClarificationWithAnswers
)
from .services.research_service import ResearchService
from .services.openai_service import OpenAIService
from .services.websearch_service import WebSearchService
from .services.mcp_service import MCPService

app = FastAPI(
    title="Deep Research API",
    description="Comprehensive implementation of OpenAI Deep Research API capabilities with multiple research modes",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

research_service = ResearchService()
openai_service = OpenAIService()
websearch_service = WebSearchService()
mcp_service = MCPService()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "message": "Deep Research API - OpenAI Implementation",
        "version": "1.0.0",
        "available_modes": [mode.value for mode in ResearchMode],
        "features": [
            "Deep Research with o3-deep-research and o4-mini-deep-research models",
            "3-step prompting workflow (clarification → prompt rewriting → deep research)",
            "WebSearch + MCP combined research",
            "WebSearch-only research",
            "MCP-only research",
            "Search and fetch tools for deep research models"
        ]
    }

@app.post("/research", response_model=ResearchResult)
async def conduct_research(request: ResearchRequest):
    """
    Main research endpoint that supports all research modes:
    - o3-deep-research: Uses OpenAI's o3 deep research model
    - o4-mini-deep-research: Uses OpenAI's o4-mini deep research model  
    - websearch-mcp: Combined WebSearch + MCP research
    - websearch-only: WebSearch only research
    - mcp-only: MCP only research
    
    Includes optional 3-step prompting workflow:
    1. Clarification (using gpt-4.1)
    2. Prompt rewriting (using gpt-4.1) 
    3. Deep research (using specified model/mode)
    """
    try:
        result = await research_service.conduct_research(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@app.post("/clarify", response_model=ClarificationResponse)
async def clarify_intent(request: dict):
    """
    Step 1 of the prompting workflow: Clarify user intent and generate follow-up questions
    """
    try:
        query = request.get("query", "")
        result = await openai_service.clarify_intent(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clarification failed: {str(e)}")

@app.post("/rewrite-prompt", response_model=PromptRewriteResponse)
async def rewrite_prompt(request: dict):
    """
    Step 2 of the prompting workflow: Rewrite the prompt using clarification and user answers
    """
    try:
        original_query = request.get("original_query", "")
        clarification_with_answers = ClarificationWithAnswers(**request.get("clarification_with_answers", {}))
        result = await openai_service.rewrite_prompt(original_query, clarification_with_answers)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt rewriting failed: {str(e)}")

@app.post("/websearch", response_model=List[SearchResult])
async def web_search(request: WebSearchRequest):
    """
    Perform web search using OpenAI's web search capabilities
    """
    try:
        results = await websearch_service.search(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")

@app.post("/mcp/search", response_model=List[SearchResult])
async def mcp_search(request: MCPSearchRequest):
    """
    Search internal documents and data sources via MCP server
    """
    try:
        results = await mcp_service.search(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP search failed: {str(e)}")

@app.post("/mcp/fetch", response_model=FetchResult)
async def mcp_fetch(request: MCPFetchRequest):
    """
    Fetch detailed content from internal sources via MCP server
    """
    try:
        result = await mcp_service.fetch(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP fetch failed: {str(e)}")

@app.get("/research-modes")
async def get_research_modes():
    """
    Get available research modes and their descriptions
    """
    return {
        "modes": {
            ResearchMode.DEEP_RESEARCH_O3.value: {
                "name": "Pesquisa Profunda O3",
                "description": "Usa o modelo o3-deep-research da OpenAI com ferramentas de busca e fetch",
                "capabilities": ["busca_web", "busca_mcp", "fetch_mcp"],
                "workflow": "Prompting de 3 etapas (clarificação → reescrita → pesquisa)"
            },
            ResearchMode.DEEP_RESEARCH_O4_MINI.value: {
                "name": "Pesquisa Profunda O4 Mini", 
                "description": "Usa o modelo o4-mini-deep-research da OpenAI com ferramentas de busca e fetch",
                "capabilities": ["busca_web", "busca_mcp", "fetch_mcp"],
                "workflow": "Prompting de 3 etapas (clarificação → reescrita → pesquisa)"
            },
            ResearchMode.WEBSEARCH_MCP.value: {
                "name": "WebSearch + MCP Combinado",
                "description": "Pesquisa combinada usando busca web e fontes internas MCP",
                "capabilities": ["busca_web", "busca_mcp", "fetch_mcp", "síntese"],
                "workflow": "Prompting de 3 etapas + análise de fontes combinadas"
            },
            ResearchMode.WEBSEARCH_ONLY.value: {
                "name": "Apenas WebSearch",
                "description": "Pesquisa usando apenas capacidades de busca web",
                "capabilities": ["busca_web", "análise_web"],
                "workflow": "Prompting de 3 etapas + pesquisa focada na web"
            },
            ResearchMode.MCP_ONLY.value: {
                "name": "Apenas MCP",
                "description": "Pesquisa usando apenas fontes internas MCP",
                "capabilities": ["busca_mcp", "fetch_mcp", "análise_interna"],
                "workflow": "Prompting de 3 etapas + análise de fontes internas"
            }
        }
    }

@app.get("/research-depth-options")
async def get_research_depth_options():
    """Get available research depth configurations"""
    from .config import RESEARCH_DEPTH_CONFIG
    return {
        "depth_options": RESEARCH_DEPTH_CONFIG,
        "default": "medium",
        "description": "Opções de profundidade de pesquisa para controlar custo e velocidade"
    }

@app.get("/tools")
async def get_available_tools():
    """
    Get the tool definitions that deep research models can access
    """
    try:
        web_search_tool = await websearch_service.get_web_search_tool_definition()
        mcp_search_tool = await mcp_service.get_mcp_search_tool_definition()
        mcp_fetch_tool = await mcp_service.get_mcp_fetch_tool_definition()
        
        return {
            "tools": [web_search_tool, mcp_search_tool, mcp_fetch_tool],
            "note": "Deep research models (o3-deep-research, o4-mini-deep-research) only access search and fetch tools"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")

@app.post("/research-analysis", response_model=ResearchResult)
async def conduct_analysis_only(request: dict):
    """
    Conduct analysis step only, after clarification and prompt rewriting are complete
    """
    try:
        from .config import RESEARCH_DEPTH_CONFIG
        
        research_depth = request.get('research_depth', 'medium')
        max_tool_calls = request.get('max_tool_calls')
        if max_tool_calls is None and research_depth in RESEARCH_DEPTH_CONFIG:
            max_tool_calls = RESEARCH_DEPTH_CONFIG[research_depth]["max_tool_calls"]
        
        analysis_request = ResearchRequest(
            query=request.get('rewritten_prompt', ''),
            mode=ResearchMode(request.get('mode', 'o3-deep-research')),
            include_clarification=False,
            include_prompt_rewriting=False,
            research_depth=research_depth,
            max_tool_calls=max_tool_calls,
            background_mode=request.get('background_mode', True)
        )
        result = await research_service.conduct_research(analysis_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize MCP server connection on startup"""
    try:
        await mcp_service.initialize_mcp_server()
        print("Deep Research API started successfully")
        print("Available research modes:", [mode.value for mode in ResearchMode])
    except Exception as e:
        print(f"Warning: MCP server initialization failed: {e}")
        print("MCP functionality may be limited")
