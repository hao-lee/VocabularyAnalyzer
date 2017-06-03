# -*- coding: utf-8 -*-
# 关于 gevent + Flask 的例子: https://github.com/pallets/flask/issues/1073
from gevent import monkey
monkey.patch_all()

from gevent import wsgi
from flask import Flask
import sys
sys.path.append("utils")
import interpreter
import analyzer

# 创建 Application
app = Flask(__name__)
app.static_folder = 'static'

# 注册 Blueprint
app.register_blueprint(interpreter.bp_pti)
app.register_blueprint(analyzer.bp_va)

if __name__ == '__main__':
	#app.run()  # 单纯的 Flask app
	# 使用 gevent 异步处理请求
	server = wsgi.WSGIServer(('127.0.0.1', 5000), app)
	server.serve_forever()