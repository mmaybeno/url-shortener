import base64
import secrets
import hashlib
from peewee import CharField, Model, SqliteDatabase
from flask import Flask, request, redirect
app = Flask(__name__)

SECRETS_URL_TOKEN_BTYES = 6
sqlite_db = SqliteDatabase('test.db')


# DB class
class UrlShortener(Model):
    short_id = CharField(primary_key=True, max_length=10)
    query_hash = CharField(unique=True, max_length=24)
    url = CharField(max_length=500)

    class Meta:
        database = sqlite_db


# Url Shortener
def hash_url_query(url):
    hash_digest = hashlib.md5(url.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(hash_digest)


def create_short_url_query():
    return secrets.token_urlsafe(SECRETS_URL_TOKEN_BTYES)


def shorten(url):
    query_hash = hash_url_query(url)
    _id = create_short_url_query()
    defaults = {
        'short_id': _id,
        'query_hash': query_hash,
        'url': url
    }
    url_shortener, created = UrlShortener.get_or_create(
        query_hash=query_hash,
        defaults=defaults
    )
    return url_shortener.short_id


@app.route('/')
def short_app():
    url = request.args.get('url')
    if url:
        short_url_key = shorten(url)
        return f'{request.url_root}s/{short_url_key}'
    return 'no short url'


@app.route('/s/<short_url_key>')
def redirect_app(short_url_key):
    url_model = UrlShortener.get(short_id=short_url_key)
    return redirect(url_model.url)


if __name__ == '__main__':
    sqlite_db.connect()
    sqlite_db.drop_tables([UrlShortener], safe=True)
    sqlite_db.create_tables([UrlShortener])
    app.run()
