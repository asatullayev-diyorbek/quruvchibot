import re
import datetime
from asgiref.sync import sync_to_async
from aiogram import Bot
from aiogram.types import Message, ChatPermissions

from bot.models import TgGroup, GroupAdmin, BlockedWord
from bot.instance.handlers.keyboards import start_group_inline


URL_PATTERN = re.compile(r"(https?://\S+|t\.me/\S+)", re.IGNORECASE)


@sync_to_async
def is_group_admin(chat_id: int, user_id: int) -> bool:
    return GroupAdmin.objects.filter(
        tg_group__chat_id=chat_id,
        user_chat_id=user_id
    ).exists()


@sync_to_async
def get_blocked_words() -> list:
    return list(BlockedWord.objects.values_list("word", flat=True))


async def handle_first_check(message: Message, bot: Bot):
    """
    Guruhdagi xabarlarni tekshiradi va kerak bo‘lsa o‘chiradi.
    Adminlar bundan mustasno.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Agar admin bo‘lsa cheklov ishlamasin
    if await is_group_admin(chat_id, user_id):
        return False

    # 1. Kirdi-chiqishni o‘chirish
    if message.left_chat_member or message.new_chat_members:
        await delete_message(message, bot)
        return True

    # 2. Avtomatik forward bloklash
    if message.is_automatic_forward:
        return True

    if message.sender_chat and message.chat:
        same_sender = (
                message.sender_chat.id == message.chat.id and
                message.sender_chat.type == message.chat.type and
                message.sender_chat.title == message.chat.title
        )
        if same_sender:
            return True

    # 3. Kanal nomidan yozish
    if message.sender_chat and message.sender_chat.type == "channel":
        await delete_message(message, bot)
        await message.answer(
            "❌ <b>Kanal</b> nomidan yozish mumkin emas!",
            parse_mode="HTML",
            reply_markup=await start_group_inline()
        )
        return True

    # 4. Fayl/media o‘chirish
    if any([message.document, message.video, message.audio, message.photo]):
        await delete_message(message, bot)
        return True

    # 5. Bloklangan so‘zlar
    blocked_words = await get_blocked_words()
    text = (message.text or message.caption or "").lower()
    for word in blocked_words:
        if word.lower() in text:
            await delete_message(message, bot)
            await restrict_user(chat_id, user_id, bot)
            return True

    # 6. Ssilkani o‘chirish
    if URL_PATTERN.search(text):
        await delete_message(message, bot)
        return True

    return False


async def delete_message(message: Message, bot: Bot):
    """Xabarni xavfsiz o‘chiradi."""
    try:
        await bot.delete_message(message.chat.id, message.message_id)
        print(f"✅ Xabar o‘chirildi: {message.chat.id} - {message.message_id}")
    except Exception as e:
        print(f"⚠️ Xabarni o‘chirishda xato: {e}")


async def restrict_user(group_chat_id, user_chat_id, bot):
    """Foydalanuvchini 1 daqiqa yozishdan cheklaydi."""
    try:
        until_date = datetime.datetime.now() + datetime.timedelta(minutes=1)
        await bot.restrict_chat_member(
            chat_id=group_chat_id,
            user_id=user_chat_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_invite_users=True
            ),
            until_date=until_date
        )
        print(f"⛔ {user_chat_id} foydalanuvchi 1 daqiqa cheklangan")
    except Exception as e:
        print(f"⚠️ Foydalanuvchini cheklashda xato: {e}")
