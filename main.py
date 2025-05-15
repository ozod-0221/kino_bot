from aiogram import Bot, Dispatcher,F
from aiogram.types import Message, CallbackQuery
import os
import logging
from datetime import datetime
import asyncio
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import *
from aiogram.filters import Command,CommandStart
from database.db import async_session, init_db
from database.db_utils import *
from aiogram.methods.get_chat_member_count import GetChatMemberCount
from pytz import timezone
import pytz
from func import *
from  config import *

admin_filter = F.from_user.id.in_([5361589149])


class KinoCode(StatesGroup):
    waiting_for_language = State()
    waiting_for_message = State()
    waiting_for_subscription = State()
class AddKino(StatesGroup):
    waiting_for_code = State()
    waiting_for_name = State()
    waiting_for_type_media = State()
    waiting_for_type_janr = State()
    waiting_for_language = State()
    waiting_for_post_link = State()
    waiting_for_confirmation = State()
class AddChannel(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_channel_url = State()
    waiting_for_confirmation = State()
class AddJanr(StatesGroup):
    waiting_for_janr_name = State()
    
class AddMediaType(StatesGroup):
    waiting_for_media_type = State()

    
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    if message.from_user.username:
        user_name = message.from_user.username
    else:
        user_name = "No username"
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
  
        
        
    
    if user_id == ADMIN_ID:
        
        await message.answer("Salom admin!", reply_markup=key_admin())
    else:
        if  not await is_user_exists(user_id):
            await message.answer("Tilni tanlang:\nВыберите язык\nChoose your language", reply_markup=key_language())
            await state.set_state(KinoCode.waiting_for_language)
            await state.update_data(user_id=user_id, user_name=user_name, first_name=first_name, last_name=last_name)
        else:
            await state.set_state(KinoCode.waiting_for_message)
            await message.answer("Menga kodni yuboring:\n\nОтправь мне код:\n\nSend me the code:")
        
@dp.callback_query(KinoCode.waiting_for_language)
async def handle_language(callback_query: CallbackQuery, state: FSMContext):
    language = callback_query.data
    
    await state.set_state(KinoCode.waiting_for_message)
    user_data= await state.get_data()
    user_id= user_data.get("user_id")
    user_name= user_data.get("user_name")
    first_name=user_data.get("first_name") 
    last_name= user_data.get("last_name")
    try:
        await add_user(user_id=user_id, username=user_name, first_name=first_name, last_name=last_name,language=language)
    except Exception as e:
        print("Error adding user:", str(e))
    
    await callback_query.answer()
    await callback_query.message.answer("Menga kodni yuboring:\n\nОтправь мне код:\n\nSend me the code:")
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    
    
    
        
    
@dp.message(KinoCode.waiting_for_message)
async def handle_message(message: Message, state: FSMContext):
    code = message.text
    await state.update_data(code=code)
    
    await state.set_state(KinoCode.waiting_for_subscription)
    await message.answer("Отлично! Теперь подпишитесь на каналы:\n\nJuda ham zo`r! Endi kanallarga obuna bo'ling:",reply_markup=await key_subscribe())

async def check_subscription(channel_id,user_id:int,bot:Bot) -> bool:
    try:
        user = await bot.get_chat_member(channel_id, user_id)
        if user.status in ["member", "administrator", "creator"]:
            return True
    except Exception as e:
        logging.error(f"Error checking subscription: {e}")
    return False 

@dp.callback_query(KinoCode.waiting_for_subscription)
async def handle_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data == "check_subscription":
        user_id = callback.from_user.id
        user_data = await state.get_data()
        code = user_data.get("code")
        try:
            channels = await get_all_channels()
            for i,ch in enumerate(channels, start=1):
                 if not await check_subscription(ch.telegram_id, user_id, bot):  # ✅ Endi to‘g‘ri
                        await bot.send_message(user_id, f"❌ Siz {i} kanaliga obuna emassiz!")
                        return
                 else:
                    await bot.send_message(user_id, f"✅ Siz {i} kanaliga obuna bo`lgansiz!")
                     
            await bot.send_message(user_id, f"Siz kanallarga obuna bo`lgansiz!\n\nKod: {code}")
            await state.clear()
            kino = await get_kino_by_code(code)
            kino_id=kino.id
            lang=kino.language
            janrlar = await get_janrlar_by_kino_id(kino_id)
            media_id=kino.media_id
            media_name=await get_media_name_by_id(media_id)
            janr_matni = " | ".join(janrlar).title()

            janr_matni = "\n• " + "\n• ".join(janrlar)
            
            
            
            
            
            
            if kino:
                text = (
        f"🎬 <b>Media turi:</b> {media_name}\n"
        f"🎬 <b>Nom:</b> {kino.name}\n"
        f"🆔 <b>Kod:</b> {kino.code}\n"
        f"🌐 <b>Til:</b> {lang}\n"
        f"📝 <b>Janr:</b> {janr_matni}\n"
        f"🔗 <b>Post havolasi:</b> <a href='{kino.post_link}'>Ko‘rish</a>"
        
    )
                try:
                    print(text)
                except Exception as e:
                    logging.error(f"Error formatting message: {e}")
                await bot.send_message(user_id, text, parse_mode="HTML")
                kino_id=kino.id
                try:
                    await add_searched_kino(user_id=user_id,kino_id=kino_id)
                except Exception as e:
                    logging.error(f"searched channel error: {e}")
                
            else:
                await bot.send_message(user_id, "❌ Bunday kodga ega kino topilmadi.")

            
        except Exception as e:
            logging.error(f"Error checking subscription: {e}")
            await state.clear()
@dp.message(admin_filter,F.text=="Yangi kino qo'shish")
async def add_kino_handler(message: Message,state: FSMContext):
    await message.answer("Yangi kino qo'shish uchun kodni yuboring:")
    await state.set_state(AddKino.waiting_for_code)
@dp.message(AddKino.waiting_for_code)
async def handle_code(message: Message, state: FSMContext):
    code = message.text
    kino=await get_kino_by_code(code)
    if kino:
        await message.answer("Bunday kodli kino mavjud!")
        return
    else:
        await state.update_data(newcode=code)
        await state.set_state(AddKino.waiting_for_language)
        await message.answer("Yangi kino  tilini tanlang:", reply_markup=await key_lang_kino())
@dp.callback_query(AddKino.waiting_for_language)
async def handle_language_selection_for_kino(callback_query: CallbackQuery, state: FSMContext):
    language = callback_query.data
    await state.update_data(newlang=language)
    await state.set_state(AddKino.waiting_for_name)
    await callback_query.answer("Til saqlandi!")
    await callback_query.message.answer("Yangi kino nomini kiriting:")
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
@dp.message(AddKino.waiting_for_name)
async def handle_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(newname=name)
    await state.update_data(customs=[])  # ← mana shunaqa
    await state.set_state(AddKino.waiting_for_type_janr)
    await message.answer("Janrlarni tanlang :", reply_markup=await custom_keyboard_janr())

@dp.callback_query(AddKino.waiting_for_type_janr, F.data.startswith("customjanr_"))
async def handle_custom_selection(
    callback_query: CallbackQuery,
    bot: Bot,
    state: FSMContext
):
    try:
        
        data = await state.get_data()
        customs = data.get("customs", [])
        callback_data = callback_query.data.split("_")[-1]
        
        # Toggle selection
        if callback_data in customs:
            customs.remove(callback_data)
        else:
            customs.append(callback_data)
        
        await state.update_data({"customs": customs})
        
        selected_text = "\n".join([f"✅ {item}" for item in customs])
        text = "Janrlarini  tanlang:\n\nTanlanganlar:\n" + (selected_text if customs else "Hech narsa tanlanmadi")
        
        await callback_query.answer(f"Siz {callback_data} tanladingiz")
        
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=text,
            reply_markup=await custom_keyboard_janr(customs=customs)
        )
        
    except Exception as e:
        print("Error:", e)
        await callback_query.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
@dp.callback_query(AddKino.waiting_for_type_janr, F.data== "send_janr")
async def handle_send_button(
    callback_query: CallbackQuery,
    bot: Bot,
    state: FSMContext
):
    try:
        data = await state.get_data()
        customs = data.get("customs", [])
        
        if not customs:
            await callback_query.answer("Hech qanday maydon tanlanmadi!", show_alert=True)
            return
        await state.set_state(AddKino.waiting_for_type_media)
        await callback_query.answer("Janrlar saqlandi!")
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message(callback_query.message.chat.id, "Media turini tanlang:", reply_markup=await custom_keyboard_media())
        
    except Exception as e:
        print("Error:", e)
        await callback_query.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

        
@dp.callback_query(AddKino.waiting_for_type_media, F.data.startswith("custommedia_"))
async def handle_custom_media(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    
        media_data=callback_query.data.split("_")[1]
        await state.update_data(newmedia_turi=media_data)
        await state.set_state(AddKino.waiting_for_post_link)
        await callback_query.answer("Media turi saqlandi!")
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message(callback_query.message.chat.id, "Post havolasi kiriting:")
@dp.message(AddKino.waiting_for_post_link)
async def handle_post_link(message: Message, state: FSMContext):
    post_link = message.text
    await state.update_data(newpost_link=post_link)
    kino_data = await state.get_data()
    newcode = kino_data.get("newcode")
    newname = kino_data.get("newname")
    lang=kino_data.get("newlang")
    janrlar = kino_data.get("customs", [])
    newpost_link = kino_data.get("newpost_link")
    media=kino_data.get("newmedia_turi")
    janr_matni = " | ".join(janrlar).title()
# yoki
    janr_matni = "\n• " + "\n• ".join(janrlar)
    await message.answer(
    f"Yangi Media ma'lumotlari:\n\n"
    f"Kod: {newcode}\n"
    f"Til: {lang}\n"
    f"Nom: {newname}\n"
    f"Media turi: {media}\n"
    f"Janrlar: {janr_matni}\n"
    f"Post havolasi: {newpost_link}\n\n"
    "Tasdiqlaysizmi?",
    reply_markup=key_yes_no()
)

    await state.set_state(AddKino.waiting_for_confirmation)
@dp.message(AddKino.waiting_for_confirmation)
async def handle_confirmation(message: Message, state: FSMContext):
    if message.text == "Tasdiqlash":
        kino_data = await state.get_data()
        newcode = kino_data.get("newcode")
        newname = kino_data.get("newname")
        janrlar = kino_data.get("customs", [])
        lang=kino_data.get("newlang")
        newpost_link = kino_data.get("newpost_link")
        media=kino_data.get("newmedia_turi")
        try:
            await add_kino(code=newcode, name=newname, janrlar=janrlar, post_link=newpost_link, media=media,language=lang)
            await message.answer("Yangi kino qo'shildi!",reply_markup=key_admin())
            text = f"<code>Kino haqida bizning botimiz orqali bilib olishingiz mumkin ❗\n🔢 Kino kodi: {newcode} 📥\nBot manzili profilda yoki telegram orqali ushbu @get_kinoBot username orqali izlab topishingiz mumkin\n\nУзнайте больше о фильме через нашего бота ❗\n🔢 Код фильма: {newcode} 📥\nСсылку на бота можно найти в профиле или найти по имени пользователя в Telegram: @get_kinoBot</code>"


            await bot.send_message(message.chat.id, text, parse_mode="HTML")
            await state.clear()
        except Exception as e:
            await message.answer(f"kino qo`shishda Xatolik yuz berdi: {e}",reply_markup=key_admin())
            
        
    else:
        
        await message.answer("Yangi kino qo'shish bekor qilindi.",reply_markup=key_admin())
        await state.clear()
        
@dp.message(admin_filter,F.text=="Kanal qo'shish")
async def add_channel_handler(message: Message,state: FSMContext):
    await message.answer("Kanal qo'shish uchun kanal id sini yuboring:")
    await state.set_state(AddChannel.waiting_for_channel_id)
@dp.message(AddChannel.waiting_for_channel_id)
async def handle_channel_id(message: Message, state: FSMContext):
    channel_id = message.text
    await state.update_data(channel_id=channel_id)
    await state.set_state(AddChannel.waiting_for_channel_url)
    await message.answer("Kanal qo'shish uchun kanal urlini yuboring:")
@dp.message(AddChannel.waiting_for_channel_url)
async def handle_channel_url(message: Message, state: FSMContext):
    url = message.text
    await state.update_data(url=url)
    channel_data = await state.get_data()
    url_for_admin = f"{channel_data.get('url')}"
    channel_id=channel_data.get("channel_id")
    await state.set_state(AddChannel.waiting_for_confirmation)
    quote = (
    "Kanalga admin qilish uchun quyidagilarni bajaring:\n"
    "1. Kanalni oching\n"
    "2. Yuqoridagi ‘qalamcha’ga bosing\n"
    "3. ‘Administratorlar’ bo‘limiga kiring\n"
    "4. ‘Administrator qo‘shish’ tugmasini bosing\n"
    "5. Meni yoki @get_kinoBot ni tanlang\n"
    "6. Barcha ruxsatlarni belgilang va saqlang ✅"
)

    await message.answer(f"Kanal ma'lumotlari:\n\nKanal id: {channel_data.get('channel_id')}\nKanal url: {channel_data.get('url')}\n\n<blockquote>{quote}</blockquote>\n",parse_mode="HTML", reply_markup=key_confirm_channel(channel_id,url_for_admin))
@dp.callback_query(AddChannel.waiting_for_confirmation)
async def handle_confirm_channel(callback_query: CallbackQuery,state: FSMContext,bot: Bot):
    channel_data = await state.get_data()
    channel_id = (channel_data.get("channel_id"))
    url= channel_data.get("url")
    if await is_bot_admin(channel_id,bot):
        await callback_query.answer("Bot adminligi tekshirildi!")
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        channel_name = await get_channel_name(bot,channel_id)
        count_of_members = await get_channel_followers_count(bot,channel_id)
        
        
        try:
            await add_channel(channel_id=channel_id,url=url,name=channel_name,count=count_of_members)
        except Exception as e:
            logging.error(f"❌ Kanal qo'shishda xato: {e}")
        await bot.send_message(callback_query.from_user.id, "Kanal qo'shildi!",reply_markup=key_admin())
        await state.clear()
    else:
        await callback_query.answer("Bot adminligi tekshirilmadi!")
        await callback_query.message.edit_text("Bot adminligi tekshirilmadi!",reply_markup=key_admin())
        await state.clear()
    
async def is_bot_admin(channel_id: any, bot: Bot) -> bool:
    try:
        bot_user = await bot.get_me()
        member = await bot.get_chat_member(chat_id=channel_id, user_id=bot_user.id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        logging.error(f"❌ Botni adminligi tekshiruvida xato: {e}")
        return False
@dp.callback_query(admin_filter,F.text=="channel_stats")  
async  def channel_handler_callback(callback_query: CallbackQuery,state: FSMContext):
    await state.clear()
    await callback_query.message.answer("Kanallar ro'yxati:",reply_markup=await key_channels())
@dp.message(admin_filter,F.text=="Kanallar")
async def channels_handler(message: Message,state: FSMContext):
    await state.clear()
    await message.answer("Kanallar ro'yxati:",reply_markup=await key_channels())
def get_user_joined_date(joined_at_utc: datetime) -> datetime:
    tashkent = timezone('Asia/Tashkent')
    joined_at_utc = joined_at_utc.replace(tzinfo=pytz.utc).astimezone(tashkent)
    return joined_at_utc
        
        
    
            
    
    joined_tashkent = joined_at_utc.astimezone(tashkent)
    return joined_tashkent  # formatlash ixtiyoriy
@dp.callback_query(F.data.startswith("channel_"))
async def channel_callback(callback_query: CallbackQuery,bot: Bot):
    
    channel_id = callback_query.data.split("_")[1]
    channel_name = await get_channel_name(bot,channel_id)
    current_count_of_members = await get_channel_followers_count(bot,channel_id)
    channel_data= await get_channel_by_id(int(channel_id))
    joined_at=channel_data.bot_joined_at
    count_of_members_when_bot_joined =int(channel_data.count_of_members_when_bot_joined)
    
    url=channel_data.url
    current_time = datetime.utcnow()
    
    time_difference = current_time - joined_at
    days_difference = time_difference.days
    difference_of_members = current_count_of_members - count_of_members_when_bot_joined
    joined_at_formatted = get_user_joined_date(joined_at)
    joined_at_formatted=joined_at_formatted.strftime("%Y-%m-%d %H:%M:%S")
    
    text=(
        f"<b>📛Kanal nomi:</b> {channel_name}\n"
        f"<b>ℹ️Kanal ID:</b> {channel_id}\n"
        f"<b>🔗Kanal URL:</b> {url}\n"
        f"<b>👥Hozir kanal kuzatuvchilari soni :</b> {current_count_of_members}\n"
        f"<b>👥Bot kanalga qo'shilgan vaqtdagi kanal kuzatuvchilari soni:</b> {count_of_members_when_bot_joined}\n"
        f"<b>🔝Bot kanalga qo'shilgan vaqtdan hozirgacha kanal kuzatuvchilari soni o'zgarishi:</b> {difference_of_members}\n"
        f"<b>🕛Bot  kanalga qo'shilgan vaqti:</b> {joined_at_formatted}\n"
        f"<b>🌞🌚Bot kanalga qo'shilgan vaqtdan hozirgacha o'tgan vaqt:</b> {days_difference} kun"
    )
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await callback_query.message.answer(text,parse_mode="HTML",reply_markup=await settings_channel(channel_id))
    
@dp.callback_query(F.data.startswith("delete_channel_"))
async def delete_channel_callback(callback_query: CallbackQuery, state: FSMContext):
    channel_id = int(callback_query.data.split("_")[2])
    await delete_channel(channel_id)
    await callback_query.message.edit_text("Kanal o'chirildi!")
    await bot.send_message(callback_query.from_user.id, "Kanal o'chirildi!",reply_markup=key_admin())
    
@dp.callback_query(F.data=="BackToChannelList")
async def back_to_channel_list(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Kanallar ro'yxati:",reply_markup=await key_channels())
@dp.callback_query(F.data=="BackToAdminPanel")
async def back_to_admin_panel(callback_query: CallbackQuery, state: FSMContext,bot: Bot):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await callback_query.message.answer("Admin panel:",reply_markup=key_admin())
  

    
async def get_channel_name(bot: Bot, channel_id: str) -> str:
    """
    Kanal ID'si orqali kanal nomini olish
    :param bot: Aiogram bot obyekti
    :param channel_id: Kanal ID yoki kanal foydalanuvchi nomi
    :return: Kanal nomi
    """
    try:
        chat = await bot.get_chat(channel_id)
        return chat.title
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"
async def get_channel_followers_count(bot: Bot, channel_id: str) -> int:
    """
    Kanal ID'si orqali kanal kuzatuvchilari sonini olish
    :param bot: Aiogram bot obyekti
    :param channel_id: Kanal ID yoki kanal foydalanuvchi nomi
    :return: Kanal kuzatuvchilari soni
    """
    try:
        count = await bot.get_chat_member_count(channel_id)
        return count
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"   
@dp.message(admin_filter,F.text=="Janr qo`shish")
async def add_janr_handler(message: Message,state: FSMContext):
    await message.answer("Janr qo'shish uchun janr nomini yuboring:")
    await state.set_state(AddJanr.waiting_for_janr_name)
@dp.message(AddJanr.waiting_for_janr_name)
async def handle_janr_name(message: Message, state: FSMContext):
    janr_name = message.text
    await state.update_data(janr_name=janr_name)
    if await is_janr_exists(janr_name):
        await message.answer("Bunday janr mavjud!")
        return
    else:
        await add_janr(janr_name)
        await message.answer("Janr qo'shildi!",reply_markup=key_admin())
        await state.clear()
@dp.message(admin_filter,F.text=="Media turini qo'shish")
async def add_media_type_handler(message: Message,state: FSMContext):
    await message.answer("Media turini qo'shish uchun media turining nomini yuboring:")
    await state.set_state(AddMediaType.waiting_for_media_type)
@dp.message(AddMediaType.waiting_for_media_type)
async def handle_media_type_name(message: Message, state: FSMContext):
    media_type_name = message.text
    await state.update_data(media_type_name=media_type_name)
    if await is_media_turi_exists(media_type_name):
        await message.answer("Bunday media turi mavjud!")
        return
    else:
        await add_media_turi(media_type_name)
        await message.answer("Media turi qo'shildi!",reply_markup=key_admin())
        await state.clear()
@dp.message(admin_filter,F.text=="Statistika")
async def statistics_handler(message: Message,state: FSMContext):
    await message.answer("Statistika:",reply_markup=await key_stats())

@dp.callback_query(F.data=="kino_stats")
async def kino_stats_handler(callback_query: CallbackQuery,state: FSMContext,bot:Bot):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await callback_query.message.answer("Kinolar Statistikasi:")
    stats_movies= await get_most_searched_movies()
    stats_kino_text = format_movie_stats(stats_movies)
    
    
    await callback_query.message.answer(stats_kino_text)
@dp.callback_query(F.data=="janr_stats")
async def janr_stats_handler(callback_query: CallbackQuery,state: FSMContext):
    await callback_query.message.edit_text("Janrlar Statistikasi:")
    stats_janrs = await get_most_searched_genres()
    stats_janr_text = format_genre_stats(stats_janrs)
    await callback_query.message.answer(stats_janr_text)
@dp.callback_query(F.data=="general_stats")
async def genre_stats_handler(callback_query: CallbackQuery,state: FSMContext):
    await callback_query.message.edit_text("Umumiy Statistikalar:")
    general_stats = await get_general_stats()
    general_stats_text = format_general_stats(general_stats)
    await callback_query.message.answer(general_stats_text)
@dp.callback_query(F.data=="media_stats")
async def media_stats_handler(callback_query: CallbackQuery,state: FSMContext):
    await callback_query.message.edit_text("Media turi Statistikasi:")
    stats_media_turi = await get_media_type_stats()
    stats_media_turi_text = format_media_stats(stats_media_turi)
    await callback_query.message.answer(stats_media_turi_text,parse_mode="HTML")
    
    
async def main():
    
    
    await init_db()
    await dp.start_polling(bot)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')
    except Exception as e:
        print(e)


