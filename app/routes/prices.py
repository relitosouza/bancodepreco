from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Municipio, CacheContratacao
from app.schemas import PriceSearchResponse, PriceSearchResponseItem, MunicipioSchema
from app.services.pncp import search_local_cache, fetch_and_cache_pncp

router = APIRouter(prefix="/api/prices", tags=["Preços (PNCP)"])

@router.get("/search", response_model=PriceSearchResponse)
async def search_prices(
    termo: str = Query(..., description="Palavra-chave do item de contratação (ex: resma de papel, notebook)"),
    uf: str | None = Query(None, description="Filtrar por Unidade Federativa (UF)"),
    municipio_origem_id: int | None = Query(None, description="Código IBGE do município comprador de referência"),
    mesmo_porte: bool = Query(False, description="Filtrar apenas por municípios do mesmo estado e mesmo porte populacional"),
    db: AsyncSession = Depends(get_db)
):
    """
    Pesquisa e compara preços praticados em contratações similares do PNCP.
    Permite filtrar por UF e por municípios do mesmo porte populacional do município de referência.
    """
    termo_clean = termo.strip().lower()
    if len(termo_clean) < 3:
        raise HTTPException(status_code=400, detail="O termo de busca deve ter no mínimo 3 caracteres.")

    # 1. Resolver município de origem e verificar porte
    municipio_origem_model = None
    porte_filtro = None
    uf_filtro = uf.upper() if uf else None

    if municipio_origem_id:
        q_muni = await db.execute(select(Municipio).where(Municipio.id == municipio_origem_id))
        municipio_origem_model = q_muni.scalars().first()
        if not municipio_origem_model:
            raise HTTPException(status_code=404, detail="Município de referência não encontrado na base local do IBGE.")
        
        if mesmo_porte:
            # Regra de negócio: Filtrar por municípios do mesmo estado com o mesmo porte populacional
            porte_filtro = municipio_origem_model.porte
            uf_filtro = municipio_origem_model.uf  # Força a busca a ser no estado do comprador de referência

    # Se mesmo_porte estiver ativo mas não fornecer o município comprador de referência, lança erro
    if mesmo_porte and not municipio_origem_id:
        raise HTTPException(
            status_code=400, 
            detail="Para filtrar por 'Mesmo Porte', é obrigatório fornecer o 'municipio_origem_id' de referência."
        )

    # Para buscar na API do PNCP, precisamos de uma UF de destino para evitar sobrecarga nacional
    uf_pesquisa_api = uf_filtro
    if not uf_pesquisa_api:
        # Se não informou UF nem município, pede para informar ao menos um parâmetro geográfico de escopo
        raise HTTPException(
            status_code=400,
            detail="Por favor, especifique uma UF ou um municipio_origem_id para definir o escopo geográfico da pesquisa."
        )

    # 2. Verificar cache local
    cache_results = await search_local_cache(db, termo_clean, uf_filtro, porte_filtro)

    # 3. Se o cache estiver vazio, consome a API externa do PNCP
    if not cache_results:
        # Integra com o PNCP e salva os resultados no cache local SQLite
        await fetch_and_cache_pncp(db, termo_clean, uf_pesquisa_api)
        # Refaz a busca local contendo a base atualizada
        cache_results = await search_local_cache(db, termo_clean, uf_filtro, porte_filtro)

    # 4. Formatar resposta final
    items_response = []
    for item in cache_results:
        fonte = "Cache Local"
        # Marcar de onde veio no demo
        if item.id.startswith("mock_"):
            fonte = "Simulador Compras.gov.br (Offline Fallback)"
        elif item.created_at.date() == date.today():
            # Se acabou de ser inserido hoje, foi da API externa
            fonte = "API Compras.gov.br (Tempo Real)"

        muni_nome = item.municipio.nome if item.municipio else None
        muni_uf = item.municipio.uf if item.municipio else None
        muni_pop = item.municipio.populacao if item.municipio else None
        muni_porte = item.municipio.porte if item.municipio else None

        items_response.append(
            PriceSearchResponseItem(
                id=item.id,
                nome_item=item.nome_item,
                valor_unitario=float(item.valor_unitario),
                quantidade=item.quantidade,
                orgao_comprador=item.orgao_comprador,
                municipio_id=item.municipio_id,
                municipio_nome=muni_nome,
                municipio_uf=muni_uf,
                municipio_populacao=muni_pop,
                municipio_porte=muni_porte,
                link_contrato=item.link_contrato,
                data_compra=item.data_compra,
                fonte=fonte
            )
        )

    # Ordenar por valor unitário (menor para maior) para facilitar a comparação de preços
    items_response.sort(key=lambda x: x.valor_unitario)

    municipio_origem_schema = None
    if municipio_origem_model:
        municipio_origem_schema = MunicipioSchema.model_validate(municipio_origem_model)

    from datetime import date
    return PriceSearchResponse(
        termo=termo,
        municipio_origem=municipio_origem_schema,
        total_items=len(items_response),
        items=items_response
    )
