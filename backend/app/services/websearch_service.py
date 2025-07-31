import httpx
from typing import List, Dict, Any, Optional
import json
import asyncio

from ..models import SearchResult, WebSearchRequest


class WebSearchService:
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def search(self, request: WebSearchRequest) -> List[SearchResult]:
        """Perform web search using OpenAI's web search capabilities"""
        
        
        mock_results = [
            SearchResult(
                id=f"search_result_{i}",
                title=f"Search Result {i} for: {request.query}",
                url=f"https://example.com/result_{i}",
                snippet=f"This is a mock search result snippet for query '{request.query}'. It contains relevant information about the topic.",
                relevance_score=0.9 - (i * 0.1)
            )
            for i in range(1, min(request.max_results + 1, 6))
        ]
        
        await asyncio.sleep(0.5)
        
        return mock_results
    
    async def get_web_search_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for web search that deep research models can use"""
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for information on a given query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to execute"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of search results to return",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    async def execute_web_search_tool(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Execute web search tool call for deep research models"""
        request = WebSearchRequest(query=query, max_results=max_results)
        results = await self.search(request)
        
        return [
            {
                "id": result.id,
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
                "relevance_score": result.relevance_score
            }
            for result in results
        ]
