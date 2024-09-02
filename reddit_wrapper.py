import praw

from prawcore import NotFound

from models import Submission


class RedditWrapper:
    def __init__(self, reddit: praw.Reddit, limit: int = 10):
        self.reddit = reddit
        self.limit = limit

    @property
    def subreddits(self):
        return [sub['name'] for sub in self.config]

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

    # TODO: Periodically get new posts, save them to db, send them to respective users.


reddit = RedditWrapper()
