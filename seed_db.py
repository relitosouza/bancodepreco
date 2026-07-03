import asyncio
import sys
from app.database import engine, Base, async_session_maker
from app.services.ibge import seed_municipios_from_ibge

async def main():
    print("--------------------------------------------------")
    print("Iniciando carga de dados do Banco de Preços...")
    print("--------------------------------------------------")
    
    # Garantir que as tabelas estejam criadas no banco de dados SQLite
    async with engine.begin() as conn:
        print("Criando tabelas no SQLite...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tabelas criadas com sucesso!")

    # Chamar o serviço de carga de municípios do IBGE
    async with async_session_maker() as session:
        try:
            print("Conectando à API do IBGE (Serviço de Localidades)...")
            count = await seed_municipios_from_ibge(session)
            if count > 0:
                print(f"Sucesso! {count} municípios do IBGE importados e classificados por porte.")
            else:
                print("Operação concluída. Os municípios já estavam cadastrados no banco de dados local.")
        except Exception as e:
            print(f"Erro ao carregar dados do IBGE: {e}", file=sys.stderr)
            print("Verifique sua conexão com a internet.", file=sys.stderr)
            
    print("--------------------------------------------------")
    print("Processo concluído!")
    print("--------------------------------------------------")

if __name__ == "__main__":
    # Tratamento especial de Event Loop para ambientes Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
