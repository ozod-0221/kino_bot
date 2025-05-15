from database.db import async_session
from database.models import Kino, Channel, User,SearchedKino,kino_janr,Janr,MediaTuri
from sqlalchemy.orm import  selectinload
from sqlalchemy.future import select
from datetime import datetime, timedelta



async def add_kino(code: str, name: str, janrlar: list[str], post_link: str, media: str,language:str):
    async with async_session() as session:
        # Media topiladi
        result = await session.execute(select(MediaTuri).where(MediaTuri.name == media))
        media_obj = result.scalar_one_or_none()
        if not media_obj:
            raise Exception("Bunday media topilmadi!")

        # Janrlar obyektga aylanadi
        genre_objects = []
        for janr in janrlar:
            result = await session.execute(select(Janr).where(Janr.name == janr))
            genre = result.scalar_one_or_none()
            if genre:
                genre_objects.append(genre)

        # Yangi kino obyekt
        new_kino = Kino(
            code=code,
            name=name,
            post_link=post_link,
            media=media_obj,
            janrlar=genre_objects,
            language=language
        )

        session.add(new_kino)
        await session.commit()
async def is_kino_exists(code: str):
    async with async_session() as session:
        query = select(Kino).filter(Kino.code == code)
        result = await session.execute(query)
        kino = result.scalar()
        return kino is not None
async def get_kino_by_code(code: str)-> Kino:
    async with async_session() as session:
        query = select(Kino).filter(Kino.code == code)
        result = await session.execute(query)
        kino = result.scalar()
        return kino
    
async def add_channel(channel_id:int, url: str,name: str,count: int):
    async with async_session() as session:
        channel_id = int(channel_id)
        new_channel = Channel(telegram_id=channel_id, url=url,name=name,count_of_members_when_bot_joined=count)
        session.add(new_channel)
        await session.commit()
async def get_all_channels():
    async with async_session() as session:
        query = select(Channel)
        result = await session.execute(query)
        channels = result.scalars().all()
        return channels
async def delete_channel(channel_id: int):
    async with async_session() as session:
        query = select(Channel).filter(Channel.telegram_id == channel_id)
        result = await session.execute(query)
        channel = result.scalar()
        if channel:
            await session.delete(channel)
            await session.commit()
async def get_channel_by_id(channel_id: int):
    async with async_session() as session:
        query = select(Channel).filter(Channel.telegram_id == channel_id)
        result = await session.execute(query)
        channel = result.scalar()
        return channel
    
async def is_user_exists(user_id: int):
    async with async_session() as session:
        query = select(User).filter(User.telegram_id == user_id)
        result = await session.execute(query)
        user = result.scalar()
        return user is not None
async def add_user(user_id: int, username: str, first_name: str, last_name: str,language=None):
    async with async_session() as session:
        new_user = User(telegram_id=user_id, username=username, first_name=first_name, last_name=last_name,language=language)
        session.add(new_user)
        await session.commit()
async def get_user_by_id(user_id: int) -> User:
    async with async_session() as session:
        query = select(User).filter(User.telegram_id == user_id)
        result = await session.execute(query)
        user = result.scalar()
        return user       
async def add_searched_kino(user_id: int, kino_id: int):
    async with async_session() as session:
        new_searched_kino = SearchedKino(user_id=user_id, kino_id=kino_id)
        session.add(new_searched_kino)
        await session.commit()
        
async def update_user_language(user_id: int, language: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.language = language
            await session.commit()
async def add_janr(name: str):
    async with async_session() as session:
        new_janr = Janr(name=name)
        session.add(new_janr)
        await session.commit()
async def is_janr_exists(name: str):
    async with async_session() as session:
        query = select(Janr).filter(Janr.name == name)
        result = await session.execute(query)
        janr = result.scalar()
        return janr is not None
async def get_janr_buttons():
    async with async_session() as session:
        result = await session.execute(select(Janr))
        janrlar = result.scalars().all()
        return [(janr.name, f"customjanr_{janr.name.lower().replace(' ', '_')}") for janr in janrlar]
    
async def is_media_turi_exists(name: str):
    async with async_session() as session:
        query = select(MediaTuri).filter(MediaTuri.name == name)
        result = await session.execute(query)
        media_turi = result.scalar()
        return media_turi is not None
async def add_media_turi(name: str):
    async with async_session() as session:
        new_media_turi = MediaTuri(name=name)
        session.add(new_media_turi)
        await session.commit()
async def get_media_turi_buttons():
    async with async_session() as session:
        result = await session.execute(select(MediaTuri))
        media_turlari = result.scalars().all()
        return [(media_turi.name, f"custommedia_{media_turi.name.replace(' ', '_')}") for media_turi in media_turlari]
async def get_media_turi_by_id(media_turi_id: int) -> MediaTuri:
    async with async_session() as session:
        query = select(MediaTuri).filter(MediaTuri.id == media_turi_id)
        result = await session.execute(query)
        media_turi = result.scalar()
        return media_turi
async def get_janr_by_id(janr_id: int) -> Janr:
    async with async_session() as session:
        query = select(Janr).filter(Janr.id == janr_id)
        result = await session.execute(query)
        janr = result.scalar()
        return janr
async def biriktir_janrlar(kino_id: int, janr_nomi_list: list[str]):
    async with async_session() as session:
        # 1. Kino obyektini olish
        result = await session.execute(
            select(Kino).options(selectinload(Kino.janrlar)).filter(Kino.id == kino_id)
        )
        kino = result.scalar_one_or_none()
        if not kino:
            print("Kino topilmadi!")
            return

        # 2. Kiritilgan janr nomlari asosida Janr obyektlarini olish
        result = await session.execute(
            select(Janr).filter(Janr.name.in_(janr_nomi_list))
        )
        janrlar = result.scalars().all()

        # 3. Kino uchun janrlar biriktirish
        kino.janrlar = janrlar  # eski bog‘lamalarni o‘chirib yangilarini qo‘yadi

        await session.commit()
        print(f"{kino.name} uchun janrlar biriktirildi: {[j.name for j in janrlar]}")
async def get_janrlar_by_kino_id(kino_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Kino)
            .options(selectinload(Kino.janrlar))
            .where(Kino.id == kino_id)
        )
        kino = result.scalar_one_or_none()
        if kino:
            return [janr.name for janr in kino.janrlar]
        return []
async def get_media_name_by_id(media_id)->str:
    async with async_session() as session:
        query = select(MediaTuri).filter(MediaTuri.id == media_id)
        result = await session.execute(query)
        media = result.scalar()
        return media.name
from sqlalchemy import func, desc

async def get_most_searched_movies(limit=10):
    async with async_session() as session:
        stmt = select(
            Kino.name,
            Kino.code,
            func.count(SearchedKino.id).label('search_count')
        ).join(
            SearchedKino, SearchedKino.kino_id == Kino.id
        ).group_by(
            Kino.id
        ).order_by(
            desc('search_count')
        ).limit(limit)
        
        result = await session.execute(stmt)
        return [{"name": r.name, "code": r.code, "count": r.search_count} for r in result]
async def get_most_searched_genres(limit=5):
    async with async_session() as session:
        stmt = select(
            Janr.name,
            func.count(SearchedKino.id).label('search_count')
        ).join(
            kino_janr, kino_janr.c.janr_id == Janr.id
        ).join(
            Kino, kino_janr.c.kino_id == Kino.id
        ).join(
            SearchedKino, SearchedKino.kino_id == Kino.id
        ).group_by(
            Janr.id
        ).order_by(
            desc('search_count')
        ).limit(limit)
        
        result = await session.execute(stmt)
        return [{"genre": r.name, "count": r.search_count} for r in result]
async def get_general_stats():
    async with async_session() as session:
        stats = {
            "total_movies": (await session.execute(select(func.count(Kino.id)))).scalar(),
            "total_genres": (await session.execute(select(func.count(Janr.id)))).scalar(),
            "total_users": (await session.execute(select(func.count(User.id)))).scalar(),
            "total_searches": (await session.execute(select(func.count(SearchedKino.id)))).scalar(),
            "total_channels": (await session.execute(select(func.count(Channel.id)))).scalar(),
        }
        
        # Oxirgi 24 soatdagi qidiruvlar
        last_24h = (await session.execute(select(func.count(SearchedKino.id)).filter(
            SearchedKino.searched_at >= datetime.utcnow() - timedelta(hours=24)
        ))).scalar()
        stats['last_24h_searches'] = last_24h
        
        return stats
async def get_media_type_stats():
    async with async_session() as session:
        stmt = select(
            MediaTuri.name,
            func.count(Kino.id).label('movie_count'),
            func.count(SearchedKino.id).label('search_count')
        ).join(
            Kino, Kino.media_id == MediaTuri.id
        ).outerjoin(
            SearchedKino, SearchedKino.kino_id == Kino.id
        ).group_by(
            MediaTuri.id
        )
        
        result = await session.execute(stmt)
        return [{
            "media_type": r.name,
            "movie_count": r.movie_count,
            "search_count": r.search_count
        } for r in result]
        

    
    