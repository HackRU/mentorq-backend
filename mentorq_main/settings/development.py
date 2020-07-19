from .common import *
import django_heroku

DEBUG = True

# doesn't matter what the string is, it just has to be set
os.environ["LCS_DEV"] = "t"

django_heroku.settings(locals())
