from flask import Flask,jsonify
from flask_cors import CORS
from config import *
from model.gemma import Gemma
from retrieval.rag import RAG
from weather.openmeteo import get_weather
from api.chat import register as register_chat
from api.health import register as register_health
app=Flask(__name__);CORS(app);gemma=Gemma(MODEL_PATH,LLAMA_SERVER_URL);rag=RAG(INDEX_DIR,PDF_DIR)
try:rag.load()
except Exception as e:print('[RAG] load skipped:',e)
def live_web(q):
 from crawler.web import search_sources
 return search_sources(q,ROOT_URLS)
app.register_blueprint(register_chat(gemma,rag,live_web if LIVE_WEB_ENABLED else None,get_weather));app.register_blueprint(register_health(gemma,rag))
@app.post('/api/index/build')
def build_index():
 try:return jsonify({'status':'ok','chunks':rag.build()})
 except Exception as e:return jsonify({'error':str(e)}),500
@app.get('/')
def root():return jsonify({'name':'KrishiGPT','status':'running','endpoints':['/api/health','/api/chat','/api/index/build']})
if __name__=='__main__':app.run(host=HOST,port=PORT,debug=False)
