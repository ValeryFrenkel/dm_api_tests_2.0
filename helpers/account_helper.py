import time
from json import (
    loads,
    JSONDecodeError,
)

from dm_api_account.models.change_email import ChangeEmail
from dm_api_account.models.change_password import ChangePassword
from dm_api_account.models.login_credentials import LoginCredentials
from dm_api_account.models.registration import Registration
from dm_api_account.models.reset_password import ResetPassword
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
        response = self.user_login(
            login=login,
            password=password
        )
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
        registration = Registration(
            login=login,
            email=email,
            password=password
        )

        response = self.dm_api_account.account_api.post_v1_account(registration=registration)
        assert response.status_code == 201, f"Пользователь не был создан, Код:{response.status_code}"
        return response

    def register_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        registration = Registration(
            login=login,
            email=email,
            password=password
        )

        response = self.dm_api_account.account_api.post_v1_account(registration=registration)
        assert response.status_code == 201, f"Пользователь не был создан, Код:{response.status_code}"
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        assert response.status_code == 200, "Письма не были получены"
        start_time = time.time()
        token = self.get_activation_token_by_login(login=login)
        end_time = time.time()
        assert start_time - end_time < 3, "Время ожидания активации превышено"
        assert token is not None, f'Токен для пользователя {login} не был получен'
        response = self.dm_api_account.account_api.put_v1_account_token(token=token)
        return response

    def user_login(
            self,
            login: str,
            password: str,
            remember_me: bool = True
    ):
        login_credentials = LoginCredentials(
            login=login,
            password=password,
            remember_me=remember_me
        )
        response = self.dm_api_account.login_api.post_v1_account_login(login_credentials=login_credentials,validate_response=False)
        assert response.headers["x-dm-auth-token"], "Токен для пользователя не был получен"
        assert response.status_code == 200, "Пользователь не смог авторизоваться"
        return response

    def change_user_email(
            self,
            login: str,
            password: str,
            email: str
    ):
        change_email = ChangeEmail(
            login=login,
            password=password,
            email=email
        )

        response = self.dm_api_account.account_api.put_v1_account_email(change_email=change_email)
        token = self.get_activation_token_by_login(login=login)
        assert token is not None, f'Токен для пользователя {login} не был получен'
        response = self.dm_api_account.account_api.put_v1_account_token(token=token)
        return response

    def change_user_password(
            self,
            login: str,
            email: str,
            old_password: str,
            new_password: str
    ):
        reset_password = ResetPassword(
            login=login,
            email=email
        )
        response = self.dm_api_account.account_api.post_v1_account_password(reset_password=reset_password)
        assert response.status_code == 200, "Пользователь не отправил запрос на смену пароля"
        token = self.get_reset_password_token_by_login(login=login)
        assert token is not None, f'Токен для пользователя {login} не был получен'

        change_password = ChangePassword(
            login=login,
            token=token,
            old_password=old_password,
            new_password=new_password
        )

        response = self.dm_api_account.account_api.put_v1_account_password(change_password=change_password)
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
