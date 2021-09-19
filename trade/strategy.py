import logging
from bisect import bisect_right

logger = logging.getLogger("futu-grid-trading")


def round_hundred(x):
    """
    Round a number to nearest 100

    :param x: number to be rounded
    :type x: float
    :return: rounded number
    :rtype: int
    """
    return int(round(x / 100.0)) * 100


class GridTradingStrategy:
    def __init__(self, grid_upper_limit_price, grid_lower_limit_price, grid_count, grid_lower_limit_position,
                 inverse_equity_max_position):
        """

        :param grid_upper_limit_price:
        :type grid_upper_limit_price: float
        :param grid_lower_limit_price:
        :type grid_lower_limit_price: float
        :param grid_count: total number of grids
        :type grid_count: int
        :param grid_lower_limit_position: the position when grid is below the lower limit
        :type grid_lower_limit_position: int
        :param inverse_equity_max_position:
        :type inverse_equity_max_position: int
        """

        assert grid_count >= 1 and type(grid_count) is int
        assert grid_upper_limit_price > grid_lower_limit_price
        assert grid_lower_limit_position > grid_count * 100
        assert inverse_equity_max_position > grid_count * 100

        price_diff = (grid_upper_limit_price - grid_lower_limit_price) / grid_count
        self.grids = []
        for i in range(grid_count + 1):
            price = round(grid_lower_limit_price + price_diff * i, 3)
            self.grids.append(price)

        self.grid_count = grid_count
        self.inverse_equity_max_position = inverse_equity_max_position
        self.position_per_grid = round_hundred(grid_lower_limit_position / grid_count)
        self.inverse_equity_position_per_grid = round_hundred(inverse_equity_max_position / grid_count)

    def cal_grid_index_by_price(self, price):
        """
        calculate which grid the price falls in

        :param price: current stock price
        :type price: float
        :return: grid index
        :rtype: int
        """
        grid_index = bisect_right(self.grids, price)
        return grid_index

    def cal_order_quantity(self, price, position, inverse_equity_position):
        """
        calculate the order quantity and inverse equity order quantity

        :param price: current stock price
        :type price: float
        :param position: current stock position
        :type position: int
        :param inverse_equity_position: current inverse equity position
        :type inverse_equity_position: int
        :return: order quantity, inverse equity order quantity. Positive means buy, negative means sell, zero means
            do nothing
        :rtype: int, int
        """
        grid_index = self.cal_grid_index_by_price(price)
        min_grid_position = round_hundred((self.grid_count - grid_index) * self.position_per_grid)
        max_grid_position = min_grid_position + self.position_per_grid

        if position < min_grid_position:
            new_position = min_grid_position
        elif position > max_grid_position:
            new_position = max_grid_position
        else:
            new_position = position

        order_quantity = new_position - position

        logger.debug(f"grid_index={grid_index}, min_grid_position={min_grid_position}, "
                     f"max_grid_position={max_grid_position}, new_position={new_position}, "
                     f"order_quantity={order_quantity}")

        inverse_equity_grid_index = (self.grid_count - new_position / self.position_per_grid)
        inverse_equity_new_position = inverse_equity_grid_index * self.inverse_equity_position_per_grid
        inverse_equity_order_quantity = inverse_equity_new_position - inverse_equity_position

        logger.debug(f"inverse_equity_grid_index={inverse_equity_grid_index}, "
                     f"inverse_equity_new_position={inverse_equity_new_position}, "
                     f"inverse_equity_order_quantity={inverse_equity_order_quantity}")

        return order_quantity, inverse_equity_order_quantity
