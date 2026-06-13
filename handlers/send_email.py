import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os, sys

load_dotenv()


def sender(name, phone):
    msg = EmailMessage()
    msg['Subject'] = 'Тема письма - - '
    msg['From'] = os.getenv('SENDER_EMAIL')
    msg['To'] = os.getenv('GETTER_EMAIL')
    msg.set_content(f'Пользователь оставил контакты: \n Имя: {name} \n Телефон: {phone}')

    # 2. Настройки почтового сервера (например, для Gmail)
    SMTP_SERVER = 'smtp.yandex.ru'
    SMTP_PORT = 587
    SENDER_EMAIL = os.getenv('SENDER_EMAIL') or sys.exit()

    # Используйте "Пароль приложения" (App Password), а не ваш основной пароль
    # SENDER_PASSWORD = 'hpfbbujoynkgudpu'

    SENDER_PASSWORD = os.getenv('EMAIL_PASSWORD') or sys.exit()

    try:
        # 3. Подключение к серверу и отправка
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Безопасное шифрование соединения
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
