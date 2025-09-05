import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_postgres import PGVector

load_dotenv()
for k in ("GOOGLE_API_KEY", 
          "DATABASE_URL",
          "PG_VECTOR_COLLECTION_NAME",
          "PDF_PATH",
          "GOOGLE_EMBEDDING_MODEL"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def _database_search(question):

  embeddings = GoogleGenerativeAIEmbeddings(model=os.getenv("GOOGLE_EMBEDDING_MODEL"))

  store = PGVector(
      embeddings=embeddings,
      collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
      connection=os.getenv("DATABASE_URL"),
      use_jsonb=True,
  )

  return store.similarity_search_with_score(question, k=10)


def search_prompt(question=None): 
  template = PromptTemplate(
      input_variables=["contexto","pergunta"],
      template=PROMPT_TEMPLATE
  )

  contexto = _database_search(question)

  if question:
    return template.format(contexto=contexto, pergunta=question)
  else:
    return template


if __name__ == "__main__":
  print(search_prompt("Qual é a capital da França?"))