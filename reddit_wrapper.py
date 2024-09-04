from functools import lru_cache

import praw
from praw import Reddit

from prawcore import NotFound

from bot import BotWrapper
from models import Submission
from repository import RedditRepository, SubredditUserRepository


class RedditWrapper:
    def __init__(self, reddit: praw.Reddit, bot_wrapper, limit: int = 20):
        self.reddit = reddit
        self.limit = limit
        self.latest_posts = {}
        self.bot_wrapper: BotWrapper = bot_wrapper

    @property
    def subreddits(self):
        return RedditRepository.get_all_subreddits()

    @lru_cache
    def get_subreddits_from_db(self):
        return RedditRepository.get_all_subreddits()

    def subreddit_exists(self, subreddit):
        try:
            self.reddit.subreddits.search_by_name(subreddit, exact=True)
            return True
        except NotFound as e:
            return False

    def get_new_posts(self):
        new_posts = {}
        latest_post_by_subreddit = {}

        for subreddit in self.subreddits:
            new_posts[subreddit] = list(self.reddit.subreddit(subreddit).new(limit=self.limit))
            latest_post = Submission.select().where(Submission.subreddit == subreddit).order_by(
                Submission.created.desc()).first()
            if latest_post:
                new_posts[subreddit] = [post for post in new_posts[subreddit] if post.created_utc > latest_post.created]
        return new_posts

    def get_latest_posts_from_db(self):
        for subreddit in self.subreddits:
            if subreddit.name not in self.latest_posts:
                self.latest_posts[subreddit.name] = RedditRepository.get_latest_post_from_subreddit(subreddit)
        return self.latest_posts


    @staticmethod
    def get_telegram_ids_per_subreddit():
        ids = SubredditUserRepository.get_telegram_ids_per_subreddit()
        return {r['name']: r['telegram_id'] for r in ids}

    def get_latest_posts_from_reddit(self):
        ids = self.get_telegram_ids_per_subreddit()
        for subreddit in self.subreddits:
            new_posts = list(self.reddit.subreddit(subreddit.name).new(limit=self.limit))
            for post in reversed(new_posts):
                if post.created_utc > self.latest_posts[subreddit.name].created:
                    self.latest_posts[subreddit.name] = post.created_utc
                    RedditRepository.create_submission(post.id, post.title, subreddit, post.created_utc, post.url, post.permalink)
                    for _id in ids[subreddit.name]:
                        self.bot_wrapper.send_message(_id, f'New post in {subreddit.name}:\n{post.title}\n{post.url}')



reddit = RedditWrapper(Reddit('bot1'))
