import uuid
from threading import Lock
from config import MAX_MEMORY_MESSAGES
class ConversationMemory:
 def __init__(self): self.data={}; self.lock=Lock()
 def create(self):
  cid=str(uuid.uuid4())
  with self.lock:self.data[cid]=[]
  return cid
 def ensure(self,cid=None):
  if cid:
   with self.lock:
    if cid in self.data:return cid
  return self.create()
 def get(self,cid):
  with self.lock:return list(self.data.get(cid,[]))
 def add(self,cid,role,content):
  with self.lock:
   self.data.setdefault(cid,[]).append({'role':role,'content':content}); self.data[cid]=self.data[cid][-MAX_MEMORY_MESSAGES:]
 def delete(self,cid):
  with self.lock:self.data.pop(cid,None)
memory=ConversationMemory()
