from typing import List

from telegram.constants import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    InvalidCallbackData,
    PicklePersistence,
)

from repository import UserRepository, TelegramDataRepository, RedditRepository
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
        admins = UserRepository.get_admins_with_tg_data()
        for admin in admins:
            await self.bot.send_message(
                admin.telegram_data.telegram_id,
                f'New user {user.first_name} {user.last_name} ({telegram_data.username}) wants to use the bot',
                reply_markup=self.approval_keyboard(user.id),
            )

    @staticmethod
    async def get_user(update: Update):
        user = UserRepository.get_by_telegram_id(update.message.from_user.id)
        if not user.approved:
            await update.message.reply_text('You are not approved to use the bot')
            return
        return user

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        sender = update.message.from_user
        td = TelegramDataRepository.get_telegram_data_and_user_by_id(sender.id)
        if not td:
            user = UserRepository.create_user(sender.first_name, sender.last_name)
            td = TelegramDataRepository.create_telegram_data(sender.id, user, sender.username)
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
        subreddit = RedditRepository.get_subreddit_by_name(subreddit_name)
        if not subreddit:
            if reddit.subreddit_exists(subreddit_name):
                subreddit = RedditRepository.create_subreddit(subreddit_name)
            else:
                await update.message.reply_text(f'Subreddit {subreddit_name} does not exist')

        RedditRepository.create_subreddit_user(user, subreddit)
        await update.message.reply_text(f'Subreddit {subreddit_name} added')

    async def remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not (user := await self.get_user(update)):
            return
        subreddit_name = context.args[0]
        subreddit = RedditRepository.get_subreddit_by_name(subreddit_name)
        if subreddit:
            # TODO : if no subuser, will this raise error?
            RedditRepository.delete_subreddit_user(user, subreddit)
            await update.message.reply_text(f'Subreddit {subreddit_name} removed')
        else:
            await update.message.reply_text(f'Subreddit {subreddit_name} not found')

    async def handle_approval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        action, user_id = query.data.split('_')
        user = UserRepository.get_by_id(user_id)
        if not user:
            await query.edit_message_text('User not found')
            print('User not found')
            return
        if action == 'approve':
            user.approved = True
            user.save()
            await query.edit_message_text('User approved')
            await context.bot.send_message(user.telegram_data.telegram_id, 'You have been approved to use the bot')
        else:
            await query.edit_message_text('User rejected')
            await context.bot.send_message(user.telegram_data.telegram_id, 'You have been rejected')

    async def send_message(self, chat_id, text, parse_mode=ParseMode.MARKDOWN_V2):
        await self.bot.send_message(chat_id, text, parse_mode=parse_mode)






