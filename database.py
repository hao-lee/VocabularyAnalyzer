import sqlite3

def save_to_db(word, pos, phonetic):
	con = sqlite3.connect('phonetic.db')
	cursor = con.cursor()
	cursor.execute('insert into phonetic_table (word, pos, phonetic) values(?,?,?)',(word, pos, phonetic))
	cursor.close()
	con.commit()
	con.close()
	
def query(word):
	sql = '''
	SELECT
	phonetic_table.word,
	phonetic_table.pos,
	phonetic_table.phonetic
	FROM
	phonetic_table
	WHERE
	phonetic_table.word = 
	'''
	con = sqlite3.connect('phonetic.db')
	cursor = con.cursor()
	sql = sql + "'"+ word +"'"
	cursor.execute(sql)
	records = cursor.fetchall()
	cursor.close()
	con.commit()
	con.close()
	return records

def create_db():
	sql = '''
	CREATE TABLE "phonetic_table" (
	"id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	"word"  TEXT,
	"pos"  TEXT,
	"phonetic"  TEXT,
	CONSTRAINT "unique" UNIQUE ("word" ASC, "pos" ASC) ON CONFLICT IGNORE
	);
	'''
	con = sqlite3.connect('phonetic.db')
	cursor = con.cursor()
	cursor.execute(sql)
	cursor.close()
	con.commit()
	con.close()	

# For Test
if __name__ == '__main__':
	#create_db()
	#print(query('I'))
	pass