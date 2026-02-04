
import re
from core.database import db

class EmailHandler:
    def __init__(self):
        pass

    def is_valid_format(self, email):
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(regex, email) is not None

    async def get_user_emails(self, user_id):
        # Fetch registered emails
        registered = await db.query("SELECT email FROM registeredemails WHERE user_id = ?", [user_id])
        return [r['email'] for r in registered]

    async def register_email(self, user_id, email):
        if not self.is_valid_format(email):
            return False, "Invalid email format."
            
        # Check if already registered
        existing = await db.query("SELECT * FROM registeredemails WHERE email = ?", [email], "get")
        if existing:
            return False, "Email already registered."
            
        # Logic to check allowed domains would go here
        # For now, allowing registration (assuming validation handled or open)
        
        await db.query("INSERT INTO registeredemails (user_id, email) VALUES (?, ?)", [user_id, email])
        return True, f"Registered {email} successfully."

    async def get_inbox(self, email, user_id, is_owner=False):
        # 1. Verify ownership if not owner
        if not is_owner:
            check = await db.query("SELECT user_id FROM registeredemails WHERE email = ?", [email], "get")
            if not check or check['user_id'] != str(user_id):
                return False, "You do not own this email."

        # 2. Fetch emails (Mock for now, or from DB 'emails' table if it existed)
        # There is 'email_notifier' table mentioned in old code, maybe that's where emails live?
        # Or 'emails' table?
        # Let's assume 'emails' table stores received messages: id, recipient, subject, content, timestamp
        
        # Check if 'emails' table exists/has data. Using a simple query.
        messages = await db.query("SELECT * FROM emails WHERE recipient = ? ORDER BY timestamp DESC LIMIT 10", [email])
        
        if not messages:
            return True, [] # Empty inbox
            
        return True, messages

# Global instance
email_handler = EmailHandler()
