"""This module contains the TokenPriceCollector implementation and necessary parameters for its working."""
from datetime import datetime, timedelta

import logging
import sys
import threading
import time
import requests

from database_manager import DatabaseManager


logger = logging.getLogger(__name__)

SECOND = 1


class TokenPriceCollector(threading.Thread):
    """Initialize a thread with a defined URL to retrieve a price for the specific token and save it to the database."""
    def __init__(self, database_manager: DatabaseManager, initial_date: str, max_request_attempts: int,
                 symbol: str, timeout: int, token_price_url: str):
        threading.Thread.__init__(self)
        self.database_manager = database_manager
        self.date = initial_date
        self.lock = threading.Lock()
        self.max_request_attempts = max_request_attempts
        self.stop = False
        self.symbol = symbol
        self.timeout = timeout
        self.token_price_url = token_price_url

    def run(self):
        """Start scraping the token price since an initial date"""
        wrote_in_logs = False

        while True:
            with self.lock:
                if self.stop:
                    sys.exit()

            url = self.token_price_url.replace("<date>", self.date)
            token_price = self.database_manager.get_token_price(self.symbol, self.date)

            if token_price:
                date_prev = self.date
                self.date = self._get_next_day()
                if self.date == date_prev and not wrote_in_logs:
                    logger.info("[%s] Waiting for the next day", self.symbol)
                    wrote_in_logs = True
                continue
            wrote_in_logs = False

            logger.info("[%s] Making a request to retrieve the token price: %s", self.symbol, url)
            token_price = None
            for i in range(self.max_request_attempts):
                try:
                    response = requests.get(url, timeout=self.timeout)
                    token_price = float(response.json()['market_data']['current_price']['usd'])
                    self.database_manager.insert_token_price(self.symbol, self.date, token_price)
                    self.date = self._get_next_day()
                    self._wait(SECOND)
                    break
                except Exception as exc:
                    logger.warning("[%s] Failed to get token price, attempt %s. %s: %s", self.symbol, i + 1, self.date, exc)
                self._wait(SECOND)

            if token_price is None:
                logger.warning("[%s] Failed to get the token price for the %s", self.symbol, self.date)
                logger.info("[%s] Sleep for %s seconds", self.symbol, self.timeout)
                self._wait(self.timeout)

    def _get_next_day(self) -> str:
        """Get the next day in the 'dd-mm-yyyy' format"""
        today = datetime.strptime(self.date, "%d-%m-%Y")
        tomorrow = today + timedelta(days=1)
        if datetime.now() < tomorrow:
            logger.debug("The next day has not started yet")
            return datetime.strftime(today, "%d-%m-%Y")

        return datetime.strftime(tomorrow, "%d-%m-%Y")

    def _wait(self, seconds: int):
        """Wait for N seconds """
        # to prevent spam
        if seconds == SECOND:
            logger.debug("Waiting for %s seconds", seconds)
        else:
            logger.info("Waiting for %s seconds", seconds)

        for _ in range(seconds):
            with self.lock:
                if self.stop:
                    sys.exit()
            time.sleep(SECOND)
