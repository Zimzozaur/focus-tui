import sqlite3
from sqlite3 import connect
from pathlib import Path
from datetime import datetime

from platformdirs import user_data_dir


class DatabaseManager:
    def __init__(self):
        self.db_file = Path(user_data_dir()) / 'Focus-Seeds/app_data/focus_seeds.db'

    def db_setup(self) -> None:
        """Method used only to set up DB on app initialization"""
        with connect(self.db_file) as con:
            # Setup Session table
            con.cursor().execute("""
                CREATE TABLE study_sessions(
                    id INTEGER PRIMARY KEY,
                    length INTEGER,
                    date DATE,
                    done BIT
                )
            """)
            # Setup Settings table
            con.cursor().execute("""
                CREATE TABLE settings_table(
                    id INTEGER PRIMARY KEY,
                    key TEXT,
                    value TEXT
                )
            """)
            con.commit()
            default_values = (
                ('selected_alarm', 'Unfa_Braam'),
                ('selected_signal', 'Unfa_Braam'),
                ('selected_ambient', 'Unfa_Acid_Bassline')
            )
            con.cursor().executemany(
                "INSERT INTO settings_table (key, value) VALUES(?, ?)",
                default_values
            )
            con.commit()

    def create_session_entry(self, length: int, is_successful: int):
        with connect(self.db_file) as con:
            con.cursor().execute("""
                INSERT INTO study_sessions(length, date, done)
                VALUES (?, ?, ?)
            """, (length, datetime.now(), is_successful)
            )