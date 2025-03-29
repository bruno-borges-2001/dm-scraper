from concurrent.futures import ThreadPoolExecutor
from scraper.dm_scraper import DMScraper, CityNotFoundException
from threading import Lock
from streamlit.runtime.scriptrunner import add_script_run_ctx


def get_city_data(city, opts, callback):
    try:
        return DMScraper().scrape_city(city, opts=opts, callback=callback)
    except CityNotFoundException:
        return []


def retrieve_data(cities: list[str], opts, update_product_callback, update_company_callback):
    product_lock = Lock()
    company_lock = Lock()

    def callback(*, product_data=None, company_data=None):
        if (product_data and update_product_callback):
            with product_lock:
                update_product_callback(product_data)

        if (company_data and update_company_callback):
            with company_lock:
                update_company_callback([company_data])

    with ThreadPoolExecutor(max_workers=4) as executor:
        {executor.submit(
            get_city_data,
            city,
            opts,
            callback
        ): city for city in cities}

        for t in executor._threads:
            add_script_run_ctx(t)
