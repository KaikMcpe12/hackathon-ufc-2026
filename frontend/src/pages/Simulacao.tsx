import { useMutation, useQuery } from "@tanstack/react-query";
import { GitCompareArrows } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client";
import type { Eixo, PlanoDeCarga } from "../api/types";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, SectionCard } from "../components/ui/card";
import { Combobox } from "../components/ui/combobox";
import { Field } from "../components/ui/field";
import { PageHero } from "../components/ui/hero";
import { Truck } from "../components/ui/truck";
import { moeda, pct } from "../lib/format";

interface Cenario {
  veiculo: string;
  resultado: PlanoDeCarga;
}

export default function Simulacao() {
  const eixos = useQuery({ queryKey: ["eixos"], queryFn: () => api.get<{ eixos: Eixo[] }>("/eixos") });
  const [eixo, setEixo] = useState("4");
  const comparar = useMutation({
    mutationFn: () =>
      api.post<{ cenarios: Cenario[]; recomendado: string }>("/otimizar/comparar", {
        eixo: Number(eixo),
        veiculos: ["HR / BONGO", "ACELLO 815"],
      }),
  });

  const eixoOpts = eixos.data?.eixos.map((e) => ({ value: String(e.id), label: `Eixo ${e.id}`, hint: e.nome })) ?? [];

  return (
    <div className="space-y-4">
      <PageHero title="Simulação" highlight="e comparação de cenários" subtitle="Compare o mesmo eixo em dois veículos e escolha o melhor equilíbrio." />

      <SectionCard icon={<GitCompareArrows className="h-5 w-5" />} title="Parâmetros da simulação" subtitle="Escolha o eixo para comparar HR / BONGO e ACELLO 815.">
        <div className="flex flex-col items-end gap-3 sm:flex-row">
          <div className="w-full sm:w-72">
            <Field label="Eixo de entrega">
              <Combobox options={eixoOpts} value={eixo} onChange={setEixo} ariaLabel="Eixo de entrega" />
            </Field>
          </div>
          <Button onClick={() => comparar.mutate()} disabled={comparar.isPending}>
            {comparar.isPending ? "Simulando…" : "Comparar cenários"}
          </Button>
        </div>
      </SectionCard>

      {comparar.data && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {comparar.data.cenarios.map((c) => {
            const t = c.resultado.totais;
            const rec = c.veiculo === comparar.data!.recomendado;
            return (
              <Card key={c.veiculo} className={`p-5 ${rec ? "ring-2 ring-brand" : ""}`}>
                <div className="mb-2 flex items-center justify-between">
                  <h2 className="text-lg font-semibold">{c.veiculo}</h2>
                  {rec && <Badge variant="warn">★ Recomendado</Badge>}
                </div>
                <Truck />
                <dl className="tnum mt-2 space-y-1 text-sm">
                  <Row k="Ocupação peso" v={pct(t.ocupacao_peso)} />
                  <Row k="Ocupação volume" v={pct(t.ocupacao_volume)} />
                  <Row k="Valor" v={moeda(t.valor_total)} />
                  <Row k="Pedidos" v={String(t.quantidade_pedidos)} />
                  <div className="flex items-center justify-between pt-1">
                    <dt className="text-muted">Fator limitante</dt>
                    <dd><Badge variant="warn">{c.resultado.gargalo}</Badge></dd>
                  </div>
                </dl>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between border-b border-line py-1.5 last:border-0">
      <dt className="text-muted">{k}</dt>
      <dd className="font-semibold">{v}</dd>
    </div>
  );
}
