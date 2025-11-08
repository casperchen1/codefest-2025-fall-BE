import pymysql
import os
from dotenv import load_dotenv
import csv
import pandas as pd

load_dotenv()

PASSWORD = os.getenv("DB_PASSWORD")
HOSTNAME = os.getenv("DB_HOST")


def deleteTable(cursor, tableName):
    #刪除表
    cursor.execute(f"DROP TABLE IF EXISTS {tableName}")

def createTable(cursor, tableName, **kwargs):
    # 型態輸入格式: colName = colType
    # EX: id = "TRY"
    columns = ", ".join(f"{key} {value}" for key, value in kwargs.items())
    sql = f"CREATE TABLE IF NOT EXISTS {tableName} ({columns});"
    cursor.execute(sql)
    print(f"Table '{tableName}' created successfully.")

def getinfo(cursor, tableName, Username):
    #取得tableName的所有資料
    cursor.execute("SELECT * FROM %s WHERE Username = %s", (tableName, Username))
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df

def getAllInfo(cursor, tableName):
    #取得tableName的所有資料
    cursor.execute(f"SELECT * FROM {tableName}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df

def updateData(cursor, tableName, newValues, Username):
    cursor.execute("UPDATE %s SET Points = %s WHERE Username = %s", (tableName, newValues, Username))
    cursor.connection.commit()  # 如果你只有 cursor，也可以這樣 commit

def getColumnsName(cursor, tableName):
    #取得tableName的所有欄位名稱及型態
    columns = []
    cursor.execute(f"DESCRIBE {tableName}")
    for item in cursor.fetchall():
        columns.append({"Name" : item["Field"], "Type" : item["Type"]})
    return columns

def insertDataFromCSV(cursor, tableName, csvFilePath):
    #將CSV檔插入資料表裡面
    with open(csvFilePath, mode='r', encoding='Big5') as file:
        reader = csv.reader(file)
        headers = next(reader)  # 取得欄位名稱
        placeholders = ", ".join(["%s"] * len(headers))
        sql = f"INSERT INTO {tableName} ({', '.join(headers)}) VALUES ({placeholders})"
        for row in reader:
            print(sql, row)
            cursor.execute(sql, row)
        cursor.connection.commit()
    #print(cursor.fetchall())

def insertUser(cursor, username, password):
    #插入使用者帳號密碼
    sql = "INSERT INTO Points (Username, Points) VALUES (%s, %s)"
    cursor.execute(sql, (username, 0))
    sql = "INSERT INTO UserInfo (Username, Password) VALUES (%s, %s)"
    cursor.execute(sql, (username, password))
    cursor.connection.commit()
    

def connectToDB():
    #連接資料庫
    timeout = 10
    connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db="defaultdb",
    host=HOSTNAME,
    password=PASSWORD, 
    read_timeout=timeout,
    port=23720,
    user="User",
    write_timeout=timeout,
    )
    cursor = connection.cursor()
    return cursor
'''
try:
  cursor = connectToDB()
  #deleteTable(cursor, "UserInfo")
  createTable(cursor, "sports_places" ,
  id    =    "INT AUTO_INCREMENT PRIMARY KEY",
  行政區 = "VARCHAR(20)   NOT NULL",
  場地  =   "VARCHAR(255)  NOT NULL",
  類別 = "VARCHAR(100)  NOT NULL",
  緯度   =    "DECIMAL(9,6)  NOT NULL",
  經度   =    "DECIMAL(9,6)  NOT NULL")
  createTable(cursor, "UserInfo", 
  id    =    "INT AUTO_INCREMENT PRIMARY KEY",
  Username = "VARCHAR(50)",
  Password = "VARCHAR(50)",
  )
  
  
  #column = getColumnsName(cursor, "UserInfo")
  insertUser(cursor, "testuser", "testpassword")
  #cursor.execute("DELETE FROM sports_places;")
  #insertDataFromCSV(cursor, "sports_places", "importData/output.csv")
  cursor.execute("SELECT * FROM points")
  print(cursor.fetchall())

  getinfo(cursor, "sports_places")
finally:
    cursor.connection.close()
'''

'''
cursor = connectToDB()
cursor.execute("SHOW PROCESSLIST;")
rows = cursor.fetchall()
for row in cursor.fetchall():
    if row["Command"] == "Sleep":
        cursor.execute(f"KILL {row['Id']}")
print(rows)
cursor.close()
'''