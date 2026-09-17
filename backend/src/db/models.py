"""Modelos SQLAlchemy — guardam os campos CRUS (TEXT) por chave natural.

Assim a re-materialização em CSV é lossless e o pipeline (ETL/cubagem) roda idêntico,
preservando o gate. Ver [[prd/12-persistencia-banco]].
"""
from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Produto(Base):
    __tablename__ = "produto"
    codigo: Mapped[str] = mapped_column(String, primary_key=True)
    rank: Mapped[str] = mapped_column(String, default="")
    produto: Mapped[str] = mapped_column(String, default="")
    pedidos: Mapped[str] = mapped_column(String, default="")
    qtd_entregue: Mapped[str] = mapped_column(String, default="")
    unidade_venda: Mapped[str] = mapped_column(String, default="")
    peso_kg: Mapped[str] = mapped_column(String, default="")
    volume_m3: Mapped[str] = mapped_column(String, default="")
    dado_estimado: Mapped[str] = mapped_column(String, default="NAO")
    fonte: Mapped[str] = mapped_column(String, default="")

    # nome no CSV do Ranking -> atributo
    CSV = {
        "Rank": "rank", "Codigo": "codigo", "Produto": "produto", "Pedidos": "pedidos",
        "Qtd_Entregue": "qtd_entregue", "Unidade_Venda": "unidade_venda",
        "Peso_kg": "peso_kg", "Volume_m3": "volume_m3",
        "Dado_Estimado": "dado_estimado", "Fonte": "fonte",
    }


class Pedido(Base):
    __tablename__ = "pedido"
    pedido: Mapped[str] = mapped_column(String, primary_key=True)
    data: Mapped[str] = mapped_column(String, default="")
    vendedor: Mapped[str] = mapped_column(String, default="")
    situacao: Mapped[str] = mapped_column(String, default="")
    cidade: Mapped[str] = mapped_column(String, default="")
    logistica: Mapped[str] = mapped_column(String, default="")
    situacao_csv_entrega: Mapped[str] = mapped_column(String, default="")
    valor_pedido: Mapped[str] = mapped_column(String, default="")
    qtd_itens: Mapped[str] = mapped_column(String, default="")
    itens_resumo: Mapped[str] = mapped_column(String, default="")
    semana: Mapped[int] = mapped_column(Integer, default=4)

    CSV = {
        "Pedido": "pedido", "Data": "data", "Vendedor": "vendedor", "Situacao": "situacao",
        "Cidade": "cidade", "Logistica": "logistica",
        "Situacao_CSV_Entrega": "situacao_csv_entrega", "Valor_Pedido": "valor_pedido",
        "Qtd_Itens": "qtd_itens", "Itens_Resumo": "itens_resumo",
    }
