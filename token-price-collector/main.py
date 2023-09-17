#!/usr/bin/env python3
"""An entrypoint of the token-price-collector.

It creates and starts 4 instances of the TokenPriceCollector class.
Each instance collects its own token price (DOT, GLMR, KSM and MOVR respectively).
"""
from functools import partial
from threading import Thread
from typing import List
import signal
import sys
import prometheus_client

from database_manager import DatabaseManager
from service_parameters import ServiceParameters
from token_price_collector import TokenPriceCollector


def main():
    """Create instances and start the service."""
    try:
        service_params = ServiceParameters()
        register_prometheus_metrics_with_prefix(service_params.metrics_prefix, service_params.api_port)
    except Exception as exc:
        sys.exit(f"An exception occurred: {exc}")

    try:
        database_manager = DatabaseManager(service_params.database_url)
    except Exception as exc:
        sys.exit(f"An exception occurred: {exc}")

    threads: List[Thread] = []
    for url, symbol in (
            (service_params.token_price_url_dot, 'dot'),
            (service_params.token_price_url_glmr, 'glmr'),
            (service_params.token_price_url_ksm, 'ksm'),
            (service_params.token_price_url_movr, 'movr'),
    ):
        threads.append(TokenPriceCollector(
            database_manager=database_manager,
            initial_date=service_params.initial_date,
            max_request_attempts=service_params.max_request_attempts,
            symbol=symbol,
            timeout=service_params.timeout,
            token_price_url=url,
        ))

    signal.signal(signal.SIGTERM, partial(stop_signal_handler, database_manager=database_manager, threads=threads))
    signal.signal(signal.SIGINT, partial(stop_signal_handler, database_manager=database_manager, threads=threads))

    for thread in threads:
        if thread:
            thread.start()
    for thread in threads:
        if thread:
            thread.join()


def register_prometheus_metrics_with_prefix(prefix: str, port: int):
    """Unregister default metrics, register a ProcessCollector with a prefix and start the server"""
    # Remove metrics without prefix
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
    # Add process metrics (CPU and memory) with a prefix
    prometheus_client.ProcessCollector(namespace=prefix)
    prometheus_client.start_http_server(port)


def stop_signal_handler(sig: int = None, frame=None,
                        threads: [TokenPriceCollector] = None, database_manager: DatabaseManager = None):
    """Stop threads and shutdown the process."""
    if threads:
        for thread in threads:
            if thread:
                with thread.lock:
                    thread.stop = True
        for thread in threads:
            thread.join()

    if database_manager and database_manager.conn:
        database_manager.conn.close()

    sys.exit(sig)


if __name__ == '__main__':
    main()
