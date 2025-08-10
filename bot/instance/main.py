from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command

from bot.instance.handlers.callback import process_ad_target, cancel_ad, process_allow_inviter
from bot.instance.handlers.chat_member import handle_new_member
from bot.instance.handlers.command_handler import handle_start, handle_help, cmd_set_invite_count, \
    cmd_set_required_channel, cmd_disable_invite_count, cmd_disable_required_channel
from bot.instance.handlers.messages import group_message_filter
from bot.instance.handlers.my_chat_member import handler_my_chat_member

webhook_dp = Dispatcher()
webhook_dp.message.register(handle_start, CommandStart())  # /start
webhook_dp.message.register(handle_help, Command('help'))  # /start
webhook_dp.message.register(cmd_set_invite_count, Command('majbur'))
webhook_dp.message.register(cmd_disable_invite_count, Command('majburoff'))
webhook_dp.message.register(cmd_set_required_channel, Command('kanal'))
webhook_dp.message.register(cmd_disable_required_channel, Command('kanaloff'))
webhook_dp.message.register(group_message_filter)  # barcha xabarlar

webhook_dp.my_chat_member.register(handler_my_chat_member)

webhook_dp.chat_member.register(handle_new_member)

webhook_dp.callback_query.register(
    process_ad_target,
    F.data.startswith("ad_target_")
)

# Bekor qilish tugmasi
webhook_dp.callback_query.register(cancel_ad, F.data == "ad_cancel")
webhook_dp.callback_query.register(process_allow_inviter, F.data.startswith("allow_"))

async def feed_update(token: str, update: dict):
    try:
        webhook_book = Bot(token=token)
        aiogram_update = types.Update(**update)
        await webhook_dp.feed_update(bot=webhook_book, update=aiogram_update)
    finally:
        await webhook_book.session.close()