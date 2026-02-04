
import json
import os
import time
from core.database import db

# CleanBot is one level deeper, so config.json is likely at ..\..\config.json if running from CleanBot root?
# No, CleanBot is d:\Autosecure\CleanBot.
# config.json is d:\Autosecure\config.json
# So path is ..\config.json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

class Permissions:
    def __init__(self):
        self.config_path = CONFIG_PATH
        self.cached_config = None
        self.last_load = 0
        self.cache_duration = 60 # Reload config every 60s
        
    def get_config(self):
        now = time.time()
        if not self.cached_config or (now - self.last_load > self.cache_duration):
            try:
                with open(self.config_path, 'r') as f:
                    self.cached_config = json.load(f)
                    self.last_load = now
            except Exception as e:
                # Fallback: maybe path is different if running from main.py?
                # If running from CleanBot/main.py, relative path ..\config.json is correct.
                # If running from root, ..\ is out of Autosecure?
                # Let's try explicit absolute path for safety if relative fails, or catch it.
                print(f"[Permissions] Error loading config: {e}")
                
        return self.cached_config or {}

    async def is_owner(self, user_id):
        config = self.get_config()
        owners = config.get('owners', [])
        return str(user_id) in owners

    async def has_access(self, user_id):
        # 1. Check Owner
        if await self.is_owner(user_id):
            return True
            
        # 2. Check License
        current_ms = int(time.time() * 1000)
        
        # We need to query usedLicenses
        rows = await db.query("SELECT expiry FROM usedLicenses WHERE user_id = ?", [str(user_id)], "all")
        
        if rows:
            for row in rows:
                try:
                    expiry = int(row['expiry'])
                    if expiry > current_ms:
                        return True
                except:
                    continue
                    
        return False

# Global instance
permissions = Permissions()
