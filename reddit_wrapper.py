import praw
from configparser import ConfigParser
from models import Submission


class RedditWrapper:
    def __init__(self, reddit: praw.Reddit, config: str, limit: int = 10):
        self.reddit = reddit
        self.config = ConfigParser().read(config)
        self.limit = limit

    @property
    def subreddits(self):
        return [sub['name'] for sub in self.config]

    def get_new_posts(self):
        new_posts = {}
        for subreddit in self.subreddits:
            new_posts[subreddit] = list(self.reddit.subreddit(subreddit).new(limit=self.limit))
            latest_post = Submission.select().where(Submission.subreddit == subreddit).order_by(
                Submission.created.desc()).first()
            if latest_post:
                new_posts[subreddit] = [post for post in new_posts[subreddit] if post.created_utc > latest_post.created]
        return new_posts

