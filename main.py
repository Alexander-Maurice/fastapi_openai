from fastapi import FastAPI

from clean_surrogates import clean_surrogates
from agents.guitar_agent import guitar_agent
from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv
from agents.contacts_checker import check_contacts_from_message, write_contact_to_txt
import sqlite3
from handlers.send_email import sender


load_dotenv()

conn = sqlite3.connect('contacts_db.db')
cursor = conn.cursor()
app = FastAPI()

# cursor.execute(
#     '''
#     CREATE TABLE IF NOT EXISTS contacts(
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     phone TEXT NOT NULL)
#     '''
# )

def insert_data_to_db(name, phone):
    if not name:
        name = 'None'
    if not phone:
        phone = 'None'
    sql_query = 'INSERT INTO contacts(name, phone) values (?, ?)'
    user_data = (name, phone)
    cursor.execute(sql_query, user_data)

    conn.commit()


@app.get('/')
def get_root():
    return {'message': 'Upload main page...'}


if __name__ == '__main__':
    CURRENT_SESSION = None
    while question := clean_surrogates(input('USER: ').strip()):

        if check_contacts_from_message(question): #если обнаруживаем контакты в сообщении
            write_contact_to_txt(question) #сохраняем их в файл txt
            name, phone = check_contacts_from_message(question)
            insert_data_to_db(name, phone) #вставляем данные в бд
            sender(name, phone) #отправляем данные по почте


        answer = guitar_agent.run(question).content
        current_session_id = guitar_agent.session_id

        filename = f'dialogues/dialogue_{current_session_id}.txt'
        with open(filename, 'a', encoding='utf-8') as f:
            f.write('USER----------------')
            f.write(question)
            f.write('END_USER------------')
            f.write('\n\n')
            f.write('AI------------------')
            f.write(answer)
            f.write('END_AI--------------')
            f.write('\n\n')
        print('AI: ', answer)
        txt_file = f'dialogue_{current_session_id}.txt'


    conn.close()

