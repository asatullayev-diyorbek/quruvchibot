from aiogram import Bot
from aiogram.types import ChatMemberUpdated
from asgiref.sync import sync_to_async
from django.utils import timezone
from bot.models import TgGroup, TgInviterUser, ChannelMember

async def handle_new_member(event: ChatMemberUpdated, bot: Bot):
    try:
        # Kanalga qo'shilgan bo'lsa
        if event.chat.type == "channel":
            if (
                event.old_chat_member.status in ("left", "kicked") and
                event.new_chat_member.status in ("member", "administrator", "creator")
            ):
                await sync_to_async(save_channel_member)(
                    event.chat.id,
                    event.new_chat_member.user
                )
            else:
                await sync_to_async(del_channel_member)(
                    event.chat.id,
                    event.new_chat_member.user
                )
            return  # kanal bo‘lsa guruh qismi ishlamaydi\


        # Guruhga qo'shilgan bo'lsa
        if (
            event.old_chat_member.status in ("left", "kicked") and
            event.new_chat_member.status == "member"
        ):
            group_chat_id = event.chat.id
            group_title = event.chat.title or "No title"

            inviter = event.from_user
            new_user = event.new_chat_member.user

            if inviter.id == new_user.id:
                return

            await sync_to_async(save_invite)(group_chat_id, group_title, inviter, new_user)

    except Exception as e:
        print(f"❌ handle_new_member xatosi: {e}")


def save_invite(group_chat_id, group_title, inviter, new_user):
    group, _ = TgGroup.objects.get_or_create(
        chat_id=group_chat_id,
        defaults={"title": group_title, "is_admin": False}
    )

    inviter_obj, _ = TgInviterUser.objects.get_or_create(
        tg_group=group,
        inviter_chat_id=inviter.id,
        defaults={
            "inviter_full_name": inviter.full_name,
            "invite_count": 0
        }
    )

    inviter_obj.invite_count += 1
    inviter_obj.last_invite_at = timezone.now()
    inviter_obj.save()

    print(f"✅ {inviter.full_name} {new_user.full_name} ni guruhga qo'shdi. ({inviter_obj.invite_count} ta)")


def save_channel_member(channel_id, user):
    ChannelMember.objects.get_or_create(
        channel_id=channel_id,
        user_chat_id=user.id,
        defaults={"full_name": user.full_name}
    )
    print(f"📢 {user.full_name} kanalga qo‘shildi ({channel_id})")


def del_channel_member(channel_id, user):
    ChannelMember.objects.filter(
        channel_id=channel_id,
        user_chat_id=user.id
    ).delete()
    print(f"📢 {user.full_name} kanaldan chiqib ketdi ({channel_id})")
