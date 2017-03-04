# -*- coding: utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup

# 从一段文本中正则表达式暴力提取音标，音标的格式是固定的 NAmE//xxxxx//
def search_phonetic(text):
	pattern = re.compile("\/(\/.*?\/)\/")
	phonetic = set(re.findall(pattern, text))
	return phonetic

# 传入一个页面的内容，提取出里面的所有可提取的单词、词性、音标
def extracter(pagecontent):
	result = [] # 最终结果数组，包含本页面所有能提取的单词及其对应的词性和音标
	soup = BeautifulSoup(pagecontent, "lxml")
	# 清理一些干扰内容，这是个多余的词性标识，会造成get_text后出现连续的两个词性标识
	soup.find("div", class_="webtop-g").find("span",class_="pos").extract()
	'''
	将<div class="top-container">标签和<span class="sn-gs">标签
	一对一对的提取出来，他俩是兄弟
	组成(top_container,sn_gs)这样的元组，再追加入list
	'''
	top_container_WITH_sn_gs = [] # 每个元素都是tuple
	for top_container in soup.find_all("div", class_="top-container"):
		# 个别单词有 Idioms 区块（如present），我们跳过去；注意，这里取class的值返回的是list
		if top_container.parent.get("class")[0] == "idm-g":
			continue
		# top_container 的兄弟结点就是 sn-gs
		sn_gs = top_container.find_next_sibling("span", class_="sn-gs")
		top_container_WITH_sn_gs.append((top_container, sn_gs))

	# 对于主词条来说，音标可能在单词下方（如impossible），也可能在每个义项开头（如recall_2）
	# 分情况匹配很繁琐，此处直接获取标签的纯文本内容，然后正则表达式搜出所有音标，去重
	entry_top_container_tag = top_container_WITH_sn_gs[0][0]
	entry_sn_gs_tag = top_container_WITH_sn_gs[0][1]
	# 获取单词和词性(打印get_text的结果看看就知道为何要这样提取了)
	tmp = entry_top_container_tag.get_text().split()
	word = tmp[0]
	pos = tmp[1]
	# 搜索音标（不确定音标在top_container的标签里，还是在sn_gs的标签里，直接正则暴力搜索）
	tmp = entry_top_container_tag.get_text() + entry_sn_gs_tag.get_text()
	phonetic = search_phonetic(tmp)
	
	# 将主词条的提取结果保存
	result.append((word, pos, str(phonetic)))
	
	# 对于页面下方可能存在的其他附属词条和音标
	#（如impossible页面下方的impossibility及其音标）
	# 单词在top_container的标签里，音标和词性在sn_gs里
	for i in range(1, len(top_container_WITH_sn_gs)):
		tmp = top_container_WITH_sn_gs[i][0].get_text() # top_container
		word = tmp.split()[0] #(打印tmp看看就知道为何要这样提取了)
		tmp = top_container_WITH_sn_gs[i][1].get_text() # sn_gs
		# 此处的音标应该只有一个，调用函数主要是为了去掉NAmE和两个多余的斜杠
		phonetic = search_phonetic(tmp)
		pos = tmp.split()[1]
		# 将附属词条的提取结果保存
		result.append((word, pos, phonetic))
	
	return result

def crawler(word):
	'''
	术语：
	待查单词-当前查询的单词
	异性单词-与当前单词拼写相同但词性不同的单词
	'''
	pagecontent_list = [] # 存储了该单词所有词性的页面内容
	base_url = "http://www.oxfordlearnersdictionaries.com/us/search/american_english/?q="
	r=requests.get(base_url + word)
	print(r.status_code)
	print(r.history)	
	# 判断待查单词是否能查到
	if r.url.find("us/spellcheck/") != -1:
		print("当前单词查不到！")
		exit() # 最终URL里有spellcheck子串，说明待查单词查不到
	pagecontent_list.append(r.text) # 添加当前页面内容
	# 下面读取Other results列表，以此获取异性单词的URL集合
	other_url_set = set()
	soup = BeautifulSoup(r.text, "lxml")
	relatedentries = soup.find("div", id="relatedentries")
	# Other results的列表存在，说明待查单词有其他词性
	if relatedentries is not None:
		# 删掉relatedentries标签范围内的所有pos标签，不然会干扰提取单词
		pos_list = relatedentries.find_all("pos")
		for pos in pos_list:
			pos.extract()
		# 拿到Other results列表
		li_list = relatedentries.find_all("li")
		# 遍历Other results中的每一个单词，如果与待查单词相同则将其URL加入集合
		for li in li_list:
			# 取出一个单词（strip去掉词尾空格）
			releated_word = li.a.span.string.strip()
			# 若与待查单词相同则找到一个异性单词
			if releated_word == word:
				other_url_set.add(li.a.get("href"))
	# 爬取异性单词的页面	
	for url in other_url_set:
		r=requests.get(url)
		pagecontent_list.append(r.text) # 添加当前页面内容
	
	# 开始提取这些页面里的单词、词性、音标
	for pagecontent in pagecontent_list:
		result = extracter(pagecontent)
		print("\n--分页面---\n")
		print(result)
	

if __name__ == '__main__':
	# 测试单词：possibilities impossible record recall present readabilities
	crawler("present")