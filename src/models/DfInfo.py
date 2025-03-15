from dataclasses import dataclass
from typing import Optional

from pandas import DataFrame


@dataclass
class DfInfo:
    df: Optional[DataFrame] = None

    def has_data(self):
        return self.df is not None and not self.df.empty

    def rows(self):
        return self.df.shape[0] if self.has_data() else 0

    def cities_visited(self):
        return len(self.df['city'].unique()) if self.has_data() else 0

    def company_visited(self):
        return len(self.df['company_name'].unique()) if self.has_data() else 0

    def memory_usage(self):
        memory = self.df.memory_usage(
            deep=True).sum() if self.has_data() else 0

        if memory < 1024:
            return f"{memory} bytes"
        elif memory < 1024 ** 2:
            return f"{memory / 1024:.2f} KB"
        else:
            return f"{memory / (1024 ** 2):.2f} MB"
