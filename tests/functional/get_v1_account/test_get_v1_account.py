def test_get_v1_account(auth_account_helper):
    auth_account_helper.dm_api_account.account_api.get_v1_account()

def test_get_v1_account_no_auth(account_helper):
    account_helper.dm_api_account.account_api.get_v1_account()