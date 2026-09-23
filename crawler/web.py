import time,requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .robots import allowed
from retrieval.chunking import chunk_text
UA='KrishiGPT/1.0 (Educational)'
def fetch(url):
 if not allowed(url,UA):return None
 r=requests.get(url,headers={'User-Agent':UA},timeout=10);r.raise_for_status()
 return r.text if 'text/html' in r.headers.get('content-type','') else None
def search_sources(query,roots,max_pages=6):
 urls=[]
 for root in roots:
  if 'duckduckgo.com/html/?q=' in root or 'britannica.com/search?query=' in root:urls.append(root+quote_plus(query))
  elif root.endswith('/'):urls.append(root+quote_plus(query).replace('%20','_'))
  else:urls.append(root)
 out=[]
 for url in urls[:max_pages]:
  try:
   page=fetch(url)
   if page:
    soup=BeautifulSoup(page,'html.parser')
    for tag in soup(['script','style','noscript','nav','footer','header']):tag.decompose()
    title=soup.title.get_text(' ',strip=True) if soup.title else url
    for chunk in chunk_text(soup.get_text(' ',strip=True)):out.append({'text':chunk,'source':title,'url':url,'type':'web'})
   time.sleep(1)
  except Exception:pass
 return out
