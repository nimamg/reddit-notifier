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


class TelegramData(BaseModel):
    telegram_id = CharField(primary_key=True)
    user = ForeignKeyField(User, backref='telegram_data')
    username = CharField(null=True)


class Subreddit(BaseModel):
    name = CharField(primary_key=True)


class UserSubreddit(BaseModel):
    user = ForeignKeyField(User, backref='subreddits')
    subreddit = ForeignKeyField(Subreddit, backref='users')


class Submission(BaseModel):
    id = CharField(primary_key=True)
    title = CharField()
    subreddit = ForeignKeyField(Subreddit, backref='submissions')
    created = DateTimeField(index=True)
    url = CharField(max_length=1000)


models = [Submission, User, TelegramData, Subreddit]


def init_db():
    db.connect()
    db.create_tables(models, safe=True)
