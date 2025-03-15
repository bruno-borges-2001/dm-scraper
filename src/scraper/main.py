from concurrent.futures import ThreadPoolExecutor
from src.scraper.dm_scraper import DMScraper, CityNotFoundException
from threading import Lock
from streamlit.runtime.scriptrunner import add_script_run_ctx
import streamlit as st


def get_city_data(city, opts, callback):
    try:
        return DMScraper().scrape_city(city, opts=opts, callback=callback)
    except CityNotFoundException:
        return []


def retrieve_data(cities: list[str], opts, update_product_callback):
    lock = Lock()

    def callback(data):
        with lock:
            if (update_product_callback):
                update_product_callback(data)

    with ThreadPoolExecutor(max_workers=4) as executor:
        {executor.submit(
            get_city_data,
            city,
            opts,
            callback
        ): city for city in cities}

        for t in executor._threads:
            add_script_run_ctx(t)
