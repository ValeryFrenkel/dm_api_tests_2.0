from dm_api_account.models.auth_error import AuthError
from dm_api_account.models.bad_request_error import BadRequestError
from dm_api_account.models.change_email import ChangeEmail
from dm_api_account.models.change_password import ChangePassword
from dm_api_account.models.general_error import GeneralError
from dm_api_account.models.registration import Registration
from dm_api_account.models.reset_password import ResetPassword
from dm_api_account.models.user_details_envelope import UserDetailsEnvelope
from dm_api_account.models.user_envelope import UserEnvelope
from restclient.client import RestClient


class AccountApi(RestClient):

    def post_v1_account(
            self,
            registration: Registration
    ):
        """
        Register new user
        :return:
        """
        response = self.post(
            path='/v1/account',
            json=registration.model_dump(exclude_none=True, by_alias=True)
        )
        if response.status_code == 400:
            return BadRequestError(**response.json())
        return response

    def get_v1_account(
            self,
            validate_response=True,
            **kwargs
    ):
        """
        Get current user
        :param validate_response:
        :param kwargs:
        :return:
        """
        response = self.get(
            path='/v1/account',
            **kwargs
        )
        if validate_response and response.status_code == 200:
            return UserDetailsEnvelope(**response.json())
        else:
            return AuthError(**response.json())

    def put_v1_account_token(
            self,
            token,
            validate_response=True,
    ):
        """
        Activate registered user
        :param validate_response:
        :param token:
        :return:
        """
        headers = {
            'accept': 'text/plain'
        }
        response = self.put(
            path=f'/v1/account/{token}',
            headers=headers
        )
        if validate_response and response.status_code == 200:
            return UserEnvelope(**response.json())
        elif response.status_code == 400 or response.status_code == 410:
            return GeneralError(**response.json())
        else:
            return response

    def post_v1_account_password(
            self,
            reset_password: ResetPassword,
            validate_response=True

    ):
        """
        Reset registered user
        :return:
        """
        response = self.post(
            path='/v1/account/password',
            json=reset_password.model_dump(exclude_none=True, by_alias=True)
        )
        if validate_response and response.status_code == 201:
            return UserEnvelope(**response.json())
        elif response.status_code == 400:
            return BadRequestError(**response.json())
        else:
            return response

    def put_v1_account_password(
            self,
            change_password: ChangePassword,
            validate_response=True
    ):
        """
        Change registered user password
        :param validate_response:
        :param change_password:
        :return:
        """
        response = self.put(
            path='/v1/account/password',
            json=change_password.model_dump(exclude_none=True, by_alias=True)
        )
        if validate_response and response.status_code == 200:
            return UserEnvelope(**response.json())
        else:
            return BadRequestError(**response.json())

    def put_v1_account_email(
            self,
            change_email: ChangeEmail,
            validate_response=True
    ):
        """
        Change registered user email
        :param validate_response:
        :param change_email
        :return:
        """
        headers = {
            'accept': 'text/plain',
            'Content-Type': 'application/json'
        }
        response = self.put(
            path='/v1/account/email',
            headers=headers,
            json=change_email.model_dump(exclude_none=True, by_alias=True)
        )
        if validate_response and response.status_code == 200:
            return UserEnvelope(**response.json())
        else:
            return BadRequestError(**response.json())
