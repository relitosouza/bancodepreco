from datetime import datetime, date
from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime, Date, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Municipio(Base):
    __tablename__ = "municipios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # Código IBGE de 7 dígitos
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    populacao: Mapped[int] = mapped_column(Integer, nullable=False)
    porte: Mapped[str] = mapped_column(String(50), nullable=False)  # Pequeno I, Pequeno II, Médio, Grande

    contratacoes: Mapped[list["CacheContratacao"]] = relationship(
        "CacheContratacao", back_populates="municipio", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Municipio {self.nome}-{self.uf} (Pop: {self.populacao})>"


class CacheContratacao(Base):
    __tablename__ = "cache_contratacoes"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)  # Ex: {cnpj_compra}_{ano_compra}_{sequencial_compra}_{item_numero}
    termo_busca: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    nome_item: Mapped[str] = mapped_column(String, nullable=False)
    valor_unitario: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    orgao_comprador: Mapped[str] = mapped_column(String(255), nullable=False)
    
    municipio_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("municipios.id", ondelete="SET NULL"), nullable=True
    )
    municipio: Mapped["Municipio | None"] = relationship("Municipio", back_populates="contratacoes")

    link_contrato: Mapped[str | None] = mapped_column(String, nullable=True)
    data_compra: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CacheContratacao {self.nome_item[:20]} - R$ {self.valor_unitario}>"
