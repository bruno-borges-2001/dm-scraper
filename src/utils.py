from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from models.Product import Product, product_column_map
from models.Company import company_column_map
from functools import wraps

import streamlit as st
import polars as pl

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


def format_df(df: pl.DataFrame):
    return df.select(
        pl.col("name").alias(product_column_map['name']),
        pl.col("original_price").alias(product_column_map['original_price']),
        pl.col("final_price").alias(product_column_map['final_price']),
        pl.when(pl.col("original_price") > 0).then(
            (pl.col("original_price") - pl.col("final_price")) /
            pl.col("original_price") * 100
        ).otherwise(0).cast(pl.Float32).alias(product_column_map['discount_percentage']),
        pl.col("company_name").alias(product_column_map['company_name']),
        pl.col("city").alias(product_column_map['city']),
        pl.col("category").alias(product_column_map['category']),
        pl.col("company_url").alias(product_column_map['company_url']),
        pl.col("image_url").alias(product_column_map['image_url']),
        pl.col("is_closed").map_elements(lambda x: "Não" if x else "Sim", return_dtype=pl.Utf8).alias(
            product_column_map['is_open']
        ),
    ).fill_null("")


def get_rating_string(value: float | None):
    if value is None or value < 0:
        return ''
    rounded_value = round(value)
    return "★" * rounded_value + " " + str(value)


def format_cdf(df: pl.DataFrame):
    return df.select(
        pl.col("name").alias(company_column_map['name']),
        pl.col("rating").map_elements(
            get_rating_string,
            return_dtype=pl.Utf8
        ).alias(company_column_map['rating']),
        pl.col("city").alias(company_column_map['city']),
        pl.col("banners").alias(company_column_map['banners']),
        pl.col("company_url").alias(company_column_map['company_url']),
        pl.col("image_url").alias(company_column_map['image_url']),
        pl.col("is_closed").map_elements(lambda x: "Sim" if x else "Não").alias(
            company_column_map['is_open']
        ),
    ).fill_null("")


def apply_filters(df: pl.DataFrame, filters: dict):
    new_df = df.clone()

    for column, value in filters.items():
        if isinstance(value, str):
            if value and value != ALL_KEYWORD:
                new_df = new_df.filter(
                    pl.col(column).str.contains(value, case=False))

        if isinstance(value, list):
            if len(value) > 0:
                col_type = new_df.schema[column]

                if col_type == pl.Utf8:
                    new_df = new_df.filter(pl.col(column).is_in(value))
                else:
                    new_df = new_df.filter(pl.col(column).map_elements(
                        lambda x: any(item in value for item in x), return_dtype=pl.Boolean))

        if isinstance(value, tuple):
            if len(value) != 2:
                raise ValueError("Tuple filter must have 2 values")

            new_df = new_df.filter(
                pl.col(column).is_between(value[0], value[1]))

    return new_df
