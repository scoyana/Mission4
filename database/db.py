import pymysql
import os
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class DbManager:
    def __init__(self):
        self.conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            charset=os.getenv("DB_CHARSET", "utf8mb4"),
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

    def init_db(self):
        """초기 테이블 생성"""
        queries = [
            """CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                userId VARCHAR(255) UNIQUE,
                password VARCHAR(255),
                name VARCHAR(255),
                school VARCHAR(255),
                email VARCHAR(255),
                profile_image VARCHAR(255),
                find_password VARCHAR(255),
                find_password_answer VARCHAR(255),
                created_at DATETIME
            )""",
            
            """CREATE TABLE IF NOT EXISTS post (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                content TEXT,
                created_at DATETIME,
                views INT DEFAULT 0,
                secret VARCHAR(255) DEFAULT '',
                user_id INT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            
            """CREATE TABLE IF NOT EXISTS post_files (
                id INT AUTO_INCREMENT PRIMARY KEY,
                post_id INT,
                original_filename VARCHAR(255),
                stored_filename VARCHAR(255),
                file_size INT,
                download_count INT DEFAULT 0,
                created_at DATETIME,
                FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
            )"""
        ]
        for query in queries:
            self.cursor.execute(query)
        self.conn.commit()

    def execute_query(self, query, params=None, fetchone=False, commit=False):
        self.cursor.execute(query, params or ())

        if commit:
            self.conn.commit()

        if fetchone:
            result = self.cursor.fetchone()
        else:
            result = self.cursor.fetchall()

        return result


    def close(self):
        """데이터베이스 연결 종료"""
        self.cursor.close()
        self.conn.close()

    def get_current_time(self):
        """현재 시간을 MySQL DATETIME 형식으로 반환"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 객체 생성
db = DbManager()
db.init_db()


  