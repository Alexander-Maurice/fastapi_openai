from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


# ===== ИМПОРТИРУЕМ СУЩЕСТВУЮЩИЕ МОДУЛИ =====
from clean_surrogates import clean_surrogates  # Очистка текста
from agents.guitar_agent import guitar_agent
from agents.contacts_checker import check_contacts_from_message, write_contact_to_txt  # Проверка контактов
from handlers.send_email import sender           # Отправка email
import sqlite3                                  # База данных
import os
from dotenv import load_dotenv


# ===== ЗАГРУЖАЕМ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ =====
load_dotenv()


# ===== ПОДКЛЮЧАЕМ БАЗУ ДАННЫХ) =====
conn = sqlite3.connect('contacts_db.db', check_same_thread=False)
cursor = conn.cursor()


# ===== СОЗДАЁМ ПРИЛОЖЕНИЕ FASTAPI =====
app = FastAPI(title="AI Guitar Agent Chat", version="1.0.0")


# ===== РАЗДАЁМ СТАТИЧЕСКИЕ ФАЙЛЫ (HTML, CSS, JS) =====
app.mount("/static", StaticFiles(directory="static"), name="static")


# ===== ФУНКЦИЯ ДОБАВЛЕНИЯ КОНТАКТОВ В БД =====
def insert_data_to_db(name, phone):
    """
    Сохраняет имя и телефон в базу данных.
    """
    if not name:
        name = 'None'
    if not phone:
        phone = 'None'

    sql_query = 'INSERT INTO contacts(name, phone) values (?, ?)'
    user_data = (name, phone)
    cursor.execute(sql_query, user_data)
    conn.commit()


# ===== МОДЕЛЬ ЗАПРОСА (что приходит от пользователя) =====
class QuestionRequest(BaseModel):
    """
    Модель данных, которую ожидаем от веб-интерфейса.
    Содержит только вопрос пользователя.
    """
    question: str = Field(
        ...,  # Обязательное поле
        min_length=1,  # Минимум 1 символ
        max_length=2000,  # Максимум 2000 символов
        description="Вопрос пользователя"
    )


# ===== МОДЕЛЬ ОТВЕТА (что отправляем обратно) =====
class AnswerResponse(BaseModel):
    """
    Модель ответа сервера.
    Отправляем только текст ответа от ИИ.
    """
    answer: str = Field(..., description="Ответ ИИ-агента")


# ===== ГЛАВНАЯ СТРАНИЦА (отдаём HTML) =====
@app.get('/')
async def get_main_page():
    """
    Когда пользователь открывает сайт — показываем чат-виджет.
    """
    return FileResponse('static/index.html')


# ===== ГЛАВНЫЙ ЭНДПОИНТ ДЛЯ ОБРАБОТКИ СООБЩЕНИЙ =====
@app.post('/api/chat', response_model=AnswerResponse)
async def chat_with_agent(request: QuestionRequest):
    """
    САМОЕ ВАЖНОЕ МЕСТО!
    Здесь вопрос пользователя передаётся ВАШЕМУ ИИ-агенту.

    Как это работает:
    1. Получаем вопрос из веб-интерфейса
    2. Очищаем текст (ВАША функция clean_surrogates)
    3. Проверяем, есть ли в сообщении контакты
    4. Отправляем вопрос ИИ-агенту (guitar_agent)
    5. Сохраняем диалог в файл
    6. Возвращаем ответ обратно в веб-интерфейс
    """

    try:
        # === ШАГ 1: Получаем и очищаем вопрос ===
        question = clean_surrogates(request.question.strip())

        # === ШАГ 2: Проверяем, есть ли контакты в сообщении ===
        if check_contacts_from_message(question):
            write_contact_to_txt(question)  # Сохраняем в файл
            name, phone = check_contacts_from_message(question)
            insert_data_to_db(name, phone)  # Сохраняем в БД
            sender(name, phone)  # Отправляем на почту

        # === ШАГ 3: Отправляем вопрос ИИ-агенту ===
        answer = guitar_agent.run(question).content
        current_session_id = guitar_agent.session_id

        # === ШАГ 4: Сохраняем диалог в файл ===
        # Создаём папку dialogues если её нет
        os.makedirs('dialogues', exist_ok=True)

        filename = f'dialogues/dialogue_{current_session_id}.txt'
        with open(filename, 'a', encoding='utf-8') as f:
            f.write('USER----------------\n')
            f.write(question + '\n')
            f.write('END_USER------------\n\n')
            f.write('AI------------------\n')
            f.write(answer + '\n')
            f.write('END_AI--------------\n\n')

        # === ШАГ 5: Возвращаем ответ в веб-интерфейс ===
        return AnswerResponse(answer=answer)

    except Exception as e:
        # Если что-то пошло не так — отправляем ошибку
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке вопроса: {str(e)}"
        )


# ===== ЗАПУСК СЕРВЕРА =====
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Автоматически перезагружать при изменениях
    )

