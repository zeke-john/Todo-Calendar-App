# import mysql.connector

# mydb = mysql.connector.connect(
# 	host="localhost",
# 	user="root",
# 	passwd = "CAez0208",
# 	)

# my_cursor = mydb.cursor()

# #CREATE ALL TABLES:

# # CREATE TABLE users (
# #     id INT AUTO_INCREMENT PRIMARY KEY,
# #     name VARCHAR(200) NOT NULL,
# #     email VARCHAR(200) UNIQUE NOT NULL,
# #     date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
# #     password_hash VARCHAR(128),
# #     password_hash2 VARCHAR(128)
# # );

# # CREATE TABLE todo (
# #     id INT AUTO_INCREMENT PRIMARY KEY,
# #     name VARCHAR(50) NOT NULL,
# #     complete BOOLEAN,
# #     description VARCHAR(150),
# #     start VARCHAR(150),
# #     date VARCHAR(150) NOT NULL,
# #     day VARCHAR(150) NOT NULL,
# #     month VARCHAR(150) NOT NULL,
# #     year VARCHAR(150) NOT NULL,
# #     labels VARCHAR(200),
# #     poster_id INT,
# #     FOREIGN KEY (poster_id) REFERENCES users(id)
# # );

# # CREATE TABLE labels (
# #     id INT AUTO_INCREMENT PRIMARY KEY,
# #     name TEXT NOT NULL,
# #     poster_labels_id INT,
# #     FOREIGN KEY (poster_labels_id) REFERENCES users(id)
# # );

# # CREATE TABLE notes (
# #     id INT AUTO_INCREMENT PRIMARY KEY,
# #     name TEXT,
# #     description TEXT,
# #     poster_notes_id INT,
# #     FOREIGN KEY (poster_notes_id) REFERENCES users(id)
# # );


# # my_cursor.execute("CREATE DATABASE todoapp")

# my_cursor.execute("SHOW DATABASES")
# for db in my_cursor:
# 	print(db)


# import psycopg2

# # Database connection details
# PGHOST = "ep-bold-sea-a437urkv-pooler.us-east-1.aws.neon.tech"
# PGDATABASE = "neondb"
# PGUSER = "neondb_owner"
# PGPASSWORD = "npg_SYVA1LXKtef0"

# # Establish connection
# conn = psycopg2.connect(
#     host=PGHOST,
#     database=PGDATABASE,
#     user=PGUSER,
#     password=PGPASSWORD,
#     sslmode="require"
# )

# # Create a cursor object
# cur = conn.cursor()

# # SQL statements to create tables
# create_tables_sql = """
# CREATE TABLE IF NOT EXISTS users (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(200) NOT NULL,
#     email VARCHAR(200) UNIQUE NOT NULL,
#     date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     password_hash VARCHAR(128),
#     password_hash2 VARCHAR(128)
# );

# CREATE TABLE IF NOT EXISTS todo (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     complete BOOLEAN,
#     description VARCHAR(150),
#     start VARCHAR(150),
#     date VARCHAR(150) NOT NULL,
#     day VARCHAR(150) NOT NULL,
#     month VARCHAR(150) NOT NULL,
#     year VARCHAR(150) NOT NULL,
#     labels VARCHAR(200),
#     poster_id INT,
#     FOREIGN KEY (poster_id) REFERENCES users(id) ON DELETE CASCADE
# );

# CREATE TABLE IF NOT EXISTS labels (
#     id SERIAL PRIMARY KEY,
#     name TEXT NOT NULL,
#     poster_labels_id INT,
#     FOREIGN KEY (poster_labels_id) REFERENCES users(id) ON DELETE CASCADE
# );

# CREATE TABLE IF NOT EXISTS notes (
#     id SERIAL PRIMARY KEY,
#     name TEXT,
#     description TEXT,
#     poster_notes_id INT,
#     FOREIGN KEY (poster_notes_id) REFERENCES users(id) ON DELETE CASCADE
# );
# """

# # Execute the table creation
# cur.execute(create_tables_sql)

# # Commit changes and close connection
# conn.commit()
# cur.close()
# conn.close()

# print("Tables created successfully!")
