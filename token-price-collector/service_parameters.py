"""This module contains the ServiceParameters class implementation and constants."""
import logging
import os
from datetime import datetime

import log

from database_manager import DatabaseManager


DEFAULT_API_PORT = '8000'
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_MAX_REQUEST_ATTEMPTS = '2'
DEFAULT_INITIAL_DATE = '01-01-2023'
DEFAULT_PROMETHEUS_METRICS_PREFIX = 'token_price_collector_'
DEFAULT_TIMEOUT = '600'

TOKEN_PRICE_URL = 'https://api.coingecko.com/api/v3/coins/<token>/history?date=<date>&localization=false'

LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

logger = logging.getLogger(__name__)


class ServiceParameters:
    """Service parameters for the TokenPriceCollector and the DatabaseManager classes."""
    api_port: int
    database_url: str
    initial_date: str
    max_request_attempts: int
    metrics_prefix: str
    timeout: int
    token_price_url_dot: str
    token_price_url_glmr: str
    token_price_url_ksm: str
    token_price_url_movr: str

    def __init__(self):
        log_level = os.getenv('LOG_LEVEL', DEFAULT_LOG_LEVEL)
        self._check_log_level(log_level)
        log.init_log(log_level)

        logger.info("Checking configuration parameters")

        logger.info("[ENV] LOG_LEVEL: %s", log_level)

        self.max_request_attempts = int(os.getenv('MAX_REQUEST_ATTEMPTS', DEFAULT_MAX_REQUEST_ATTEMPTS))
        assert self.max_request_attempts > 0, "The 'MAX_REQUEST_ATTEMPTS' parameter must be a positive integer"
        logger.info("[ENV] MAX_REQUEST_ATTEMPTS: %s", self.max_request_attempts)

        self.token_price_url_dot = TOKEN_PRICE_URL.replace('<token>', 'polkadot')
        logger.info("[dot] URL: %s", self.token_price_url_dot)
        self.token_price_url_glmr = TOKEN_PRICE_URL.replace('<token>', 'moonbeam')
        logger.info("[glmr] URL: %s", self.token_price_url_glmr)
        self.token_price_url_ksm = TOKEN_PRICE_URL.replace('<token>', 'kusama')
        logger.info("[ksm] URL: %s", self.token_price_url_ksm)
        self.token_price_url_movr = TOKEN_PRICE_URL.replace('<token>', 'moonriver')
        logger.info("[movr] URL: %s", self.token_price_url_movr)

        self.initial_date = os.getenv('INITIAL_DATE', DEFAULT_INITIAL_DATE)
        try:
            datetime.strptime(self.initial_date, "%d-%m-%Y")
        except ValueError as exc:
            raise ValueError("The 'INITIAL_DATE' parameter is incorrect. An appropriate format: dd-mm-yyyy") from exc
        logger.info("[ENV] INITIAL_DATE: %s", self.initial_date)

        self.timeout = int(os.getenv('TIMEOUT', DEFAULT_TIMEOUT))
        assert self.timeout >= 0, "The 'TIMEOUT' parameter must be a non-negative integer"
        logger.info("[ENV] TIMEOUT: %s", self.timeout)

        logger.info("[ENV] Get 'API_PORT'")
        self.api_port = int(os.getenv('API_PORT', DEFAULT_API_PORT))
        logger.info("[ENV] 'API_PORT': %s", self.api_port)

        logger.info("[ENV] Get 'PROMETHEUS_METRICS_PREFIX'")
        self.metrics_prefix = os.getenv('PROMETHEUS_METRICS_PREFIX', DEFAULT_PROMETHEUS_METRICS_PREFIX)
        logger.info("[ENV] 'PROMETHEUS_METRICS_PREFIX': %s", self.metrics_prefix)

        logger.info("Checking the configuration parameters for the database")
        self.database_url = os.getenv('DATABASE_URL')
        assert self.database_url, "The 'DATABASE_URL' parameter is not provided"
        DatabaseManager.try_to_establish_connection(self.database_url)
        logger.info("Configuration parameters for the database checked")

        logger.info("Successfully checked configuration parameters")

    @staticmethod
    def _check_log_level(log_level: str):
        """Check the logger level based on the default list."""
        if log_level not in LOG_LEVELS:
            raise ValueError(f"Valid 'LOG_LEVEL' values: {LOG_LEVELS}")
