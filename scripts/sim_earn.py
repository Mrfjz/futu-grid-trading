import argparse


def get_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-d', '--data_file', type=str, required=True, help='stock historic price data file')
    args = vars(parser.parse_args())
    return args


def main(args):
    with open(args['data_file']) as f:
        data = f.read().splitlines()
        # remove the header
        # Date,Open,High,Low,Close,Adj Close,Volume
        data = data[1:]

    prev_close = None
    arr = []
    for line in data:
        if "null" in line:
            continue
        date, _open, high, low, close, adj_close, volume = line.split(",")
        _open = float(_open)
        high = float(high)
        low = float(low)
        close = float(close)
        volume = float(volume)
        if volume == 0:
            continue

        if prev_close is None:
            prev_close = close
            continue

        open_vs_prev_close = (_open - prev_close) / prev_close
        high_vs_open = (high - _open) / _open
        low_vs_open = (low - _open) / _open
        close_vs_open = (close - _open) / _open
        arr.append([open_vs_prev_close, high_vs_open, low_vs_open, close_vs_open])
        prev_close = close

    profit = 0
    count = 0
    stop_losses = 0.1
    total_count = 0
    for d in arr:
        open_vs_prev_close, high_vs_open, low_vs_open, close_vs_open = d
        # If the open vs close price is -5%
        if open_vs_prev_close < -0.05:
            # We will sell the stock when its price is lower than X% (short selling)
            take_profit = 0.02
        # If the open vs close price is +5%
        elif open_vs_prev_close > 0.05:
            # We will sell the stock when its price is lower than X% (short selling)
            take_profit = 0.012
        # If the open vs close price less than 0%
        elif open_vs_prev_close < 0:
            # We will sell the stock when its price is lower than X% (short selling)
            take_profit = 0.012
        else:
            # take_profit = 0.01
            # do nothing
            continue

        # Within this day, if the stock price each the tack_profit
        if low_vs_open <= -take_profit:
            profit += take_profit
            count += 1
        else:
            # At the end of the day or if the stock price drop too much, we will sell all the stock.
            # e.g close_vs_open might be 4%, -2% (if the take_profit is 3%), etc.
            # At the worse case, close_vs_open is greater than stop_losses(10%) so the loss will be 10%
            loss = min(stop_losses, high_vs_open)
            profit -= loss

        total_count += 1

    print("profit trade: {}/{}".format(count, total_count))
    print("profit: {}".format(profit))


if __name__ == "__main__":
    main(get_args())
