# -*- coding: utf-8 -*-

from flask import request, render_template, Blueprint
import json
import sqlite3
import nlp
import cambridge_crawler

# Phonetic Transcription Interpreter

# 创建 Blueprint
bp_pti = Blueprint("Phonetic Transcription Interpreter", __name__)

# 提交文本的页面
@bp_pti.route('/phonetic_transcription_interpreter', methods=['GET'])
def submit():
	return render_template('pti_submit.html')

# 处理数据并返回结果页面
@bp_pti.route('/phonetic_transcription_interpreter', methods=['POST'])
def processing():
	text = request.form["text"]
	# 断句分词
	matrix = []  # 每行都是句子被分词之后的
	for sentence in nlp.nltk_sentence_tokenizer(text):
		matrix.append(nlp.regex_word_tokenizer(sentence))
	'''
	生成字典，其对应的json字符串如下：
	refer_dict_str = '{
		"word1":{"pos_pron":["pos1:pron1", "pos2:pron2,pron3"], "index":0},
		"word2":{"pos_pron":["pos1:pron1", "pos2:pron2,pron3"], "index":0},
		"word3":{"pos_pron":["pos1:pron1", "pos2:pron2,pron3"], "index":0}
	}'
	'''
	refer_dict = {}
	for row in matrix: # 一行
		for word in row: # 行中某个词
			# need_pos=False 为了简洁起见，不返回与音标对应的词性
			pos_pron = cambridge_crawler.crawler(word, need_pos=False)
			# pos_pron 是一个list，存储了该单词每个词性的音标
			refer_dict[word] = {"pos_pron":pos_pron, "index":0}
	
	# 字典转json字符串
	refer_dict_str = json.dumps(refer_dict)

	# 组装 HTML 片段
	content_block = ""
	for row in matrix: # 一行
		# 行首加一格空的div，以便换行
		content_block += "<div class=\"no-data\"></div>"		
		for word in row: # 行中某个词
			pos_pron = refer_dict[word]["pos_pron"]
			content_block += \
				"<div class=\"group\">\n" +\
				"\t<p class=\"word\">" + word + "</p>" +\
				"\t<p class=\"pronunciation\">" + pos_pron[0] + "</p>" +\
				"</div>\n"
		# 一行拼接完成
	# 循环完成后，HTML 片段生成完毕

	# print(refer_dict_str)
	return render_template('pti_result.html',
	                       refer_dict_str=refer_dict_str,
	                       content_block=content_block)
