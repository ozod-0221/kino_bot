# generate database,engine and session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base


DB_USER = "postgres"
DB_PASS = "123456"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "kinoBot"


# Connection URI
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)

# Session yaratuvchi
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Bazani yaratish funksiyasi
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)