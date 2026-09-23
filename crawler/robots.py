from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
cache={}
def allowed(url,ua='KrishiGPT/1.0 (Educational)'):
 p=urlparse(url); origin=f'{p.scheme}://{p.netloc}'
 if origin not in cache:
  rp=RobotFileParser();rp.set_url(origin+'/robots.txt')
  try:rp.read();cache[origin]=rp
  except Exception:return False
 return cache[origin].can_fetch(ua,url)
