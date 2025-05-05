'''User experience testing'''
import faker
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)
fake = faker.Faker()

client.user_login = fake.user_name()
client.user_password = fake.password()
client.user_new_id = 0

def test_register_user():
    response = client.post(
        '/users/register',
        json = {
            'login': client.user_login,
            'password': client.user_password
        }
    )

    assert response.status_code == 201
    client.user_new_id = response.json()
    print(client.user_new_id)