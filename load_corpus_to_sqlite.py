import sqlite3
import yaml
import os
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return model.encode(text).tolist()

db_name = "chat_knowledge.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        user_input TEXT,
        bot_response TEXT,
        embedding TEXT
    )
''')

def load_data(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".yml"):
            category = filename.replace(".yml", "")
            filepath = os.path.join(directory, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
                if 'conversations' in data:
                    for conversation in data['conversations']:
                        for i in range(len(conversation) - 1):
                            user_input = conversation[i]
                            bot_response = conversation[i+1]

                            embedding = json.dumps(get_embedding(user_input))

                            cursor.execute('''
                                INSERT INTO knowledge_base (category, user_input, bot_response, embedding)
                                VALUES (?, ?, ?, ?)
                            ''', (category, user_input, bot_response, embedding))
    
    conn.commit()
    print(" داده‌ها با embedding ذخیره شدند")

load_data('.')
conn.close()