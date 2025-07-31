from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    openai_api_key: str
    deep_research_model_o3: str = "o3-deep-research"
    deep_research_model_o4_mini: str = "o4-mini-deep-research"
    clarification_model: str = "gpt-4.1"
    prompt_rewriting_model: str = "gpt-4.1"
    
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8001
    
    debug: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


settings = Settings()

RESEARCH_DEPTH_CONFIG = {
    "fast": {
        "max_tool_calls": 5, 
        "description": "Pesquisa rápida com menos chamadas de ferramentas - ideal para respostas rápidas e economia de créditos"
    },
    "medium": {
        "max_tool_calls": 15, 
        "description": "Pesquisa balanceada entre velocidade e profundidade - configuração padrão recomendada"
    },
    "deep": {
        "max_tool_calls": 30, 
        "description": "Pesquisa profunda e abrangente - máxima qualidade com maior uso de créditos"
    }
}
