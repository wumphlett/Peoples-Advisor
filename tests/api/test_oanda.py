from pa.settings import api_token
from pa.api import oanda


class TestOandaAPI:
    @classmethod
    def setup_class(cls):
        cls.api = oanda.API(live=False, auth=api_token)

    def test_accounts(self):
        response = self.api.accounts()
        assert response.get('accounts')

    def test_account_details(self):
        response = self.api.account_details()
        assert response.get('account')

    def test_account_summary(self):
        response = self.api.account_summary()
        assert response.get('account')

    def test_account_instruments(self):
        response = self.api.account_instruments()
        assert response.get('instruments')

    def test_account_configure(self):
        response = self.api.account_details()
        margin_rate = response['account']['marginRate']
        response = self.api.account_configure(configure={'marginRate': margin_rate})
        assert response.get('clientConfigureTransaction')
        configured_rate = response.get('clientConfigureTransaction').get('marginRate')
        assert margin_rate == configured_rate

    def test_account_changes(self):
        response = self.api.account_changes()
        assert response.get('changes').get('transactions')

    def test_instrument_candles(self): # TODO bolster test
        response = self.api.instrument_candles('AUD_USD', count=400)
        assert response.get('candles')

    def test_instrument_order_book(self):
        response = self.api.instrument_order_book('AUD_USD')
        assert response.get('orderBook')

    def test_instrument_position_book(self):
        response = self.api.instrument_position_book('AUD_USD')
        assert response.get('positionBook')



if __name__ == '__main__':
    test_api = oanda.API(live=False, auth=api_token)
    print(test_api.instrument_candles('AUD_USD', count=500))
