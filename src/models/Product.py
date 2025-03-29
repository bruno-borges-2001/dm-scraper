from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    # product info
    name: str
    original_price: float
    final_price: float | None
    category: str

    # company info
    company_name: str
    is_closed: bool
    city: str
    company_url: str

    # optional fields
    image_url: Optional[str] = None

    def __post_init__(self):
        """Sets final_price to original_price if not provided."""
        if self.final_price is None:
            self.final_price = self.original_price

    @property
    def discount_percentage(self) -> float | None:
        """Calculates the discount percentage based on the original and final price."""
        if self.original_price > 0 and self.original_price != self.final_price:
            return ((self.original_price - self.final_price) / self.original_price) * 100
        return None  # Avoid division by zero


product_column_map = {
    "name": "Produto",
    "original_price": "Preço Original",
    "final_price": "Preço Final",
    "discount_percentage": "Desconto (%)",
    "category": "Categoria",
    "company_name": "Nome da Empresa",
    "company_url": "URL da Empresa",
    "is_closed": "Fechado",
    "is_open": "Aberto",
    "city": "Cidade",
    "image_url": "URL da Imagem"
}
