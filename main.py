import logging
from logging.handlers import TimedRotatingFileHandler
import argparse
import re
from time import sleep

import yaml
from trade.api import *
from trade.strategy import GridTradingStrategy

logger = logging.getLogger("futu-grid-trading")

FORMATTER = logging.Formatter(
    '%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s',
    '%d %b %Y %H:%M:%S')

SYMBOL = "HK.07226"
PRICE_ADJUST = 0.02
INVERSE_EQUITY_SYMBOL = "HK.07552"
INVERSE_EQUITY_PRICE_ADJUST = 0.05


def get_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--dry_run', action='store_true', default=False, help='do not place the order')
    parser.add_argument('-c', '--config', type=str, required=True, help='config file')
    args = vars(parser.parse_args())
    return args


def configure_logger(log_file, log_level="INFO"):
    """

    :param log_file:
    :type log_file: str
    :param log_level:
    :type log_level: str
    :return:
    :rtype:
    """
    Path(log_file).parent.mkdir(exist_ok=True, parents=True)
    logger.setLevel(getattr(logging, log_level))
    file_handler = TimedRotatingFileHandler(log_file, "midnight", 1, 365)
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


def main(args):
    dry_run = args['dry_run']
    with open(args['config']) as f:
        config = yaml.safe_load(f)

    configure_logger(**config['logging'])
    strategy = GridTradingStrategy(**config['grid_trading_strategy'])
    logger.info("Futu-grid-trading started")

    while 1:
        if check_market_open() and check_all_submitted_order_filled_all():
            _, price = get_latest_price(SYMBOL)
            position = get_position(SYMBOL)
            _, inverse_equity_price = get_latest_price(INVERSE_EQUITY_SYMBOL)
            inverse_equity_position = get_position(INVERSE_EQUITY_SYMBOL)

            order_quantity, inverse_equity_order_quantity = strategy.cal_order_quantity(price, position,
                                                                                        inverse_equity_position)

            logger.debug(f"price={price}, position={position}, "
                         f"inverse_equity_position={inverse_equity_position}, "
                         f"order_quantity={order_quantity}, "
                         f"inverse_equity_order_quantity={inverse_equity_order_quantity}")

            # place sell order
            if order_quantity < 0:
                order_price = price - PRICE_ADJUST
                logger.info(f"Placing sell market order, symbol={SYMBOL}, quantity={abs(order_quantity)}, "
                            f"order_price={order_price}")
                if not dry_run:
                    order_id = place_sell_normal_order(SYMBOL, abs(order_quantity), order_price)
                    logger.info("Order placed")
                    wait_order_filled_all(order_id)

            if inverse_equity_order_quantity < 0:
                order_price = inverse_equity_price - INVERSE_EQUITY_PRICE_ADJUST
                logger.info(f"Placing sell market order, symbol={INVERSE_EQUITY_SYMBOL}, "
                            f"quantity={abs(inverse_equity_order_quantity)}, order_price={order_price}")
                if not dry_run:
                    order_id = place_sell_normal_order(INVERSE_EQUITY_SYMBOL, abs(inverse_equity_order_quantity),
                                                       order_price)
                    logger.info("Order placed")
                    wait_order_filled_all(order_id)

            # place buy order
            if order_quantity > 0:
                order_price = price + PRICE_ADJUST
                logger.info(f"Placing buy market order, symbol={SYMBOL}, quantity={abs(order_quantity)} "
                            f"order_price={order_price}")
                if not dry_run:
                    order_id = place_buy_normal_order(SYMBOL, abs(order_quantity), order_price)
                    logger.info("Order placed")
                    wait_order_filled_all(order_id)

            if inverse_equity_order_quantity > 0:
                order_price = inverse_equity_price + INVERSE_EQUITY_PRICE_ADJUST
                logger.info(f"Placing buy market order, symbol={INVERSE_EQUITY_SYMBOL}, "
                            f"quantity={abs(inverse_equity_order_quantity)}, order_price={order_price}")
                if not dry_run:
                    order_id = place_buy_normal_order(INVERSE_EQUITY_SYMBOL, abs(inverse_equity_order_quantity),
                                                      order_price)
                    logger.info("Order placed")
                    wait_order_filled_all(order_id)
        else:
            logger.debug("Market is not open")

        sleep(10)


if __name__ == "__main__":
    main(get_args())
