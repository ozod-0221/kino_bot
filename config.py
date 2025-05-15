
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
BOT_USERNAME = os.getenv("BOT_USERNAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

