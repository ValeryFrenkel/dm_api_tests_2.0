from dm_api_account.apis.account_api import AccountApi


def test_post_v1_account():
    account_api = AccountApi(host='http://185.185.143.231:5051')

    login = 'tony_soprano18'
    password = '12345678'
    email = f'{login}@mail.ru'

    json_data = {
        'login': login,
        'email': email,
        'password': password
    }

    response = account_api.post_v1_account(json_data=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 201, f"Пользователь не был создан, Код:{response.status_code}"