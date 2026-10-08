import time
from json import (
    loads,
    JSONDecodeError,
)
from services.dm_api_account import DMApiAccount
from services.api_mailhog import MailHogApi


def retrier(
        func
):
    def wrapper(
            *args,
            **kwargs
    ):
        token = None
        count = 0
        while token is None:
            print(f"Попытка получения активационного токена номер {count}!")
            token = func(*args, **kwargs)
            count += 1
            if count == 5:
                raise AssertionError("Превышено кол-во попыток активационного токен")
            if token:
                return token
            time.sleep(1)

    return wrapper


class AccountHelper:
    def __init__(
            self,
            dm_api_account: DMApiAccount,
            mailhog: MailHogApi
    ):
        self.dm_api_account = dm_api_account
        self.mailhog = mailhog

    def auth_client(
            self,
            login: str,
            password: str
    ):
        response = self.dm_api_account.login_api.post_v1_account_login(
            json_data={
                "login": login,
                "password": password
            }
        )
        assert response.status_code == 200, "Пользователь не смог авторизоваться"
        token = {
            "x-dm-auth-token": response.headers["x-dm-auth-token"]
        }
        self.dm_api_account.account_api.set_headers(token)
        self.dm_api_account.login_api.set_headers(token)

    def create_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        json_data = {
            'login': login,
            'email': email,
            'password': password
        }

        response = self.dm_api_account.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f"Пользователь не был создан, Код:{response.status_code}"
        return response

    def register_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        json_data = {
            'login': login,
            'email': email,
            'password': password
        }

        response = self.dm_api_account.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f"Пользователь не был создан, Код:{response.status_code}"
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        assert response.status_code == 200, "Письма не были получены"
        token = self.get_activation_token_by_login(login=login)
        assert token is not None, f'Токен для пользователя {login} не был получен'
        response = self.dm_api_account.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, "Пользователь не был активирован"
        return response

    def user_login(
            self,
            login: str,
            password: str,
            remember_me: bool = True
    ):
        json_data = {
            'login': login,
            'password': password,
            'rememberMe': remember_me
        }

        response = self.dm_api_account.login_api.post_v1_account_login(json_data=json_data)
        assert response.status_code == 200, "Пользователь не смог авторизоваться"
        return response

    def change_user_email(
            self,
            login: str,
            password: str,
            email: str
    ):
        json_data = {
            'login': login,
            'password': password,
            'email': email
        }

        response = self.dm_api_account.account_api.put_v1_account_email(json_data=json_data)
        assert response.status_code == 200, "Пользователь не смог отправить запрос на смену почты"
        token = self.get_activation_token_by_login(login=login)
        assert token is not None, f'Токен для пользователя {login} не был получен'
        response = self.dm_api_account.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, "Пользователь не был активирован"
        return response

    def change_user_password(
            self,
            login: str,
            email: str,
            old_password: str,
            new_password: str
    ):
        json_data = {
            'login': login,
            'email': email
        }
        response = self.dm_api_account.account_api.post_v1_account_password(json_data=json_data)
        assert response.status_code == 200, "Пользователь не отправил запрос на смену пароля"
        token = self.get_reset_password_token_by_login(login=login)
        assert token is not None, f'Токен для пользователя {login} не был получен'

        json_data = {
            'login': login,
            'token': token,
            'oldPassword': old_password,
            'newPassword': new_password
        }

        response = self.dm_api_account.account_api.put_v1_account_password(json_data=json_data)
        assert response.status_code == 200, "Пользователь не смог изменить пароль"
        return response

    def logout_current_user(
            self
    ):
        response = self.dm_api_account.login_api.delete_v1_account_login()
        assert response.status_code == 204, "Пользователь не был разлогинен"

    def logout_from_every_device(
            self
    ):
        response = self.dm_api_account.login_api.delete_v1_account_login_all()
        assert response.status_code == 204, "Пользователь не был разлогинен"

    @retrier
    def get_activation_token_by_login(
            self,
            login,
    ):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()['items']:
            try:
                user_data = loads(item['Content']['Body'])
            except (JSONDecodeError, KeyError):
                continue
            user_login = user_data['Login']
            if user_login == login:
                token = user_data['ConfirmationLinkUrl'].split('/')[-1]
        return token

    @retrier
    def get_reset_password_token_by_login(
            self,
            login,
    ):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()['items']:
            try:
                user_data = loads(item['Content']['Body'])
            except (JSONDecodeError, KeyError):
                continue
            user_login = user_data['Login']
            if user_login == login and 'ConfirmationLinkUri' in user_data:
                token = user_data['ConfirmationLinkUri'].split('/')[-1]
        return token
