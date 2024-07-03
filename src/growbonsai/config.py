# config.py

import os

# Get the current file's directory (config.py)
config_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate up two levels to reach the base directory
BASE_DIR = os.path.dirname(os.path.dirname(config_dir))

# Define other directories relative to the base directory
STATIC_DIR = os.path.join(BASE_DIR, 'static')
MP3_DIR = os.path.join(STATIC_DIR, 'mp3')
USERS_MP3_DIR = os.path.join(MP3_DIR, 'users_mp3')

UNFS_BRAAM = os.path.join(MP3_DIR, 'Unfa_Braam.mp3')
UNFS_WOOHOO = os.path.join(MP3_DIR, 'Unfa_Woohoo.mp3')
UNFA_ACID_BASSLINE = os.path.join(MP3_DIR, 'Unfa_Acid_Bassline.mp3')
UNFA_LANDING = os.path.join(MP3_DIR, 'Unfa_Landing.mp3')