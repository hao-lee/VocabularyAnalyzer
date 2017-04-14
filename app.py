# -*- coding: utf-8 -*-

from flask import Flask
import interpreter

# 创建 Application
app = Flask(__name__)
app.static_folder = 'static'

# 注册 Blueprint
app.register_blueprint(interpreter.bp_pti)

if __name__ == '__main__':
	app.run()