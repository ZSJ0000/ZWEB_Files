import os
from urllib.parse import urlparse, urljoin
import requests
from flask import Flask, Response, abort, request, redirect, render_template_string

app = Flask(__name__)
PASSWORD = os.environ.get("WEB_PASSWORD", "").strip()
ALLOWED = {"github.com", "www.github.com", "raw.githubusercontent.com", "api.github.com", "codeload.github.com", "github.githubassets.com"}

PAGE = '''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GitHub Proxy</title><style>body{font:16px Arial;max-width:900px;margin:40px auto;padding:15px}input{width:80%;padding:10px}button{padding:10px}</style><h1>个人 GitHub 代理</h1><form action="/github" method="get"><input name="url" placeholder="https://github.com/ZSJ0000/ZWEB_Files"><input type="hidden" name="key" value="{{key}}"><button>访问</button></form><p>仅允许 GitHub 相关域名。</p>'''

def check():
    if not PASSWORD:
        abort(503, "Set WEB_PASSWORD first")
    if request.args.get("key", "") != PASSWORD and request.headers.get("X-Proxy-Key", "") != PASSWORD:
        return False
    return True

def allowed(url):
    p = urlparse(url)
    return p.scheme in ("http", "https") and (p.hostname or "").lower() in ALLOWED

def key_url(url):
    return "/github?url=" + requests.utils.quote(url, safe="") + "&key=" + requests.utils.quote(PASSWORD, safe="")

def rewrite_html(text, base):
    import re
    def sub(m):
        attr, val = m.group(1), m.group(2)
        if val.startswith(("#", "data:", "mailto:", "javascript:")):
            return m.group(0)
        u = urljoin(base, val)
        return ' %s="%s"' % (attr, key_url(u)) if allowed(u) else m.group(0)
    return re.sub(r'\s(href|src|action)=["\']([^"\']+)["\']', sub, text, flags=re.I)

@app.route("/")
def index():
    if not check():
        return Response("Password required", 401, {"WWW-Authenticate": "Basic realm=GitHubProxy"})
    return render_template_string(PAGE, key=PASSWORD)

@app.route("/github")
def github():
    if not check():
        return Response("Password required", 401, {"WWW-Authenticate": "Basic realm=GitHubProxy"})
    url = request.args.get("url", "").strip()
    if not allowed(url):
        abort(400, "Only GitHub domains are allowed")
    r = requests.get(url, headers={"User-Agent": "Personal-GitHub-Proxy"}, stream=True, timeout=(30, 300), allow_redirects=False)
    if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("Location"):
        u = urljoin(url, r.headers["Location"])
        if allowed(u):
            return redirect(key_url(u), code=302)
        abort(403, "Redirect outside allowed GitHub domains")
    content_type = r.headers.get("Content-Type", "application/octet-stream")
    if "text/html" in content_type:
        body = r.content.decode(r.encoding or "utf-8", "replace")
        return Response(rewrite_html(body, url), status=r.status_code, content_type="text/html; charset=utf-8")
    def stream():
        try:
            for b in r.iter_content(1024 * 1024):
                if b: yield b
        finally: r.close()
    h={"Content-Type":content_type}
    if r.headers.get("Content-Length"): h["Content-Length"]=r.headers["Content-Length"]
    return Response(stream(), status=r.status_code, headers=h, direct_passthrough=True)

@app.route("/health")
def health(): return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
