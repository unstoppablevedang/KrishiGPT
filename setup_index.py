from config import PDF_DIR,INDEX_DIR
from retrieval.rag import RAG
if __name__=='__main__':print('Indexed chunks:',RAG(INDEX_DIR,PDF_DIR).build())
