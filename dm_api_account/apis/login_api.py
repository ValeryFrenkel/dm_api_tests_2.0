from dm_api_account.models.auth_error import AuthError
from dm_api_account.models.bad_request_error import BadRequestError
from dm_api_account.models.general_error import GeneralError
from dm_api_account.models.login_credentials import LoginCredentials
from dm_api_account.models.user_envelope import UserEnvelope
from restclient.client import RestClient


class LoginApi(RestClient):

    def post_v1_account_login(
            self,
            login_credentials: LoginCredentials,
            validate_response = True

    ):
        """
        Authenticate via credentials
        :return:
        """
        response = self.post(
            path='/v1/account/login',
            json=login_credentials.model_dump(exclude_none=True, by_alias=True)
        )
        if validate_response and response.status_code == 200:
            return UserEnvelope(**response.json())
        elif response.status_code == 400:
            return BadRequestError(**response.json())
        elif response.status_code == 403:
            return GeneralError(**response.json())
        return response

    def delete_v1_account_login(
            self,
            validate_response=True
    ):
        """
        Logout as current user
        :return:
        """
        response = self.delete(
            path='/v1/account/login'
        )
        if validate_response and response.status_code == 401:
            return AuthError(**response.json())
        return response

    def delete_v1_account_login_all(
            self,
            validate_response=True
    ):
        """
        Logout from every device
        :return:
        """
        response = self.delete(
            path='/v1/account/login/all'
        )
        if validate_response and response.status_code == 401:
            return AuthError(**response.json())
        return response
