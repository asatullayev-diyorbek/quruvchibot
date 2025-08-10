import re

from aiogram import Bot
from asgiref.sync import sync_to_async
from aiogram.types import Message

from bot.instance.handlers.keyboards import join_channel_inline, advertisement_target_keyboard, allow_message_inline
from bot.instance.handlers.utils import delete_message
from bot.models import TgGroup, GroupAdmin, BlockedWord, ChannelMember, TgInviterUser, TgUser

# URL aniqlash uchun regex
URL_PATTERN = re.compile(
    r"(https?://\S+|t\.me/\S+|[\w-]+\.[a-z]{2,}|@\w+)",
    re.IGNORECASE
)


@sync_to_async
def is_group_admin(chat_id: int, user_id: int) -> bool:
    return GroupAdmin.objects.filter(
        tg_group__chat_id=chat_id,
        user_chat_id=user_id
    ).exists()


@sync_to_async
def is_bot_admin(chat_id: int) -> bool:
    return TgUser.objects.filter(
        chat_id=chat_id,
        is_admin=True
    ).exists()


@sync_to_async
def get_blocked_words() -> list:
    return list(BlockedWord.objects.values_list("word", flat=True))


async def check_required_channel_membership(user_id: int, group_id: int) -> bool:
    """
    Guruh talab qilgan kanalga foydalanuvchi a'zo bo'lganini tekshiradi.
    """
    group = await sync_to_async(TgGroup.objects.filter(chat_id=group_id).first)()
    if not group or not group.required_channel:
        print("Majburiy kanal yo'q")
        return True  # Kanal talabi yo'q

    # Yoki ChannelMember modelidan tekshirish
    exists = await sync_to_async(ChannelMember.objects.filter(
        channel_id=group.required_channel,
        user_chat_id=user_id
    ).exists)()
    print(f"Kanalda bormi? {exists}")

    inviter = await sync_to_async(TgInviterUser.objects.filter(
        tg_group=group,
        inviter_chat_id=user_id
    ).first)()

    if not inviter:
        return False
    return exists or inviter.is_allow


async def check_group_invite_count(user_id: int, group_id: int) -> bool:
    """
    Guruhdagi foydalanuvchi talab qilingan odam sonini qo‘shganini tekshiradi.
    """
    group = await sync_to_async(TgGroup.objects.filter(chat_id=group_id).first)()
    if group is None:
        return True  # Guruh bazada yo'q bo'lsa cheklov qo‘llanmaydi

    if group.invite_count is None or group.invite_count <= 0:
        return True  # Talab yo‘q

    inviter = await sync_to_async(TgInviterUser.objects.filter(
        tg_group=group,
        inviter_chat_id=user_id
    ).first)()
    if not inviter:
        return False

    return inviter.invite_count >= group.invite_count or inviter.is_allow


async def group_message_filter(message: Message, bot: Bot):
    """Guruh xabarlarini filtrlaydi."""
    if message.chat.type == 'private' and await is_bot_admin(message.from_user.id):
        # Forward qilingan xabarni tekshiramiz
        if message.forward_from_chat and message.forward_from_message_id:
            # Forward qilingan joy ma'lumotlari
            from_chat_id = message.chat.id
            from_message_id = message.message_id

            await message.answer(
                text=f"From chat id: {from_chat_id}\nXabar id: {from_message_id}\n\nKimlarga yuborilsin?",
                reply_markup=await advertisement_target_keyboard(from_chat_id, from_message_id)
            )
            # Keyinchalik reklama uchun saqlash
            print(f"Forward xabar: from_chat_id={from_chat_id}, from_message_id={from_message_id}")

        return

    # 1. 📥 Kanal xabarini avtomatik forward qilinsa — log yozish
    if message.is_automatic_forward:
        print("Kanaldan keldi")
        return

    # Faqat guruh/superguruh
    if message.chat.type not in ["group", "supergroup"]:
        print("Guruhdan kelmadi")
        return

    # Admin bo'lsa cheklov ishlamaydi
    if await is_group_admin(message.chat.id, message.from_user.id):
        print("Admin uchun ishlamaydi")
        return

    if message.sender_chat and message.chat:
        same_sender = (
                message.sender_chat.id == message.chat.id and
                message.sender_chat.type == message.chat.type and
                message.sender_chat.title == message.chat.title
        )
        if same_sender:
            print("Guruh nomidan yozdi")
            return

    # 1️⃣ Kanal a'zoligini tekshirish
    if not await check_required_channel_membership(message.from_user.id, message.chat.id):
        await delete_message(message, bot)
        group = await sync_to_async(TgGroup.objects.filter(chat_id=message.chat.id).first)()
        await message.answer(
            f"⚠️ <a href=\"tg://user?id={message.from_user.id}\">{message.from_user.full_name}</a>, "
            f"guruhda yozishdan oldin talab qilingan kanalga a‘zo bo‘lishingiz kerak.\n\n"
            f"Agar allaqachon kanalga a‘zo bo‘lsangiz, lekin guruhda yozolmayotgan bo‘lsangiz, kanaldan chiqib qaytadan a‘zo bo‘ling.",
            parse_mode="HTML",
            reply_markup=await join_channel_inline(group.required_channel_title, group.required_channel_username, message.from_user.id)
        )
        return

    # 2️⃣ Majburiy odam qo‘shish talabini tekshirish
    if not await check_group_invite_count(message.from_user.id, message.chat.id):
        group = await sync_to_async(TgGroup.objects.filter(chat_id=message.chat.id).first)()
        again_count = group.invite_count
        inviter = await sync_to_async(TgInviterUser.objects.filter(
            tg_group=group,
            inviter_chat_id=message.from_user.id
        ).first)()
        if inviter:
            again_count -= inviter.invite_count

        await delete_message(message, bot)
        await message.answer(
            f"⚠️ <a href=\"tg://user?id={message.from_user.id}\">{message.from_user.full_name}</a>, "
            f"guruhga yozishdan oldin kamida <b>{group.invite_count}</b> ta odam qo‘shishingiz kerak.\n"
            f"Siz yana {again_count} ta odam qo'shishingiz kerak",
            parse_mode="HTML",
            reply_markup=await allow_message_inline(message.from_user.id)
        )
        return

    # 1. So'zlarni o'chirish
    blocked_words = await get_blocked_words()
    text = message.text or message.caption or ""
    for word in blocked_words:
        if word.lower() in text.lower():
            await delete_message(message, bot)
            print("Bloklangan so'z ishlatdi")
            return

    # 2. Faylni o'chirish
    if any([message.document, message.video, message.audio, message.voice, message.photo]):
        await delete_message(message, bot)
        print("Fayl yubordi")
        return

    # 3. Kirdi-chiqtini o'chirish
    if message.new_chat_members or message.left_chat_member:
        await delete_message(message, bot)
        print("Kirdi-chiqdi edi")
        return

    # 4. Ssilkani o'chirish
    if URL_PATTERN.search(text):
        await delete_message(message, bot)
        print("Ssilka ishlatdi")
        return