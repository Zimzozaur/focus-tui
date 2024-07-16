import sqlite3
from sqlite3 import connect
from pathlib import Path
from datetime import datetime
from typing import Literal

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
                CREATE TABLE sound_settings(
                    id INTEGER PRIMARY KEY,
                    type TEXT,
                    name TEXT,
                    is_default BIT
                )
            """)
            con.commit()
            default_values = (
                ('alarm', 'Unfa_Braam.mp3', 1),
                ('signal', 'Unfa_Braam.mp3', 1),
                ('ambient', 'Unfa_Acid_Bassline.mp3', 1)
            )
            con.cursor().executemany(
                "INSERT INTO sound_settings(type, name, is_default) VALUES(?, ?, ?)",
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

    def get_sound_name(
            self,
            sound_type: Literal['alarm', 'signal', 'ambient']
    ) -> tuple[str, int]:
        """Get from db file name and location of chosen sound
        if int is 0 it is default else users sound
        """
        with connect(self.db_file) as con:
            cur = con.cursor().execute(f"""
                SELECT name, is_default FROM sound_settings WHERE type = '{sound_type}'
            """)
            return cur.fetchone()



