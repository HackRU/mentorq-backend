from datetime import timedelta
from .common import *

DEBUG = True

# doesn't matter what the string is, it just has to be set
os.environ["LCS_DEV"] = "t"

SECRET_KEY = "placeholder_secret_key"

ALLOWED_HOSTS = ["*"]

STATIC_URL = "/static/"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1)
}
