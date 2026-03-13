import sqlite3

class CityBotDatabase:
    def __init__(self, db_path='citybot.db'):
        self.conexao = sqlite3.connect(db_path, check_same_thread=False)
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
            return self.conexao.execute("SELECT user_message, assistant_response FROM conversations;").fetchall()

    def limpar_banco(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        for (tabela,) in tabelas:
            cursor.execute(f"DROP TABLE IF EXISTS {tabela};")
        self.conexao.commit()
