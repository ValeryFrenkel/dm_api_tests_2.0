import structlog
from restclient.configuration import Configuration as MailHogConfiguration
from helpers.account_helper import AccountHelper
from restclient.configuration import Configuration as DmApiConfiguration
from services.api_mailhog import MailHogApi
from services.dm_api_account import DMApiAccount

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(
            indent=4,
            ensure_ascii=True,
            # sort_keys=True
        )
    ]
)


def test_post_v1_account():
    dm_api_configuration = DmApiConfiguration(host='http://185.185.143.231:5051', disable_log=False)
    mailhog_configuration = MailHogConfiguration(host='http://185.185.143.231:5025', disable_log=False)

    account = DMApiAccount(configuration=dm_api_configuration)
    mailhog = MailHogApi(configuration=mailhog_configuration)

    account_helper = AccountHelper(dm_api_account=account, mailhog=mailhog)

    login = 'tony_soprano52'
    password = '12345678'
    email = f'{login}@mail.ru'

    account_helper.create_new_user(login=login,password=password,email=email)