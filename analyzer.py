# -*- coding: utf-8 -*-

import sys
sys.path.append("utils")
from flask import request, render_template, Blueprint
import nlp
import requests, json
import collections, time
from collections import OrderedDict

'''
数据预读取
'''
# 读取词频表，注意要用list，保证次序（排名）
coca_word_list = []
with open("data/coca-20000.txt", 'r', encoding='utf-8') as fd:
	for line in fd.readlines():
		coca_word_list.append(line.strip('\n'))

# 读取难词表
difficult_word_list = []
with open("data/total.txt", 'r', encoding='utf-8') as fd:
	for line in fd.readlines():
		difficult_word_list.append(line.strip('\n'))

# 转换为 set 查找效率更高		
difficult_word_set = set(difficult_word_list)


'''
Vocabulary Analyzer
'''
# 创建 Blueprint
bp_va = Blueprint("Vocabulary Analyzer", __name__)

# 提交文本的页面
@bp_va.route('/vocabulary_analyzer', methods=['GET'])
def submit():
	return render_template('va_submit.html')

# 处理数据并返回结果页面
@bp_va.route('/vocabulary_analyzer', methods=['POST'])
def processing():
	# 获取用户 IP 地址
	user_ip = request.remote_addr
	try:
		real_ip = request.headers["X-Real-IP"]
		if real_ip is not None:
			user_ip = real_ip
	except Exception as e:
		pass
	# 获取用户输入的文本
	text = request.form["text"]
	# 保存日志
	save_log(user_ip, text)
	
	start_time = time.time()  # 计时起点
	wordlist = nlp.nltk_word_tokenizer(text)
	lemmalist = nlp.nltk_word_lemmatizer(wordlist)
	result = collections.OrderedDict()
	for word in lemmalist:  # 对每一个待查词汇
		if word in difficult_word_set:  # 如果它在高阶词典里
			try:
				ranking = coca_word_list.index(word)  # 查找coca排名
			except ValueError:  # coca不包含此单词
				ranking = -1
			result[word] = ranking+1  # 下标加1为排名    
	# 按照 value 排序
	result = OrderedDict(sorted(result.items(), key=lambda t: t[1]))
	# 组装 HTML Block
	content_block = ""
	for word, ranking in result.items():
		content_block += ("<tr><td>%s</td><td>%s</td></tr>" %(word, ranking))
	content_block = "<table border=\"1\">" + content_block + "</table>"

	end_time = time.time()  # 计时终点
	text_wc = len(text.split(" "))
	result_wc = len(result)
	elapsed_time = end_time-start_time
	content_block = ("<h5>输入词汇数: %d</h5>" %text_wc) \
	        + ("<h5>高阶词汇数: %d</h5>" %result_wc) \
		+ ("<h5>执行时间: %f</h5>" %elapsed_time) \
	        + content_block
	return render_template('va_result.html',
	                       content_block=content_block)
	
# 记录用户数据
def save_log(user_ip, text):
	url = ("http://freegeoip.net/json/%s" %user_ip)
	r = requests.get(url)
	ip_info = json.loads(r.text)
	country = ip_info['country_name']
	region = ip_info['region_name']
	city = ip_info['city']
	# 保存文件
	with open("va.log", 'a', encoding='utf-8') as fd:
		log = ("User IP: %s, Country: %s, Region: %s, City: %s\n\n"
			%(user_ip, country, region, city))
		log += text + "\n\n"
		fd.write(log)