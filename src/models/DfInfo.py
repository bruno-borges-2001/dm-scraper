from dataclasses import dataclass
from typing import Optional

import polars as pl


@dataclass
class DfInfo:
    df: Optional[pl.DataFrame] = None

    def has_data(self):
        return self.df is not None and not self.df.is_empty()

    def rows(self):
        return self.df.shape[0] if self.has_data() else 0

    def cities_visited(self):
        return self.df.select(pl.col('city').unique().len()).item() if self.has_data() else 0

    def company_visited(self):
        return self.df.select(pl.col('company_name').unique().len()).item() if self.has_data() else 0

    def memory_usage(self):
        return self.df.estimated_size('mb') if self.has_data() else 0
