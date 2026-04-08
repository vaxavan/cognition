from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Импорты моделей (чтобы create_all их видел)
from app.models.user import User
# from app.models.chat import Chat
# from app.models.message import Message
# from app.models.file import File