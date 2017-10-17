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
	if pos_header is None: # 极其特殊的单词
		print("pos_header is None, dump entry_body_el:\n%s\n" %entry_body_el.prettify())
		return "NO-POS"
	pos_tag = pos_header.find(name="span", attrs={"class":"pos"})
	if pos_tag is None:  # 有些单词没有词性，例如 taken
		print("pos_tag is None, dump entry_body_el:\n%s\n" %entry_body_el.prettify())
		return "NO-POS"
	return pos_tag.string

def get_pron(entry_body_el):
	'''
	entry_body_el 包含某单词一个词性的全部内容，<span class="pron"> 标签内就是音标，
	但直接搜索该标签可能会混入动词过去式/过去分词(Irregular inflection)的音标，例如(have词条)，
	所以，需要首先找出 <span pron-region="US" class="pron-info"> 标签，然后再在其内部
	找出 <span class="pron"> 标签。
	另外，不必担心某个词性的多音问题，因为多个音在网页上被合成到同一个/xxx,xxx/内当作一个音标整体，不会落下。
	'''
	pron_info = entry_body_el.find(name="span", attrs={"pron-region":"US","class":"pron-info"})
	if pron_info is None:  # 单词 democratic 的 pron-info 标签没有 pron-region 属性
		pron_info = entry_body_el.find(name="span", attrs={"class":"pron-info"})
	if pron_info is None:  # 如果还是空，那就是根本没音标了，例如字母 s 的第二个词性
		return "NO-PRON"
	pron_tag = pron_info.find(name="span", attrs={"class":"pron"})
	if pron_tag is None:
		return "NO-PRON"
	return pron_tag.get_text()

'''
@return 返回一个list，存储了word这个单词不同词性的音标
["pos1:pron1", "pos2:pron2", "pos3:pron3",]
'''
def crawler(word):
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"}
	base_url = "http://dictionary.cambridge.org/us/search/english/direct/?q="
	r=requests.get(base_url + word, headers=headers)
	#print(r.status_code)
	#print(r.history)
	if r.status_code == 404:
		print("单词查不到，状态码 %d" %r.status_code)
		return [":"]
	if r.url.startswith("http://dictionary.cambridge.org/us/spellcheck/english/"):
		print("单词查不到，已跳转拼写检查，状态码 %d" %r.status_code)
		return [":"]
	soup = BeautifulSoup(r.text, "lxml")

	'''
	直接获取 British 子页面的内容:
	1. 某些单词(spotted)不存在 American 子页面，而 British 子页面几乎一定存在
	2. American 子页面的音标 ɝ/ɚ 标成了 ɜr/ər，不易于理解，而 British 子页面没这个问题
	'''
	tabs_content = soup.find(name="div",attrs={"data-tab":"ds-american-english"})
	if tabs_content is None:  # 如果没有那就算查不着
		return [":"]

	'''
	搜索出所有<div class="entry-body__el clrd js-share-holder">
	record 有3个entry-body__el，每个都包含了以一种词性的音标和释义
	'''
	entry_body_el_list = tabs_content.find_all(name="div",
					attrs={"class":"entry-body__el"})

	# 对每个entry_body_el做提取处理，每个entry_body_el都代表一种词性
	pos_pron = []
	for entry_body_el in entry_body_el_list:
		pos = get_pos(entry_body_el)
		pron = get_pron(entry_body_el)
		pos_pron.append(pos + ":" + pron)

	# 注意这是一个list，因为一个词可能有多个词性
	# 形如：["pos1:pron1", "pos2:pron1", "pos3:pron2"]
	return pos_pron

if __name__ == '__main__':
	'''
	测试单词: possibilities impossible record
	recall present readabilities have I a is am
	'''
	crawler('have')