import sqlite3
from pathlib import Path

from src.utils.paths import project_path


DEFAULT_DB_PATH = project_path('citybot.db')


def _resolve_db_path(db_path):
    if db_path is None:
        return DEFAULT_DB_PATH
    if db_path == ':memory:':
        return db_path

    path = Path(db_path)
    if path.is_absolute():
        return path
    return project_path(path)

class CityBotDatabase:
    def __init__(self, db_path=None):
        self.db_path = _resolve_db_path(db_path)
        self.conexao = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conexao:
            self.conexao.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                preferences TEXT
            );
            """)

            self.conexao.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                user_message TEXT,
                assistant_response TEXT
            );
            """)

    def save_user(self, name, preferences):
        with self.conexao:
            self.conexao.execute("INSERT INTO users (name, preferences) VALUES (?, ?);", (name, preferences))

    def load_user(self, name):
        with self.conexao:
            return self.conexao.execute("SELECT * FROM users WHERE name = ?;", (name,)).fetchone()

    def save_conversation(self, user_message, assistant_response):
        with self.conexao:
            self.conexao.execute("INSERT INTO conversations (user_message, assistant_response) VALUES (?, ?);", (user_message, assistant_response))

    def load_conversations(self):
        with self.conexao:
            return self.conexao.execute(
                'SELECT user_message, assistant_response '
                'FROM conversations ORDER BY id;'
            ).fetchall()

    def limpar_conversas(self):
        with self.conexao:
            self.conexao.execute('DELETE FROM conversations;')

    def limpar_banco(self):
        with self.conexao:
            self.conexao.execute('DELETE FROM conversations;')
            self.conexao.execute('DELETE FROM users;')
