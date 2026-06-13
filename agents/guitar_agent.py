import os, sys
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.knowledge.knowledge import Knowledge
from agno.db.sqlite import SqliteDb
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.chunking.fixed import FixedSizeChunking
from instructions import acoustic_guitar_role

from agno.knowledge.reader.csv_reader import CSVReader
from agno.knowledge.chunking.row import RowChunking

from agno.run.agent import RunOutput


load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY') or sys.exit()
model_id = os.getenv('MODEL_ID_USED_1') or sys.exit()

#
# class UserContacts(BaseModel):
#     name: Optional[str] = Field(default=None, description='Имя пользователя')
#     email: Optional[str] = Field(default=None, description='Email адрес')
#     phone: Optional[str] = Field(default=None, description='Номер телефона')
#     telegram: Optional[str] = Field(default=None, description='Telegram username')
#
#     def has_any_contact(self):
#         return any([self.email, self.phone, self.telegram])


# def analyze_and_extract_contacts(user_message): -----не отрабатывает на бесплатных моделях, просит OPEN AI
#     extractor = Agent(
#         name='Агент извлечения контактов из сообщения',
#         output_schema=UserContacts,
#         instructions='''
#         Найди и извлеки контакты из сообщения пользователя
#         Примеры телефона: +7(999)999-99-99, 7(999)999-99-99,
#         8(999)999-99-99, 79999999999,555444, 666-444,
#         Примеры email: example@mail.ru, example@yandex.ru,
#         example@gmail.com,
#         Примеры имени: Александр, Алексей, Ирина, Сергей,
#         Примеры телеграм: alexmadnesss, @alexmadnesss, тг alexmadnesss
#         '''
#     )
#
#     result: RunOutput = extractor.run(user_message)
#     contacts: UserContacts = result.content
#
#     print(f'вероятные контакты: {contacts}')



# База хранения разговоров в сессии
db = SqliteDb(
    db_file='db/data_guitar.db'
)

# Преобразователь текста в чанки
embedder = SentenceTransformerEmbedder(
    id='all-MiniLM-L6-v2'
)

# Настраиваем размер чанков
# FixedSizeChunking(
#     chunk_size=1000,
#     overlap=200
# )

# Задаем векторную бд, в которой будут храниться векторы чанков
vector_db = LanceDb(
    table_name='guitar_vector',
    uri='vector_dbs/guitar_vector_files',
    search_type=SearchType.hybrid,
    embedder=embedder,
)

reader = CSVReader(
    # chunk_size=1000,
    # encoding='utf-8',
    chunking_strategy=RowChunking()
)

# Создаем объект для хранения знаний
knowledge = Knowledge(
    vector_db=vector_db
)

# Добавляем в знания инфу по гитарам
# knowledge.add_content(
#     path='data/guitars_data.txt',
#     skip_if_exists=True,
# )


knowledge.add_content(
    reader=reader,
    path='data/acoustic_guitars.csv'
)

# Создаем агента
guitar_agent = Agent(
    model=OpenRouter(id=model_id, temperature=0.2, top_p=0.4),
    description='ты помощник в выборе акустических гитар, используй товары только из базы знаний',
    # tools=[analyze_and_extract_contacts],
    instructions=acoustic_guitar_role,
    session_id='acoustic_guitar_helper',
    db=db,
    add_history_to_context=True,
    add_knowledge_to_context=True,
    num_history_runs=5,
    knowledge=knowledge,
    search_knowledge=True,
    markdown=True
)

