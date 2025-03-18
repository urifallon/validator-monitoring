import sqlite3
import os
from werkzeug.security import generate_password_hash

# Đường dẫn đến database
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')

def create_database():
    # Tạo kết nối đến database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tạo bảng user
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tạo bảng tab
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tab (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'OFF',
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tạo bảng tab_metrics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tab_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tab_id INTEGER NOT NULL,
        value1 REAL,
        value2 REAL,
        value3 REAL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tab_id) REFERENCES tab (id)
    )
    ''')

    # Thêm user mẫu
    cursor.execute('INSERT OR IGNORE INTO user (username, password_hash, email) VALUES (?, ?, ?)',
                  ('test', generate_password_hash('test'), 'test@example.com'))

    # Thêm dữ liệu mẫu vào bảng tab
    sample_tabs = [
        ('Tab 1', 'ON'),
        ('Tab 2', 'OFF'),
        ('Tab 3', 'ON'),
        ('Tab 4', 'OFF'),
        ('Tab 5', 'ON'),
        ('Tab 6', 'OFF'),
        ('Tab 7', 'ON'),
        ('Tab 8', 'OFF')
    ]
    cursor.executemany('INSERT INTO tab (name, status) VALUES (?, ?)', sample_tabs)

    # Thêm dữ liệu mẫu vào bảng tab_metrics
    for i in range(1, 9):
        cursor.execute('''
        INSERT INTO tab_metrics (tab_id, value1, value2, value3)
        VALUES (?, ?, ?, ?)
        ''', (i, 0.0, 0.0, 0.0))

    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("Database đã được tạo thành công!") 