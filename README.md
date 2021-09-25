# futu-grid-trading

Automatic [grid trading](https://www.binance.com/en/support/faq/f4c453bab89648beb722aa26634120c3) with Futu API


## Usage

Build image 
```
docker-compose build
```

Make sure [Futu-OpenD](https://github.com/Mrfjz/futu-opend-docker) is running, and the connection is ok.
```
docker-compose run futu-grid-trading python3 /opt/futu-grid-trading/bin/test_connection.py
```

Create and customize your own production config file
```
cp examples/example.config.yml vol/prod.config.yml
```

Create and customize .env file
```
cp examples/example.env .env
```

Start the service
```
docker-compose up -d
```

Check the log file
```
tail -f ./vol/log/futu-grid-trading.log
```
