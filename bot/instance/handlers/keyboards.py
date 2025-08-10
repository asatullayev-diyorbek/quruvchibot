from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import BOT_USERNAME


async def start_group_inline():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔗 Guruhga qo‘shish",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )]
    ])
    return keyboard


async def join_channel_inline(title, username: str, chat_id):
    if username.startswith("@"):
        username = username[1:]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=title,
            url=f"https://t.me/{username}"
        )],
        [InlineKeyboardButton(
            text="✅ Ruxsat berish",
            callback_data=f"allow_{chat_id}"
        )],
    ])
    return keyboard


async def allow_message_inline(chat_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Ruxsat berish",
            callback_data=f"allow_{chat_id}"
        )],
    ])
    return keyboard


async def advertisement_target_keyboard(from_chat_id, from_message_id):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Guruhlarga", callback_data=f"ad_target_groups_{from_chat_id}__{from_message_id}")],
        [InlineKeyboardButton(text="👤 Userlarga", callback_data=f"ad_target_users_{from_chat_id}__{from_message_id}")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="ad_cancel")]
    ])
    return kb