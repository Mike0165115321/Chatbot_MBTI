# database_manager.py (เวอร์ชันอัปเกรด)

import sqlite3

HISTORY_LIMIT = 20

def init_db():
    """สร้าง Database และ Table 'messages' พร้อม Index เพื่อเพิ่มประสิทธิภาพ"""
    try:
        with sqlite3.connect("chat.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'model')),
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON messages(session_id)")
        print("🗄️  ฐานข้อมูล 'chat.db' พร้อมใช้งานแล้ว")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเริ่มต้นฐานข้อมูล: {e}")

def add_message(session_id: str, role: str, content: str):
    """เพิ่มข้อความใหม่ลงในฐานข้อมูล"""
    try:
        with sqlite3.connect("chat.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                           (session_id, role, content))
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการบันทึกข้อความ: {e}")

def get_recent_messages(session_id: str) -> list[dict]:
    """ดึงประวัติการสนทนาล่าสุดตามจำนวนที่กำหนด (HISTORY_LIMIT)
    และคืนค่าเป็น List of Dictionaries เพื่อให้อ่านง่าย
    """
    try:
        with sqlite3.connect("chat.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, HISTORY_LIMIT)
            )
            messages = [dict(row) for row in cursor.fetchall()]
            
            return list(reversed(messages))
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงข้อความ: {e}")
        return []
def get_chat_sessions() -> list[dict]:
    try:
        with sqlite3.connect("chat.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    s.session_id, 
                    m.content AS title
                FROM (
                    SELECT 
                        session_id, 
                        MIN(id) as first_user_message_id
                    FROM messages
                    WHERE role = 'user'
                    GROUP BY session_id
                ) s
                JOIN messages m ON s.first_user_message_id = m.id
                ORDER BY m.timestamp DESC
            """)
            
            sessions = [dict(row) for row in cursor.fetchall()]
            return sessions
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงรายการแชท: {e}")
        return []

def get_full_history_by_session_id(session_id: str) -> list[dict]:
    """ดึงประวัติการสนทนา 'ทั้งหมด' ของ session ที่กำหนด"""
    try:
        with sqlite3.connect("chat.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            )
            messages = [dict(row) for row in cursor.fetchall()]
            return messages
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงประวัติทั้งหมด: {e}")
        return []

def delete_session(session_id: str):
    """[ฟีเจอร์ใหม่] ลบข้อความทั้งหมดที่เกี่ยวข้องกับ session_id ที่ระบุ"""
    try:
        with sqlite3.connect("chat.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            print(f"🗑️ ลบเซสชั่น {session_id} เรียบร้อยแล้ว")
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการลบเซสชั่น: {e}")