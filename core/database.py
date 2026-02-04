
import sqlite3
import os
import asyncio

# Database path: Local to this CleanBot folder for fully isolated environment
# Or we can link to the old one. User said "create from scratch", but likely wants to keep data?
# I will use the local db folder to be fully "clean" as requested, but I'll migrate the schema if needed.
# Converting to use the copied DB.

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "database.db")

class Database:
    def __init__(self):
        self.path = DB_PATH
        self.conn = None

    def connect(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

    def get_connection(self):
        if not self.conn:
            self.connect()
        return self.conn

    async def query(self, command, params=None, method="all"):
        if params is None:
            params = []
            
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._execute, command, params, method)

    def _execute(self, command, params, method):
        self.connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute(command, params)
            
            # Auto-detect write operations
            command_upper = command.strip().upper()
            is_write = any(command_upper.startswith(p) for p in ["INSERT", "UPDATE", "DELETE", "REPLACE", "CREATE", "DROP", "ALTER"])
            
            if method == "all":
                result = [dict(row) for row in cursor.fetchall()]
                if is_write: self.conn.commit()
            elif method == "get":
                row = cursor.fetchone()
                result = dict(row) if row else None
                if is_write: self.conn.commit()
            elif method == "run" or is_write:
                self.conn.commit()
                result = cursor.lastrowid
            else:
                result = cursor.fetchall()
                if is_write: self.conn.commit()
                
            return result
        except Exception as e:
            print(f"[DB Error] {e}")
            raise e

# Global instance
db = Database()
