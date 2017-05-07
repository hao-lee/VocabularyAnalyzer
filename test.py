import nlp, time, cambridge_crawler, json

# 计时器
def timer(func):
	def wrapper(*args, **kw):
		start_time = time.time()  # 计时起点
		result = func(*args, **kw)
		end_time = time.time()  # 计时终点
		print("[Elapsed Time: %ds]" %(end_time - start_time))
		return result
	return wrapper

# 测试爬虫
@timer
def test_crawler():
	with open("source_text.txt", 'r', encoding='utf-8') as fd:
		text = fd.read()
	matrix = []
	result = ""
	count = 0
	for sentence in nlp.nltk_sentence_tokenizer(text):
		matrix.append(nlp.nltk_word_tokenizer(sentence))
	for row in matrix:
		for word in row:
			pos_pron = cambridge_crawler.crawler(word.lower(), need_pos=True)
			result += word + " : " + json.dumps(pos_pron) + "\n"
			count += 1
	with open("result.txt", 'a', encoding='utf-8') as fd:
		fd.write(result)
	print("处理 %d 个单词" %count)	


if __name__ == '__main__':
	test_crawler()