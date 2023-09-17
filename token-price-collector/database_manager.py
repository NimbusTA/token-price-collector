"""This module contains the DatabaseManager class that is required by the TokenPriceCollector."""
from threading import Lock

import logging
import psycopg2


logger = logging.getLogger(__name__)

EXPECTED_POSTGRES_EXCEPTIONS = (
    psycopg2.errors.DuplicateObject,
    psycopg2.errors.DuplicateTable,
    psycopg2.errors.InFailedSqlTransaction,
)


class DatabaseManager:
    """A class that provides the methods to insert and get token prices from the PostgreSQL database."""
    conn: psycopg2.extensions.connection
    cursor: psycopg2.extensions.cursor
    lock: Lock

    def __init__(self, dsn: str):
        self.conn = psycopg2.connect(dsn=dsn)
        self.lock = Lock()

        logger.info("Creating the 'token_price_dot' table")
        try:
            with self.conn:
                with self.conn.cursor() as curs:
                    curs.execute("CREATE TABLE token_price_dot (date varchar(10) PRIMARY KEY, price float)")
        except EXPECTED_POSTGRES_EXCEPTIONS:
            logger.info("The 'token_price_dot' table already exists")
        else:
            logger.info("The 'token_price_dot' table is created")

        logger.info("Creating the 'token_price_glmr' table")
        try:
            with self.conn:
                with self.conn.cursor() as curs:
                    curs.execute("CREATE TABLE token_price_glmr (date varchar(10) PRIMARY KEY, price float)")
        except EXPECTED_POSTGRES_EXCEPTIONS:
            logger.info("The 'token_price_glmr' table already exists")
        else:
            logger.info("The 'token_price_glmr' table is created")

        logger.debug("Creating the 'token_price_ksm' table")
        try:
            with self.conn:
                with self.conn.cursor() as curs:
                    curs.execute("CREATE TABLE token_price_ksm (date varchar(10) PRIMARY KEY, price float)")
        except EXPECTED_POSTGRES_EXCEPTIONS:
            logger.info("The 'token_price_ksm' table already exists")
        else:
            logger.info("The 'token_price_dot' table is created")

        logger.info("Creating the 'token_price_movr' table")
        try:
            with self.conn:
                with self.conn.cursor() as curs:
                    curs.execute("CREATE TABLE token_price_movr (date varchar(10) PRIMARY KEY, price float)")
        except EXPECTED_POSTGRES_EXCEPTIONS:
            logger.info("The 'token_price_movr' table already exists")
        else:
            logger.info("The 'token_price_movr' table is created")

    @staticmethod
    def try_to_establish_connection(dsn: str):
        """Try to establish connection to the database."""
        psycopg2.connect(dsn=dsn)

    def insert_token_price(self, postfix: str, date: str, price: float):
        """Insert a price into the token_price_{postfix} table."""
        logger.debug("[INSERT] token_price_%s: %s - %s", postfix, date, price)
        with self.lock:
            try:
                with self.conn:
                    with self.conn.cursor() as curs:
                        curs.execute(f"INSERT INTO token_price_{postfix}(date, price) VALUES (%s, %s)", (date, price))
            except EXPECTED_POSTGRES_EXCEPTIONS as exc:
                logger.debug("An expected postgres exception occurred: %s", exc)
            except Exception as exc:
                logger.error("Failed to save token price into the database. %s: %s", date, exc)

    def get_token_price(self, postfix: str, date: str) -> tuple:
        """Select a price from the token_price_{postfix} table."""
        logger.debug("[SELECT] token_price_%s: %s", postfix, date)
        result = ()
        with self.lock:
            try:
                with self.conn:
                    with self.conn.cursor() as curs:
                        curs.execute(f"SELECT price FROM token_price_{postfix} WHERE token_price_{postfix}.date = %s", (date,))
                        result = curs.fetchone()
            except EXPECTED_POSTGRES_EXCEPTIONS as exc:
                logger.debug("An expected postgres exception occurred: %s", exc)
            except Exception as exc:
                logger.error("Failed to get token price from the database. %s: %s", date, exc)

        return result
