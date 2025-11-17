from tinydb import TinyDB

# Database file create / open
db = TinyDB("hamsaaya_db.json")

# Tables
users = db.table("users")
chats = db.table("chats")
