import pyodbc
from faker import Faker
import random
from datetime import datetime

# Initialize Faker to generate random data
fake = Faker()

# Database connection parameters
server = 'Lenovo'
database = 'Production '
username = 'flask_app_bot'
password = 'flaskApp'
driver = '{ODBC Driver 17 for SQL Server}'

# Establish connection
conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor = conn.cursor()

# SQL command to insert data
sql_command = """
INSERT INTO prodEntries (Cell, Item, DateWorked, Line, TimeShift, NumberPeople, NumberHours, NumberProduced, NumberDefects, Notes, Operator)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

# Generate and insert dummy data
for _ in range(100):  # Adjust the range for the number of records you want
    Cell = fake.bothify(text='Cell-##??')
    Item = fake.bothify(text='Item-###')
    # ItemDescription = fake.text(max_nb_chars=150)
    DateWorked = fake.date_between(start_date='-2y', end_date='today')
    Line = fake.bothify(text='Line-##')
    TimeShift = random.randint(1, 3)
    NumberPeople = random.randint(1, 10)
    NumberHours = random.randint(1, 24)
    NumberProduced = random.randint(0, 1000)
    NumberDefects = random.randint(0, 100)
    # Efficiency = random.uniform(50.0, 100.0)
    # PPM = random.uniform(0.0, 50.0)
    Notes = fake.text(max_nb_chars=300)
    Operator = fake.name()

    # Execute SQL command
    cursor.execute(sql_command, (Cell, Item, DateWorked, Line, TimeShift, NumberPeople, NumberHours, NumberProduced, NumberDefects, Notes, Operator))

# Commit the transactions and close the connection
conn.commit()
cursor.close()
conn.close()
print("Data insertion complete.")
