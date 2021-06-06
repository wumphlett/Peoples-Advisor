import pytest
from peoples_advisor.settings import API_TOKEN
from peoples_advisor.api.oanda.oanda_api import API, OandaError


class TestOandaAPI:
    @classmethod
    def setup_class(cls):
        cls.api = API(live=False, auth=API_TOKEN)

    def test_accounts(self):
        response = self.api.get_accounts()
        assert response.get('accounts')

    def test_account_details(self):
        response = self.api.get_account_details()
        assert response.get('account')

    def test_account_summary(self):
        response = self.api.get_account_summary()
        assert response.get('account')

    def test_account_instruments(self):
        response = self.api.get_account_instruments()
        assert response.get('instruments')
        response = self.api.get_account_instruments(['EUR_USD', 'GBP_USD'])
        assert response.get('instruments')

    def test_account_changes(self):
        last_transaction_id = self.api.get_transactions()['lastTransactionID']
        response = self.api.get_account_changes(last_transaction_id)
        assert response.get('changes')

    def test_configure_account(self):
        with pytest.raises(OandaError):
            self.api.configure_account()
        response = self.api.get_account_details()
        margin_rate = response['account']['marginRate']
        alias = response['account']['alias']
        response = self.api.configure_account(margin_rate=margin_rate, alias=alias)
        assert response.get('clientConfigureTransaction')
