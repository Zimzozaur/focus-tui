import sqlite3
from sqlite3 import Connection
from pathlib import Path
from datetime import datetime

from platformdirs import user_data_dir


class DatabaseManager:
    def __init__(self):
        self.db_file = Path(user_data_dir()) / 'Focus-Seeds/user_data/focus_seeds.db'

    def connect(self) -> Connection:
        """Return DB connection"""
        return sqlite3.connect(self.db_file)

    def _db_setup(self) -> None:
        """Method used only to set up DB on app initialization"""
        with self.connect() as con:
            con.cursor().execute("""
                CREATE TABLE study_session(
                id INTEGER PRIMARY KEY,
                    length INTEGER, 
                    date TIMESTAMP, 
                    done BIT
                ) 
            """)
            con.commit()


