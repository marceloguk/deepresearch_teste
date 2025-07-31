import openai
from typing import List, Dict, Any, Optional
import json
import time
from datetime import datetime
import logging

from ..config import settings
from ..models import (
    ResearchRequest, ResearchResult, ClarificationResponse, 
    PromptRewriteResponse, ResearchStep, ResearchMode,
    ClarificationWithAnswers
)


logger = logging.getLogger(__name__)
if not logger.handlers:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


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
                Você é um assistente de pesquisa especializado. Um usuário enviou a seguinte consulta de pesquisa:
                
                "{query}"
                
                Sua tarefa é:
                1. Identificar ambiguidades ou contexto ausente na consulta
                2. Gerar 2-3 perguntas de clarificação que ajudariam a melhorar a pesquisa
                3. Fornecer uma declaração de intenção clarificada baseada em suposições razoáveis
                
                Foque em entender:
                - O escopo específico e profundidade da pesquisa necessária
                - Público-alvo ou caso de uso
                - Período de tempo ou restrições geográficas
                - Tipos preferidos de fontes ou evidências
                
                Responda em formato JSON com:
                {{
                    "questions": [
                        {{"question": "...", "context": "..."}},
                        ...
                    ],
                    "clarified_intent": "Uma declaração clara do que o usuário provavelmente quer pesquisar"
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
        Você é um especialista em engenharia de prompts para tarefas de pesquisa. Você precisa reescrever uma consulta do usuário em um prompt abrangente e detalhado adequado para pesquisa profunda.
        
        Consulta original: "{original_query}"
        Intenção clarificada: "{clarification_with_answers.clarified_intent}"
        {user_answers_text}
        
        Crie um prompt detalhado e expandido que:
        1. Define claramente o escopo e objetivos da pesquisa baseado nas respostas do usuário
        2. Especifica o tipo de análise necessária incorporando as preferências do usuário
        3. Inclui orientações sobre tipos de fontes e qualidade de evidências conforme especificado pelo usuário
        4. Fornece estrutura para a saída esperada correspondendo aos requisitos do usuário
        5. Incorpora as melhores práticas para pesquisa abrangente
        
        O prompt reescrito deve ser adequado para um modelo de pesquisa profunda que irá:
        - Buscar informações relevantes usando ferramentas de busca web
        - Buscar conteúdo detalhado de fontes promissoras
        - Sintetizar descobertas em uma análise abrangente
        
        IMPORTANTE: O prompt reescrito deve ser em PORTUGUÊS BRASILEIRO e instruir o modelo a responder em português.
        
        Responda em formato JSON:
        {{
            "original_query": "{original_query}",
            "rewritten_prompt": "O prompt de pesquisa abrangente e detalhado incorporando as respostas do usuário, escrito em português brasileiro",
            "reasoning": "Explicação de como as respostas do usuário melhoraram o prompt de pesquisa"
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
                rewritten_prompt=f"Conduza pesquisa abrangente sobre: {original_query}. Forneça análise detalhada com evidências de apoio de múltiplas fontes confiáveis. Responda em português brasileiro.",
                reasoning="Reescrita de prompt de fallback devido a erro de processamento"
            )
    
    async def deep_research(self, prompt: str, mode: ResearchMode, tools: List[Dict[str, Any]]) -> str:
        """Step 3: Perform deep research using specified model and tools"""
        logger.info("Starting deep research in mode %s", mode.value)
        logger.debug("Research prompt: %s", prompt)
        logger.debug("Tools: %s", tools)
        if mode == ResearchMode.DEEP_RESEARCH_O3:
            model = settings.deep_research_model_o3
        elif mode == ResearchMode.DEEP_RESEARCH_O4_MINI:
            model = settings.deep_research_model_o4_mini
        else:
            model = "gpt-4"
        
        system_prompt = """
        Você é um analista de pesquisa especializado. Sua tarefa é conduzir pesquisa minuciosa sobre o tópico dado usando as ferramentas disponíveis.
        
        Processo de Pesquisa:
        1. Use a ferramenta de busca para encontrar fontes de informação relevantes
        2. Use a ferramenta de busca para recuperar conteúdo detalhado das fontes mais promissoras
        3. Analise e sintetize as informações para fornecer insights abrangentes
        4. Cite suas fontes e forneça evidências para suas conclusões
        
        Diretrizes:
        - Priorize fontes autoritativas e recentes
        - Procure múltiplas perspectivas sobre tópicos controversos
        - Forneça exemplos específicos e dados quando disponíveis
        - Estruture sua resposta claramente com títulos e marcadores
        - Inclua citações adequadas e referências de fontes
        
        IMPORTANTE: Responda sempre em PORTUGUÊS BRASILEIRO.
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
            logger.exception("Deep research failed")
            return f"Error during deep research: {str(e)}"
    
    async def _make_openai_request(self, **kwargs) -> Any:
        """Make an OpenAI API request with error handling"""
        try:
            logger.debug("OpenAI request payload: %s", kwargs)
            if "tools" in kwargs and kwargs["tools"]:
                response = self.client.chat.completions.create(**kwargs)
            else:
                response = self.client.chat.completions.create(**kwargs)
            logger.debug("OpenAI response status: %s", getattr(response, "status_code", "n/a"))
            return response
        except Exception as e:
            logger.exception("OpenAI API request failed")
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
            
            logger.debug("Deep research payload: %s", payload)
            logger.info("Iniciando chamada para API de Deep Research - isso pode levar até 20 minutos...")
            async with httpx.AsyncClient(timeout=httpx.Timeout(1200.0)) as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers=headers,
                    json=payload
                )
            logger.info("Deep research API respondeu com status: %s", response.status_code)
            if response.status_code == 200:
                logger.info("Deep research concluída com sucesso!")
            logger.debug("Deep research response body: %s", response.text)
                
            if response.status_code != 200:
                error_detail = response.text
                logger.error("Deep research request failed with code %s: %s", response.status_code, error_detail)
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
                    
        except httpx.ReadTimeout:
            logger.error("Deep research API timeout - a operação pode estar levando mais tempo que o esperado")
            raise Exception("Deep research API timeout: A pesquisa está levando mais tempo que o esperado. Tente novamente ou use um prompt mais específico.")
        except Exception as e:
            logger.exception("Deep research API request failed")
            error_msg = f"Deep research API error: {str(e)}"
            if hasattr(e, 'response'):
                response = getattr(e, 'response', None)
                if response and hasattr(response, 'text'):
                    error_msg += f" Response: {response.text}"
            raise Exception(error_msg)
