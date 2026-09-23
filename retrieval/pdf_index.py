import json
from pathlib import Path
from pypdf import PdfReader
from .chunking import chunk_text
def load_pdf_chunks(pdf_dir):
 out=[]
 for path in sorted(Path(pdf_dir).glob('*.pdf')):
  try:
   for page_no,page in enumerate(PdfReader(str(path)).pages,1):
    for i,chunk in enumerate(chunk_text(page.extract_text() or '')):out.append({'text':chunk,'source':path.name,'page':page_no,'chunk':i,'type':'pdf'})
  except Exception as e:print(f'[PDF] {path.name}: {e}')
 return out
def save_records(records,path):Path(path).write_text(json.dumps(records,ensure_ascii=False),encoding='utf-8')
def load_records(path):
 p=Path(path); return json.loads(p.read_text(encoding='utf-8')) if p.exists() else []
