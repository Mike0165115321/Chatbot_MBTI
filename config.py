# config.py (เวอร์ชันใหม่: สำหรับจัดการหลาย Persona)

import os
import glob
from dotenv import load_dotenv

# โหลดค่า API Key จากไฟล์ .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

PERSONA_DIR = "personas"

def get_persona_files() -> list:
    search_path = os.path.join(PERSONA_DIR, "*.txt")
    return glob.glob(search_path)

def get_persona_names() -> list:
    files = get_persona_files()
    if not files:
        return ["(ไม่พบ Persona)"]
        
    names = [
        os.path.basename(file_path).replace('.txt', '').replace('_', ' ')
        for file_path in files
    ]
    return sorted(names) 

def load_persona_instruction(persona_name: str) -> str:
    if persona_name == "(ไม่พบ Persona)":
        return "เกิดข้อผิดพลาด: ไม่พบไฟล์ Persona ในโฟลเดอร์ 'personas' กรุณาสร้างไฟล์ .txt"

    file_name = f"{persona_name.replace(' ', '_')}.txt"
    file_path = os.path.join(PERSONA_DIR, file_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            instruction = f.read()
        return instruction.strip().encode('utf-8', 'replace').decode('utf-8')
    except FileNotFoundError:
        return f"เกิดข้อผิดพลาด: ไม่พบไฟล์ '{file_name}' กรุณาตรวจสอบชื่อไฟล์"
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการอ่านไฟล์ Persona: {e}"
