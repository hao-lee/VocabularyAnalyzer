# -*- coding: utf-8 -*-

import re
import os
import sqlite3
import nlp
import crawler
import database

# Phonetic Transcription Interpreter	

def interpreter(source_text):
	word_css_class = "word"
	phonetic_css_class = "phonetic"
	with open(source_text, 'r', encoding='utf-8') as fd:
		text = fd.read()
	# 断句分词
	matrix = []  # 每行都是句子被分词之后的
	for sentence in nlp.sentence_tokenizer(text):
		matrix.append(nlp.regex_tokenizer(sentence))
	# 放爬虫先把文章中的每个词汇都爬取一遍
	count = 1
	for row in matrix:
		for word in row:
			crawler.crawler(word.lower())
			print("%d %s" %(count, word))
			count += 1
	# 然后开始从数据库内查询音标
	refer_dict = {}
	for row in matrix: # 一行
		for word in row: # 行中某个词
			records = database.query(word.lower())
			# 每条记录都是word这个词不同词性的发音
			'''
			records是一组记录(list)，每条记录(tuple)都是word这个词不同词性的发音
			例如：records[0] = (word, pos1, /phon1/)
			records[1] = (word, pos2, /phon1/,/phon2/,/phon3/)
			records[2] = (word, pos3, /phon2/,/phon3/)
			'''
			value = ""
			for record in records: # (word, pos1, /phon1/,/phon2/)
				value += record[1]+'. '+record[2]+'; '
			# 该单词的所有词性的条目已经拼接成一条了
			refer_dict[word] = value # 存入参考字典
			'''
			refer_dict字典格式如下:
			'word' : "verb. /phon1/,/phon2/; noun. /phon3/; adv. /phon2/"
			'''
	# 组装HTML
	html_block = ""
	for row in matrix: # 一行
		# 行首加一格空的div，以便换行
		html_block += "<div class=\"split-line\"></div>"		
		for word in row: # 行中某个词
			phonetic = refer_dict[word]
			html_block += \
				"<div>\n" +\
				"\t<p class=\"" + word_css_class + "\">" + word + "</p>" +\
				"\t<p class=\"" + phonetic_css_class + "\">" + phonetic + "</p>" +\
				"</div>\n"
		# 一行拼接完成
	# 循环完成后，HTML块生成完毕
	# 开始拼接网页
	with open('part-1.html', mode='r', encoding='utf-8') as fd:
		html_part1 = fd.read()
	with open('part-2.html', mode='r', encoding='utf-8') as fd:
		html_part2 = fd.read()
	html = html_part1 + html_block + html_part2
	with open(r'E:\桌面迁移\result.html', mode='w', encoding='utf-8') as fd:
		fd.write(html)

if __name__ == '__main__':
	if not os.path.exists("phonetic.db"):
		database.create_db()
	interpreter('source_text.txt')
	
'''
TODO:
takes/astronomers等词汇，抓取并存储的是原型，所以数据库内是原型，用变型去查是查不到的
需要词形还原之后再去查
'''