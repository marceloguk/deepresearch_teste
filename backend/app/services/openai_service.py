import openai
from typing import List, Dict, Any, Optional
import json
import time
from datetime import datetime

from ..config import settings
from ..models import (
    ResearchRequest, ResearchResult, ClarificationResponse, 
    PromptRewriteResponse, ResearchStep, ResearchMode,
    ClarificationWithAnswers
)


class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def clarify_intent(self, query: str) -> ClarificationResponse:
        """Step 1: Use intermediate model to clarify user intent"""
        start_time = time.time()
        
        mock_questions = [
            {
                "question": "Qual é o foco específico da sua pesquisa sobre IA no mercado de trabalho?",
                "context": "Você gostaria de focar em setores específicos (tecnologia, saúde, educação), tipos de trabalho (manual, intelectual, criativo), ou uma análise geral?"
            },
            {
                "question": "Que período de tempo você gostaria que a análise cobrisse?",
                "context": "Você está interessado em tendências atuais (2023-2025), projeções futuras (próximos 5-10 anos), ou uma perspectiva histórica comparativa?"
            },
            {
                "question": "Você tem interesse em aspectos específicos do impacto da IA?",
                "context": "Por exemplo: criação vs. eliminação de empregos, mudanças nas habilidades necessárias, impacto salarial, ou políticas públicas relacionadas?"
            }
        ]
        
        clarified_intent = f"Realizar pesquisa abrangente sobre como a inteligência artificial está transformando o mercado de trabalho no Brasil, incluindo análise de impactos atuais, tendências futuras e implicações socioeconômicas."
        
        try:
            if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
                clarification_prompt = f"""
                You are an expert research assistant. A user has submitted the following research query:
                
                "{query}"
                
                Your task is to:
                1. Identify any ambiguities or missing context in the query
                2. Generate 2-3 clarifying questions that would help improve the research
                3. Provide a clarified intent statement based on reasonable assumptions
                
                Focus on understanding:
                - The specific scope and depth of research needed
                - Target audience or use case
                - Time frame or geographical constraints
                - Preferred types of sources or evidence
                
                Respond in JSON format with:
                {{
                    "questions": [
                        {{"question": "...", "context": "..."}},
                        ...
                    ],
                    "clarified_intent": "A clear statement of what the user likely wants to research"
                }}
                """
                
                response = await self._make_openai_request(
                    model=settings.clarification_model,
                    messages=[{"role": "user", "content": clarification_prompt}],
                    response_format={"type": "json_object"}
                )
                
                result_data = json.loads(response.choices[0].message.content)
                return ClarificationResponse(**result_data)
            else:
                return ClarificationResponse(
                    questions=mock_questions,
                    clarified_intent=clarified_intent
                )
                
        except Exception as e:
            return ClarificationResponse(
                questions=mock_questions,
                clarified_intent=clarified_intent
            )
    
    async def rewrite_prompt(self, original_query: str, clarification_with_answers: ClarificationWithAnswers) -> PromptRewriteResponse:
        """Step 2: Rewrite the prompt for deep research using user answers"""
        start_time = time.time()
        
        user_answers_text = ""
        if clarification_with_answers.answers:
            user_answers_text = "\n\nUser provided the following answers to clarification questions:\n"
            for answer in clarification_with_answers.answers:
                if answer.question_index < len(clarification_with_answers.questions):
                    question = clarification_with_answers.questions[answer.question_index]
                    user_answers_text += f"Q: {question.question}\nA: {answer.answer}\n\n"
        
        rewrite_prompt = f"""
        You are an expert prompt engineer for research tasks. You need to rewrite a user query into a comprehensive, detailed prompt suitable for deep research.
        
        Original query: "{original_query}"
        Clarified intent: "{clarification_with_answers.clarified_intent}"
        {user_answers_text}
        
        Create a detailed, expanded prompt that:
        1. Clearly defines the research scope and objectives based on user answers
        2. Specifies the type of analysis needed incorporating user preferences
        3. Includes guidance on source types and evidence quality as specified by user
        4. Provides structure for the expected output matching user requirements
        5. Incorporates best practices for comprehensive research
        
        The rewritten prompt should be suitable for a deep research model that will:
        - Search for relevant information using web search tools
        - Fetch detailed content from promising sources
        - Synthesize findings into a comprehensive analysis
        
        Respond in JSON format:
        {{
            "original_query": "{original_query}",
            "rewritten_prompt": "The comprehensive, detailed research prompt incorporating user answers",
            "reasoning": "Explanation of how user answers improved the research prompt"
        }}
        """
        
        try:
            response = await self._make_openai_request(
                model=settings.prompt_rewriting_model,
                messages=[{"role": "user", "content": rewrite_prompt}],
                response_format={"type": "json_object"}
            )
            
            result_data = json.loads(response.choices[0].message.content)
            return PromptRewriteResponse(**result_data)
            
        except Exception as e:
            return PromptRewriteResponse(
                original_query=original_query,
                rewritten_prompt=f"Conduct comprehensive research on: {original_query}. Provide detailed analysis with supporting evidence from multiple reliable sources.",
                reasoning="Fallback prompt rewrite due to processing error"
            )
    
    async def deep_research(self, prompt: str, mode: ResearchMode, tools: List[Dict[str, Any]]) -> str:
        """Step 3: Perform deep research using specified model and tools"""
        
        if mode == ResearchMode.DEEP_RESEARCH_O3:
            model = settings.deep_research_model_o3
        elif mode == ResearchMode.DEEP_RESEARCH_O4_MINI:
            model = settings.deep_research_model_o4_mini
        else:
            model = "gpt-4"
        
        system_prompt = """
        You are an expert research analyst. Your task is to conduct thorough research on the given topic using the available tools.
        
        Research Process:
        1. Use the search tool to find relevant information sources
        2. Use the fetch tool to retrieve detailed content from the most promising sources
        3. Analyze and synthesize the information to provide comprehensive insights
        4. Cite your sources and provide evidence for your conclusions
        
        Guidelines:
        - Prioritize authoritative and recent sources
        - Look for multiple perspectives on controversial topics
        - Provide specific examples and data when available
        - Structure your response clearly with headings and bullet points
        - Include proper citations and source references
        """
        
        try:
            if mode in [ResearchMode.DEEP_RESEARCH_O3, ResearchMode.DEEP_RESEARCH_O4_MINI]:
                response = await self._make_deep_research_request(
                    model=model,
                    prompt=f"{system_prompt}\n\nUser Query: {prompt}",
                    tools=tools
                )
                return response
            else:
                response = await self._make_openai_request(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    tools=tools
                )
                return response.choices[0].message.content
            
        except Exception as e:
            return f"Error during deep research: {str(e)}"
    
    async def _make_openai_request(self, **kwargs) -> Any:
        """Make an OpenAI API request with error handling"""
        try:
            if "tools" in kwargs and kwargs["tools"]:
                response = self.client.chat.completions.create(**kwargs)
            else:
                response = self.client.chat.completions.create(**kwargs)
            return response
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _make_deep_research_request(self, model: str, prompt: str, tools: List[Dict[str, Any]]) -> str:
        """Make a request to the OpenAI Responses API for deep research models"""
        try:
            import httpx
            
            headers = {
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            formatted_tools = [{"type": "web_search_preview"}]
            
            payload = {
                "model": model,
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt}
                        ]
                    }
                ],
                "reasoning": {"summary": "auto"},
                "tools": formatted_tools
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers=headers,
                    json=payload,
                    timeout=300.0  # 5 minutes timeout for deep research
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    raise Exception(f"Error code: {response.status_code} - {error_detail}")
                
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                    elif "content" in choice:
                        return choice["content"]
                    else:
                        return "No content returned"
                else:
                    return "No response generated"
                    
        except Exception as e:
            raise Exception(f"Deep research API error: {str(e)}")
