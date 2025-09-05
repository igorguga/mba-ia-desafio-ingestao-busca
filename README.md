# Desafio MBA Engenharia de Software com IA - Full Cycle

## 📋 Sobre o Projeto

Este projeto implementa um sistema de **RAG (Retrieval-Augmented Generation)** que permite fazer perguntas sobre documentos PDF utilizando inteligência artificial. O sistema utiliza:

- **Google Gemini** para geração de respostas
- **Google Embeddings** para busca semântica
- **PostgreSQL com pgvector** para armazenamento de vetores
- **LangChain** para orquestração do pipeline

## 🏗️ Estrutura do Projeto

```
mba-ia-desafio-ingestao-busca/
├── src/
│   ├── chat.py              # Interface de chat interativa
│   ├── ingest.py            # Script de ingestão de documentos PDF
│   ├── search.py            # Módulo de busca semântica
│   └── utils/
│       ├── logs.py          # Configuração de logging
│       └── logs_conf.yaml   # Configuração YAML para logs
├── document.pdf             # Documento PDF para ingestão
├── docker-compose.yml       # Configuração do banco PostgreSQL
├── requirements.txt         # Dependências Python
└── README.md               # Este arquivo
```

## 🚀 Funcionalidades

### 1. **Ingestão de Documentos** (`ingest.py`)
- Carrega documentos PDF
- Divide o conteúdo em chunks otimizados
- Gera embeddings usando Google AI
- Armazena no banco PostgreSQL com pgvector
- Implementa rate limiting para respeitar limites da API

### 2. **Busca Semântica** (`search.py`)
- Realiza busca por similaridade no banco vetorial
- Retorna os chunks mais relevantes para a pergunta
- Utiliza prompt template para contexto controlado

### 3. **Interface de Chat** (`chat.py`)
- Interface interativa com Rich para melhor UX
- Integra busca semântica com geração de respostas
- Comandos especiais: `sair`, `limpar`, `ajuda`
- Respostas baseadas apenas no contexto do documento

## ⚙️ Configuração e Instalação

### Pré-requisitos
- Python 3.8+
- Docker e Docker Compose
- Chave da API do Google AI (Gemini)

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd mba-ia-desafio-ingestao-busca
```

### 2. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Google AI Configuration
GOOGLE_API_KEY=sua_chave_da_api_google
GEMINI_MODEL=gemini-1.5-flash
GOOGLE_EMBEDDING_MODEL=text-embedding-004

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=documentos

# Document Configuration
PDF_PATH=./document.pdf
```

### 3. Instale as dependências
```bash
# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 4. Configure o banco de dados
```bash
# Inicie o PostgreSQL com pgvector
docker-compose up -d

# Aguarde o banco estar pronto (verifique com docker-compose logs)
```

## 🎯 Como Executar

### 1. **Ingestão do Documento**
Primeiro, execute a ingestão do PDF para popular o banco de dados:

```bash
python src/ingest.py
```

Este script irá:
- Carregar o `document.pdf`
- Dividir em chunks de 1000 caracteres
- Gerar embeddings
- Armazenar no banco PostgreSQL

### 2. **Iniciar o Chat**
Após a ingestão, inicie a interface de chat:

```bash
python src/chat.py
```

### 3. **Usar o Sistema**
- Digite suas perguntas sobre o documento
- O sistema buscará informações relevantes e gerará respostas
- Use os comandos especiais:
  - `sair`/`quit`/`exit` - Encerrar o chat
  - `limpar` - Limpar a tela
  - `ajuda` - Mostrar comandos disponíveis

## 🔧 Configurações Avançadas

### Parâmetros de Ingestão
No arquivo `ingest.py`, você pode ajustar:
- `CHUNK_SIZE = 1000` - Tamanho dos chunks de texto
- `CHUNK_OVERLAP = 100` - Sobreposição entre chunks
- `EMBEDDINGS_BATCH_SIZE = 100` - Tamanho do lote para embeddings
- `EMBEDDINGS_DELAY_IN_SECONDS = 60` - Delay entre lotes (rate limiting)

## 🐛 Solução de Problemas

### Erro de Conexão com o Banco
```bash
# Verifique se o container está rodando
docker-compose ps

# Reinicie se necessário
docker-compose restart
```

### Erro de API Key
- Verifique se a `GOOGLE_API_KEY` está correta no arquivo `.env`
- Confirme se a API está habilitada no Google Cloud Console

### Rate Limiting
- O sistema implementa delay automático entre requisições
- Ajuste `EMBEDDINGS_DELAY_IN_SECONDS` se necessário

## 📊 Logs

O sistema utiliza logging configurado via YAML. Os logs são exibidos no console com formato:
```
[2024-01-01 12:00:00: ingest INFO] Mensagem do log
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **LangChain** - Framework para aplicações LLM
- **Google Gemini** - Modelo de linguagem
- **PostgreSQL + pgvector** - Banco vetorial
- **Rich** - Interface de terminal rica
- **Docker** - Containerização do banco
- **PyPDF** - Processamento de PDFs

## 📝 Notas Importantes

- O sistema responde **apenas** com base no conteúdo do documento ingerido
- Se a informação não estiver no documento, retornará: "Não tenho informações necessárias para responder sua pergunta"
- A ingestão deve ser executada sempre que houver mudanças no documento PDF
- O banco de dados persiste entre execuções (volume Docker)