from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Company:
    name: str
    rating: float | None
    banners: list[str]
    city: str
    is_closed: bool
    company_url: str | None
    image_url: str | None


company_column_map = {
    "name": "Restaurante",
    "rating": "Avaliação",
    "banners": "Banners",
    "image_url": "Logo",
    "city": "Cidade",
    "is_closed": "Fechado",
    "is_open": "Aberto",
    "company_url": "URL da Empresa",
}
