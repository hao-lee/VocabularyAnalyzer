# -*- coding: utf-8 -*-

import sys
sys.path.append("utils")
import time
import nlp
import cambridge_crawler
import database

def populate_database(filename):
	with open(filename, "r") as fd:
		text = fd.read()
	start_time = time.time()
	with open("data/words.txt") as fd:
		ultra_word_list = fd.read().split()
	wordlist = nlp.nltk_word_tokenizer(text)
	wait_to_save = {}
	db = database.DatabaseManager()
	db.open()
	count = 0
	for word in wordlist:
		word_lower = word.lower()
		if word_lower not in ultra_word_list:
			continue
		pos_pron_str = db.query(word_lower)
		if pos_pron_str is not None:
			continue
		else:
			pos_pron = cambridge_crawler.crawler(word_lower)
			wait_to_save[word_lower] = ';'.join(pos_pron)
		count += 1
		if count == 100:
			db.save_to_db(wait_to_save)
			wait_to_save.clear()
			count = 0

	db.save_to_db(wait_to_save)
	db.close()

	text_wc = len(wordlist)
	end_time = time.time()
	elapsed_time = end_time-start_time
	print("Word Count: %d\nElapsed Time: %fs" %(text_wc, elapsed_time))

if __name__ == '__main__':
	if len(sys.argv) != 2:
		exit(-1)
	else:
		populate_database(sys.argv[1])