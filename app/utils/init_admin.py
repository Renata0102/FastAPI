from ..database.db import session_local
from ..database.models import User
from ..utils.config import settings
from ..utils.authorisation_password import get_password_hash

def create_admin():
    db = session_local()
    try:
        admin = db.query(User).filter(User.login == settings.DB_USER).first()
        if not admin:
            hashed_password = get_password_hash(settings.DB_PASSWORD)
            new_admin = User(
                login=settings.DB_USER,
                is_admin = True,
                password=hashed_password
            )
            print(f'admin: ({settings.DB_USER}, {settings.DB_PASSWORD})')
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
    finally:
        db.close()
