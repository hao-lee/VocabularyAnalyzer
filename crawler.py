# -*- coding: utf-8 -*-
import re
import database
import requests
from bs4 import BeautifulSoup

# 从一段文本中正则表达式暴力提取音标，音标的格式是固定的 NAmE//xxxxx//
def search_phonetic(text):
	pattern = re.compile("\/(\/.*?\/)\/")
	phonetic = set(re.findall(pattern, text))
	# 返回一个集合
	return phonetic

# 传入一个页面的内容，提取出里面的所有可提取的单词、词性、音标
def extracter(pagecontent):
	'''
	1. 对于主词条来说，单词一定存在，且位置在top_container里，
	词性可能不存在(is)，音标可能不存在(IN)，也可能有多个(the)，而且音标位置不确定(impossible recall_2)。
	单词和词性一定在top-container里，音标可能在top-container或sn-gs
	2. 对于附属词条来说，单词一定存在，但是词性可能不存在，且位置不确定
	音标可能不存在且位置也不确定
	单词在top-container里，词性和音标可能在top-container(如mean_2)或sn-gs里
	'''
	results_in_one_page = [] # 最终结果数组，包含本页面所有能提取的单词及其对应的词性和音标
	soup = BeautifulSoup(pagecontent, "lxml")
	# 清理一些干扰内容
	# webtop-g 下一般会存在pos标签，这是个多余的词性标识，会造成get_text之后出现连续的两个词性标识
	pos_tag = soup.find("div", class_="webtop-g").find("span",class_="pos")
	if pos_tag is not None: # 如果有这个标签，则干掉他。（大部分都有，但is没有）
		pos_tag.extract()
	# can等单词有个上角标，以防万一，这里清理一下
	hm_tag = soup.find("div", class_="webtop-g").find("span",class_="hm")
	if hm_tag is not None:
		hm_tag.extract()	
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
		# 有些词汇释义为空（如in的noun词性），为了防止get_text异常，这里新建空标签
		if sn_gs is None:
			sn_gs = soup.new_tag("span", class_="sn-gs")
		top_container_WITH_sn_gs.append((top_container, sn_gs))
	
	'''处理主词条'''
	entry_top_container_tag = top_container_WITH_sn_gs[0][0]
	entry_sn_gs_tag = top_container_WITH_sn_gs[0][1]
	# 从页面上提取单词(打印看看就知道为何要这样提取了)
	# stripped_strings会把tag之间的字符串当作整体，即使中间有空格分隔
	word = next(entry_top_container_tag.stripped_strings)
	# 搜索词性标签
	pos_tag = entry_top_container_tag.find("span", class_="pos")
	if pos_tag is not None:
		pos = pos_tag.string
	else:
		pos = ""
	# 搜索音标，直接获取标签的纯文本内容，然后正则表达式搜出所有音标，去重
	phonetic = search_phonetic(entry_top_container_tag.get_text()\
	                           + entry_sn_gs_tag.get_text())
	# 将主词条的提取结果保存
	results_in_one_page.append((word, pos, phonetic))
	
	'''处理页面下方的附属词条'''
	#（如impossible页面下方的impossibility及其音标）
	for i in range(1, len(top_container_WITH_sn_gs)):
		extra_top_container_tag = top_container_WITH_sn_gs[i][0]
		# 提取单词(打印看看就知道为何要这样提取了)
		word = next(extra_top_container_tag.stripped_strings)
		# 搜索词性pos标签，范围是top_container和sn_gs
		extra_sn_gs_tag = top_container_WITH_sn_gs[i][1]
		pos1 = extra_sn_gs_tag.find("span", class_="pos")
		pos2 = extra_top_container_tag.find("span", class_="pos")
		if pos1 is not None: # 看起来词性在sn-gs标签里，这是大部分情况
			pos = pos1.string
		elif pos2 is not None: # 看起来词性在top_container标签里，如mean_2页面的meanly
			pos = pos2.string
		else:
			pos = "" # 看起来都搜不到，那就是没标注词性，这个目前还没见过
		# 搜索音标
		phonetic = search_phonetic(extra_top_container_tag.get_text()\
		                           + extra_sn_gs_tag.get_text())
		# 将附属词条的提取结果保存
		results_in_one_page.append((word, pos, phonetic))
	
	return results_in_one_page

def crawler(word):
	'''
	术语：
	待查单词-当前查询的单词
	异性单词-与当前单词拼写相同但词性不同的单词
	'''
	pagecontent_list = [] # 存储了该单词所有词性的页面内容
	base_url = "http://www.oxfordlearnersdictionaries.com/us/search/american_english/?q="
	try:
		r=requests.get(base_url + word)
	except requests.exceptions.RequestException as e:
		print("ERROR:",e)
		return
	#print(r.status_code)
	#print(r.history)
	'''
	判断待查单词是否能查到,对于拼写错误的词汇跳转到
	http://www.oxfordlearnersdictionaries.com/us/spellcheck/american_english/?q=xxx
	'''
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
		# 拿到Other results列表
		li_list = relatedentries.find_all("li")
		# 遍历Other results中的每一个单词，如果与待查单词相同则将其URL加入集合
		for li in li_list:
			'''
			stripped_strings返回标签下所有字符串的迭代器，第一个元素就是所需提取的单词
			（词后可能有空格，所以用stripped_strings函数而非strings）
			want的相关词组有want for，stripped_strings会将之作为一个整体处理，
			所以不必担心词组中间的空格造成误判，它们的url是不会被加入other_url_set的。
			'''
			#for i in li.a.stripped_strings:
				#print(i)
			releated_word = next(li.a.stripped_strings)
			# 若与待查单词相同则找到一个异性单词
			if releated_word == word:
				other_url_set.add(li.a.get("href"))
	# 爬取异性单词的页面	
	for url in other_url_set:
		try:
			r=requests.get(url)
		except requests.exceptions.RequestException as e:
			print("ERROR:",e)
			continue
		pagecontent_list.append(r.text) # 添加当前页面内容
	
	# 开始提取这些页面里的单词、词性、音标
	for pagecontent in pagecontent_list:
		results_in_one_page = extracter(pagecontent)
		#print("\n--分页面---\n")
		#print(results_in_one_page)
		for result in results_in_one_page:
			# 存入数据库，若音标set为空，则join后是空串，不会有问题
			database.save_to_db(result[0],result[1],','.join(result[2]))

if __name__ == '__main__':
	# 测试单词：possibilities impossible record recall present readabilities
	crawler('5')
'''
TODO:
目前没处理的问题是 house 这个词的主词条里多了个复数形态，
其音标会在进行音标搜索时一并看作house的音标
'''