import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKENS = {
    "bot1": os.getenv("BOT_TOKEN_1"),
    "bot2": os.getenv("BOT_TOKEN_2"),
    "bot3": os.getenv("BOT_TOKEN_3"),
    "bot4": os.getenv("BOT_TOKEN_4"),
}

MANAGER_GROUP_ID = int(os.getenv("MANAGER_GROUP_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
WEB_URL = os.getenv("WEB_URL")
