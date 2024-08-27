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

from models import User, TelegramData, Subreddit, SubredditUser
from reddit_wrapper import reddit


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

    @staticmethod
    async def get_user(update: Update):
        user = TelegramData.select().where(TelegramData.telegram_id == update.message.from_user.id).join(User).first().user
        if not user.approved:
            await update.message.reply_text('You are not approved to use the bot')
            return
        return user





    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        sender = update.message.from_user
        td = TelegramData.select().where(TelegramData.telegram_id == sender.id).join(User).first()
        if not td:
            user = User.create(first_name=sender.first_name, last_name=sender.last_name, admin=False)
            td = TelegramData.create(telegram_id=sender.id, user=user, username=sender.username)
            await self.notify_admins_for_approval(user, td)
            await update.message.reply_text('Welcome! You can use the bot when an admin approves you')
        elif not td.user.approved:
            await self.notify_admins_for_approval(td.user, td)
            await update.message.reply_text('Welcome! You can use the bot when an admin approves you')
        else:
            await update.message.reply_text('Welcome back!')

    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not (user := await self.get_user(update)):
            return
        subreddit_name = context.args[0]
        subreddit = Subreddit.select().where(Subreddit.name == subreddit_name).first()
        if subreddit:
            SubredditUser.create(user=user, subreddit=subreddit)
        else:
            if reddit.subreddit_exists(subreddit_name):
                subreddit = Subreddit.create(name=subreddit_name)
                SubredditUser.create(user=user, subreddit=subreddit)
                await update.message.reply_text(f'Subreddit {subreddit_name} added')
            else:
                await update.message.reply_text(f'Subreddit {subreddit_name} does not exist')

    async def remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not (user := await self.get_user(update)):
            return
        subreddit_name = context.args[0]
        subreddit = Subreddit.select().where(Subreddit.name == subreddit_name).first()
        if subreddit:
            # TODO : if no subuser, will this raise error?
            SubredditUser.delete().where(SubredditUser.user == user, SubredditUser.subreddit == subreddit).execute()
            await update.message.reply_text(f'Subreddit {subreddit_name} removed')
        else:
            await update.message.reply_text(f'Subreddit {subreddit_name} not found')

    async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        action, user_id = query.data.split('_')
        user = User.get_by_id(user_id)
        if not user:
            await query.edit_message_text('User not found')
            print('User not found')
            return
        if action == 'approve':
            user.approved = True
            user.save()
            await query.edit_message_text('User approved')
            await context.bot.send_message(user.telegram_data_id, 'You have been approved to use the bot')
        else:
            await query.edit_message_text('User rejected')
            await context.bot.send_message(user.telegram_data_id, 'You have been rejected')





