import os,re,requests
from flask import Flask,Response,abort,request,render_template_string
app=Flask(__name__)
REPO=os.environ.get('GITHUB_REPO','ZSJ0000/ZWEB_Files'); TAG=os.environ.get('GITHUB_TAG','minecraft-files'); TOKEN=os.environ.get('GITHUB_TOKEN','').strip(); PASSWORD=os.environ.get('WEB_PASSWORD','').strip(); API='https://api.github.com/repos/%s/releases/tags/%s'%(REPO,TAG)
PAGE='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ZWEB Files</title><style>body{font-family:Arial;max-width:900px;margin:30px auto;padding:15px;background:#f5f7fa}.box{background:white;padding:20px;border-radius:10px}a{color:#0782bd}.row{display:flex;justify-content:space-between;border-bottom:1px solid #eee;padding:12px 0}.size{color:#777}</style><div class="box"><h1>ZWEB Files</h1><p>{{repo}} / {{tag}}</p>{%if error%}<p>{{error}}</p>{%endif%}{%for a in assets%}<div class="row"><a href="/download/{{a.name|urlencode}}">{{a.name}}</a><span class="size">{{a.size}}</span></div>{%endfor%}</div>'''
def ok(): return not PASSWORD or request.args.get('key','')==PASSWORD or request.headers.get('X-Download-Key','')==PASSWORD
def hdr(accept='application/vnd.github+json'):
 if not TOKEN: abort(500,'GITHUB_TOKEN is not configured')
 return {'Authorization':'Bearer '+TOKEN,'Accept':accept,'User-Agent':'ZWEB-Flask-Proxy'}
def assets():
 r=requests.get(API,headers=hdr(),timeout=30)
 if r.status_code!=200: abort(r.status_code,'GitHub API error: '+r.text[:300])
 return r.json().get('assets',[])
@app.route('/')
def index():
 if not ok(): return Response('Password required',401,{'WWW-Authenticate':'Basic realm=ZWEB'})
 try:
  a=[{'name':x['name'],'size':'%.2f MB'%(x['size']/1048576)} for x in assets()]
  return render_template_string(PAGE,repo=REPO,tag=TAG,assets=a,error='')
 except Exception as e: return render_template_string(PAGE,repo=REPO,tag=TAG,assets=[],error=str(e)),500
@app.route('/download/<path:name>')
def download(name):
 if not ok(): return Response('Password required',401,{'WWW-Authenticate':'Basic realm=ZWEB'})
 if not re.match(r'^[A-Za-z0-9._ -]+$',name): abort(400,'Invalid filename')
 a=next((x for x in assets() if x['name']==name),None)
 if not a: abort(404,'File not found')
 r=requests.get(a['url'],headers=hdr('application/octet-stream'),allow_redirects=False,timeout=30)
 if r.status_code not in (301,302,303,307,308): abort(r.status_code,'GitHub download error')
 u=r.headers.get('Location')
 if not u: abort(502,'No download URL')
 q=requests.get(u,stream=True,timeout=(30,600))
 if q.status_code!=200: q.close(); abort(q.status_code,'Download failed')
 h={'Content-Disposition':"attachment; filename*=UTF-8''"+requests.utils.quote(name),'Content-Type':q.headers.get('Content-Type','application/octet-stream')}
 if q.headers.get('Content-Length'): h['Content-Length']=q.headers['Content-Length']
 def gen():
  try:
   for b in q.iter_content(1024*1024):
    if b: yield b
  finally: q.close()
 return Response(gen(),headers=h,direct_passthrough=True)
@app.route('/health')
def health(): return 'ok'
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT','5000')))
