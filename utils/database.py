import sqlite3
import os

class DatabaseManager:
	def __init__(self):	
		self.con = None
		self.cursor = None

	def check_table_exist(self):
		self.cursor.execute('''
			SELECT name FROM sqlite_master
		        WHERE type='table' AND name='core_data';
		''')
		results = self.cursor.fetchall()
		# 如果表不存在则创建
		if len(results) == 0:
			self.cursor.execute('''
				CREATE TABLE "core_data" (
				"word"  TEXT,
				"pos_pron_str"  TEXT,
				PRIMARY KEY ("word")
				);
			''')

	def open(self):
		# Flask 运行时，本代码的执行路径是在源码根目录下
		# 自动commit：https://my.oschina.net/tinyhare/blog/719039
		self.con = sqlite3.connect("data/pti.db", isolation_level=None)
		self.cursor = self.con.cursor()
		self.check_table_exist()

	def close(self):
		self.con.close()
		self.con = self.cursor = None

	def save_to_db(self, wait_to_save):
		self.cursor.execute("BEGIN TRANSACTION")
		for word, pos_pron_str in wait_to_save.items():
			self.cursor.execute('''INSERT OR IGNORE INTO 
						core_data 
						(word, pos_pron_str) 
						VALUES(?,?)''',
			                	(word, pos_pron_str))
		self.cursor.execute("END TRANSACTION")
		
	def query(self, word):
		self.cursor.execute('''
				SELECT
				core_data.pos_pron_str
				FROM
				core_data
				WHERE
				core_data.word = ?
				''', (word,))
		'''
		结果集是一个list，每个元素都是一个tuple，对应一行记录。
		形如：[(col1, col2, col3),(col1, col2, col3),(col1, col2, col3),...]
		word是主键，所以records必然只能查到一行，且SQL中只Select了一个字段
		'''
		records = self.cursor.fetchall()
		if len(records) == 0:
			return None
		else:
			return records[0][0]


if __name__ == '__main__':
	# 测试时需要手动改变代码执行目录，不然 data/pti.db 路径就找不到了
	os.chdir("../")
	db = DatabaseManager()
	db.open()
	'''
	添加其他测试语句	
	'''
	db.close()