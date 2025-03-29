from typing import TypeVar, Optional, Callable

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

from models.Product import Product
from models.Company import Company

from utils import get_webdriver_service
from scraper.scraper_utils import format_price

import time
import traceback

T = TypeVar("T")


class CityNotFoundException(Exception):
    pass


class IgnoreProductException(Exception):
    pass


class DMScraper:
    def __init__(self):
        self.city = None
        self.driver = None

    def attempt_to_find_element(self, driver_or_element: WebDriver | WebElement, by: By, value: str, field: Optional[str] = None) -> WebElement | str | None:
        elements = driver_or_element.find_elements(by, value)
        if len(elements) == 0:
            return None

        element = elements[0]

        if field:
            return getattr(element, field, None)

        return element

    def wait_for_element(self, by: By, value: str, timeout: float = 20):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def element_exists(self, driver_or_element: WebDriver | WebElement, by: By, value: str):
        return self.attempt_to_find_element(driver_or_element, by, value) is not None

    def scrape_company_info(self, company_wrapper: WebElement) -> Company:
        company_name = self.attempt_to_find_element(
            company_wrapper,
            By.CLASS_NAME,
            "company__name",
            "text"
        )

        company_score = self.attempt_to_find_element(
            company_wrapper,
            By.CLASS_NAME,
            "company__score",
            "text"
        )

        company_score = float(
            company_score) if company_score and company_score != "Novo" else None

        company_badges = [b.text for b in company_wrapper.find_elements(
            By.CLASS_NAME,
            "company__badges"
        )]

        company_is_closed = self.element_exists(
            company_wrapper, By.TAG_NAME, "figcaption")

        company_logo = company_wrapper.find_element(
            By.CSS_SELECTOR,
            ".company__logo > img"
        ).get_attribute("src")

        return Company(
            name=company_name,
            rating=company_score,
            banners=company_badges,
            is_closed=company_is_closed,
            city=self.city,
            # set after accessing the link
            company_url=None,
            image_url=company_logo
        )

    def scrape_product_info(self, product_wrapper: WebElement, company_info: Company, current_category: str) -> Product:
        name = self.attempt_to_find_element(
            product_wrapper,
            By.CLASS_NAME,
            "product-card__title"
        )

        if not name:
            raise IgnoreProductException("Product name not found")

        price = self.attempt_to_find_element(
            product_wrapper,
            By.CLASS_NAME,
            "product-card__original-price"
        )

        if price is None:
            price = self.attempt_to_find_element(
                product_wrapper,
                By.CLASS_NAME,
                "product-card__price"
            )

            if price is None:
                raise IgnoreProductException("Product name not found")

        price = price.text

        final_price = self.attempt_to_find_element(
            product_wrapper,
            By.CLASS_NAME,
            "product-card__sale-price"
        )

        if final_price:
            final_price = final_price.text

        img = self.attempt_to_find_element(
            product_wrapper,
            By.TAG_NAME,
            "img"
        )

        parsed_price = format_price(price)
        parsed_final_price = format_price(
            final_price) if final_price else None

        image_url = img.get_property("src") if img else None

        return Product(
            name=name.text,
            original_price=parsed_price,
            final_price=parsed_final_price,
            category=current_category.lower(),
            company_name=company_info.name,
            company_url=company_info.company_url,
            city=self.city,
            is_closed=company_info.is_closed,
            image_url=image_url,
        )

    def scrape_city(self, city_query: str, *, opts: Optional[dict], callback: Optional[Callable[[list[Product]], None]] = None, retry=0):
        products = []
        visited_stores = dict()
        store_index = 0

        include_closed_stores = opts.get("include_closed_stores", False)

        print("Initializing driver")

        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument("--headless")

        service = get_webdriver_service()
        try:
            self.driver = webdriver.Chrome(options=options, service=service)
        except Exception as e:
            print(e)

        driver = self.driver
        driver.get("https://www.deliverymuch.com.br/")

        self.wait_for_element(By.ID, "city")

        search_input = driver.find_element(By.ID, "city")

        for c in city_query:
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
                    f"{city} not found")

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

                city = driver.find_element(
                    By.CLASS_NAME,
                    "city-info__title"
                ).text

                self.city = city
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

            company_info = self.scrape_company_info(e)

            if company_info.is_closed and not include_closed_stores:
                break

            if company_info.name in visited_stores:
                continue

            try:
                visited_stores[company_info.name] = True

                # go to company page
                e.click()
                time.sleep(0.1)
                self.wait_for_element(By.CLASS_NAME, "company__name")

                company_url = driver.current_url
                company_info.company_url = company_url

                if (callback):
                    callback(company_data=company_info)

                # emit company dataframe update

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

                    for product_wrapper in products_elements:
                        try:
                            product = self.scrape_product_info(
                                product_wrapper,
                                company_info,
                                category
                            )

                            company_products.append(product)
                        except IgnoreProductException:
                            continue

                products.extend(company_products)

                if callback:
                    callback(product_data=company_products)
            except ElementClickInterceptedException:
                continue
            except TimeoutException:
                print(f"[{city}] Timeout exception on {company_info.name}")
                continue
            except Exception:
                print(traceback.format_exc())
                continue
            finally:
                driver.back()

        return products
