from datetime import datetime
from lib.api import *


def test_get_price():
    dt, price = get_latest_price("HK.07200")
    assert type(dt) == datetime
    assert price > 0


def test_get_position():
    assert get_position("HK.07200") >= 0
