# -*- coding: utf-8 -*-

import urllib.parse
import urllib.request
import json
import re

# Phonetic Transcription Interpreter

def tokenizer(sourcestring):
	sourcestring = str.lower(sourcestring)
	pattern = re.compile(r'\w+')
	word_list = pattern.findall(sourcestring)	
	return word_list

def interpreter(word, word_css_class, phonetic_css_class):
	api_url = "http://fanyi.youdao.com/openapi.do"
	request = {
	        'keyfrom': 'PhoneticTI',
	        'key': '188592885',
	        'type': 'data',
	        'doctype': 'json',
	        'version': '1.1',
	        'q': word,
	        'only': 'dict'
	}
	#将字典转为URL编码
	request = urllib.parse.urlencode(request)
	#拼接URL
	query_url = api_url + '?' + request
	#发送请求，获取应答
	with urllib.request.urlopen(query_url) as response:
		result = response.read()
	#应答为bytes object格式，解码为字符串
	result = result.decode('utf-8')
	#字符串转为json格式
	json_data = json.loads(result)

	#开始提取
	errorCode = json_data.get('errorCode')
	if errorCode == 0: # OK
		basic = json_data.get('basic')
		if basic == None:
			us_phonetic = "----"
		else:
			us_phonetic = basic.get('us-phonetic')
			if us_phonetic == None: # 可能没有音标
				us_phonetic = "----"
		
	else:
		us_phonetic = "----"
	#生成如下的HTML结构
	#<div>
	#	<p class="word_css_class">bed</p>
	#	<p class="phonetic_css_class">bɛd</p>
	#</div>
	word_phonetic_html_pairs = \
	        "<div>\n" +\
	        "\t<p class=\"" + word_css_class + "\">" + word + "</p>" +\
	        "\t<p class=\"" + phonetic_css_class + "\">" + us_phonetic + "</p>" +\
	        "</div>\n"
	
	return word_phonetic_html_pairs

if __name__ == '__main__':
	fd = open(r'text.txt', mode='rt', encoding='utf-8')
	text = fd.readlines()
	html_block = ""
	#for word in text.split():
	for line in text:
		# 行首加一格空的div，以便换行
		html_block += "<div class=\"split-line\"></div>"
		for word in tokenizer(line):
			html_block += interpreter(word, 'word', 'phonetic')

	fd = open(r'part-1.html', mode='rt', encoding='utf-8')
	html_part1 = fd.read()
	fd.close()
	fd = open(r'part-2.html', mode='rt', encoding='utf-8')
	html_part2 = fd.read()
	fd.close()

	html = html_part1 + html_block + html_part2
	fd = open(r'E:\桌面迁移\result.html', mode='wt', encoding='utf-8')
	fd.write(html)
	fd.close()	
	