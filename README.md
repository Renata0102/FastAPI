---

# Система управления финансами на FastAPI

## Описание проекта

Простая система для учета финансовых операций, управления счетами и анализа транзакций. Реализована на FastAPI с использованием SQLite в качестве базы данных. Поддерживает регистрацию пользователей, создание счетов, проведение транзакций и просмотр статистики.

## Технологии

- FastAPI — фреймворк для создания API

- SQLAlchemy — ORM для работы с базой данных

- SQLite — база данных (можно настроить другую через .env)

- Pydantic — валидация данных

- Passlib — хеширование паролей

- JWT — аутентификация с помощью токенов

## Установка и запуск

### Предварительные требования

- Python 3.7+

- Установленные зависимости из файла requirements.txt

### Шаги

1. Клонируйте репозиторий:

```bash
git clone <ваш-репозиторий>

cd <папка-проекта>
```

2. Создайте и настройте файл .env в папке app/ на основе примера:

```python
DB_URL=sqlite:///./app/wallet.db

DB_NAME=fast_api

DB_USER=admin

DB_PASSWORD=my_super_password

ACCESS_DAYS=30

SECRET_KEY=ваш-секретный-ключ

ALGORITHM=HS256
```

Примечание: DB_USER и DB_PASSWORD используются для создания администратора приложения. Создание происходит автоматически при первом запуске приложения.

Примечание: Если при запуске возникает ошибка .env файла, проблема скорее всего заключается в задании пути в файле app/utils/config.py

3. Запустите приложение:


uvicorn app.main:app --reload


4. После запуска откройте документацию API:

- Swagger UI: http://localhost:8000/docs

- ReDoc: http://localhost:8000/redoc

## Примеры использования API

### Регистрация пользователя

```
curl -X POST "http://localhost:8000/users/register" -H "Content-Type: application/json" -d '{"login": "user123", "password": "password123"}'
```

### Получение токена доступа

```
curl -X GET "http://localhost:8000/users/get-token" -u "user123:password123"
```

### Создание счета

```
curl -X POST "http://localhost:8000/accounts/" -H "Authorization: Bearer <ваш-токен>" -H "Content-Type: application/json" -d '{"account_name": "Основной счет", "amount": 1000.0, "user_id": 1}'
```

### Проведение транзакции

```
curl -X POST "http://localhost:8000/transactions/" -H "Authorization: Bearer <ваш-токен>" -H "Content-Type: application/json" -d '{"amount": -150.0, "category": "Products", "user_id": 1, "account_id": 1}'
```

### Получение статистики

```
curl -X GET "http://localhost:8000/stats/user-balances/1" -H "Authorization: Bearer <ваш-токен>"
```

## Тестирование

Для запуска тестов используйте pytest:

```
pytest app/tests/test_user.py
```

## Контакты

Автор: Уразаева Рената Рустемовна

Email: urazaeva.rr@phystech.edu
