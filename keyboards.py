from typing import List, Optional, Tuple
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.db_utils import *

# Constants for callback data
CALLBACK_PREFIXES = {
    'LANGUAGE': 'lang',
    'CHANNEL': 'channel',
    'JANR': 'customjanr',
    'MEDIA': 'custommedia',
    'STATS': {
        'KINO': 'kino_stats',
        'CHANNEL': 'channel_stats',
        'MEDIA': 'media_stats',
        'JANR': 'janr_stats',
        'LANG': 'lang_stats',
        'TIME': 'time_stats',
        'GENERAL': 'general_stats'
    }
}

# Constants for button texts
BUTTON_TEXTS = {
    'BACK': 'Ortga',
    'HOME': '🏠Bosh sahifaga',
    'CANCEL': '❌Bekor qilish',
    'SEND': '📩Yuborish',
    'CHECK': 'Tekshirish'
}

def key_language() -> InlineKeyboardMarkup:
    """
    Creates a language selection keyboard with Uzbek, Russian, and English options.
    
    Returns:
        InlineKeyboardMarkup: The language selection keyboard
    """
    key = InlineKeyboardBuilder()
    key.add(InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="uz"))
    key.add(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ru"))
    key.add(InlineKeyboardButton(text="🇺🇸 English", callback_data="en"))
    key.adjust(1)
    return key.as_markup()

async def key_subscribe() -> InlineKeyboardMarkup:
    """
    Creates a subscription keyboard with channel links and a check button.
    
    Returns:
        InlineKeyboardMarkup: The subscription keyboard
    """
    keyboard = InlineKeyboardBuilder()
    try:
        channels = await get_all_channels()
        for i, channel in enumerate(channels, start=1):
            keyboard.add(InlineKeyboardButton(text=f"{i}-Kanal", url=channel.url))
        
        keyboard.add(InlineKeyboardButton(text=BUTTON_TEXTS['CHECK'], callback_data="check_subscription"))
        keyboard.adjust(1)
        return keyboard.as_markup()
    except Exception as e:
        # Log the error here
        raise Exception(f"Failed to create subscription keyboard: {str(e)}")

def key_admin() -> ReplyKeyboardMarkup:
    """
    Creates the admin panel keyboard with various management options.
    
    Returns:
        ReplyKeyboardMarkup: The admin panel keyboard
    """
    keyboard = ReplyKeyboardBuilder()
    buttons = [
        "Kanal qo'shish",
        "Kanallar",
        "Yangi kino qo'shish",
        "Statistika",
        "Janr qo`shish",
        "Media turini qo'shish"
    ]
    for button in buttons:
        keyboard.add(KeyboardButton(text=button))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)

def key_yes_no() -> ReplyKeyboardMarkup:
    """
    Creates a yes/no confirmation keyboard.
    
    Returns:
        ReplyKeyboardMarkup: The confirmation keyboard
    """
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="Tasdiqlash"))
    keyboard.add(KeyboardButton(text="Bekor qilish"))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)

def key_confirm_channel(channel_id: int, url: str) -> InlineKeyboardMarkup:
    """
    Creates a keyboard for channel confirmation with a link and check button.
    
    Args:
        channel_id (int): The Telegram channel ID
        url (str): The channel URL
        
    Returns:
        InlineKeyboardMarkup: The channel confirmation keyboard
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Kanalga o`tish", url=url))
    keyboard.add(InlineKeyboardButton(text=BUTTON_TEXTS['CHECK'], callback_data=f"check_channel_{channel_id}"))
    keyboard.adjust(1)
    return keyboard.as_markup()

async def key_channels() -> InlineKeyboardMarkup:
    """
    Creates a keyboard listing all channels with a back button.
    
    Returns:
        InlineKeyboardMarkup: The channels list keyboard
    """
    keyboard = InlineKeyboardBuilder()
    try:
        channels = await get_all_channels()
        for channel in channels:
            keyboard.add(InlineKeyboardButton(text=channel.name, callback_data=f"channel_{channel.telegram_id}"))
        keyboard.add(InlineKeyboardButton(text=BUTTON_TEXTS['BACK'], callback_data="BackToAdminPanel"))
        keyboard.adjust(1)
        return keyboard.as_markup()
    except Exception as e:
        raise Exception(f"Failed to create channels keyboard: {str(e)}")

async def settings_channel(channel_id: int) -> InlineKeyboardMarkup:
    """
    Creates a keyboard for channel settings with delete and back options.
    
    Args:
        channel_id (int): The Telegram channel ID
        
    Returns:
        InlineKeyboardMarkup: The channel settings keyboard
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="O'chirish", callback_data=f"delete_channel_{channel_id}"))
    keyboard.add(InlineKeyboardButton(text=BUTTON_TEXTS['BACK'], callback_data="BackToChannelList"))
    keyboard.adjust(1)
    return keyboard.as_markup()

async def key_stats() -> InlineKeyboardMarkup:
    """
    Creates a keyboard for accessing various statistics with a back button.
    
    Returns:
        InlineKeyboardMarkup: The statistics menu keyboard
    """
    keyboard = InlineKeyboardBuilder()
    
    stats_buttons = [
        ("Kinolar statistikasi", CALLBACK_PREFIXES['STATS']['KINO']),
        ("Kanallar statistikasi", CALLBACK_PREFIXES['STATS']['CHANNEL']),
        ("Media statistikasi", CALLBACK_PREFIXES['STATS']['MEDIA']),
        ("Janrlar statistikasi", CALLBACK_PREFIXES['STATS']['JANR']),
        ("Til statistikasi", CALLBACK_PREFIXES['STATS']['LANG']),
        ("Vaqt statistikasi", CALLBACK_PREFIXES['STATS']['TIME']),
        ("Umumiy statistikalar", CALLBACK_PREFIXES['STATS']['GENERAL'])
    ]
    
    for text, callback_data in stats_buttons:
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    
    keyboard.add(InlineKeyboardButton(text=BUTTON_TEXTS['BACK'], callback_data="BackToAdminPanel"))
    keyboard.adjust(1)
    return keyboard.as_markup()

async def custom_keyboard_janr(custom: Optional[str] = None, customs: Optional[List[str]] = None) -> InlineKeyboardMarkup:
    """
    Creates a custom keyboard for genre selection with checkmarks for selected items.
    
    Args:
        custom (Optional[str]): A single custom genre to add
        customs (Optional[List[str]]): List of selected genres
        
    Returns:
        InlineKeyboardMarkup: The genre selection keyboard
    """
    if customs is None:
        customs = []
    
    if custom and custom not in customs:
        customs.append(custom)
    
    keyboard = InlineKeyboardBuilder()
    
    try:
        buttons = await get_janr_buttons()
        
        # Add buttons with checkmarks for selected items
        for text, callback_data in buttons:
            if callback_data.split("_")[-1] in customs:
                text = "✅ " + text
            keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        
        # Add action buttons
        keyboard.add(
            InlineKeyboardButton(text=BUTTON_TEXTS['CANCEL'], callback_data="janr_cancel"),
            InlineKeyboardButton(text=BUTTON_TEXTS['HOME'], callback_data="BackToAdminPanel"),
            InlineKeyboardButton(text=BUTTON_TEXTS['SEND'], callback_data="send_janr")
        )
        
        keyboard.adjust(len(buttons)%3, 3)
        return keyboard.as_markup()
    except Exception as e:
        # Log the error here
        raise Exception(f"Failed to create genre keyboard: {str(e)}")

async def custom_keyboard_media() -> InlineKeyboardMarkup:
    """
    Creates a keyboard for media type selection.
    
    Returns:
        InlineKeyboardMarkup: The media type selection keyboard
        
    Raises:
        Exception: If no media types are found in the database
    """
    try:
        media_buttons = await get_media_turi_buttons()
        if not media_buttons:
            raise Exception("❌ Media turlari topilmadi! Bazani tekshiring yoki avval media turlarini kiriting.")

        builder = InlineKeyboardBuilder()
        for title, callback_data in media_buttons:
            builder.button(text=title, callback_data=callback_data)

        builder.adjust(2)
        return builder.as_markup()
    except Exception as e:
        raise Exception(f"Failed to create media keyboard: {str(e)}")

async def key_janrs() -> InlineKeyboardMarkup:
    """
    Creates a keyboard for genre management with download, delete, and navigation options.
    
    Returns:
        InlineKeyboardMarkup: The genre management keyboard
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Yuklash", callback_data="get_excel_janr"))
    keyboard.add(InlineKeyboardButton(text="Janrni olib tashlash", callback_data="delete_janr"))
    keyboard.add(InlineKeyboardButton(text=BUTTON_TEXTS['BACK'], callback_data="BackToStats"))
    keyboard.add(InlineKeyboardButton(text=BUTTON_TEXTS['HOME'], callback_data="BackToAdminPanel"))
    keyboard.adjust(2)
    return keyboard.as_markup()

async def copy_text_button(text: str) -> InlineKeyboardMarkup:
    """
    Creates a keyboard with a copy text button.
    
    Args:
        text (str): The text to be copied
        
    Returns:
        InlineKeyboardMarkup: The copy text keyboard
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Nusxalash", callback_data="copy_text", url=f"tg://msg_text?{text}")]
        ]
    )

async def key_lang_kino() -> InlineKeyboardMarkup:
    """
    Creates a keyboard for movie language selection.
    
    Returns:
        InlineKeyboardMarkup: The language selection keyboard
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="O'zbekcha", callback_data="uz"))
    keyboard.add(InlineKeyboardButton(text="Русский", callback_data="ru"))
    keyboard.adjust(1)
    return keyboard.as_markup()

async def key_stats_for_kino() -> InlineKeyboardMarkup:
    """
    Creates a keyboard for movie-specific statistics.
    
    Returns:
        InlineKeyboardMarkup: The movie statistics keyboard
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Kinolar statistikasi", callback_data=CALLBACK_PREFIXES['STATS']['KINO']))
    keyboard.add(InlineKeyboardButton(text="Kanallar statistikasi", callback_data=CALLBACK_PREFIXES['STATS']['CHANNEL']))
    keyboard.add(InlineKeyboardButton(text="Media statistikasi", callback_data=CALLBACK_PREFIXES['STATS']['MEDIA']))
    keyboard.adjust(1)
    return keyboard.as_markup()
