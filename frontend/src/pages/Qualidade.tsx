import { useQuery } from "@tanstack/react-query";
import { Activity, Layers, ListChecks, PackageCheck } from "lucide-react";
import { api } from "../api/client";
import type { QualidadeResumo } from "../api/types";
import { Badge } from "../components/ui/badge";
import { Card, SectionCard } from "../components/ui/card";
import { PageHero } from "../components/ui/hero";
import { MetricCard } from "../components/ui/metric";
import { Skeleton } from "../components/ui/skeleton";

interface Correcao {
  pedido: string;
  campo: string;
  valor_original: string;
  valor_novo: string;
  acao: string;
}

const ACAO_VARIANT: Record<string, "green" | "warn" | "blue" | "purple"> = {
  CORRIGIDA: "green",
  SINALIZADA: "warn",
  ESTIMADO: "blue",
  PADRONIZADA: "purple",
};

export default function Qualidade() {
  const resumo = useQuery({ queryKey: ["qualidade"], queryFn: () => api.get<QualidadeResumo>("/qualidade/resumo") });
  const log = useQuery({ queryKey: ["qualidade-log"], queryFn: () => api.get<{ correcoes: Correcao[] }>("/qualidade/log") });
  const r = resumo.data;

  const total = r ? r.pedidos_completa + r.pedidos_estimada + r.pedidos_ausente : 1;
  const p1 = r ? (r.pedidos_completa / total) * 100 : 0;
  const p2 = r ? p1 + (r.pedidos_estimada / total) * 100 : 0;

  return (
    <div className="space-y-4">
      <PageHero title="Dados &" highlight="cubagem" subtitle="Rastreabilidade do pipeline 688 → 93 → 81 e da qualidade da cubagem." />

      {!r ? (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24" />)}</div>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <MetricCard label="Registros processados" value={r.registros_processados} format={(n) => String(Math.round(n))} />
          <MetricCard label="Materiais no ranking" value={r.materiais_ranking} format={(n) => String(Math.round(n))} />
          <MetricCard label="Cubagem completa 🟢" value={r.pedidos_completa} format={(n) => String(Math.round(n))} sub="dados oficiais" />
          <MetricCard label="Estimada 🟡" value={r.pedidos_estimada} format={(n) => String(Math.round(n))} sub={`${r.pedidos_ausente} ausentes 🔴`} />
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(300px,0.9fr)]">
        <SectionCard icon={<Activity className="h-5 w-5" />} title="Pipeline de tratamento" subtitle="Do dado bruto ao pedido pronto para o solver.">
          {r && (
            <div className="flex flex-wrap items-center gap-2">
              {r.pipeline_stages.map((s, i) => (
                <div key={s.nome} className="flex items-center gap-2">
                  <div className="rounded-xl border border-line bg-neutral-50 px-4 py-3 text-center">
                    <div className="grid h-9 w-9 place-items-center rounded-full border border-line bg-white text-xs font-bold">{i + 1}</div>
                    <div className="mt-2 text-xs uppercase text-muted">{s.nome}</div>
                    <div className="tnum text-lg font-bold">{s.registros}</div>
                    <div className="text-xs text-muted">{s.percentual}%</div>
                  </div>
                  {i < r.pipeline_stages.length - 1 && <span className="text-neutral-300">→</span>}
                </div>
              ))}
            </div>
          )}
        </SectionCard>

        <SectionCard icon={<PackageCheck className="h-5 w-5" />} title="Cobertura da cubagem" subtitle="Distribuição dos selos.">
          {r && (
            <div className="flex flex-col items-center gap-3">
              <div
                className="relative h-40 w-40 rounded-full"
                style={{ background: `conic-gradient(#18b96b 0 ${p1}%, #ffc400 ${p1}% ${p2}%, #e5484d ${p2}% 100%)` }}
                role="img"
                aria-label={`Cobertura: ${r.pedidos_completa} completa, ${r.pedidos_estimada} estimada, ${r.pedidos_ausente} ausente`}
              >
                <div className="absolute inset-7 grid place-items-center rounded-full bg-white text-center">
                  <div><div className="tnum text-2xl font-extrabold">{total}</div><div className="text-xs text-muted">pedidos</div></div>
                </div>
              </div>
              <ul className="w-full space-y-1 text-sm">
                <li className="flex justify-between"><span>🟢 Completa</span><b>{r.pedidos_completa}</b></li>
                <li className="flex justify-between"><span>🟡 Estimada</span><b>{r.pedidos_estimada}</b></li>
                <li className="flex justify-between"><span>🔴 Ausente</span><b>{r.pedidos_ausente}</b></li>
              </ul>
            </div>
          )}
        </SectionCard>
      </div>

      <SectionCard icon={<ListChecks className="h-5 w-5" />} title="Anomalias detectadas" subtitle="Correções aplicadas no ETL, com rastreabilidade.">
        {log.isLoading && <Skeleton className="h-24" />}
        {log.data?.correcoes.length ? (
          <div className="overflow-auto rounded-xl border border-line">
            <table className="w-full min-w-[560px] text-sm">
              <thead className="bg-neutral-100">
                <tr className="text-left text-xs uppercase text-muted">
                  <th className="px-3 py-2.5">Pedido</th><th className="px-3 py-2.5">Campo</th>
                  <th className="px-3 py-2.5">De</th><th className="px-3 py-2.5">Para</th><th className="px-3 py-2.5">Ação</th>
                </tr>
              </thead>
              <tbody>
                {log.data.correcoes.map((c, i) => (
                  <tr key={i} className="border-t border-line hover:bg-neutral-50">
                    <td className="px-3 py-2.5">{c.pedido}</td><td className="px-3 py-2.5">{c.campo}</td>
                    <td className="px-3 py-2.5 text-muted">{c.valor_original}</td><td className="px-3 py-2.5">{c.valor_novo}</td>
                    <td className="px-3 py-2.5"><Badge variant={ACAO_VARIANT[c.acao] ?? "gray"}>{c.acao}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          !log.isLoading && <p className="text-sm text-muted">Nenhuma correção registrada nesta base.</p>
        )}
      </SectionCard>
    </div>
  );
}
