import psycopg2 

connection = psycopg2.connect('dbname = example')
cursor = connection.cursor()

cursor.execute('DROP TABLE IF EXISTS table3;')
cursor.execute('''
CREATE TABLE table3(
    id INTEGER PRIMARY KEY,
    completed BOOLEAN NOT NULL DEFAULT false
);
''')


sql = 'INSERT INTO table3 (id, completed) VALUES (%(id)s, %(completed)s);'
cursor.execute(sql, {'id':1, 'completed':True})
cursor.execute(sql, {'id':2, 'completed':True})
cursor.execute(sql, {'id':3, 'completed':False})

cursor.execute('SELECT * FROM table3')
result = cursor.fetchall()
print('fetchall', result)

connection.commit()

cursor.close()
connection.close()