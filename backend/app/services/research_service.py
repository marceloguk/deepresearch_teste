import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..models import (
    ResearchRequest, ResearchResult, ResearchMode, ResearchStep,
    ClarificationResponse, PromptRewriteResponse, SearchResult, FetchResult
)
from .openai_service import OpenAIService
from .websearch_service import WebSearchService
from .mcp_service import MCPService


class ResearchService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.websearch_service = WebSearchService()
        self.mcp_service = MCPService()
    
    async def conduct_research(self, request: ResearchRequest) -> ResearchResult:
        """Main research orchestration method"""
        start_time = time.time()
        steps = []
        
        try:
            clarification = None
            if request.include_clarification:
                clarification_start = time.time()
                clarification = await self.openai_service.clarify_intent(request.query)
                clarification_duration = int((time.time() - clarification_start) * 1000)
                
                steps.append(ResearchStep(
                    step_type="clarification",
                    input_data={"query": request.query},
                    output_data=clarification.dict(),
                    timestamp=datetime.now().isoformat(),
                    duration_ms=clarification_duration
                ))
            
            prompt_rewrite = None
            research_prompt = request.query
            if request.include_prompt_rewriting:
                rewrite_start = time.time()
                prompt_rewrite = await self.openai_service.rewrite_prompt(
                    request.query, 
                    clarification or ClarificationResponse(questions=[], clarified_intent=request.query)
                )
                research_prompt = prompt_rewrite.rewritten_prompt
                rewrite_duration = int((time.time() - rewrite_start) * 1000)
                
                steps.append(ResearchStep(
                    step_type="prompt_rewriting",
                    input_data={"original_query": request.query, "clarification": clarification.dict() if clarification else None},
                    output_data=prompt_rewrite.dict(),
                    timestamp=datetime.now().isoformat(),
                    duration_ms=rewrite_duration
                ))
            
            search_results = []
            fetch_results = []
            final_analysis = ""
            
            if request.mode in [ResearchMode.DEEP_RESEARCH_O3, ResearchMode.DEEP_RESEARCH_O4_MINI]:
                tools = await self._get_tools_for_mode(request.mode)
                research_start = time.time()
                final_analysis = await self.openai_service.deep_research(research_prompt, request.mode, tools)
                research_duration = int((time.time() - research_start) * 1000)
                
                steps.append(ResearchStep(
                    step_type="analysis",
                    input_data={"prompt": research_prompt, "mode": request.mode.value, "tools": [tool["function"]["name"] for tool in tools]},
                    output_data={"analysis": final_analysis},
                    timestamp=datetime.now().isoformat(),
                    duration_ms=research_duration
                ))
                
            elif request.mode == ResearchMode.WEBSEARCH_MCP:
                search_results, fetch_results, final_analysis = await self._conduct_combined_research(research_prompt, steps)
                
            elif request.mode == ResearchMode.WEBSEARCH_ONLY:
                search_results, fetch_results, final_analysis = await self._conduct_websearch_only_research(research_prompt, steps)
                
            elif request.mode == ResearchMode.MCP_ONLY:
                search_results, fetch_results, final_analysis = await self._conduct_mcp_only_research(research_prompt, steps)
            
            total_duration = int((time.time() - start_time) * 1000)
            
            return ResearchResult(
                query=request.query,
                mode=request.mode,
                clarification=clarification,
                prompt_rewrite=prompt_rewrite,
                search_results=search_results,
                fetch_results=fetch_results,
                final_analysis=final_analysis,
                steps=steps,
                total_duration_ms=total_duration,
                success=True
            )
            
        except Exception as e:
            total_duration = int((time.time() - start_time) * 1000)
            return ResearchResult(
                query=request.query,
                mode=request.mode,
                clarification=None,
                prompt_rewrite=None,
                search_results=[],
                fetch_results=[],
                final_analysis="",
                steps=steps,
                total_duration_ms=total_duration,
                success=False,
                error_message=str(e)
            )
    
    async def _get_tools_for_mode(self, mode: ResearchMode) -> List[Dict[str, Any]]:
        """Get the appropriate tools for the research mode"""
        tools = []
        
        if mode in [ResearchMode.DEEP_RESEARCH_O3, ResearchMode.DEEP_RESEARCH_O4_MINI]:
            if mode in [ResearchMode.DEEP_RESEARCH_O3, ResearchMode.DEEP_RESEARCH_O4_MINI]:
                tools.append(await self.websearch_service.get_web_search_tool_definition())
                tools.append(await self.mcp_service.get_mcp_search_tool_definition())
                tools.append(await self.mcp_service.get_mcp_fetch_tool_definition())
        
        return tools
    
    async def _conduct_combined_research(self, prompt: str, steps: List[ResearchStep]) -> tuple[List[SearchResult], List[FetchResult], str]:
        """Conduct research using both WebSearch and MCP"""
        search_results = []
        fetch_results = []
        
        web_search_start = time.time()
        web_results = await self.websearch_service.execute_web_search_tool(prompt, max_results=5)
        web_search_duration = int((time.time() - web_search_start) * 1000)
        
        search_results.extend([SearchResult(**result) for result in web_results])
        
        steps.append(ResearchStep(
            step_type="search",
            input_data={"query": prompt, "source": "websearch"},
            output_data={"results_count": len(web_results)},
            timestamp=datetime.now().isoformat(),
            duration_ms=web_search_duration
        ))
        
        mcp_search_start = time.time()
        mcp_results = await self.mcp_service.execute_mcp_search_tool(prompt, max_results=3)
        mcp_search_duration = int((time.time() - mcp_search_start) * 1000)
        
        search_results.extend([SearchResult(**result) for result in mcp_results])
        
        steps.append(ResearchStep(
            step_type="search",
            input_data={"query": prompt, "source": "mcp"},
            output_data={"results_count": len(mcp_results)},
            timestamp=datetime.now().isoformat(),
            duration_ms=mcp_search_duration
        ))
        
        for result in search_results[:3]:
            if result.url.startswith("mcp://"):
                fetch_start = time.time()
                fetch_result = await self.mcp_service.execute_mcp_fetch_tool(result.id)
                fetch_duration = int((time.time() - fetch_start) * 1000)
                
                fetch_results.append(FetchResult(**fetch_result))
                
                steps.append(ResearchStep(
                    step_type="fetch",
                    input_data={"id": result.id, "source": "mcp"},
                    output_data={"content_length": len(fetch_result["content"])},
                    timestamp=datetime.now().isoformat(),
                    duration_ms=fetch_duration
                ))
        
        analysis_prompt = f"""
        Based on the research conducted on: {prompt}
        
        Search Results Found:
        {self._format_search_results_for_analysis(search_results)}
        
        Detailed Content Retrieved:
        {self._format_fetch_results_for_analysis(fetch_results)}
        
        Provide a comprehensive analysis that synthesizes the findings from both web search and internal sources.
        """
        
        analysis_start = time.time()
        final_analysis = await self.openai_service.deep_research(analysis_prompt, ResearchMode.WEBSEARCH_MCP, [])
        analysis_duration = int((time.time() - analysis_start) * 1000)
        
        steps.append(ResearchStep(
            step_type="analysis",
            input_data={"prompt": analysis_prompt},
            output_data={"analysis": final_analysis},
            timestamp=datetime.now().isoformat(),
            duration_ms=analysis_duration
        ))
        
        return search_results, fetch_results, final_analysis
    
    async def _conduct_websearch_only_research(self, prompt: str, steps: List[ResearchStep]) -> tuple[List[SearchResult], List[FetchResult], str]:
        """Conduct research using only WebSearch"""
        search_results = []
        fetch_results = []
        
        web_search_start = time.time()
        web_results = await self.websearch_service.execute_web_search_tool(prompt, max_results=8)
        web_search_duration = int((time.time() - web_search_start) * 1000)
        
        search_results.extend([SearchResult(**result) for result in web_results])
        
        steps.append(ResearchStep(
            step_type="search",
            input_data={"query": prompt, "source": "websearch_only"},
            output_data={"results_count": len(web_results)},
            timestamp=datetime.now().isoformat(),
            duration_ms=web_search_duration
        ))
        
        analysis_prompt = f"""
        Based on web search results for: {prompt}
        
        Search Results:
        {self._format_search_results_for_analysis(search_results)}
        
        Provide a comprehensive analysis based on the web search findings.
        """
        
        analysis_start = time.time()
        final_analysis = await self.openai_service.deep_research(analysis_prompt, ResearchMode.WEBSEARCH_ONLY, [])
        analysis_duration = int((time.time() - analysis_start) * 1000)
        
        steps.append(ResearchStep(
            step_type="analysis",
            input_data={"prompt": analysis_prompt},
            output_data={"analysis": final_analysis},
            timestamp=datetime.now().isoformat(),
            duration_ms=analysis_duration
        ))
        
        return search_results, fetch_results, final_analysis
    
    async def _conduct_mcp_only_research(self, prompt: str, steps: List[ResearchStep]) -> tuple[List[SearchResult], List[FetchResult], str]:
        """Conduct research using only MCP"""
        search_results = []
        fetch_results = []
        
        mcp_search_start = time.time()
        mcp_results = await self.mcp_service.execute_mcp_search_tool(prompt, max_results=6)
        mcp_search_duration = int((time.time() - mcp_search_start) * 1000)
        
        search_results.extend([SearchResult(**result) for result in mcp_results])
        
        steps.append(ResearchStep(
            step_type="search",
            input_data={"query": prompt, "source": "mcp_only"},
            output_data={"results_count": len(mcp_results)},
            timestamp=datetime.now().isoformat(),
            duration_ms=mcp_search_duration
        ))
        
        for result in search_results:
            fetch_start = time.time()
            fetch_result = await self.mcp_service.execute_mcp_fetch_tool(result.id)
            fetch_duration = int((time.time() - fetch_start) * 1000)
            
            fetch_results.append(FetchResult(**fetch_result))
            
            steps.append(ResearchStep(
                step_type="fetch",
                input_data={"id": result.id, "source": "mcp_only"},
                output_data={"content_length": len(fetch_result["content"])},
                timestamp=datetime.now().isoformat(),
                duration_ms=fetch_duration
            ))
        
        analysis_prompt = f"""
        Based on internal research for: {prompt}
        
        Internal Sources Found:
        {self._format_search_results_for_analysis(search_results)}
        
        Detailed Internal Content:
        {self._format_fetch_results_for_analysis(fetch_results)}
        
        Provide a comprehensive analysis based on the internal sources and data.
        """
        
        analysis_start = time.time()
        final_analysis = await self.openai_service.deep_research(analysis_prompt, ResearchMode.MCP_ONLY, [])
        analysis_duration = int((time.time() - analysis_start) * 1000)
        
        steps.append(ResearchStep(
            step_type="analysis",
            input_data={"prompt": analysis_prompt},
            output_data={"analysis": final_analysis},
            timestamp=datetime.now().isoformat(),
            duration_ms=analysis_duration
        ))
        
        return search_results, fetch_results, final_analysis
    
    def _format_search_results_for_analysis(self, results: List[SearchResult]) -> str:
        """Format search results for analysis prompt"""
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.title}\n   URL: {result.url}\n   Snippet: {result.snippet}")
        return "\n\n".join(formatted)
    
    def _format_fetch_results_for_analysis(self, results: List[FetchResult]) -> str:
        """Format fetch results for analysis prompt"""
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"Document {i} (ID: {result.id}):\n{result.content[:500]}...")
        return "\n\n".join(formatted)
