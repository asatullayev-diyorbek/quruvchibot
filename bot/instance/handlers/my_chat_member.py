from asgiref.sync import sync_to_async
import pprint
from aiogram import Bot
from aiogram.types import ChatMemberUpdated

from bot.instance.handlers.keyboards import start_group_inline
from bot.models import TgGroup, GroupAdmin


async def handler_my_chat_member(event: ChatMemberUpdated, bot: Bot):
    # print("🔔 My Chat Member update received:")

    if not event.chat.type in ['group', 'supergroup']:
        return

    chat_id = event.chat.id
    chat_title = event.chat.title
    new_status = event.new_chat_member.status
    is_admin = new_status in ("administrator", "creator")

    tg_group, created = await sync_to_async(TgGroup.objects.get_or_create)(
        chat_id=chat_id,
        defaults={"title": chat_title, "is_admin": is_admin}
    )

    if tg_group.is_admin != is_admin or tg_group.title != chat_title:
        tg_group.is_admin = is_admin
        tg_group.title = chat_title
        await sync_to_async(tg_group.save)()

    if is_admin:
        admins = await bot.get_chat_administrators(chat_id)

        await sync_to_async(GroupAdmin.objects.filter(tg_group=tg_group).delete)()

        bulk_admins = [
            GroupAdmin(
                tg_group=tg_group,
                user_chat_id=admin.user.id,
                user_full_name=admin.user.full_name
            )
            for admin in admins
        ]
        await sync_to_async(GroupAdmin.objects.bulk_create)(bulk_admins)
        print(f"✅ {len(bulk_admins)} ta admin saqlandi: {chat_title}")
        try:
            await bot.send_message(
                chat_id=tg_group.chat_id,
                text="Bot endi guruhda admin!",
                reply_markup= await start_group_inline()
            )
        except:
            pass
    else:
        await sync_to_async(GroupAdmin.objects.filter(tg_group=tg_group).delete)()
