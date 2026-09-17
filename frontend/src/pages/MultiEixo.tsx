import { useMutation, useQuery } from "@tanstack/react-query";
import { Boxes, Layers } from "lucide-react";
import { useState } from "react";
import { api, type ApiError } from "../api/client";
import type { MultiPlano, Veiculo } from "../api/types";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, SectionCard } from "../components/ui/card";
import { PageHero } from "../components/ui/hero";
import { MetricCard } from "../components/ui/metric";
import { moeda, pct } from "../lib/format";

export default function MultiEixo() {
  const veiculos = useQuery({
    queryKey: ["veiculos"],
    queryFn: () => api.get<{ veiculos: Veiculo[] }>("/veiculos"),
  });
  const selecionaveis = veiculos.data?.veiculos.filter((v) => v.selecionavel) ?? [];
  const [frota, setFrota] = useState<Record<string, number>>({});

  const lista = Object.entries(frota).flatMap(([nome, n]) => Array<string>(n).fill(nome));

  const distribuir = useMutation({
    mutationFn: () => api.post<MultiPlano>("/otimizar/multi-eixo", { veiculos: lista.length ? lista : undefined }),
    onError: (e) => alert((e as unknown as ApiError).detail),
  });

  const set = (nome: string, n: number) => setFrota((f) => ({ ...f, [nome]: Math.max(0, n) }));
  const r = distribuir.data;

  return (
    <div className="space-y-4">
      <PageHero
        title="Planejamento"
        highlight="multi-eixo (frota)"
        subtitle="Distribui os veículos entre os eixos buscando a melhor ocupação global. Pedidos não são divididos."
      />

      <SectionCard icon={<Layers className="h-5 w-5" />} title="Frota disponível" subtitle="Escolha quantos veículos de cada tipo entram na distribuição.">
        <div className="flex flex-wrap items-end gap-4">
          {selecionaveis.map((v) => (
            <div key={v.nome}>
              <div className="mb-1.5 text-xs font-bold">{v.nome}</div>
              <div className="text-xs text-muted">{v.capacidade_peso} kg · {v.capacidade_volume} m³</div>
              <div className="mt-1 flex items-center gap-2">
                <Button variant="light" size="icon" onClick={() => set(v.nome, (frota[v.nome] ?? 0) - 1)} aria-label={`Menos ${v.nome}`}>−</Button>
                <span className="tnum w-6 text-center font-bold">{frota[v.nome] ?? 0}</span>
                <Button variant="light" size="icon" onClick={() => set(v.nome, (frota[v.nome] ?? 0) + 1)} aria-label={`Mais ${v.nome}`}>+</Button>
              </div>
            </div>
          ))}
          <Button onClick={() => distribuir.mutate()} disabled={distribuir.isPending}>
            {distribuir.isPending ? "Distribuindo…" : `Distribuir ${lista.length || "frota"}`}
          </Button>
        </div>
      </SectionCard>

      {r && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MetricCard label="Ocupação média peso" value={r.resumo_global.ocupacao_media_peso} format={(n) => pct(n)} ocupacao={r.resumo_global.ocupacao_media_peso} />
            <MetricCard label="Ocupação média volume" value={r.resumo_global.ocupacao_media_volume} format={(n) => pct(n)} ocupacao={r.resumo_global.ocupacao_media_volume} />
            <MetricCard label="Valor total" value={r.resumo_global.valor_total} format={moeda} />
            <MetricCard label="Veículos usados" value={r.resumo_global.veiculos_usados} format={(n) => String(Math.round(n))} sub={`${r.resumo_global.veiculos_ociosos} ociosos`} />
          </div>

          {r.resumo_global.eixos_nao_atendidos.length > 0 && (
            <Card className="p-3 text-sm text-amber-900">
              Eixos sem veículo nesta distribuição: <b>{r.resumo_global.eixos_nao_atendidos.join(", ")}</b> — adicione mais veículos à frota.
            </Card>
          )}

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {r.planos.map((p) => {
              const t = p.plano.totais;
              return (
                <Card key={p.eixo_id} className="p-5">
                  <div className="mb-2 flex items-center justify-between">
                    <h2 className="font-semibold">Eixo {p.eixo_id} · {p.veiculo}</h2>
                    <Badge variant="warn">{p.plano.gargalo}</Badge>
                  </div>
                  <p className="mb-3 text-xs text-muted">{p.plano.eixo.nome}</p>
                  <div className="grid grid-cols-2 gap-3">
                    <MetricCard label="Peso" value={t.peso_utilizado} format={(n) => `${n.toFixed(0)} kg`} ocupacao={t.ocupacao_peso} />
                    <MetricCard label="Volume" value={t.volume_utilizado} format={(n) => `${n.toFixed(3)} m³`} ocupacao={t.ocupacao_volume} />
                  </div>
                  <div className="tnum mt-3 flex justify-between text-sm">
                    <span className="text-muted">Pedidos <b className="text-ink">{t.quantidade_pedidos}</b></span>
                    <span className="text-muted">Valor <b className="text-ink">{moeda(t.valor_total)}</b></span>
                  </div>
                </Card>
              );
            })}
          </div>
        </>
      )}

      {!r && (
        <Card className="grid min-h-[160px] place-items-center p-6 text-center text-sm text-muted">
          <div className="flex items-center gap-2"><Boxes className="h-4 w-4" /> Escolha a frota e clique em Distribuir para ver um plano por eixo.</div>
        </Card>
      )}
    </div>
  );
}
