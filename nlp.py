# -*- coding: utf-8 -*-
import re
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

# 将 treebank 的词性标记转换为 worknet 词性标记
def convert_to_wordnet_tag(treebank_tag):
	if treebank_tag.startswith('J'):
		return wordnet.ADJ
	elif treebank_tag.startswith('V'):
		return wordnet.VERB
	elif treebank_tag.startswith('N'):
		return wordnet.NOUN
	elif treebank_tag.startswith('R'):
		return wordnet.ADV
	else:
		return wordnet.NOUN	#默认当作名词处理

# NLP 断句
def sentence_tokenizer(text):
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	sentence_list = tokenizer.tokenize(text)
	return sentence_list

# NLP 分词
def nltk_tokenizer(content):
	wordlist = nltk.word_tokenize(content)	#分词
	return wordlist	

# NLP 词形还原
def nltk_lemmatizer(wordlist):
	'''
	打标签	
	'''
	treebank_tagged = nltk.pos_tag(wordlist)  # 打标签
	wordnet_tagged = [] 
	# 将treebank类型的tag(如NN、NNP等),转为wordnet类型的tag(如wordnet.NOUN等)
	for word, tag in treebank_tagged:  # 遍历 tuple 组成的 list
		tag = convert_to_wordnet_tag(tag)
		wordnet_tagged.append((word, tag))
	'''
	开始进行词形还原
	'''
	wordnet_lemmatizer = WordNetLemmatizer()
	lemmalist = []	# 词干列表
	for word, tag in wordnet_tagged:  # 遍历 tuple 组成的 list
		lemma = wordnet_lemmatizer.lemmatize(word, tag)
		lemmalist.append(lemma)
	return list(set(lemmalist))  # 去重后返回
	
	
# 正则分词
def regex_tokenizer(sourcestring):
	pattern = re.compile(r'\w+')
	wordlist = pattern.findall(sourcestring)	
	return wordlist

if __name__ == '__main__':
	text = '''
	I'm a student.
	And you are a worker.
	What about him?
	'''
	sentence_list = sentence_tokenizer(text)
	for sentence in sentence_list:
		wordlist = nltk_tokenizer(sentence)
		lemmalist = nltk_lemmatizer(wordlist)
		pass