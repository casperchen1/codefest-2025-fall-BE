import pymysql
import os
import csv

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
    host="test-ss12271127-28c5.i.aivencloud.com",
    password="", #請填入密碼
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
  #insertDataFromCSV(cursor, "sports_places", "importData/sports_places.csv")
  #insertUser(cursor, "testuser", "testpassword")
  cursor.execute("SELECT * FROM UserInfo")
  print(cursor.fetchall())
finally:
    cursor.connection.close()
'''