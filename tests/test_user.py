from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'not.existing@mail.com'})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'Sidor Sidorov',
        'email': 's.sidorov@mail.com'
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    assert isinstance(response.json(), int)

    # Проверим, что пользователь действительно создался
    response_check = client.get("/api/v1/user", params={'email': new_user['email']})
    assert response_check.status_code == 200
    assert response_check.json()['name'] == new_user['name']
    assert response_check.json()['email'] == new_user['email']


def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_user = users[0]
    response = client.post("/api/v1/user", json={
        'name': 'Duplicate User',
        'email': existing_user['email']
    })
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}


def test_delete_user():
    '''Удаление пользователя'''
    # Сначала создаём пользователя, которого потом удалим
    temp_user = {
        'name': 'To Be Deleted',
        'email': 'delete.me@mail.com'
    }
    client.post("/api/v1/user", json=temp_user)

    # Удаляем
    response = client.delete("/api/v1/user", params={'email': temp_user['email']})
    assert response.status_code == 204

    # Проверяем, что он больше не существует
    response_check = client.get("/api/v1/user", params={'email': temp_user['email']})
    assert response_check.status_code == 404