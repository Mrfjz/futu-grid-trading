from pathlib import Path
import os
from datetime import datetime

from futu import SysConfig, OpenHKTradeContext, RET_OK, TrdSide, OrderType, OpenQuoteContext

SysConfig.set_all_thread_daemon(True)

trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)  # Create quote object

trd_ctx.unlock_trade(os.environ['PWD_UNLOCK'])


def get_latest_price(symbol):
    """
    Get the latest price

    :param symbol: a single stock stick, e.g. 'HK.07266'
    :type symbol: str
    :return: price updated time, price
    :rtype: datetime.datetime, float
    """

    ret, data = quote_ctx.get_market_snapshot(symbol)
    if ret == RET_OK:
        update_time_s = data['update_time'][0]
        update_time = datetime.strptime(update_time_s, "%Y-%m-%d %H:%M:%S")

        price = float(data['last_price'][0])
    else:
        raise ValueError("Unable to get data of {}, error={}".format(symbol, data))

    return update_time, price


def check_market_open():
    """
    Check if Hong Kong market is open

    :return: If market is open
    :rtype: bool
    """
    ret, data = quote_ctx.get_global_state()
    if ret == RET_OK:
        return data['market_hk'] in ["MORNING", "AFTERNOON"]
    else:
        raise ValueError("Unable to check if market open, error={}".format(data))


def get_position(symbol):
    """
    Get position of a stock

    :param symbol: a single stock stick, e.g. 'HK.07266'
    :type symbol: str
    :return: position
    :rtype: int
    """
    ret, data = trd_ctx.position_list_query()
    if ret == RET_OK:
        loc = data.loc[data['code'] == symbol]
        if not loc.empty:
            return int(loc['qty'])
        else:
            return 0
    else:
        raise ValueError("Unable to get position of {}, error={}".format(symbol, data))


def place_buy_market_order(symbol, quantity):
    """
    Place a buy market order

    :param symbol: a single stock stick, e.g. 'HK.07266'
    :type symbol: str
    :param quantity: the amount of the shares you want to buy
    :type quantity: int
    :return: order being placed successfully
    :rtype: bool
    """
    assert quantity > 0, "Expect quantity to be a positive integer but got {}".format(quantity)
    _, price = get_latest_price(symbol)
    ret, data = trd_ctx.place_order(price=price, qty=quantity, code=symbol, trd_side=TrdSide.BUY,
                                    order_type=OrderType.MARKET)
    if ret == RET_OK:
        return True
    else:
        raise ValueError("Unable to place buy market order, error={}".format(data))


def place_sell_market_order(symbol, quantity):
    """
    Place a sell market order

    :param symbol: a single stock stick, e.g. 'HK.07266'
    :type symbol: str
    :param quantity: the amount of the shares you want to sell
    :type quantity: int
    :return: order being placed successfully
    :rtype: bool
    """
    assert quantity > 0, "Expect quantity to be a positive integer but got {}".format(quantity)
    _, price = get_latest_price(symbol)
    ret, data = trd_ctx.place_order(price=price, qty=quantity, code=symbol, trd_side=TrdSide.SELL,
                                    order_type=OrderType.MARKET)
    if ret == RET_OK:
        return True
    else:
        raise ValueError("Unable to place sell market order, error={}".format(data))
