import httpx
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Municipio

# Regra de Porte Oficial do IBGE
# Pequeno Porte I: Até 20.000
# Pequeno Porte II: De 20.001 a 50.000
# Médio Porte: De 50.001 a 100.000
# Grande Porte: Acima de 100.000

def get_porte_por_populacao(populacao: int) -> str:
    if populacao <= 20000:
        return "Pequeno Porte I"
    elif populacao <= 50000:
        return "Pequeno Porte II"
    elif populacao <= 100000:
        return "Médio Porte"
    else:
        return "Grande Porte"

# Populações reais de grandes capitais brasileiras para tornar o seed altamente realista
PRINCIPAIS_CAPITAIS = {
    3550308: 12396372,  # São Paulo - SP
    3304557: 6775561,   # Rio de Janeiro - RJ
    2927408: 2900319,   # Salvador - BA
    5300108: 3094325,   # Brasília - DF
    2304400: 2703391,   # Fortaleza - CE
    3106200: 2530701,   # Belo Horizonte - MG
    4106902: 1963726,   # Curitiba - PR
    4314902: 1492530,   # Porto Alegre - RS
    5208707: 1555626,   # Goiânia - GO
    1501402: 1503478,   # Belém - PA
    3509502: 1223237,   # Campinas - SP
    2111300: 1115932,   # São Luís - MA
    3518800: 1392221,   # Guarulhos - SP
    2611606: 1661017,   # Recife - PE
    2704302: 1031597,   # Maceió - AL
    3551009: 833240,    # São Vicente - SP
}

async def seed_municipios_from_ibge(session: AsyncSession) -> int:
    """
    Baixa os municípios oficiais da API de localidades do IBGE e preenche o banco.
    Usa um gerador determinístico para a população com base no ID do município,
    garantindo que os dados sejam consistentes e calibrados com a distribuição demográfica nacional.
    """
    # Verifica se já existem municípios
    result = await session.execute(select(Municipio).limit(1))
    if result.scalars().first():
        return 0

    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        municipios_json = response.json()

    municipios_a_inserir = []
    
    for item in municipios_json:
        ibge_id = int(item["id"])
        nome = item["nome"]
        # Navega no JSON para obter a UF de forma robusta e segura
        uf = None

        try:
            uf = item["microrregiao"]["mesorregiao"]["UF"]["sigla"]
        except (KeyError, TypeError):
            try:
                uf = item["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
            except (KeyError, TypeError):
                pass

        if not uf:
            continue

        
        # Determina a população de forma realista baseada no ID do IBGE
        # (semente fixada no id do IBGE para consistência em cada execução)
        if ibge_id in PRINCIPAIS_CAPITAIS:
            populacao = PRINCIPAIS_CAPITAIS[ibge_id]
        else:
            # Distribuição estatística baseada na demografia brasileira:
            # 70% cidades pequenas, 20% médias, 10% grandes
            random.seed(ibge_id)
            r = random.random()
            if r < 0.70:
                # Cidades pequenas (2.000 a 20.000)
                populacao = random.randint(2000, 20000)
            elif r < 0.88:
                # Cidades pequeno II/médias (20.001 a 70.000)
                populacao = random.randint(20001, 70000)
            elif r < 0.96:
                # Cidades médias-grandes (70.001 a 150.000)
                populacao = random.randint(70001, 150000)
            else:
                # Cidades grandes (150.001 a 600.000)
                populacao = random.randint(150001, 600000)

        porte = get_porte_por_populacao(populacao)
        
        municipio = Municipio(
            id=ibge_id,
            nome=nome,
            uf=uf,
            populacao=populacao,
            porte=porte
        )
        municipios_a_inserir.append(municipio)

    session.add_all(municipios_a_inserir)
    await session.commit()
    return len(municipios_a_inserir)
