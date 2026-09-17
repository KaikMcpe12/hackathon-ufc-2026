"""Repositório SQLite: seed único a partir dos CSVs, upsert por chave natural e
re-materialização nos CSVs que o pipeline consome (mantém o gate). Ver PRD-12."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from ..etl.loader import carregar_pedidos, carregar_ranking
from .models import Base, Pedido, Produto

# arquivos de config/enriquecimento não persistidos no v1 (vêm do seed)
_COPIAR = ["rotas_coletas.csv", "referencias_sinteticas.csv", "vendas_faturamento.csv"]


class SqliteRepo:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)

    def _count(self, model) -> int:
        with Session(self.engine) as s:
            return s.scalar(select(func.count()).select_from(model)) or 0

    def is_empty(self) -> bool:
        return self._count(Produto) == 0 and self._count(Pedido) == 0

    def contagem(self) -> dict:
        return {"produtos": self._count(Produto), "pedidos": self._count(Pedido)}

    # ---- seed (uma vez) ----
    def seed_from_csv(self, data_dir: Path) -> None:
        if not self.is_empty():
            return
        ranking = carregar_ranking(data_dir)
        self.upsert_produtos([
            {attr: str(r.get(csv, "")) for csv, attr in Produto.CSV.items()}
            for _, r in ranking.iterrows()
        ])
        pedidos = carregar_pedidos(data_dir)
        rows = []
        for _, r in pedidos.iterrows():
            row = {attr: str(r.get(csv, "")) for csv, attr in Pedido.CSV.items()}
            row["semana"] = int(r.get("semana", 4) or 4)
            rows.append(row)
        self.upsert_pedidos(rows)

    # ---- upsert ----
    def upsert_produtos(self, rows: list[dict]) -> dict:
        return self._upsert(Produto, "codigo", rows)

    def upsert_pedidos(self, rows: list[dict]) -> dict:
        return self._upsert(Pedido, "pedido", rows)

    def _upsert(self, model, pk: str, rows: list[dict]) -> dict:
        campos = {c.name for c in model.__table__.columns}
        ins = upd = rej = 0
        motivos: list[str] = []
        with Session(self.engine) as s:
            for row in rows:
                key = str(row.get(pk, "")).strip()
                if not key:
                    rej += 1
                    motivos.append("chave (PK) vazia")
                    continue
                dados = {k: v for k, v in row.items() if k in campos}
                dados[pk] = key
                obj = s.get(model, key)
                if obj:
                    for k, v in dados.items():
                        setattr(obj, k, v)
                    upd += 1
                else:
                    s.add(model(**dados))
                    ins += 1
            s.commit()
        return {"inseridos": ins, "atualizados": upd, "rejeitados": rej, "motivos": motivos[:20]}

    # ---- re-materialização nos CSVs do pipeline ----
    def materialize(self, dest: Path, seed_dir: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        with Session(self.engine) as s:
            prods = s.scalars(select(Produto)).all()
            peds = s.scalars(select(Pedido)).all()

        rank_df = pd.DataFrame(
            [{csv: getattr(p, attr) for csv, attr in Produto.CSV.items()} for p in prods],
            columns=list(Produto.CSV),
        )
        rank_df.to_csv(dest / "ranking_top85.csv", sep=";", index=False, encoding="utf-8-sig")

        por_sem: dict[int, list[dict]] = {}
        for p in peds:
            por_sem.setdefault(p.semana, []).append(
                {csv: getattr(p, attr) for csv, attr in Pedido.CSV.items()})
        for n in range(1, 5):
            df = pd.DataFrame(por_sem.get(n, []), columns=list(Pedido.CSV))
            df.to_csv(dest / f"pedidos_semana_{n}.csv", sep=";", index=False, encoding="utf-8-sig")

        for nome in _COPIAR:
            src = seed_dir / nome
            if src.exists():
                (dest / nome).write_bytes(src.read_bytes())
