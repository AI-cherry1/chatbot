import sqlite3
from datetime import datetime, timedelta
import hashlib

DB_PATH = "counselor.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        gender TEXT,
        age_group TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_admin BOOLEAN DEFAULT 0
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mode TEXT NOT NULL,
        title TEXT NOT NULL,
        question TEXT NOT NULL,
        blood_type TEXT,
        mbti TEXT,
        age INTEGER,
        consideration TEXT,
        payment_status TEXT DEFAULT 'pending',
        payment_amount REAL DEFAULT 0,
        payment_method TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        consultation_id INTEGER UNIQUE NOT NULL,
        content TEXT,
        verified BOOLEAN DEFAULT 0,
        created_at TIMESTAMP,
        admin_id INTEGER,
        is_deleted BOOLEAN DEFAULT 0,
        FOREIGN KEY (consultation_id) REFERENCES consultations(id),
        FOREIGN KEY (admin_id) REFERENCES users(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        consultation_id INTEGER,
        amount REAL NOT NULL,
        method TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (consultation_id) REFERENCES consultations(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        consultation_id INTEGER,
        message TEXT,
        read_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (consultation_id) REFERENCES consultations(id)
    )
    ''')

    conn.commit()

    ensure_column(cursor, "consultations", "blood_type TEXT")
    ensure_column(cursor, "consultations", "mbti TEXT")
    ensure_column(cursor, "consultations", "age INTEGER")
    ensure_column(cursor, "consultations", "consideration TEXT")

    conn.commit()
    conn.close()
    ensure_admin_user()


def ensure_column(cursor, table_name, column_definition):
    column_name = column_definition.split()[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing = [row[1] for row in cursor.fetchall()]
    if column_name not in existing:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")


def ensure_admin_user():
    try:
        if not get_user_by_username("admin"):
            create_user("admin", "admin123", "unknown", "40대", is_admin=True)
    except Exception:
        pass


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_username(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def create_user(username, password, gender, age_group, is_admin=False):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute('''
        INSERT INTO users (username, password_hash, gender, age_group, is_admin)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, gender, age_group, int(is_admin)))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None


def verify_password(stored_hash, password):
    return stored_hash == hash_password(password)


def update_user_password(user_id, new_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hash_password(new_password), user_id))
    conn.commit()
    conn.close()


def create_consultation(user_id, consultation_type, title, question, blood_type=None, mbti=None, age=None, consideration=None, amount=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    expires_at = datetime.now() + timedelta(days=10)
    cursor.execute('''
    INSERT INTO consultations (user_id, mode, title, question, blood_type, mbti, age, consideration, payment_amount, expires_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, consultation_type, title, question, blood_type, mbti, age, consideration, amount, expires_at.isoformat()))
    conn.commit()
    consultation_id = cursor.lastrowid
    conn.close()
    return consultation_id


def get_consultation(consultation_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM consultations WHERE id = ?', (consultation_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def get_pending_consultations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.*, u.username, a.id as answer_id
    FROM consultations c
    JOIN users u ON c.user_id = u.id
    LEFT JOIN answers a ON c.id = a.consultation_id
    WHERE a.id IS NULL
    ORDER BY c.created_at ASC
    ''')
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]


def save_answer(consultation_id, content, admin_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO answers (consultation_id, content, created_at, admin_id)
    VALUES (?, ?, ?, ?)
    ''', (consultation_id, content, datetime.now().isoformat(), admin_id))
    conn.commit()
    conn.close()


def get_answer(consultation_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM answers WHERE consultation_id = ?', (consultation_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def get_user_consultations(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, title, created_at, payment_amount, mode, expires_at, payment_status, payment_method
    FROM consultations
    WHERE user_id = ?
    ORDER BY created_at DESC
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]


def get_user_consultation_details(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.*, a.content AS answer_content, a.created_at AS answer_created_at, a.is_deleted
    FROM consultations c
    LEFT JOIN answers a ON c.id = a.consultation_id
    WHERE c.user_id = ?
    ORDER BY c.created_at DESC
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]


def get_user_payment_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, title, created_at, payment_amount, payment_method, payment_status, mode, expires_at,
           CASE WHEN EXISTS (SELECT 1 FROM answers a WHERE a.consultation_id = consultations.id) THEN '답변 완료' ELSE '대기 중' END AS answer_status
    FROM consultations
    WHERE user_id = ?
    ORDER BY created_at DESC
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]


def mark_payment_completed(consultation_id, method):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE consultations
    SET payment_status = 'completed', payment_method = ?
    WHERE id = ?
    ''', (method, consultation_id))
    conn.commit()
    conn.close()


def delete_expired_answers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE answers
    SET is_deleted = 1, content = '[조회기간 만료]'
    WHERE created_at < datetime('now', '-10 days') AND is_deleted = 0
    ''')
    conn.commit()
    conn.close()
