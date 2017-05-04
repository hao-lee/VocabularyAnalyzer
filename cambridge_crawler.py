# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

'''
通常情况下，词性和音标都在pos-header里
特殊情况如have，verb词性的音标在pos-body里
为了简化处理逻辑，提取某个词性的音标时直接搜出其下的所有音标再去重
@entry_body_el: 代表单词一个词性的全部内容
'''

def get_pos(entry_body_el):
	pos_header = entry_body_el.find(name="div", attrs={"class":"pos-header"})
	pos_tag = pos_header.find(name="span", attrs={"class":"pos"})
	if pos_tag is None:  # 有些单词没有词性，例如 taken
		return "NO-POS"
	return pos_tag.string

def get_pron(entry_body_el):
	'''
	找出所有的 <span pron-region="US" class="pron-info">，
	再从里面搜索出<span class="pron">
	不直接搜索pron标签是因为这可能会混入动词过去式/过去分词(Irregular inflection)的音标，
	例如have词条
	'''
	pron_info_list = entry_body_el.find_all(name="span", attrs={"pron-region":"US","class":"pron-info"})
	'''
	每个 pron-info 标签里面只有一个 pron 标签，所以用find即可
	(当然，pron_info_list可能本身就是个空list，比如字母s的第2、3个词性，此时本函数最终返回空字符串)
	'''
	pron_set = set([])  # 收集音标，同时去重
	for pron_info in pron_info_list:
		pron_tag = pron_info.find(name="span", attrs={"class":"pron"})
		pron_set.add(pron_tag.get_text())
	return ','.join(pron_set)  # 转为字符串，可能包含多种发音，也可能是个空串

'''
@return 返回一个list，存储了word这个单词不同词性的音标
["pos1:pron1", "pos2:pron2", "pos3:pron3",]
@need_pos 是否需要返回与音标对应的词性，默认返回
'''
def crawler(word, need_pos=True):
	print("Current Word: %s" %word)
	base_url = "http://dictionary.cambridge.org/us/search/english/direct/?q="
	r=requests.get(base_url + word)
	#print(r.status_code)
	#print(r.history)
	if r.status_code == 404:
		print("单词查不到，状态码 %d" %r.status_code)
		return ["None"+":"+"None"]
	if r.url.startswith("http://dictionary.cambridge.org/us/spellcheck/english/"):
		print("单词查不到，已跳转拼写检查，状态码 %d" %r.status_code)
		return ["None"+":"+"None"]
	soup = BeautifulSoup(r.text, "lxml")
	# 获取American子页面的内容
	tabs_content = soup.find(name="div",attrs={"data-tab":"ds-american-english"})
	if tabs_content is None:
		# 个别单词的American页面不存在，例如spotted，此时就用British页面
		tabs_content = soup.find(name="div",attrs={"data-tab":"ds-british"})
		if tabs_content is None:
			# 这也没有那就算查不着
			return ["None"+":"+"None"]
	'''
	搜索出所有<div class="entry-body__el clrd js-share-holder">
	record 有3个entry-body__el，每个都包含了以一种词性的音标和释义
	'''
	entry_body_el_list = tabs_content.find_all(name="div",
	                                  attrs={"class":"entry-body__el"})
	
	# 对每个entry_body_el做提取处理，每个entry_body_el都代表一种词性
	pos_pron = []  # 不做去重处理（一般不会出现重复）
	for entry_body_el in entry_body_el_list:
		pos = get_pos(entry_body_el)
		pron = get_pron(entry_body_el)
		if need_pos:
			pos_pron.append(pos + ":" + pron)
		else:
			pos_pron.append(pron)
	
	# 注意这是一个list，因为一个词可能有多个词性
	return pos_pron

if __name__ == '__main__':
	'''
	测试单词: possibilities impossible record 
	recall present readabilities have I a is am
	'''
	crawler('have')