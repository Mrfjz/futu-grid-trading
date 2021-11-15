import logging
from bisect import bisect_right

logger = logging.getLogger("futu-grid-trading")


class GridTradingStrategy:
    def __init__(self, grid_upper_limit_price, grid_lower_limit_price, grid_count, grid_lower_limit_position,
                 ie_max_position, lot_size, ie_lot_size):
        """

        :param grid_upper_limit_price:
        :type grid_upper_limit_price: float
        :param grid_lower_limit_price:
        :type grid_lower_limit_price: float
        :param grid_count: total number of grids
        :type grid_count: int
        :param grid_lower_limit_position: the position when grid is below the lower limit
        :type grid_lower_limit_position: int
        :param ie_max_position:
        :type ie_max_position: int
        :param lot_size: lot size
        :type lot_size: int
        :param ie_lot_size: inverse equity lot size
        :type ie_lot_size: int
        """
        assert grid_count >= 1 and type(grid_count) is int
        assert grid_upper_limit_price > grid_lower_limit_price

        factor = grid_count * lot_size
        assert grid_lower_limit_position % factor == 0, "Expect grid_lower_limit_position to be divisible by {}" \
                                                        " but got {}".format(factor, grid_lower_limit_position)
        ie_factor = grid_count * ie_lot_size
        assert ie_max_position % ie_factor == 0, "Expect ie_max_position to be divisible by {}" \
                                                 " but got {}".format(ie_factor, ie_max_position)

        price_diff = (grid_upper_limit_price - grid_lower_limit_price) / grid_count
        self.grids = []
        for i in range(grid_count + 1):
            price = round(grid_lower_limit_price + price_diff * i, 3)
            self.grids.append(price)

        self.position_per_grid = grid_lower_limit_position / grid_count
        self.ie_position_per_grid = ie_max_position / grid_count

        self.lot_size = lot_size
        self.ie_lot_size = ie_lot_size
        self.grid_count = grid_count

        logger.debug(f"lot_size={lot_size}, ie_lot_size={ie_lot_size}, "
                     f"grid_lower_limit_position={grid_lower_limit_position}, ie_max_position={ie_max_position}, "
                     f"position_per_grid={self.position_per_grid}, ie_position_per_grid={self.ie_position_per_grid}")

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

    def cal_order_quantity(self, price, position, ie_position):
        """
        calculate the order quantity and inverse equity order quantity

        :param price: current stock price
        :type price: float
        :param position: current stock position
        :type position: int
        :param ie_position: current inverse equity position
        :type ie_position: int
        :return: order quantity, inverse equity order quantity. Positive means buy, negative means sell, zero means
            do nothing
        :rtype: int, int
        """
        grid_index = self.cal_grid_index_by_price(price)
        min_grid_position = (self.grid_count - grid_index) * self.position_per_grid
        max_grid_position = min_grid_position + self.position_per_grid

        if position < min_grid_position:
            new_position = min_grid_position
        elif position > max_grid_position:
            new_position = max_grid_position
        else:
            new_position = position

        order_quantity = int(new_position - position)

        logger.debug(f"grid_index={grid_index}, min_grid_position={min_grid_position}, "
                     f"max_grid_position={max_grid_position}, new_position={new_position}, "
                     f"order_quantity={order_quantity}")

        ie_grid_index = round(self.grid_count - new_position / self.position_per_grid)
        ie_new_position = ie_grid_index * self.ie_position_per_grid
        ie_order_quantity = int(ie_new_position - ie_position)

        logger.debug(
            f"ie_grid_index={ie_grid_index}, ie_new_position={ie_new_position}, ie_order_quantity={ie_order_quantity}")

        return order_quantity, ie_order_quantity
