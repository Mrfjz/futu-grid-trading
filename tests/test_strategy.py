from lib.strategy import GridTradingStrategy


def test_position_per_grid():
    strategy = GridTradingStrategy(11, 10, 5, 10000, 20000)
    assert strategy.position_per_grid == 2000


def test_position_per_grid_cannot_be_divided():
    strategy = GridTradingStrategy(11, 10, 15, 10000, 20000)
    assert strategy.position_per_grid == 700


def test_grids():
    strategy = GridTradingStrategy(11, 10, 5, 10000, 20000)
    assert strategy.grids == [10, 10.2, 10.4, 10.6, 10.8, 11]


def test_grids_cannot_be_divided():
    strategy = GridTradingStrategy(11, 10, 3, 10000, 20000)
    assert strategy.grids == [10, 10.333, 10.667, 11]


def test_cal_grid_index_by_price():
    strategy = GridTradingStrategy(11, 10, 10, 10000, 20000)
    assert strategy.cal_grid_index_by_price(9) == 0
    assert strategy.cal_grid_index_by_price(10) == 1
    assert strategy.cal_grid_index_by_price(10.9) == 10
    assert strategy.cal_grid_index_by_price(11) == 11


def test_cal_order_quantity():
    strategy = GridTradingStrategy(11, 10, 10, 10000, 20000)
    assert strategy.cal_order_quantity(9.95, 0, 0) == (10000, 0)
    assert strategy.cal_order_quantity(10.05, 0, 0) == (9000, 2000)

    assert strategy.cal_order_quantity(10.05, 9000, 2000) == (0, 0)
    assert strategy.cal_order_quantity(10.05, 10000, 0) == (0, 0)

    assert strategy.cal_order_quantity(11.05, 0, 0) == (0, 20000)
    assert strategy.cal_order_quantity(10.95, 0, 0) == (0, 20000)

    assert strategy.cal_order_quantity(10.95, 0, 20000) == (0, 0)
    assert strategy.cal_order_quantity(10.95, 1000, 18000) == (0, 0)
