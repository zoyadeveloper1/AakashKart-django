import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'db.sqlite3')
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Delete migration records for accounts and admin
c.execute("DELETE FROM django_migrations WHERE app='accounts';")
c.execute("DELETE FROM django_migrations WHERE app='admin';")

conn.commit()
conn.close()
print("Migration records cleared.")
