from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    InvalidCallbackData,
    PicklePersistence,
)

from models import User, TelegramData


class BotWrapper:
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    def approval_keyboard(user_id):
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton('Approve', callback_data=f'approve_{user_id}'),
              InlineKeyboardButton('Reject', callback_data=f'reject_{user_id}')]]
        )

    async def notify_admins_for_approval(self, user, telegram_data):
        admins: List[User] = User.select().where(User.admin == True).join(TelegramData)
        for admin in admins:
            await self.bot.send_message(
                admin.telegram_data_id,
                f'New user {user.first_name} {user.last_name} ({telegram_data.username}) wants to use the bot',
                reply_markup=self.approval_keyboard(user.id),
            )




    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        sender = update.message.from_user
        td = TelegramData.select().where(TelegramData.telegram_id == sender.id).first()
        if not td:
            user = User.create(first_name=sender.first_name, last_name=sender.last_name, admin=False)
            td = TelegramData.create(telegram_id=sender.id, user=user, username=sender.username)
            await self.notify_admins_for_approval(user, td)
            await update.message.reply_text('Welcome! You can use the bot when an admin approves you')
        else:
            await update.message.reply_text('Welcome back!')
