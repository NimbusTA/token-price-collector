# nimbus-token-price-collector

The service that daily collects token prices (DOT, GLMR, KSM, MOVR) from coingecko.

The URL matches the pattern: `https://api.coingecko.com/api/v3/coins/<token>/history?date=<date>&localization=false`, where the `<token>` is replaced with the network's name and the `<date>` is replaced with a required date.

Default Prometheus metrics are available at `0.0.0.0:{API_PORT}/metrics`.


## Requirements
* Python 3.9


## Setup
```shell
pip install -r requirements.txt
```


## Run
The service receives its configuration parameters from environment variables. Export required parameters from the list below and start the service:
```shell
python3 ./token-price-collector/main.py
```

To stop the service, send the SIGINT or SIGTERM signal to the process.


## Configuration parameters
#### Required
* `DATABASE_URL` - Example: `postgres://admin:1234@localhost:5432/token-price-collector`.

#### Optional
* `API_PORT` - The port at which Prometheus metrics are exposed. The default value is `8000`.
* `INITIAL_DATE` - The date from which the token price collection begins. Strict format: <b>dd-mm-yyyy</b>. The default value is `01-01-2023`.
* `LOG_LEVEL` - The logging level of the logging module: `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`. The default value is `INFO`.
* `MAX_REQUEST_ATTEMPTS` - The default value is `2`.
* `TIMEOUT` - Time (in seconds) between cycles during getting token prices in case of fail. The default value is `600`.
