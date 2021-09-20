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
INVERSE_EQUITY_SYMBOL = "HK.07552"


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


def main(args):
    dry_run = args['dry_run']
    with open(args['config']) as f:
        config = yaml.safe_load(f)

    configure_logger(**config['logging'])
    strategy = GridTradingStrategy(**config['grid_trading_strategy'])
    logger.info("Futu-grid-trading started")

    while 1:
        if check_market_open():
            _, price = get_latest_price(SYMBOL)
            position = get_position(SYMBOL)
            inverse_equity_position = get_position(INVERSE_EQUITY_SYMBOL)

            order_quantity, inverse_equity_order_quantity = strategy.cal_order_quantity(price, position,
                                                                                        inverse_equity_position)

            logger.debug(f"price={price}, position={position}, "
                         f"inverse_equity_position={inverse_equity_position}, "
                         f"order_quantity={order_quantity}, "
                         f"inverse_equity_order_quantity={inverse_equity_order_quantity}")

            # place sell market order
            if order_quantity < 0:
                logger.info(f"Placing sell market order, symbol={SYMBOL}, quantity={abs(order_quantity)}")
                if not dry_run:
                    place_sell_market_order(SYMBOL, abs(order_quantity))
                    logger.info("Order placed")

            if inverse_equity_order_quantity < 0:
                logger.info(f"Placing sell market order, symbol={INVERSE_EQUITY_SYMBOL}, "
                            f"quantity={abs(inverse_equity_order_quantity)}")
                if not dry_run:
                    place_sell_market_order(INVERSE_EQUITY_SYMBOL, abs(inverse_equity_order_quantity))
                    logger.info("Order placed")

            # place buy market order
            if order_quantity > 0:
                logger.info(f"Placing buy market order, symbol={SYMBOL}, quantity={abs(order_quantity)}")
                if not dry_run:
                    place_buy_market_order(SYMBOL, abs(order_quantity))
                    logger.info("Order placed")

            if inverse_equity_order_quantity > 0:
                logger.info(f"Placing buy market order, symbol={INVERSE_EQUITY_SYMBOL}, "
                            f"quantity={abs(inverse_equity_order_quantity)}")
                if not dry_run:
                    place_buy_market_order(INVERSE_EQUITY_SYMBOL, abs(inverse_equity_order_quantity))
                    logger.info("Order placed")
        else:
            logger.debug("Market is not open")

        sleep(10)


if __name__ == "__main__":
    main(get_args())
