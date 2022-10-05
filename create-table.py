import sqlite3
import os

# Connecting to sqlite
# connection object
connection_obj = sqlite3.connect('files.db')
 
# cursor object
cursor_obj = connection_obj.cursor()
 
# Drop the GEEK table if already exists.
cursor_obj.execute("DROP TABLE IF EXISTS FILENAMES")

# https://stackoverflow.com/questions/200309/sqlite-database-default-time-value-now

# Creating table
tablesql = """ CREATE TABLE FILENAMES (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            File_name VARCHAR(1024) NOT NULL,
            File_path VARCHAR(1024) NOT NULL,
            Created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ); """
 
cursor_obj.execute(tablesql)

insertsql = """ INSERT INTO FILENAMES (File_name, File_path)
            VALUES(?,?)  
            """

parent_path = r"/media/pidrive/nas-1tb/pyuploads/"

# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk(parent_path):
    path = root
    #print((len(path) - 1) * '---', os.path.basename(root))
    for file in files:
        print(path , '---', file)
        cursor_obj.execute(insertsql,(path,file))

# Close the connection
connection_obj.close()

