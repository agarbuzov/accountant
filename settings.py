# Database
DATABASE = {
    "ENGINE": "postgresql",
    "NAME": "",
    "USER": "",
    "PASSWORD": "",
    "HOST": "localhost",
}

TELEGRAM_TOKEN = None

from local_settings import *

SQLALCHEMY_DATABASE_URI = "{ENGINE}://{USER}:{PASSWORD}@{HOST}/{NAME}".format(**DATABASE)
