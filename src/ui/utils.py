from models.Product import product_column_map
import pandas as pd
import streamlit as st
from functools import wraps

ALL_KEYWORD = "Todos"


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


def format_df(df: pd.DataFrame):
    new_df = df.copy()
    new_df.fillna("", inplace=True)

    new_df.rename(columns=product_column_map, inplace=True)

    new_df['Aberto'] = new_df['Fechado'].map({True: 'Não', False: 'Sim'})
    new_df.drop(columns=['Fechado'], inplace=True)

    return new_df.style.format({"Preço": "R$ {:.2f}"})


def apply_filters(df: pd.DataFrame, filters: dict):
    new_df = df.copy()
    for column, value in filters.items():
        if isinstance(value, str):
            if value and value != ALL_KEYWORD:
                new_df = new_df[new_df[column] == value]

        if isinstance(value, tuple):
            if len(value) != 2:
                raise ValueError("Tuple filter must have 2 values")

            new_df = new_df[
                (new_df[column] >= value[0]) &
                (new_df[column] <= value[1])
            ]

    return new_df
