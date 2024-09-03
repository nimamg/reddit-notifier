from peewee import SqliteDatabase, Model, CharField, DateTimeField, ForeignKeyField, AutoField, BooleanField

db = SqliteDatabase('reddit_notifier.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField()
    approved = BooleanField(default=False)
    admin = BooleanField(default=False)
    first_name = CharField(null=True)
    last_name = CharField(null=True)

    @property
    def telegram_data(self):
        return self.telegramdata_set.get()


class TelegramData(BaseModel):
    telegram_id = CharField(primary_key=True)
    user = ForeignKeyField(User, unique=True)
    username = CharField(null=True)


class Subreddit(BaseModel):
    name = CharField(primary_key=True)


class SubredditUser(BaseModel):
    user = ForeignKeyField(User, backref='subreddits')
    subreddit = ForeignKeyField(Subreddit, backref='users')


class Submission(BaseModel):
    id = CharField(primary_key=True)
    title = CharField()
    subreddit = ForeignKeyField(Subreddit, backref='submissions')
    created = DateTimeField(index=True)
    linked_url = CharField(max_length=1000)
    submission_url = CharField(max_length=1000)


models = [Submission, User, TelegramData, Subreddit, SubredditUser]


def init_db():
    db.connect()
    db.create_tables(models, safe=True)
