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

    def db_setup(self) -> None:
        """Method used only to set up DB on app initialization"""
        with self.connect() as con:
            con.cursor().execute("""
                CREATE TABLE study_sessions(
                id INTEGER PRIMARY KEY,
                    length INTEGER,
                    date DATE,
                    done BIT
                )
            """)
            con.commit()

    def create_session_entry(self, length: int, is_successful: int):
        with self.connect() as con:
            con.cursor().execute("""
                INSERT INTO study_sessions(length, date, done)
                VALUES (?, ?, ?)
            """, (length, datetime.now(), is_successful)
            )
