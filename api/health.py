from flask import Blueprint,jsonify
bp=Blueprint('health',__name__)
def register(gemma,rag):
 @bp.get('/api/health')
 def health():return jsonify({'status':'ok','model_loaded':bool(gemma.server_url) or gemma.llm is not None,'rag_chunks':len(rag.records)})
 return bp
