from typing import TypeVar, Optional, Callable

from selenium import webdriver

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.common.exceptions import ElementClickInterceptedException

from src.models.Product import Product

import time

T = TypeVar("T")


class CityNotFoundException(Exception):
    pass


class DMScraper:
    def __init__(self):
        self.options = None
        self.driver = None

        self.setup_driver()

    def setup_driver(self):
        self.options = Options()
        self.options.add_argument("--headless")

    def attempt_to_find_element(self, driver_or_element: WebDriver | WebElement, by: By, value: str, default_value: T = None) -> WebElement | T:
        elements = driver_or_element.find_elements(by, value)
        if len(elements) == 0:
            return default_value

        return elements[0]

    def wait_for_element(self, by: By, value: str, timeout: float = 20):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def element_exists(self, driver_or_element: WebDriver | WebElement, by: By, value: str):
        return self.attempt_to_find_element(driver_or_element, by, value) is not None

    def scrape_city(self, city: str, *, opts: Optional[dict], callback: Optional[Callable[[list[Product]], None]] = None, retry=0):
        products = []
        visited_stores = dict()
        store_index = 0

        include_closed_stores = opts.get("include_closed_stores", False)

        self.driver = webdriver.Chrome(options=self.options, keep_alive=True)
        driver = self.driver
        driver.get("https://www.deliverymuch.com.br/")

        self.wait_for_element(By.ID, "city")

        search_input = driver.find_element(By.ID, "city")

        for c in city:
            search_input.send_keys(c)
            time.sleep(0.2)

        try:
            self.wait_for_element(
                By.CSS_SELECTOR,
                "li.cursor-pointer > button",
                5
            )
        except:
            self.driver.close()

            if retry > 2:
                raise CityNotFoundException(
                    f"City '{city}' not found after {retry + 1} attempts")

            self.scrape_city(
                city, opts=opts, callback=callback, retry=retry + 1)
            return

        driver.find_element(
            By.CSS_SELECTOR,
            "li.cursor-pointer > button"
        ).click()

        while True:
            try:
                self.wait_for_element(By.CLASS_NAME, "company-list__item")
            except:
                break

            elements = driver.find_elements(
                By.CLASS_NAME,
                "company-list__item"
            )

            if store_index >= len(elements):
                button = self.attempt_to_find_element(
                    driver,
                    By.XPATH,
                    '//button[normalize-space()="Carregar mais lojas"]'
                )

                if button:
                    button.click()
                    store_index = 0
                    time.sleep(1)
                    continue
                else:
                    break

            e = elements[store_index]
            store_index += 1

            company_name = e.find_element(
                By.CLASS_NAME,
                "company__name"
            ).text

            if company_name in visited_stores:
                continue

            store_is_closed = self.element_exists(e, By.TAG_NAME, "figcaption")

            if store_is_closed and not include_closed_stores:
                break

            try:
                visited_stores[company_name] = True
                e.click()
                time.sleep(0.1)
                self.wait_for_element(By.CLASS_NAME, "company__name")

                company = driver.find_element(
                    By.CLASS_NAME,
                    "company__name"
                ).text

                company_url = driver.current_url

                self.wait_for_element(By.CLASS_NAME, "product-card", timeout=5)

                categories_elements = driver.find_elements(
                    By.CLASS_NAME,
                    "product-categories__group"
                )

                company_products = []

                for c in categories_elements:
                    category = c.find_element(
                        By.CLASS_NAME,
                        "category__title"
                    ).text

                    products_elements = c.find_elements(
                        By.CLASS_NAME,
                        "product-card"
                    )

                    for p in products_elements:
                        name = self.attempt_to_find_element(
                            p,
                            By.CLASS_NAME,
                            "product-card__title"
                        )

                        if not name:
                            continue

                        price = self.attempt_to_find_element(
                            p,
                            By.CLASS_NAME,
                            "product-card__price"
                        )

                        if price is None:
                            continue

                        img = self.attempt_to_find_element(
                            p,
                            By.TAG_NAME,
                            "img"
                        )

                        parsed_price = float(
                            price.text
                            .removeprefix("R$")
                            .replace(".", "")
                            .replace(",", ".")
                            .strip()
                        )

                        product = Product(
                            name=name.text,
                            price=parsed_price,
                            category=category.lower(),
                            company_name=company,
                            company_url=company_url,
                            city=city,
                            is_closed=store_is_closed,
                            image_url=img.get_property("src") if img else None,
                        )

                        company_products.append(product)
                        products.append(product)

                if callback:
                    callback(company_products)
            except ElementClickInterceptedException:
                continue
            except:
                print(f"[{city}] Timeout exception on {company}")
                continue
            finally:
                driver.back()

        return products
