import json,requests
SYSTEM='''You are KrishiGPT, an agriculture information assistant. Use only supplied evidence, weather data and conversation context. Do not invent sources, measurements, diagnoses or facts. If evidence is insufficient, say so. Give clear practical agricultural guidance. For important real-world farm decisions, recommend checking local experts or official advisories. Never reveal hidden reasoning.'''
class Gemma:
 def __init__(self,model_path,server_url=''):self.model_path=model_path;self.server_url=server_url.rstrip('/');self.llm=None
 def load(self):
  if self.server_url:return
  from llama_cpp import Llama
  self.llm=Llama(model_path=self.model_path,n_ctx=8192,n_threads=4,verbose=False)
 def generate(self,prompt,max_tokens=700,temperature=.2):
  if self.server_url:
   r=requests.post(self.server_url+'/v1/chat/completions',json={'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}],'temperature':temperature,'max_tokens':max_tokens},timeout=180);r.raise_for_status();return r.json()['choices'][0]['message']['content'].strip()
  if self.llm is None:self.load()
  o=self.llm.create_chat_completion(messages=[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}],temperature=temperature,max_tokens=max_tokens);return o['choices'][0]['message']['content'].strip()
 def plan(self,q):
  raw=self.generate(f'Create a compact JSON query plan for this agriculture question. Return JSON only with keys: intent, subject, task, weather_required, queries. Question: {q}',300,0)
  try:a,b=raw.find('{'),raw.rfind('}');return json.loads(raw[a:b+1])
  except Exception:return {'intent':'general_agriculture','subject':'','task':q,'weather_required':True,'queries':[q]}
