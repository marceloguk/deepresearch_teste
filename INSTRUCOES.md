# 📦 Instruções de Instalação e Execução

## 🚀 Guia Rápido de Instalação

### 1. Extrair o Arquivo ZIP
```bash
# Extraia o arquivo deep-research-api.zip
unzip deep-research-api.zip
cd deep-research-api
```

### 2. Instalar Dependências do Sistema

#### No Ubuntu/Debian:
```bash
# Instalar Python 3.12, Node.js e Poetry
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip nodejs npm
curl -sSL https://install.python-poetry.org | python3 -
```

#### No macOS:
```bash
# Instalar usando Homebrew
brew install python@3.12 node poetry
```

#### No Windows:
1. Instale Python 3.12 de https://python.org
2. Instale Node.js de https://nodejs.org
3. Instale Poetry: `pip install poetry`

### 3. Configurar Backend

```bash
cd backend

# Instalar dependências Python
poetry install

# Configurar chave da OpenAI
cp .env .env.backup
# Edite o arquivo .env e substitua 'your_openai_api_key_here' pela sua chave real da OpenAI
```

**⚠️ IMPORTANTE**: Você precisa de uma chave da API da OpenAI para usar os modelos de pesquisa profunda:
1. Acesse https://platform.openai.com/api-keys
2. Crie uma nova chave
3. Edite `backend/.env` e substitua `your_openai_api_key_here` pela sua chave

### 4. Configurar Frontend

```bash
cd ../frontend

# Instalar dependências Node.js
npm install
```

### 5. Executar a Aplicação

#### Terminal 1 - Backend:
```bash
cd backend
poetry run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### 6. Acessar a Aplicação

Abra seu navegador e acesse: **http://localhost:5173**

## 🧪 Testando a Aplicação

1. **Digite uma pergunta de pesquisa** no campo de texto
2. **Selecione um modo de pesquisa** (recomendado: "Pesquisa Profunda O3")
3. **Configure o workflow** (deixe ambas as opções ativadas)
4. **Clique em "Iniciar Pesquisa Profunda"**

### Exemplo de Pergunta para Teste:
```
Quais são as principais tendências em inteligência artificial para 2024?
```

## 🔧 Solução de Problemas Comuns

### Erro: "ModuleNotFoundError"
```bash
cd backend
poetry install
```

### Erro: "npm command not found"
Instale Node.js de https://nodejs.org

### Erro: "poetry command not found"
```bash
pip install poetry
```

### Erro de Autenticação OpenAI
- Verifique se sua chave da API está correta no arquivo `backend/.env`
- Certifique-se de que tem créditos na sua conta OpenAI
- **Importante**: Os modelos o3-deep-research e o4-mini-deep-research usam o endpoint v1/responses da OpenAI, não v1/chat/completions

### Porta já em uso
Se as portas 8000 ou 5173 estiverem em uso:

**Backend (porta 8000):**
```bash
poetry run fastapi dev app/main.py --host 0.0.0.0 --port 8001
# Então edite frontend/.env e mude VITE_API_URL para http://localhost:8001
```

**Frontend (porta 5173):**
```bash
npm run dev -- --port 3000
```

## 📋 Verificação de Funcionamento

### ✅ Backend Funcionando
Acesse http://localhost:8000 - deve mostrar informações da API

### ✅ Frontend Funcionando  
Acesse http://localhost:5173 - deve mostrar a interface da aplicação

### ✅ Integração Funcionando
Digite uma pergunta e teste a pesquisa - deve mostrar resultados ou erro de autenticação (se não configurou a chave OpenAI)

## 🎯 Próximos Passos

1. **Configure sua chave OpenAI** para usar os modelos de pesquisa profunda
2. **Teste todos os 5 modos de pesquisa** disponíveis
3. **Explore as diferentes abas** de resultados (Análise, Fluxo, Fontes, Detalhes)
4. **Experimente com diferentes tipos de perguntas** de pesquisa

## 📞 Suporte

Se encontrar problemas:
1. Verifique se seguiu todos os passos de instalação
2. Confirme que as dependências estão instaladas
3. Verifique os logs nos terminais para mensagens de erro específicas
4. Certifique-se de que sua chave OpenAI está configurada corretamente

**A aplicação está pronta para uso! 🚀**
