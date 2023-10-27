import sqlite3


connect = sqlite3.connect("db.db")
cursor = connect.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS  "users" (
	"id"	INTEGER,
	"login"	TEXT,
	"password"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
''')

cursor.execute('''
 CREATE TABLE IF NOT EXISTS "links_types" (
	"id"	INTEGER,
	"type"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
''')
cursor.execute('''
 CREATE TABLE IF NOT EXISTS "links" (
	"id"	INTEGER,
	"link"	TEXT,
	"hreflink"	TEXT,
	"user_id"	INTEGER,
	"link_type_id"	INTEGER,
	"count"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
    FOREIGN KEY (user_id)  REFERENCES users (id),
    FOREIGN KEY (link_type_id)  REFERENCES links_types (id)
);
''')
connect.commit()


# cursor.execute('''DELETE FROM links_types''')
# connect.commit()
# cursor.execute('''DELETE FROM links ''')
# connect.commit()
#
# cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'count', 'link_type_id') VALUES('https://www.youtube.com/watch?v=b_oRXHDTHNo','aaaaaa',2,0,1)''')
# connect.commit()


types = [(1,'pub'), (2,'obsh'), (3,'priv')]

have_type = cursor.execute('''SELECT * FROM links_types''').fetchall()


if (have_type==[]):
        for i in types:
            cursor.execute('''INSERT INTO links_types('type') VALUES(?)''', (i[1],))
            connect.commit()

# cursor.execute('''INSERT INTO links_types('type') VALUES('pub')''')
# connect.commit()
# cursor.execute('''INSERT INTO links_types('type') VALUES('obsh')''')
# connect.commit()
# cursor.execute('''INSERT INTO links_types('type') VALUES('obsh')''')
# connect.commit()
connect.close()