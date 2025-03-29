from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from models.Product import Product, product_column_map
from models.Company import company_column_map
from functools import wraps

import streamlit as st
import pandas as pd

ALL_KEYWORD = "Todos"


@st.cache_resource(show_spinner=False)
def get_service_path() -> str:
    return ChromeDriverManager().install()


def get_webdriver_service() -> Service:
    service = Service(
        executable_path=get_service_path(),
    )
    return service


def container(attr_name):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            container = getattr(self, attr_name, None)
            if container is None:
                setattr(self, attr_name, st.empty())
            else:
                container.empty()

            with getattr(self, attr_name, None).container():
                return func(self, *args, **kwargs)
        return wrapper
    return decorator


def get_discount_percentage(product: Product) -> float:
    if product.original_price > 0:
        return ((product.original_price - product.final_price) / product.original_price) * 100
    return 0


def format_row(row: pd.Series):
    if row[product_column_map['is_open']] == 'Não':
        return ['background-color: #CCCCCC50' for _ in row]

    return []


def format_df(df: pd.DataFrame):
    new_df = df.copy()

    new_df['discount_percentage'] = new_df.apply(
        lambda row: get_discount_percentage(row), axis=1
    )

    new_df['is_open'] = new_df['is_closed'].map({True: "Não", False: "Sim"})

    new_df = new_df[[
        "name",
        "original_price",
        "final_price",
        "discount_percentage",
        "company_name",
        "city",
        "category",
        "company_url",
        "image_url",
        "is_open"
    ]]

    new_df.fillna("", inplace=True)

    new_df.rename(columns=product_column_map, inplace=True)

    format_dict = {
        product_column_map['original_price']: "R$ {:.2f}",
        product_column_map['final_price']: "R$ {:.2f}",
        product_column_map['discount_percentage']: "{:.0f}%",
    }

    styler = new_df.style.format(format_dict).apply(format_row, axis=1)

    return new_df, styler


def get_rating_string(value: float | None):
    if value < 0:
        return ''
    rounded_value = round(value)
    return "★" * rounded_value + " " + str(value)


def format_cdf(df: pd.DataFrame):
    new_df = df.copy()

    # convert all values in rating column to string
    new_df['rating'] = new_df['rating'].fillna(-1)
    new_df['rating'] = new_df['rating'].apply(get_rating_string)
    new_df['is_open'] = new_df['is_closed'].map({True: "Não", False: "Sim"})

    new_df.fillna("", inplace=True)

    new_df = new_df[[
        "name",
        "rating",
        "city",
        "banners",
        "company_url",
        "image_url",
        "is_open"
    ]]

    new_df.rename(columns=company_column_map, inplace=True)

    styler = new_df.style.apply(format_row, axis=1)

    return new_df, styler


def apply_filters(df: pd.DataFrame, filters: dict):
    new_df = df.copy()
    for column, value in filters.items():
        if isinstance(value, str):
            if value and value != ALL_KEYWORD:
                new_df = new_df[new_df[column] == value]

        if isinstance(value, list):
            if len(value) > 0:
                new_df = new_df[new_df[column].apply(
                    lambda x: any(item in value for item in x) if isinstance(x, list) else x in value)]

        if isinstance(value, tuple):
            if len(value) != 2:
                raise ValueError("Tuple filter must have 2 values")

            new_df = new_df[
                (new_df[column] >= value[0]) &
                (new_df[column] <= value[1])
            ]

    return new_df
