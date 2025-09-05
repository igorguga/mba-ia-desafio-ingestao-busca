import os
import time
from utils.logs import setup_logging
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
EMBEDDINGS_BATCH_SIZE = 100
EMBEDDINGS_DELAY_IN_SECONDS = 60

load_dotenv()
for k in ("GOOGLE_API_KEY", 
          "DATABASE_URL",
          "PG_VECTOR_COLLECTION_NAME",
          "PDF_PATH",
          "GOOGLE_EMBEDDING_MODEL"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

logger = setup_logging("ingest")

def _store_documents_rate_limited(store: PGVector, 
                                  documents: list[Document], 
                                  ids: list[str], 
                                  batch_size:int = EMBEDDINGS_BATCH_SIZE, 
                                  delay_in_seconds:int = EMBEDDINGS_DELAY_IN_SECONDS):
    """
    Store documents in the database in a rate limited way because the Gemini Embedding API has a rate limit
    of 100 requests per minute.
    """
    if len(documents) < batch_size:
        logger.info(f"Storing all {len(documents)} documents...")
        store.add_documents(documents=documents, ids=ids)
        return

    total_parts = -(-len(documents) // batch_size)
    current_part = 0
    for i in range(0, len(documents), batch_size):
        current_part += 1
        logger.info(f"Storing part {current_part} of {total_parts}")
        batch = documents[i:i+batch_size]
        ids_batch = ids[i:i+batch_size]
        store.add_documents(documents=batch, ids=ids_batch)
        logger.info(f"\tDone.")
        if i + batch_size < len(documents):
            logger.info(f"\tSleeping for {delay_in_seconds} seconds...")
            time.sleep(delay_in_seconds)

def ingest_pdf():
    logger.info(f"Ingesting PDF from {os.getenv('PDF_PATH')}...")
    loader = PyPDFLoader(os.getenv("PDF_PATH"))
    docs = loader.load()
    logger.info(f"Loaded {len(docs)} documents...")

    logger.info(f"Splitting {len(docs)} documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, 
                                              chunk_overlap=CHUNK_OVERLAP, 
                                              add_start_index=False)
    chunks = splitter.split_documents(docs)

    logger.info(f"Enriching {len(chunks)} chunks...")
    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in chunks
    ]    
    
    logger.info(f"Creating {len(enriched)} ids...")
    ids = [f"doc-{i}" for i in range(len(enriched))]

    logger.info(f"Creating embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(model=os.getenv("GOOGLE_EMBEDDING_MODEL"))

    logger.info(f"Creating store...")
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

    logger.info(f"Storing {len(enriched)} documents...")
    _store_documents_rate_limited(store, enriched, ids)
    logger.info(f"Done!")

if __name__ == "__main__":
    ingest_pdf()



