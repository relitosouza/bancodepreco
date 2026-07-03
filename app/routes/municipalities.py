from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models import Municipio
from app.schemas import MunicipioSchema

router = APIRouter(prefix="/api/municipalities", tags=["Municípios"])

@router.get("/", response_model=list[MunicipioSchema])
async def list_municipalities(
    q: str | None = Query(None, description="Buscar por nome do município"),
    uf: str | None = Query(None, description="Filtrar por Unidade Federativa (UF)"),
    porte: str | None = Query(None, description="Filtrar por Porte (Pequeno Porte I, Pequeno Porte II, Médio Porte, Grande Porte)"),
    limit: int = Query(50, le=100, description="Limite de registros retornados"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista os municípios cadastrados aplicando filtros de busca.
    """
    query = select(Municipio)
    filters = []

    if q:
        filters.append(Municipio.nome.ilike(f"%{q}%"))
    if uf:
        filters.append(Municipio.uf == uf.upper())
    if porte:
        filters.append(Municipio.porte == porte)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Municipio.nome).limit(limit)
    result = await db.execute(query)
    municipios = result.scalars().all()
    return municipios


@router.get("/{municipio_id}", response_model=MunicipioSchema)
async def get_municipality(
    municipio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém detalhes de um município específico através do seu código IBGE de 7 dígitos.
    """
    query = select(Municipio).where(Municipio.id == municipio_id)
    result = await db.execute(query)
    municipio = result.scalars().first()
    
    if not municipio:
        raise HTTPException(status_code=404, detail="Município não encontrado na base de dados.")
        
    return municipio
