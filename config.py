import os
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent
MODEL_PATH=os.getenv('MODEL_PATH',str(BASE_DIR/'models'/'gemma-3-4b-it-Q4_K_M.gguf'))
LLAMA_SERVER_URL=os.getenv('LLAMA_SERVER_URL','').strip()
HOST=os.getenv('HOST','0.0.0.0'); PORT=int(os.getenv('PORT','5000'))
MAX_MEMORY_MESSAGES=int(os.getenv('MAX_MEMORY_MESSAGES','12'))
LIVE_WEB_ENABLED=os.getenv('LIVE_WEB_ENABLED','false').lower()=='true'
PDF_DIR=BASE_DIR/'knowledge'/'pdfs'; INDEX_DIR=BASE_DIR/'knowledge'/'index'
ROOT_URLS=['https://en.wikipedia.org/wiki/','https://www.learncbse.in/','https://www.thestudypath.com/class-9/ncert-solutions/science/chapter-15-improvement-in-food-resources/','https://agroscience.net/','https://www.learncbse.in/ncert-solutions-for-class-9-science-improvement-in-food-resources/','https://www.britannica.com/search?query=','https://duckduckgo.com/html/?q=']
