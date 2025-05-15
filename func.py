def format_movie_stats(movies):
    """Kino statistikasini chiroyli formatga keltiradi"""
    if not movies:
        return "Hozircha hech qanday statistika mavjud emas"
    
    message = "🎬 Eng ko'p qidirilgan kinolar:\n\n"
    for i, movie in enumerate(movies, 1):
        message += f"{i}. {movie['name']} - {movie['count']} marta\n"
        message += f"   Kodi: {movie['code']}\n\n"
    return message
def format_genre_stats(genres):
    """Janr statistikasini chiroyli formatga keltiradi"""
    if not genres:
        return "Hozircha hech qanday janr statistikasi mavjud emas"
    
    message = "🏷️ Eng ko'p qidirilgan janrlar:\n\n"
    for i, genre in enumerate(genres, 1):
        message += f"{i}. {genre['genre']} - {genre['count']} marta\n"
    return message
def format_general_stats(stats):
    """Umumiy statistikani chiroyli formatga keltiradi"""
    message = (
        "📊 Umumiy statistika:\n\n"
        f"🎥 Filmlar soni: {stats['total_movies']}\n"
        f"🏷️ Janrlar soni: {stats['total_genres']}\n"
        f"👤 Foydalanuvchilar soni: {stats['total_users']}\n"
        f"🔍 Jami qidiruvlar: {stats['total_searches']}\n"
        f"📢 Kanallar soni: {stats['total_channels']}\n"
        f"⏳ So'nggi 24 soatdagi qidiruvlar: {stats['last_24h_searches']}"
    )
    return message
def format_media_stats(media_stats):
    """Media turlari bo'yicha statistikani chiroyli formatga keltiradi"""
    if not media_stats:
        return "📊 Hozircha media turlari bo'yicha statistika mavjud emas"
    
    message = "📊 Media turlari bo'yicha statistika:\n\n"
    
    for stat in media_stats:
        message += (
            f"📌 <b>{stat['media_type']}</b>\n"
            f"   🎥 Filmlar soni: {stat['movie_count']}\n"
            f"   🔍 Qidiruvlar soni: {stat['search_count']}\n\n"
        )
    
    # Umumiy hisobni qo'shamiz
    total_movies = sum(stat['movie_count'] for stat in media_stats)
    total_searches = sum(stat['search_count'] for stat in media_stats)
    
    message += (
        f"📈 <b>Umumiy:</b>\n"
        f"   🎥 Jami filmlar: {total_movies}\n"
        f"   🔍 Jami qidiruvlar: {total_searches}"
    )
    
    return message