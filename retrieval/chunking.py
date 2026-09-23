import re
def chunk_text(text,size=900,overlap=150):
 text=re.sub(r'\s+',' ',text or '').strip(); out=[]; start=0
 while start<len(text):
  end=min(len(text),start+size)
  if end-start>=120:out.append(text[start:end])
  if end>=len(text):break
  start=end-overlap
 return out
