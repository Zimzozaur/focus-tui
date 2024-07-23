import os

from dotenv import load_dotenv


load_dotenv(override=True)

DEBUG = True if os.getenv('DEBUG') == 'True' else False

# Number of seconds in Minute
MINUTE = 60 if not DEBUG else 1
MIN_SESSION_LEN = 5 if not DEBUG else 1


