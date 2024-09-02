from models import User, TelegramData, Subreddit, Submission


class UserRepository:
    @staticmethod
    def get_admins_with_tg_data():
        return User.select().where(User.admin == True).join(TelegramData)

    @staticmethod
    def get_by_telegram_id(telegram_id):
        return User.select().where(TelegramData.telegram_id == telegram_id).first()


class TelegramDataRepository:
    @staticmethod
    def get_telegram_data_and_user_by_id(telegram_id):
        return TelegramData.select().where(TelegramData.telegram_id == telegram_id).join(User).first()


class RedditRepository:
    @staticmethod
    def get_subreddit_by_name(name):
        return Subreddit.select().where(Subreddit.name == name).first()

    @staticmethod
    def get_all_subreddits():
        return Subreddit.select()

    @staticmethod
    def get_latest_post_from_each_subreddit():
        return Submission.select(Submission.subreddit, Submission.created).group_by(Submission.subreddit).order_by(Submission.created.desc())
