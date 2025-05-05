'''Creating a session with a database connection and closing it when exiting'''

from .db import session_local

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
