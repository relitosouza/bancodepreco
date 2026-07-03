import httpx
import asyncio
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging

from app.config import settings
from app.models import CacheContratacao, Municipio
from app.schemas import PriceSearchResponseItem

logger = logging.getLogger("app.services.pncp")

async def search_local_cache(
    session: AsyncSession,
    termo: str,
    uf: str | None = None,
    porte: str | None = None
) -> list[CacheContratacao]:
    """
    Pesquisa itens no cache local SQLite.
    Aplica filtros de UF e Porte (via join com a tabela de municipios).
    """
    termo_clean = termo.strip().lower()
    
    # Validade do cache
    limite_cache = datetime.utcnow() - timedelta(days=settings.cache_expiry_days)
    
    query = select(CacheContratacao).options(selectinload(CacheContratacao.municipio)).join(
        Municipio, CacheContratacao.municipio_id == Municipio.id, isouter=True
    ).where(
        and_(
            CacheContratacao.termo_busca == termo_clean,
            CacheContratacao.created_at >= limite_cache
        )
    )

    if uf:
        query = query.where(Municipio.uf == uf)
    if porte:
        query = query.where(Municipio.porte == porte)

    result = await session.execute(query)
    return list(result.scalars().all())


async def fetch_items_for_contracao(
    client: httpx.AsyncClient,
    contracao: dict,
    session: AsyncSession,
    termo_clean: str,
    semaphore: asyncio.Semaphore
) -> bool:
    """
    Busca e processa os itens de uma contratação específica sob proteção de um semáforo.
    """
    cnpj = contracao.get("orgaoEntidadeCnpj")
    ano = contracao.get("anoCompraPncp")
    sequencial = contracao.get("sequencialCompraPncp")
    orgao_nome = contracao.get("orgaoEntidadeRazaoSocial", "Órgão Não Informado")
    municipio_ibge_7 = contracao.get("unidadeOrgaoCodigoIbge")
    data_publicacao = contracao.get("dataPublicacaoPncp")
    numero_controle_pncp = contracao.get("numeroControlePNCP")

    if not (cnpj and ano and sequencial and numero_controle_pncp):
        return False

    url_itens = f"{settings.pncp_api_base_url}/modulo-contratacoes/2.1_consultarItensContratacoes_PNCP_14133_Id"
    params_itens = {
        "tipo": "numeroControlePNCPCompra",
        "codigo": numero_controle_pncp
    }

    async with semaphore:
        try:
            res_itens = await client.get(url_itens, params=params_itens)
            if res_itens.status_code != 200:
                return False

            itens_data = res_itens.json()
            itens_json = itens_data.get("resultado", [])

            # Trata a data de publicação
            data_compra_dt = date.today()
            if data_publicacao:
                try:
                    data_pub_clean = data_publicacao.split(".")[0].replace("Z", "").split("+")[0]
                    data_compra_dt = datetime.fromisoformat(data_pub_clean).date()
                except ValueError:
                    pass

            real_data_fetched = False
            for item in itens_json:
                descricao_item = item.get("descricaodetalhada") or item.get("descricaoResumida") or ""

                # Salva apenas se o termo de busca estiver contido na descrição do item
                if termo_clean not in descricao_item.lower():
                    continue

                numero_item = item.get("numeroItemPncp") or item.get("numeroItemCompra") or 1

                # Obtém o valor unitário final do resultado (se houver), caso contrário pega o estimado
                valor_unitario = float(item.get("valorUnitarioResultado") or item.get("valorUnitarioEstimado") or 0.0)
                quantidade = int(item.get("quantidade", 1) or 1)

                # Link real do edital no PNCP
                link_contrato = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"
                item_id = f"{cnpj}_{ano}_{sequencial}_{numero_item}"

                # Cruzamento com a base de municípios local por código IBGE de 7 dígitos
                municipio_id = None
                if municipio_ibge_7:
                    municipio_id = int(municipio_ibge_7)
                    m_check = await session.execute(select(Municipio).where(Municipio.id == municipio_id))
                    if not m_check.scalars().first():
                        municipio_id = None

                # Cria ou atualiza o item no cache local
                cache_item = CacheContratacao(
                    id=item_id,
                    termo_busca=termo_clean,
                    nome_item=descricao_item,
                    valor_unitario=valor_unitario,
                    quantidade=quantidade,
                    orgao_comprador=orgao_nome,
                    municipio_id=municipio_id,
                    link_contrato=link_contrato,
                    data_compra=data_compra_dt,
                    created_at=datetime.utcnow()
                )
                await session.merge(cache_item)
                real_data_fetched = True

            return real_data_fetched
        except Exception as e:
            logger.error(f"Erro ao consultar itens para contratação {numero_controle_pncp}: {e}")
            return False


async def fetch_and_cache_pncp(
    session: AsyncSession,
    termo: str,
    uf: str
) -> None:
    """
    Busca contratações reais no portal de Dados Abertos do Compras.gov.br
    dos últimos 90 dias para o Estado (UF) informado, obtém os itens de cada compra,
    cruza com a população do município no banco local e salva no cache SQLite.
    """
    termo_clean = termo.strip().lower()
    data_final = datetime.now()
    data_inicial = data_final - timedelta(days=90) # 90 dias atrás para evitar timeout
    
    data_ini_str = data_inicial.strftime("%Y-%m-%d")
    data_fim_str = data_final.strftime("%Y-%m-%d")
    
    real_data_fetched = False
    modalidades = [5, 8] # 5: Dispensa de Licitação, 8: Pregão (as duas mais comuns)
    
    try:
        semaphore = asyncio.Semaphore(10) # Limita a 10 requisições simultâneas para evitar rate limit
        async with httpx.AsyncClient(timeout=20.0) as client:
            all_contratacoes = []

            for cod_modalidade in modalidades:
                for page in range(1, 4): # Pages 1, 2, and 3
                    # 1. Buscar contratações publicadas para esta modalidade
                    url_publicacoes = f"{settings.pncp_api_base_url}/modulo-contratacoes/1_consultarContratacoes_PNCP_14133"
                    params = {
                        "dataPublicacaoPncpInicial": data_ini_str,
                        "dataPublicacaoPncpFinal": data_fim_str,
                        "codigoModalidade": cod_modalidade,
                        "pagina": page,
                        "tamanhoPagina": 80, # Busca até 80 registros por página
                        "unidadeOrgaoUfSigla": uf
                    }
                    
                    logger.info(f"Chamando API Consulta Compras.gov.br: {url_publicacoes} para UF={uf}, Modalidade={cod_modalidade}, Página={page}")
                    response = await client.get(url_publicacoes, params=params)
                    
                    if response.status_code != 200:
                        logger.warning(f"Erro ao consultar modalidade {cod_modalidade} pág {page} no Compras.gov.br: {response.status_code}")
                        continue

                    data = response.json()
                    contratacoes = data.get("resultado", [])
                    all_contratacoes.extend(contratacoes)

            if all_contratacoes:
                # 2. Consultar os itens de todas as contratações em paralelo usando Semaphore
                tasks = [
                    fetch_items_for_contracao(client, c, session, termo_clean, semaphore)
                    for c in all_contratacoes
                ]
                results = await asyncio.gather(*tasks)
                if any(results):
                    real_data_fetched = True

            await session.commit()

        # Se a API de Consultas rodou mas não trouxe nenhum item coincidente para o termo,
        # apenas registramos o log. Não geramos dados simulados para garantir que apenas dados reais sejam exibidos nas pesquisas.
        if not real_data_fetched:
            logger.info(f"Nenhuma contratação real de '{termo_clean}' encontrada na API do Compras.gov.br para a UF {uf}.")

    except Exception as e:
        logger.error(f"Erro na integração Compras.gov.br: {e}.")



async def generate_mock_pncp_data(session: AsyncSession, termo: str, uf: str) -> None:
    """
    Gera dados simulados caso a API pública do PNCP falhe ou para testes locais rápidos.
    Mapeia os itens criados para municípios reais da UF solicitada no banco de dados local.
    """
    termo_clean = termo.strip().lower()
    
    # Busca municípios reais do banco na UF informada para vincular aos itens de mock
    result = await session.execute(
        select(Municipio).where(Municipio.uf == uf).limit(10)
    )
    municipios = result.scalars().all()
    if not municipios:
        # Fallback para o caso de o banco estar vazio
        return

    import random
    
    orgaos_exemplo = [
        "Prefeitura Municipal",
        "Câmara Municipal de Vereadores",
        "Secretaria Municipal de Saúde",
        "Secretaria Municipal de Educação",
        "Serviço Autônomo de Água e Esgoto (SAAE)"
    ]

    for i in range(15):
        muni = random.choice(municipios)
        orgao = f"{random.choice(orgaos_exemplo)} de {muni.nome}"
        
        # Gera valores condizentes com o termo pesquisado
        if "resma" in termo_clean or "papel" in termo_clean:
            valor = round(random.uniform(22.0, 38.0), 2)
            nome_completo = f"Resma de Papel Sulfite A4, 75g/m², branco - Marca {random.choice(['Chamex', 'Report', 'Senninha'])}"
            quant = random.randint(100, 2000)
        elif "notebook" in termo_clean or "computador" in termo_clean:
            valor = round(random.uniform(3200.0, 6800.0), 2)
            nome_completo = f"Notebook Corporativo, Intel Core i5, 16GB RAM, SSD 512GB - {random.choice(['Dell', 'Lenovo', 'HP'])}"
            quant = random.randint(10, 150)
        elif "limpeza" in termo_clean or "serviço" in termo_clean:
            valor = round(random.uniform(4500.0, 12000.0), 2)
            nome_completo = f"Prestação de Serviços Terceirizados de Limpeza e Conservação Predial, incluindo insumos."
            quant = 1
        else:
            valor = round(random.uniform(15.0, 1500.0), 2)
            nome_completo = f"{termo.capitalize()} para suprimento de demandas da administração pública."
            quant = random.randint(5, 500)

        item_id = f"mock_{uf.lower()}_{muni.id}_{i}_{random.randint(1000, 9999)}"
        
        cache_item = CacheContratacao(
            id=item_id,
            termo_busca=termo_clean,
            nome_item=nome_completo,
            valor_unitario=valor,
            quantidade=quant,
            orgao_comprador=orgao,
            municipio_id=muni.id,
            link_contrato="https://pncp.gov.br/app/editais",
            data_compra=date.today() - timedelta(days=random.randint(5, 90)),
            created_at=datetime.utcnow()
        )
        await session.merge(cache_item)

    await session.commit()
