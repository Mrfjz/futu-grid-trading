from pathlib import Path
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import argparse
import re
from time import sleep

import yaml
from trade.api import *
from trade.strategy import GridTradingStrategy

logger = logging.getLogger("futu-grid-trading")
LOG_FILE = "/var/log/futu-grid-trading/futu-grid-trading.log"
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

FORMATTER = logging.Formatter(
    '%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s',
    '%d %b %Y %H:%M:%S')

SYMBOL = "HK.07226"
PRICE_ADJUST = 0.02
# IE = INVERSE_EQUITY
IE_SYMBOL = "HK.07552"
IE_PRICE_ADJUST = 0.05

DRY_RUN = os.environ.get("DRY_RUN", 'False').lower() == 'true'


def get_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--config', type=str, required=True, help='config file')
    args = vars(parser.parse_args())
    return args


def configure_logger():
    Path(LOG_FILE).parent.mkdir(exist_ok=True, parents=True)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    file_handler = TimedRotatingFileHandler(LOG_FILE, "midnight", 1, 365)
    file_handler.setFormatter(FORMATTER)
    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    logger.addHandler(file_handler)


def wait_order_filled_all(order_id, timeout=10):
    """
    Wait for the order to be filled all

    :param order_id:
    :type order_id: str
    :param timeout:
    :type timeout: float
    :return:
    :rtype: bool
    """
    sleep(1)
    if check_order_filled_all(order_id):
        return True

    sleep(timeout)
    if check_order_filled_all(order_id):
        return True
    else:
        raise TimeoutError(f"Order '{order_id}' is not filled all after {timeout} seconds")


def place_order(symbol, quantity, price, price_adjust, trade_side):
    """
    Place order with different trade side

    :param symbol: a single stock stick, e.g. 'HK.07266'
    :type symbol: str
    :param quantity: order quantity
    :type quantity: int
    :param price: current market price
    :type price: float
    :param price_adjust: the actual order place will be adjusted (increase for BUY order and decrease for SELL order)
        so the orders can be filled.
    :type price_adjust: float
    :param trade_side: ['BUY', 'SELL']
    :type trade_side: str
    :return:
    :rtype:
    """
    if trade_side == "BUY":
        price_after_adjust = price + price_adjust
    elif trade_side == "SELL":
        price_after_adjust = price - price_adjust
    else:
        raise ValueError(f"Expect trade_side to be ['BUY', 'SELL'] but got '{trade_side}'")

    logger.info(f"Placing {trade_side} order, symbol={symbol}, quantity={quantity}, price={price_after_adjust}")

    if DRY_RUN:
        logger.debug("Dry run is on, do not process")
    else:
        if trade_side == "BUY":
            order_id = place_buy_normal_order(symbol, quantity, price_after_adjust)
        elif trade_side == "SELL":
            order_id = place_sell_normal_order(symbol, quantity, price_after_adjust)
        else:
            raise ValueError(f"Expect trade_side to be ['BUY', 'SELL'] but got '{trade_side}'")

        logger.info(f"Order placed, id={order_id}")
        wait_order_filled_all(order_id)


def main(args):
    with open(args['config']) as f:
        config = yaml.safe_load(f)

    configure_logger()
    strategy = GridTradingStrategy(**config['grid_trading_strategy'])
    logger.info("Futu-grid-trading started")

    while 1:
        if check_market_open():
            assert check_all_submitted_order_filled_all(), "Not all submitted order is filled all!"

            _, price = get_latest_price(SYMBOL)
            position = get_position(SYMBOL)
            # ie = inverse equity
            _, ie_price = get_latest_price(IE_SYMBOL)
            ie_position = get_position(IE_SYMBOL)

            logger.debug(f"price={price}, position={position}, "
                         f"ie_price={ie_price}, ie_position={ie_position}, ")

            order_quantity, ie_order_quantity = strategy.cal_order_quantity(price, position, ie_position)

            logger.debug(f"order_quantity={order_quantity}, ie_order_quantity={ie_order_quantity}")

            # place sell order for equity
            if order_quantity < 0:
                place_order(SYMBOL, abs(order_quantity), price, PRICE_ADJUST, "SELL")

            # place sell order for inverse equity
            if ie_order_quantity < 0:
                place_order(IE_SYMBOL, abs(ie_order_quantity), ie_price, IE_PRICE_ADJUST, "SELL")

            # place buy order for equity
            if order_quantity > 0:
                place_order(SYMBOL, abs(order_quantity), price, PRICE_ADJUST, "BUY")

            # place buy order for inverse equity
            if ie_order_quantity > 0:
                place_order(IE_SYMBOL, abs(ie_order_quantity), ie_price, IE_PRICE_ADJUST, "BUY")

        else:
            logger.debug("Market is not open")

        sleep(10)


if __name__ == "__main__":
    main(get_args())
