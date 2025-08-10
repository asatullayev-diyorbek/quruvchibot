from datetime import datetime

from aiogram import types
from asgiref.sync import sync_to_async
from bot.models import Advertisement, TgInviterUser


@sync_to_async
def update_or_create_inviter(group_chat_id, inviter_chat_id):
    from bot.models import TgInviterUser, TgGroup

    tg_group = TgGroup.objects.filter(chat_id=group_chat_id).first()
    if not tg_group:
        return False, "Guruh bazada topilmadi!"

    obj, created = TgInviterUser.objects.update_or_create(
        tg_group=tg_group,
        inviter_chat_id=inviter_chat_id,
        defaults={
            "inviter_full_name": "Noma'lum",  # Keyin kerak bo‘lsa to‘ldirish mumkin
            "is_allow": True
        }
    )
    return True, "created" if created else "updated"



async def process_ad_target(callback: types.CallbackQuery):
    try:
        action, chat_id_msg = callback.data.split("_target_")[1].split("_", 1)
        from_chat_id, from_message_id = chat_id_msg.split("__")

        # Maqsadni aniqlash
        if action == "groups":
            target_type = Advertisement.TARGET_GROUPS
        elif action == "users":
            target_type = Advertisement.TARGET_USERS
        else:
            await callback.answer("❌ Noto‘g‘ri ma'lumot.", show_alert=True)
            return

        # Bazaga saqlash
        await sync_to_async(Advertisement.objects.create)(
            forward_from_chat_id=int(from_chat_id),
            forward_message_id=int(from_message_id),
            target_type=target_type,
            created_by=callback.from_user.id
        )

        await callback.message.edit_text(
            f"✅ Reklama { 'guruhlar' if target_type == 'groups' else 'foydalanuvchilar' } uchun muvaffaqiyatli saqlandi.\n"
            f"📅 Cron orqali yuboriladi."
        )

    except Exception as e:
        await callback.answer(f"❌ Xatolik: {e}", show_alert=True)


async def cancel_ad(callback: types.CallbackQuery):
    await callback.message.edit_text("❌ Reklama yuborish bekor qilindi.")


async def process_allow_inviter(callback: types.CallbackQuery):
    try:
        print("so'rov keldida")
        inviter_chat_id = int(callback.data.split("_")[1])
        group_chat_id = callback.message.chat.id  # tugma bosilgan guruh

        # 1️⃣ Guruh adminligini tekshirish
        try:
            member = await callback.bot.get_chat_member(group_chat_id, callback.from_user.id)
            if member.status not in ("administrator", "creator"):
                await callback.answer("❌ Siz admin emassiz!", show_alert=True)
                return
        except Exception as e:
            await callback.answer(f"❌ Tekshirishda xatolik: {e}", show_alert=True)
            return

        # callback ichida
        success, status = await update_or_create_inviter(group_chat_id, inviter_chat_id)

        if success:
            old_text = callback.message.text or ""
            new_text = f"{old_text}\n\n✅ Ruxsat berildi"
            # Tugma bo'lsa, olib tashlaymiz
            if callback.message.reply_markup:
                await callback.message.edit_reply_markup()
            await callback.message.edit_text(new_text)
            await callback.answer("✅ Ruxsat berildi!", show_alert=True)
        else:
            await callback.answer("⚠️ Guruh topilmadi!", show_alert=True)
    except Exception as e:
        print(e)
        await callback.answer("Nimadir xato ketdi! Qayta urinib ko'ring!")