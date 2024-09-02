from models import User, TelegramData, Subreddit, Submission, SubredditUser


class UserRepository:
    @staticmethod
    def get_admins_with_tg_data():
        return User.select().where(User.admin == True).join(TelegramData)

    @staticmethod
    def create_user(first_name, last_name, admin=False):
        return User.create(first_name=first_name, last_name=last_name, admin=admin)

    @staticmethod
    def get_by_telegram_id(telegram_id):
        return User.select().where(TelegramData.telegram_id == telegram_id).first()

    @staticmethod
    def get_by_id(user_id):
        return User.get_by_id(user_id)


class TelegramDataRepository:
    @staticmethod
    def get_telegram_data_and_user_by_id(telegram_id):
        return TelegramData.select().where(TelegramData.telegram_id == telegram_id).join(User).first()

    @staticmethod
    def create_telegram_data(telegram_id, user, username):
        return TelegramData.create(telegram_id=telegram_id, user=user, username=username)


class RedditRepository:
    @staticmethod
    def get_subreddit_by_name(name):
        return Subreddit.select().where(Subreddit.name == name).first()

    @staticmethod
    def get_all_subreddits():
        return Subreddit.select()

    @staticmethod
    def get_latest_post_from_each_subreddit():
        return Submission.select(Submission.subreddit, Submission.created).group_by(Submission.subreddit).order_by(
            Submission.created.desc())

    @staticmethod
    def create_submission(id, title, subreddit, created, linked_url, submission_url):
        return Submission.create(id=id, title=title, subreddit=subreddit, created=created, linked_url=linked_url,
                                 submission_url=submission_url)

    @staticmethod
    def create_subreddit(name):
        return Subreddit.create(name=name)

    @staticmethod
    def create_subreddit_user(user, subreddit):
        return SubredditUser.create(user=user, subreddit=subreddit)

    @staticmethod
    def delete_subreddit_user(user, subreddit):
        return SubredditUser.delete().where(SubredditUser.user == user, SubredditUser.subreddit == subreddit).execute()