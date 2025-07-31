# API de Pesquisa Profunda da OpenAI

Implementação completa das capacidades de Pesquisa Profunda da OpenAI com múltiplos modos de pesquisa.

## 🎯 Funcionalidades

### 5 Modos de Pesquisa Profunda
- **o3-deep-research**: Modelo OpenAI o3 com ferramentas de busca e fetch
- **o4-mini-deep-research**: Modelo OpenAI o4-mini com ferramentas de busca e fetch  
- **WebSearch + MCP**: Pesquisa combinada usando WebSearch e MCP
- **WebSearch Only**: Pesquisa somente com WebSearch
- **MCP Only**: Pesquisa somente com MCP

### Workflow de 3 Etapas "Prompting Deep Research Models"
1. **Clarificação**: Usa gpt-4.1 para clarificar intenção e coletar contexto
2. **Reescrita de Prompt**: Usa gpt-4.1 para reescrever o prompt para melhor pesquisa
3. **Pesquisa Profunda**: Executa a pesquisa usando o modelo especificado

### Ferramentas Corretas para Modelos Deep Research
- Os modelos de deep research só acessam ferramentas `search` e `fetch`
- Sistema respeita as limitações especificadas pela OpenAI

## 🚀 Como Executar

### Pré-requisitos
- Python 3.12+
- Node.js 18+
- Poetry (para gerenciamento de dependências Python)
- npm ou yarn

### 1. Configuração do Backend

```bash
cd backend

# Instalar dependências
poetry install

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env e adicione sua chave da OpenAI:
# OPENAI_API_KEY=sua_chave_aqui

# Executar o servidor
poetry run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

### 2. Configuração do Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Executar o servidor de desenvolvimento
npm run dev
```

### 3. Acessar a Aplicação

Abra seu navegador e acesse: `http://localhost:5173`

## 📋 Configuração da Chave da OpenAI

1. Obtenha sua chave da API da OpenAI em: https://platform.openai.com/api-keys
2. Edite o arquivo `backend/.env`
3. Substitua `your_openai_api_key_here` pela sua chave real:
   ```
   OPENAI_API_KEY=sk-proj-sua_chave_real_aqui
   ```

## 🧪 Como Testar

1. **Teste Básico**: Digite uma pergunta de pesquisa e clique em "Iniciar Pesquisa Profunda"
2. **Teste de Modos**: Experimente diferentes modos de pesquisa no dropdown
3. **Teste de Workflow**: Ative/desative as etapas de clarificação e reescrita de prompt
4. **Visualização de Resultados**: Explore as abas Análise, Fluxo, Fontes e Detalhes

### Exemplo de Consulta de Teste
```
Quais são os últimos desenvolvimentos em inteligência artificial e aprendizado de máquina em 2024, particularmente focando em grandes modelos de linguagem e suas aplicações em pesquisa científica?
```

## 📁 Estrutura do Projeto

```
deep-research-api/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── main.py         # Endpoints principais
│   │   ├── config.py       # Configurações
│   │   ├── models.py       # Modelos Pydantic
│   │   └── services/       # Lógica de negócio
│   │       ├── openai_service.py
│   │       ├── research_service.py
│   │       ├── websearch_service.py
│   │       └── mcp_service.py
│   ├── pyproject.toml      # Dependências Python
│   └── .env               # Variáveis de ambiente
├── frontend/               # Interface React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── lib/           # Utilitários
│   │   └── types/         # Tipos TypeScript
│   ├── package.json       # Dependências Node.js
│   └── .env              # Configurações do frontend
└── README.md             # Este arquivo
```

## 🔧 Endpoints da API

### Principais
- `POST /research` - Conduzir pesquisa profunda
- `POST /clarify` - Clarificar intenção do usuário
- `POST /rewrite-prompt` - Reescrever prompt
- `GET /research-modes` - Obter modos disponíveis
- `GET /tools` - Obter ferramentas disponíveis

### Utilitários
- `POST /websearch` - Busca web direta
- `POST /mcp/search` - Busca MCP
- `POST /mcp/fetch` - Fetch MCP
- `GET /healthz` - Verificação de saúde

## 🛠️ Desenvolvimento

### Backend
```bash
cd backend
poetry run fastapi dev app/main.py --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

### Build para Produção
```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
poetry run fastapi run app/main.py
```

## 📚 Referências Consultadas

- [OpenAI Deep Research API](https://platform.openai.com/docs/guides/deep-research)
- [OpenAI MCP Documentation](https://platform.openai.com/docs/mcp)
- [Deep Research API Agents](https://cookbook.openai.com/examples/deep_research_api/introduction_to_deep_research_api_agents)
- [Building Deep Research MCP Server](https://cookbook.openai.com/examples/deep_research_api/how_to_build_a_deep_research_mcp_server/readme)
- [Web Search Documentation](https://platform.openai.com/docs/guides/tools-web-search)

## 🐛 Solução de Problemas

### Erro de Autenticação OpenAI
- Verifique se a chave da API está correta no arquivo `.env`
- Certifique-se de que a chave tem permissões para os modelos deep research
- **Importante**: Os modelos o3-deep-research e o4-mini-deep-research usam o endpoint v1/responses da OpenAI, não v1/chat/completions

### Erro de Conexão
- Verifique se o backend está rodando na porta 8000
- Verifique se o frontend está configurado para acessar `http://localhost:8000`

### Dependências
- Execute `poetry install` no backend
- Execute `npm install` no frontend

## 📄 Licença

Este projeto é uma implementação de demonstração das capacidades da API de Pesquisa Profunda da OpenAI.
