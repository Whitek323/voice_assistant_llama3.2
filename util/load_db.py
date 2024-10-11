import sqlite3
import pandas as pd

# Path to your .sqlite3 file
db_path = '../db/chroma.sqlite3'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Create a cursor object
cursor = conn.cursor()

# Query to get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Create a Pandas Excel writer object
with pd.ExcelWriter('/mnt/c/Users/white/Desktop/sql/output_database1.xlsx', engine='openpyxl') as writer:
    # Loop through each table and export it to a separate sheet
    for table in tables:
        table_name = table[0]
        # Query to get all data from the table
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql_query(query, conn)
        # Write the DataFrame to Excel, using the table name as the sheet name
        df.to_excel(writer, sheet_name=table_name, index=False)

# Close the connection to the database
conn.close()

print("Export completed. Data saved to output_database.xlsx")
