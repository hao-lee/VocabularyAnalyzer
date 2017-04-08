# -*- coding: utf-8 -*-
#!/usr/bin/python
import nltk.data
import re

# NLP 断句
def sentence_tokenizer(text):
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	sentence_list = tokenizer.tokenize(text)
	return sentence_list

# NLP 分词
def word_tokenizer(sentence):
	#转为小写（不转似乎也没影响）
	sentence = sentence.lower()
	word_list = nltk.word_tokenize(sentence)	#分词
	return word_list	#单词<---->词性，一一对应

# 正则分词
def regex_tokenizer(sourcestring):
	sourcestring = str.lower(sourcestring)
	pattern = re.compile(r'\w+')
	word_list = pattern.findall(sourcestring)	
	return word_list

if __name__ == '__main__':
	fd = open(r'text.txt', mode='rt', encoding='utf-8')
	text = fd.read()
	sentence_list = sentence_tokenizer(text)
	for sentence in sentence_list:
		word_list = word_tokenizer(sentence)
		pass