from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class MunicipioSchema(BaseModel):
    id: int
    nome: str
    uf: str
    populacao: int
    porte: str

    model_config = ConfigDict(from_attributes=True)


class PriceSearchResponseItem(BaseModel):
    id: str
    nome_item: str
    valor_unitario: float
    quantidade: int
    orgao_comprador: str
    municipio_id: int | None = None
    municipio_nome: str | None = None
    municipio_uf: str | None = None
    municipio_populacao: int | None = None
    municipio_porte: str | None = None
    link_contrato: str | None = None
    data_compra: date
    fonte: str  # "Cache Local" ou "API Compras.gov.br"

    model_config = ConfigDict(from_attributes=True)


class PriceSearchResponse(BaseModel):
    termo: str
    municipio_origem: MunicipioSchema | None = None
    total_items: int
    items: list[PriceSearchResponseItem]
