api_version = 'v3'
practice_url = 'https://api-fxpractice.oanda.com'
live_url = 'https://api-fxtrade.oanda.com'
# TODO timeout? Env variable timeout?

from datetime import datetime
from pa.api.oanda_endpoints.account import *
from pa.api.oanda_endpoints.instrument import *
from pa.api.oanda_endpoints.order import *
from pa.api.oanda_endpoints.position import *
from pa.api.oanda_endpoints.trade import *
from pa.api.oanda_endpoints.transaction import *

# TODO api exceptions, trade object, make objects to replace complex dicts
class API: # TODO type hinting, replace order_dicts with an Order object for clearer use
    CLOSE = 'ALL'
    LEAVE_OPEN = 'NONE'

    def __init__(self, live=False, auth='', account_index=0):
        self.live = live
        self.auth = auth
        self.account_id = self.accounts()['accounts'][account_index]['id']
        self.last_checked_transaction = self.account_summary()['account']['lastTransactionID']

    def accounts(self):
        return get_accounts(self.live, self.auth)

    def account_details(self):
        return get_account_details(self.live, self.auth, self.account_id)

    def account_summary(self):
        return get_account_summary(self.live, self.auth, self.account_id)

    def account_instruments(self):
        return get_account_instruments(self.live, self.auth, self.account_id)

    def account_configure(self, configure):
        return patch_account_configure(self.live, self.auth, self.account_id, configure)

    def account_changes(self):
        response = get_account_changes(self.live, self.auth, self.account_id, self.last_checked_transaction)
        self.last_checked_transaction = response['lastTransactionID']
        return response

    # TODO refactor, determine viable arguments
    def instrument_candles(self, instrument, count=None, granularity=None, start=None, end=None, params=None):
        if (not count and not start) or (end and not start):
            raise Exception
        if start and type(start) == str:
            start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%f')
        if end and type(end) == str:
            end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%f')
        granularity = 'S5' if not granularity else granularity
        if not count:
            convert_to_seconds = {
                'S': 1,
                'M': 60,
                'H': 60 * 60,
                'D': 24 * 60 * 60,
                'W': 7 * 24 * 60 * 60,
                'Mo': 30 * 24 * 60 * 60
            }
            end = datetime.now()
            convert = convert_to_seconds.get(granularity[0]) if granularity != 'M' else convert_to_seconds.get('Mo')
            if len(granularity) > 1:
                convert *= int(granularity[1])
            count = int((end - start).total_seconds() // convert)
        if count > 5000:
            running_count = 0
            candles = {'instrument': instrument, 'granularity': granularity, 'candles': []}
            if start:
                while running_count < count:
                    step = 4000 if count - running_count > 4000 else count - running_count
                    params = self._get_instrument_candles_params(step, granularity, start, end, params)
                    response = get_instrument_candles(self.live, self.auth, instrument, params)
                    candles['candles'].extend(response.get('candles'))
                    running_count += len(response.get('candles'))
                    index = candles['candles'][-1]['time'].index('.') + 3
                    start = datetime.strptime(candles['candles'][-1]['time'][:index], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                # TODO determine if there's a way to walkback the count
                raise Exception
        else:
            params = self._get_instrument_candles_params(count, granularity, start, end, params)
            candles = get_instrument_candles(self.live, self.auth, instrument, params)
        return candles

    @staticmethod
    def _get_instrument_candles_params(count=None, granularity=None, start=None, end=None, params=None):
        params = params if params else {}
        if count:
            params['count'] = count
        if granularity:
            params['granularity'] = granularity
        if start:
            params['start'] = start.strftime('%Y-%m-%dT%H:%M:%S.%f')
        if end:
            params['end'] = end.strftime('%Y-%m-%dT%H:%M:%S.%f')
        return params

    def instrument_order_book(self, instrument, date=None):
        params = {'time': date.strftime('%Y-%m-%dT%H:%M:%S.%f')} if date else None
        return get_instrument_order_book(self.live, self.auth, instrument, params)

    def instrument_position_book(self, instrument, date=None):
        params = {'time': date.strftime('%Y-%m-%dT%H:%M:%S.%f')} if date else None
        return get_instrument_position_book(self.live, self.auth, instrument, params)

    def orders(self, params=None):
        return get_orders(self.live, self.auth, self.account_id, params)

    def create_order(self, order_dict):
        return post_orders(self.live, self.auth, self.account_id, order_dict)

    def cancel_order(self, order_id):
        return put_order_cancel(self.live, self.auth, self.account_id, order_id)

    def replace_order(self, order_id, order_dict):
        return put_order_replacement(self.live, self.auth, self.account_id, order_id, order_dict)

    def pending_orders(self):
        return get_pending_orders(self.live, self.auth, self.account_id)

    def order_details(self, order_id):
        return get_order_details(self.live, self.auth, self.account_id, order_id)

    def trades(self):
        return get_trades(self.live, self.auth, self.account_id)

    def open_trades(self):
        return get_open_trades(self.live, self.auth, self.account_id)

    def trade_details(self, trade_id):
        return get_trade_details(self.live, self.auth, self.account_id, trade_id)

    def close_trade(self, trade_id, close=CLOSE):
        close_dict = {'units': str(close)}
        return put_close_trade(self.live, self.auth, self.account_id, trade_id, close_dict)

    def modify_trade_orders(self, trade_id, order_dict):
        return put_modify_trade_orders(self.live, self.auth, self.account_id, trade_id, order_dict)

    def transactions(self, params=None):
        return get_transactions(self.live, self.auth, self.account_id, params)

    def transaction_details(self, transaction_id):
        return get_transaction_details(self.live, self.auth, self.account_id, transaction_id)

    def transactions_range(self, from_id, to_id, params=None):
        params = {} if not params else params
        params['from'] = from_id
        params['to'] = to_id
        return get_transactions_range(self.live, self.auth, self.account_id, params)

    def transactions_since(self, since_id, params=None):
        params = {} if not params else params
        params['id'] = since_id
        return get_transactions_since(self.live, self.auth, self.account_id, params)

    def transactions_stream(self):
        pass
        # TODO https://github.com/mhallsmoore/qsforex/blob/master/data/streaming.py

    def positions(self):
        return get_positions(self.live, self.auth, self.account_id)

    def open_positions(self):
        return get_open_positions(self.live, self.auth, self.account_id)

    def instrument_position(self, instrument):
        return get_instrument_position(self.live, self.auth, self.account_id, instrument)

    def close_position(self, instrument, long_close=CLOSE, short_close=CLOSE):
        close_dict = {'longUnits': str(long_close), 'shortUnits': str(short_close)}
        return put_close_position(self.live, self.auth, self.account_id, instrument, close_dict)

