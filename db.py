import sqlite3
import os
from datetime import datetime, timedelta
import hashlib

DB_PATH = "counselor.db"

def init_db():
    """데이터베이스 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 사용자 테이블
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
    
    # 상담 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        question TEXT NOT NULL,
        mode TEXT NOT NULL,
        payment_status TEXT DEFAULT 'pending',
        payment_amount REAL,
        payment_method TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # 답변 테이블
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
    
    # 결제 테이블
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
    
    # 알림 테이블
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
    conn.close()

def hash_password(password):
    """비밀번호 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_username(username):
    """사용자 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(username, password, gender, age_group, is_admin=False):
    """사용자 생성"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute('''
        INSERT INTO users (username, password_hash, gender, age_group, is_admin)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, gender, age_group, is_admin))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None

def verify_password(stored_hash, password):
    """비밀번호 검증"""
    return stored_hash == hash_password(password)

def create_consultation(user_id, title, question, mode, amount):
    """상담 신청"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    expires_at = datetime.now() + timedelta(days=10)
    cursor.execute('''
    INSERT INTO consultations (user_id, title, question, mode, payment_amount, expires_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, title, question, mode, amount, expires_at.isoformat()))
    conn.commit()
    consultation_id = cursor.lastrowid
    conn.close()
    return consultation_id

def get_consultation(consultation_id):
    """상담 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM consultations WHERE id = ?', (consultation_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def get_pending_consultations():
    """답변 대기 중인 상담 목록 (관리자)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.*, u.username, a.id as answer_id
    FROM consultations c
    JOIN users u ON c.user_id = u.id
    LEFT JOIN answers a ON c.id = a.consultation_id
    WHERE c.payment_status = 'completed' AND a.id IS NULL
    ORDER BY c.created_at ASC
    ''')
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

def save_answer(consultation_id, content, admin_id):
    """답변 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO answers (consultation_id, content, created_at, admin_id)
    VALUES (?, ?, ?, ?)
    ''', (consultation_id, content, datetime.now().isoformat(), admin_id))
    conn.commit()
    conn.close()

def get_answer(consultation_id):
    """답변 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM answers WHERE consultation_id = ?', (consultation_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def get_user_consultations(user_id):
    """사용자 상담이력 (제목/날짜/금액만)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, title, created_at, payment_amount, mode, expires_at
    FROM consultations
    WHERE user_id = ?
    ORDER BY created_at DESC
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

def mark_payment_completed(consultation_id, method):
    """결제 완료 처리"""
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
    """10일 지난 답변 삭제"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE answers
    SET is_deleted = 1, content = '[조회기간 만료]'
    WHERE created_at < datetime('now', '-10 days') AND is_deleted = 0
    ''')
    conn.commit()
    conn.close()

# 초기화 시 관리자 계정 자동 생성
if get_user_by_username is not None:
    # DB 최초 생성 시에만 실행
    try:
        if not get_user_by_username("admin"):
            create_user("admin", "admin123", "unknown", "40대", is_admin=True)
    except:
        pass
