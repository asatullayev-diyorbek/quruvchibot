from aiogram.exceptions import TelegramBadRequest
from asgiref.sync import sync_to_async
from aiogram.types import Message
from aiogram import Bot

from bot.models import TgUser, TgGroup, GroupAdmin
from .keyboards import start_group_inline
from .utils import delete_message


@sync_to_async
def is_group_admin(chat_id: int, user_id: int) -> bool:
    return GroupAdmin.objects.filter(
        tg_group__chat_id=chat_id,
        user_chat_id=user_id
    ).exists()


START_TEXT = """
Salom👋
Men ozbekcha va arabcha reklamalarni, ssilkalani va har xil nomaqbul so'zlarni guruhlardan ochirib beraman✅

Bundan tashqari juda ko'p foydali hislatlarim bor. Buni amalda ko'rasiz😉

Man ishlashim uchun guruhizga qoshib admin berishiz kerak😄
"""


async def handle_start(message: Message, bot: Bot) -> None:
    # Private chat bo'lsa, foydalanuvchini bazaga yozamiz
    if message.chat.type == "private":
        await sync_to_async(TgUser.objects.get_or_create)(
            chat_id=message.from_user.id,
            defaults={"full_name": message.from_user.full_name}
        )

    # Start matni va tugmalarni yuborish
    await message.answer(
        START_TEXT,
        reply_markup=await start_group_inline()
    )


HELP_TEXT = """
𝐆𝐔𝐑𝐔𝐇𝐆𝐀 𝐌𝐀𝐉𝐁𝐔𝐑𝐈𝐘 𝐎𝐃𝐀𝐌 𝐐𝐎'𝐒𝐇𝐓𝐈𝐑𝐈𝐒𝐇 Odam qo'shmasa yozdirmaydi

/majbur 10 - Majburiy odam qo'shish funksiyasi. ⚠️10 bu istalgan sonni belgilash
/majburoff - O'chirish.
/ruxsat - Ответить qilib yoki @ orqali belgilangan guruh a'zosiga yozishga ruxsat berish.


𝐆𝐔𝐑𝐔𝐇𝐃𝐀𝐆𝐈𝐋𝐀𝐑𝐍𝐈 𝐊𝐀𝐍𝐀𝐋𝐆𝐀 𝐀'𝐙𝐎 𝐐𝐈𝐋𝐃𝐈𝐑𝐈𝐒𝐇
/kanal @username - Guruhda a'zo bo'lish shart bo'lgan KANAL ulash. (⚠️USERNAME o'rniga kanal usernamesi yoziladi!)
/kanaloff - Funksiyani o'chirish.
/ruxsat - Ответить qilib yoki @ orqali belgilangan odamga yozishga ruxsat berish.
"""


async def handle_help(message: Message, bot: Bot) -> None:
    # Private chat bo'lsa, foydalanuvchini bazaga yozamiz
    if message.chat.type == "private":
        await sync_to_async(TgUser.objects.get_or_create)(
            chat_id=message.from_user.id,
            defaults={"full_name": message.from_user.full_name}
        )

    await message.answer(
        HELP_TEXT,
        parse_mode="HTML",
        reply_markup= await start_group_inline()
    )

@sync_to_async
def set_invite_count(chat_id: int, count: int):
    group, _ = TgGroup.objects.get_or_create(chat_id=chat_id)
    group.invite_count = count
    group.save()
    return group

@sync_to_async
def disable_invite_count(chat_id: int):
    group, _ = TgGroup.objects.get_or_create(chat_id=chat_id)
    group.invite_count = 0
    group.save()
    return group

@sync_to_async
def set_required_channel(chat_id: int, username: str, title: str, channel_id: int):
    group, _ = TgGroup.objects.get_or_create(chat_id=chat_id)
    group.required_channel_username = username
    group.required_channel = channel_id
    group.required_channel_title = title
    group.save()
    return group

@sync_to_async
def disable_required_channel(chat_id: int):
    group, _ = TgGroup.objects.get_or_create(chat_id=chat_id)
    group.required_channel_username = None
    group.required_channel_title = None
    group.required_channel = None
    group.save()
    return group

@sync_to_async
def is_bot_admin(chat_id: int) -> bool:
    return TgUser.objects.filter(
        chat_id=chat_id,
        is_admin=True
    ).exists()

# /majbur 10
async def cmd_set_invite_count(message: Message, bot: Bot):
    await delete_message(message, bot)

    if not message.chat.type in ['group', 'supergroup']:
        await message.answer("Bu buyruq faqat guruhlarda ishlaydi!")
        return

    # Admin bo'lsa cheklov ishlamaydi
    if message.sender_chat and message.chat:
        same_sender = (
                message.sender_chat.id == message.chat.id and
                message.sender_chat.type == message.chat.type and
                message.sender_chat.title == message.chat.title
        )
        if not same_sender:
            await message.answer("Siz guruhda admin emassiz!")
            return
    elif not await is_group_admin(message.chat.id, message.from_user.id):
        await message.answer("Siz guruhda admin emassiz!")
        return

    try:
        count_str = message.text.split(maxsplit=1)[1]
        count = int(count_str)
    except (IndexError, ValueError):
        await message.answer("⚠️ To‘g‘ri ishlatish: <code>/majbur 10</code>", parse_mode="HTML")
        return

    group = await set_invite_count(message.chat.id, count)
    await message.answer(f"✅ Guruh uchun majburiy qo‘shish soni <b>{count}</b> qilib belgilandi.", parse_mode="HTML")

# /majburoff
async def cmd_disable_invite_count(message: Message, bot: Bot):
    await delete_message(message, bot)

    if not message.chat.type in ['group', 'supergroup']:
        await message.answer("Bu buyruq faqat guruhlarda ishlaydi!")
        return

    # Admin bo'lsa cheklov ishlamaydi
    if message.sender_chat and message.chat:
        same_sender = (
                message.sender_chat.id == message.chat.id and
                message.sender_chat.type == message.chat.type and
                message.sender_chat.title == message.chat.title
        )
        if not same_sender:
            await message.answer("Siz guruhda admin emassiz!")
            return
    elif not await is_group_admin(message.chat.id, message.from_user.id):
        await message.answer("Siz guruhda admin emassiz!")
        return

    group = await disable_invite_count(message.chat.id)
    await message.answer("✅ Majburiy odam qo‘shish talabi o‘chirildi.", parse_mode="HTML")


# /kanal @username
async def cmd_set_required_channel(message: Message, bot: Bot):
    await delete_message(message, bot)
    if not message.chat.type in ['group', 'supergroup']:
        await message.answer("Bu buyruq faqat guruhlarda ishlaydi!")
        return

    # Admin bo'lsa cheklov ishlamaydi
    if message.sender_chat and message.chat:
        same_sender = (
                message.sender_chat.id == message.chat.id and
                message.sender_chat.type == message.chat.type and
                message.sender_chat.title == message.chat.title
        )
        if not same_sender:
            await message.answer("Siz guruhda admin emassiz!")
            return
    elif not await is_group_admin(message.chat.id, message.from_user.id):
        await message.answer("Siz guruhda admin emassiz!")
        return

    try:
        username = message.text.split(maxsplit=1)[1]
        if not username.startswith("@"):
            await message.answer("⚠️ To‘g‘ri ishlatish: <code>/kanal @kanal_username</code>", parse_mode="HTML")
            return
    except IndexError:
        await message.answer("⚠️ To‘g‘ri ishlatish: <code>/kanal @kanal_username</code>", parse_mode="HTML")
        return

    # Bot kanalga ulanganmi tekshiramiz
    try:
        kanal_info = await bot.get_chat(username)
        if kanal_info.type != 'channel':
            msg = await message.answer(
                text="❌ *Bu username kanalga tegishli emas!*\n\n"
                     "Faqat kanal usernamesini kiriting.",
                parse_mode="Markdown",
            )
            return
        try:
            bot_member = await bot.get_chat_member(chat_id=kanal_info.id, user_id=bot.id)
        except:
            msg = await message.answer(
                "❌ *Xatolik!*\n\n"
                "Bot ushbu kanalda mavjud emas yoki kanal topilmadi.\n\n"
                "ℹ️ Iltimos, kanal username'sini to‘g‘ri kiriting va botni kanalga qo‘shganingizga ishonch hosil qiling.",
                parse_mode="Markdown"
            )
            return
    except TelegramBadRequest:
        await message.answer("❌ Bot ushbu kanalga qo‘shilmagan. Avval botni kanalga admin qiling.")
        return

    group = await set_required_channel(message.chat.id, username, kanal_info.title, kanal_info.id)
    await message.answer(f"✅ Endi guruhga qo‘shilish uchun {username} kanaliga a‘zo bo‘lish shart.", parse_mode="HTML")

# /kanaloff
async def cmd_disable_required_channel(message: Message, bot: Bot):
    await delete_message(message, bot)
    if not message.chat.type in ['group', 'supergroup']:
        await message.answer("Bu buyruq faqat guruhlarda ishlaydi!")
        return

    # Admin bo'lsa cheklov ishlamaydi
    if message.sender_chat and message.chat:
        same_sender = (
                message.sender_chat.id == message.chat.id and
                message.sender_chat.type == message.chat.type and
                message.sender_chat.title == message.chat.title
        )
        if not same_sender:
            await message.answer("Siz guruhda admin emassiz!")
            return
    elif not await is_group_admin(message.chat.id, message.from_user.id):
        await message.answer("Siz guruhda admin emassiz!")
        return

    group = await disable_required_channel(message.chat.id)
    await message.answer("✅ Kanalga majburiy a‘zo bo‘lish talabi o‘chirildi.", parse_mode="HTML")


async def web_panel(message: Message, bot: Bot):
    await delete_message(message, bot)
    if not message.chat.type in ['private']:
        return

    if not await is_bot_admin(message.from_user.id):
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Panelga o‘tish",
            web_app=WebAppInfo(url="https://quruvchibot.asatullayev.uz")
        )]
    ])

    await message.answer(
        text=(
            "👋 *Xush kelibsiz!*\n\n"
            "📊 Sizning shaxsiy *Admin Panelingiz* tayyor.\n"
            "Quyidagi tugma orqali panelni *bot ichida* ochishingiz mumkin:\n\n"
            "✨ Ishlaringizga omad va samarali boshqaruv tilaymiz!"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )



