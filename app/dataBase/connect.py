import pymysql
import os
import csv

def deleteTable(cursor, tableName):
    cursor.execute(f"DROP TABLE IF EXISTS {tableName}")

def createTable(cursor, tableName, **kwargs):
    # 型態輸入格式: colName = colType
    # EX: id = "TRY"
    columns = ", ".join(f"{key} {value}" for key, value in kwargs.items())
    sql = f"CREATE TABLE IF NOT EXISTS {tableName} ({columns});"
    cursor.execute(sql)
    print(f"Table '{tableName}' created successfully.")
def getColumnsName(cursor, tableName):
    columns = []
    cursor.execute(f"DESCRIBE {tableName}")
    for item in cursor.fetchall():
        columns.append({"Name" : item["Field"], "Type" : item["Type"]})
    return columns
def insertDataFromCSV(cursor, tableName, csvFilePath):
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
  
try:
  cursor = connection.cursor()
  #deleteTable(cursor, "mytest")
  '''
  createTable(cursor, "mytest" ,
  id    =    "INT AUTO_INCREMENT PRIMARY KEY",
  行政區 = "VARCHAR(20)   NOT NULL",
  場地  =   "VARCHAR(255)  NOT NULL",
  類別 = "VARCHAR(100)  NOT NULL",
  緯度   =    "DECIMAL(9,6)  NOT NULL",
  經度   =    "DECIMAL(9,6)  NOT NULL")
  '''
  #cursor.execute("INSERT INTO mytest (id) VALUES (3), (2), (1)")
  #column = getColumnsName(cursor, "mytest")
  #insertDataFromCSV(cursor, "mytest", "importData/sports_places.csv")
  cursor.execute("SELECT * FROM mytest")
  print(cursor.fetchall())
finally:
  connection.close()
