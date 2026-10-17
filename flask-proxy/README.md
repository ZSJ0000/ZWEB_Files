# ZWEB Files Flask 下载代理

服务器使用 GITHUB_TOKEN 访问私有 Release，浏览器不会看到 Token，文件采用流式转发，不保存完整下载文件。

安装：

```bash
python3 -m pip install --user -r requirements.txt
```

启动：

```bash
export GITHUB_TOKEN='新建的只读 Token'
export WEB_PASSWORD='你的网页密码'
python3 app.py
```

可选：`GITHUB_REPO`、`GITHUB_TAG`、`PORT`。

PythonAnywhere WSGI 示例：

```python
import sys,os
sys.path.insert(0,'/home/你的用户名/ZWEB_Files/flask-proxy')
os.environ['GITHUB_TOKEN']='新建的 Token'
os.environ['WEB_PASSWORD']='你的网页密码'
from app import app as application
```

不要把 Token 提交到 GitHub。之前泄露的 Token 必须撤销并重新创建。
