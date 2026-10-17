# ZWEB Flask GitHub 个人代理

让 PythonAnywhere 作为个人 GitHub 访问代理。代理只允许 GitHub 相关域名，并且必须设置 `WEB_PASSWORD`，避免成为公开开放代理。

## PythonAnywhere WSGI

```python
import sys, os
sys.path.insert(0, '/home/ZSJ0000/SERVER_ZSJ/flask-proxy')
os.environ['WEB_PASSWORD'] = '设置一个复杂密码'
from app import app as application
```

打开网站后，在输入框填写：

```text
https://github.com/ZSJ0000/ZWEB_Files
```

也可以直接访问：

```text
https://你的域名.pythonanywhere.com/github?url=https%3A%2F%2Fgithub.com%2FZSJ0000%2FZWEB_Files&key=你的密码
```

## 限制

只允许 `github.com`、`raw.githubusercontent.com`、`api.github.com`、`codeload.github.com` 和 GitHub 静态资源域名。不会代理任意网站，也不保存下载文件。

不要把 `WEB_PASSWORD` 或 GitHub Token 提交到仓库。
