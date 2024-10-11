import sqlite3

# Path to your .sqlite3 file
db_path = '../db/chroma.sqlite3'

# Connect to the database
conn = sqlite3.connect(db_path)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Example query to get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in the database:")
for table in tables:
    print(table[0])

# Example: reading data from a table (replace 'your_table' with actual table name)
cursor.execute("SELECT * FROM embedding_metadata;")
rows = cursor.fetchall()

print("Data in your_table:")
for row in rows:
    print(row)

# Close the connection
conn.close()
