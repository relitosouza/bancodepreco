import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.config import settings
from app.routes import prices, municipalities
from app.database import engine, Base

app = FastAPI(
    title="Banco de Preços PNCP",
    description="Sistema de comparação de preços baseado nas contratações públicas do PNCP cruzadas com portes de municípios do IBGE.",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(municipalities.router)
app.include_router(prices.router)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # Cria as tabelas do banco de dados no SQLite caso não existam
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.get("/search")
async def search_page():
    return FileResponse("app/static/search.html")



if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
