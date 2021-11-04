# futu-grid-trading

Automatic [grid trading](https://www.binance.com/en/support/faq/f4c453bab89648beb722aa26634120c3) with Futu API in HK
market.

## Strategy

Unlike the normal grid trading strategy, this strategy trades two ETFs at the same time. Below demonstrate the strategy:

First let's define a few parameters.

| Parameter | Description | Value|
| --------------------------- | ----------- | -------- |
| symbol | The target stock symbol| "HK.07226" |
| ie_symbol | The inverse equity symbol, this equity always go reverse direction against the target stock. | "HK.07552" |
| grid_upper_limit_price | For the target stock, you expect the price will not be higher than this value | 6 |
| grid_lower_limit_price | For the target stock, you expect the price will not be lower than this value|  4 |
| grid_count | Number of grid, small value -> less trade and more profit per trade, large value -> more trade and less profit per trade | 10 |
| grid_lower_limit_position | The maximum position of target stock | 10000|
| ie_max_position | The maximum position of inverse equity | 6000 |

At the beginning, assume that

| Symbol | Price | Position | Value |
| --- | --- | --- | --- |
| HK.07226 | 4 | 0 | 0 | 
| HK.07552 | 10 | 0 | 0 |
| Cash | | | 50000 |
| Total asset | | | 50000 | 

Since the target stock price hit the lower limit, the strategy hold the target stock with max position. i.e. 

| Symbol | Price | Position | Value |
| --- | --- | --- | --- |
| HK.07226 | 4 | 10000 | 40000 | 
| HK.07552 | 10 | 0 | 0 |
| Cash | | | 10000 |
| Total asset | | | 50000 | 

Let the target stock price rises to 4.2, the inverse equity price falls to 9.5. Based on the strategy, 
decrease target stock position and increase inverse equity position. 

| Symbol | Price | Position | Value |
| --- | --- | --- | --- |
| HK.07226 | 4.2 | 9000 | 37800 | 
| HK.07552 | 9.5 | 600 | 5700 |
| Cash | | | 8500 (=10000 + 4.2 * 1000 - 9.5 * 600) |
| Total asset | | | 52000 | 

Let the target stock price falls back to 4, the inverse equity price raises to 10. Based on the strategy, 
increase target stock position and decrease inverse equity position. 

| Symbol | Price | Position | Value |
| --- | --- | --- | --- |
| HK.07226 | 4 | 10000 | 40000 | 
| HK.07552 | 10 | 0 | 0 |
| Cash | | | 10500 (=8500 - 4 * 1000 + 10 * 600) |
| Total asset | | | 50500 | 

As the target stock rises 5% (0.2) and falls 5% (0.2), you earn 1% revenue.

**IMPORTANT**: Since the strategy use market order for trading, the max money utilization must be under 90%. 
i.e. in the above example your cash must be greater than 45000. 

## Usage

1. Start [Futu OpenD docker](https://github.com/Mrfjz/futu-opend-docker)

2. Build image

```
docker-compose build
```

3. Test the connection with Futu OpenD

```
docker-compose run futu-grid-trading python3 scripts/test_connection.py
```

Expected output:
> test connection pass

4. Customize production configurations

```
cp examples/example.config.yml vol/prod.config.yml
nano vol/prod.config.yml
```

5. set environment variables

```
export PWD_UNLOCK=
export LOG_LEVEL=INFO
export DRY_RUN=False
```

6. Start the service

```
docker-compose up -d
```

7. Check the log file

```
tail -f ./vol/log/futu-grid-trading.log
```

Expected output:
> Futu-grid-trading started