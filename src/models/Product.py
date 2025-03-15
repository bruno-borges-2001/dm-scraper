from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    # product info
    name: str
    price: float
    category: str

    # company info
    company_name: str
    company_url: str
    is_closed: bool
    city: str

    # optional fields
    image_url: Optional[str] = None


product_column_map = {
    "name": "Nome",
    "price": "Preço",
    "category": "Categoria",
    "company_name": "Nome da Empresa",
    "company_url": "URL da Empresa",
    "is_closed": "Fechado",
    "city": "Cidade",
    "image_url": "URL da Imagem"
}
