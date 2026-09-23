from flask import Blueprint,request,jsonify
from memory.store import memory
bp=Blueprint('chat',__name__)
def register(gemma,rag,web_search,weather_get):
 @bp.post('/api/chat')
 def chat():
  d=request.get_json(silent=True) or {};q=(d.get('message') or '').strip();city=(d.get('city') or '').strip()
  if not q:return jsonify({'error':'message is required'}),400
  cid=memory.ensure(d.get('conversation_id'));history=memory.get(cid)
  try:plan=gemma.plan(q)
  except Exception:plan={'queries':[q],'weather_required':bool(city)}
  evidence=[]
  for x in (plan.get('queries') or [q])[:3]:
   evidence.extend(rag.search(x,5))
   if web_search:evidence.extend(web_search(x))
  seen=set();unique=[]
  for e in sorted(evidence,key=lambda x:x.get('score',0),reverse=True):
   k=(e.get('source'),e.get('page'),e.get('url'),e.get('text','')[:100])
   if k not in seen:seen.add(k);unique.append(e)
  evidence=unique[:8];weather=None
  if city and plan.get('weather_required',True):
   try:weather=weather_get(city)
   except Exception as e:weather={'error':str(e)}
  hist='\n'.join(f"{x['role']}: {x['content']}" for x in history[-8:]) or '(none)'; ev='\n\n'.join(f"[{i+1}] {e.get('source')} | {e.get('url','')} | page={e.get('page','')}\n{e['text']}" for i,e in enumerate(evidence)) or '(No retrieved evidence.)'
  prompt=f'''User question: {q}\nCity: {city or '(not provided)'}\nConversation:\n{hist}\nWeather:\n{weather or '(not available)'}\nEvidence:\n{ev}\nAnswer clearly and cite supplied evidence as [1], [2], etc. Never invent citations.'''
  answer=gemma.generate(prompt);memory.add(cid,'user',q);memory.add(cid,'assistant',answer)
  return jsonify({'conversation_id':cid,'answer':answer,'plan':plan,'weather':weather,'sources':[{k:e[k] for k in ('source','url','page','score','type') if k in e} for e in evidence]})
 return bp
