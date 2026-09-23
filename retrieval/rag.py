from pathlib import Path
class RAG:
 def __init__(self,index_dir,pdf_dir):self.index_dir=Path(index_dir);self.pdf_dir=Path(pdf_dir);self.index_dir.mkdir(parents=True,exist_ok=True);self.records=[];self.model=None;self.index=None
 def build(self):
  from .pdf_index import load_pdf_chunks,save_records
  rec=load_pdf_chunks(self.pdf_dir); self.records=rec
  if not rec:return 0
  import faiss
  from sentence_transformers import SentenceTransformer
  self.model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); v=self.model.encode([r['text'] for r in rec],normalize_embeddings=True,show_progress_bar=True).astype('float32'); self.index=faiss.IndexFlatIP(v.shape[1]); self.index.add(v); faiss.write_index(self.index,str(self.index_dir/'knowledge.faiss')); save_records(rec,self.index_dir/'records.json'); return len(rec)
 def load(self):
  import faiss
  from .pdf_index import load_records
  idx=self.index_dir/'knowledge.faiss'; rec=self.index_dir/'records.json'
  if not idx.exists() or not rec.exists():return False
  from sentence_transformers import SentenceTransformer
  self.model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); self.index=faiss.read_index(str(idx)); self.records=load_records(rec); return True
 def search(self,q,k=8):
  if self.index is None or not self.records:return []
  v=self.model.encode([q],normalize_embeddings=True).astype('float32'); scores,ids=self.index.search(v,min(k,len(self.records))); out=[]
  for score,i in zip(scores[0],ids[0]):
   if i>=0:x=dict(self.records[i]);x['score']=float(score);out.append(x)
  return out
