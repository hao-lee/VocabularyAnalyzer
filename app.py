# -*- coding: utf-8 -*-
# 关于 gevent + Flask 的例子: https://github.com/pallets/flask/issues/1073
from gevent import monkey
monkey.patch_all()

from gevent import wsgi
from flask import Flask, render_template
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

# 为了能获取到 server 对象以便关闭 app，在这里将 server 定义为全局
server = None

# 关闭 FLask 应用 http://flask.pocoo.org/snippets/67/
@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown_app():
	from flask import request
	response = ""
	shutdown = request.environ.get('werkzeug.server.shutdown')
	if shutdown is not None:
		response += "Running with the Werkzeug Server"
		shutdown()
	else:
		response += "Running with the gevent server"
		server.stop()
	response += "<br>" + 'Server shutting down...'
	print(response.replace("<br>", "\n"))
	return response

# 处理由异常导致的服务器内部错误
@app.errorhandler(500)
def internal_server_error(e):
	print("Internal Server Error:\n%s\n" %e)
	return render_template('error.html'), 500

if __name__ == '__main__':
	#app.run()  # 单纯的 Flask app
	# 使用 gevent 异步处理请求
	server = wsgi.WSGIServer(('127.0.0.1', 5000), app)
	server.serve_forever()