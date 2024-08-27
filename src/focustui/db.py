from datetime import datetime
from sqlite3 import connect

from focustui.constants import DB_FILE_PATH


class DatabaseManager:
    _instance = None

    def __new__(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.db_file = DB_FILE_PATH

    def db_setup(self) -> None:
        """Use only to set up DB on app initialization."""
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
            con.commit()

    def create_session_entry(self, length: int, is_successful: int) -> None:
        with connect(self.db_file) as con:
            con.cursor().execute("""
                INSERT INTO study_sessions(length, date, done)
                VALUES (?, ?, ?)
            """, (length, datetime.now(), is_successful),
            )
