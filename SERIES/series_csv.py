import csv
import mysql.connector

# 데이터베이스 연결
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='0106',
    database='complete'
)

try:
    cursor = connection.cursor()

    # 쿼리 실행
    cursor.execute("SELECT * FROM SERIES")

    # 결과 가져오기
    results = cursor.fetchall()

    # CSV 파일에 결과 작성
    with open('series_240517.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        # 헤더 작성
        csvwriter.writerow([i[0] for i in cursor.description])
        # 데이터 작성
        csvwriter.writerows(results)

finally:
    # 연결 닫기
    if connection.is_connected():
        cursor.close()
        connection.close()
