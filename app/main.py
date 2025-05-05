'''Starting service'''

from fastapi import FastAPI

from .database.db import engine
from .database.models import Base
from .utils.init_admin import create_admin
from .routes import account, greeting, statistic, transaction, user

app = FastAPI(
    title="Система управления финансами",
    description="Простейшая система управления финансами, основанная на "
                "фреймворке FastAPI. Дает возможность как вести запись "
                "транзакций, так и проводить анализ этих записей",
    version="1.0.1",
    contact={
        "name": "Уразаева Рената Рустемовна",
        "url": "https://vk.com/reno_logann",
        "email": "urazaeva.rr@phystech.edu"
    }
)


Base.metadata.create_all(bind=engine)


create_admin()


app.include_router(greeting.router)
app.include_router(user.router)
app.include_router(account.router)
app.include_router(transaction.router)
app.include_router(statistic.router)
