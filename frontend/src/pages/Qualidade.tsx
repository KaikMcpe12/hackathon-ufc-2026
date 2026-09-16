import { useQuery } from "@tanstack/react-query";
import { Activity, ListChecks, PackageCheck } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client";
import type { QualidadeResumo } from "../api/types";
import { Badge } from "../components/ui/badge";
import { Card, SectionCard } from "../components/ui/card";
import { Dialog } from "../components/ui/dialog";
import { PageHero } from "../components/ui/hero";
import { MetricCard } from "../components/ui/metric";
import { Skeleton } from "../components/ui/skeleton";

interface Correcao {
  pedido: string;
  campo: string;
  valor_original: string;
  valor_novo: string;
  regra: string;
  criterio: string;
  acao: string;
  aplicada_em?: string;
}

const ACAO_VARIANT: Record<string, "green" | "warn" | "blue" | "purple"> = {
  CORRIGIDA: "green",
  SINALIZADA: "warn",
  ESTIMADO: "blue",
  PADRONIZADA: "purple",
};

const ACAO_TXT: Record<string, string> = {
  CORRIGIDA: "Valor corrigido automaticamente (com rastreabilidade).",
  PADRONIZADA: "Valor padronizado para a forma canônica.",
  ESTIMADO: "Cubagem estimada aplicada (marcada como 🟡).",
  SINALIZADA: "Sinalizado para revisão manual.",
};

// Explicação humana por regra: o que é e por que é uma anomalia.
const REGRA_INFO: Record<string, { titulo: string; oque: string; porque: string }> = {
  ano_fora_do_lote: {
    titulo: "Data fora do lote",
    oque: "O ano da data do pedido não corresponde ao período processado.",
    porque:
      "Erros de digitação/sistema geram datas impossíveis (ex.: 2014 num lote de 2026), o que quebraria filtros por semana e a rastreabilidade.",
  },
  cidade_trailing_space: {
    titulo: "Espaço extra na cidade",
    oque: "O nome da cidade vinha com espaços sobrando.",
    porque: "Espaços extras impedem o cruzamento exato da cidade com o eixo de entrega.",
  },
  cidade_typo: {
    titulo: "Erro de grafia na cidade",
    oque: "A cidade estava escrita de forma divergente do padrão.",
    porque: "A grafia divergente impede mapear o pedido ao eixo correto.",
  },
  campo_obrigatorio_ausente: {
    titulo: "Campo obrigatório ausente",
    oque: "Um campo essencial do pedido estava vazio.",
    porque: "Sem o campo, o pedido não pode ser processado com segurança.",
  },
};

export default function Qualidade() {
  const resumo = useQuery({ queryKey: ["qualidade"], queryFn: () => api.get<QualidadeResumo>("/qualidade/resumo") });
  const log = useQuery({ queryKey: ["qualidade-log"], queryFn: () => api.get<{ correcoes: Correcao[] }>("/qualidade/log") });
  const r = resumo.data;
  const [sel, setSel] = useState<Correcao | null>(null);
  const info = sel ? REGRA_INFO[sel.regra] : null;

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
                  <div className="min-w-[108px] rounded-xl border border-line bg-neutral-50 px-4 py-3 text-center">
                    <div className="mx-auto grid h-9 w-9 place-items-center rounded-full border border-line bg-white text-xs font-bold">{i + 1}</div>
                    <div className="mt-2 text-xs uppercase text-muted">{s.nome}</div>
                    <div className="tnum text-lg font-bold">{s.registros}</div>
                    <div className="text-xs text-muted">{s.percentual}%</div>
                  </div>
                  {i < r.pipeline_stages.length - 1 && <span className="self-center text-neutral-300">→</span>}
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
                  <tr
                    key={i}
                    className="cursor-pointer border-t border-line hover:bg-neutral-50 focus:bg-neutral-50"
                    tabIndex={0}
                    role="button"
                    onClick={() => setSel(c)}
                    onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), setSel(c))}
                  >
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
        <p className="mt-2 text-xs text-muted">Clique numa anomalia para ver o que é, por que foi detectada e o que foi feito.</p>
      </SectionCard>

      {sel && (
        <Dialog
          open={!!sel}
          onOpenChange={(o) => !o && setSel(null)}
          title={info?.titulo ?? `Anomalia: ${sel.regra}`}
          subtitle={`Pedido ${sel.pedido} · campo "${sel.campo}"`}
        >
          <div className="space-y-3 text-sm">
            <div>
              <div className="text-xs font-semibold uppercase text-muted">O que é</div>
              <p>{info?.oque ?? "Divergência detectada no dado de origem."}</p>
            </div>
            <div>
              <div className="text-xs font-semibold uppercase text-muted">Por que é uma anomalia</div>
              <p>{info?.porque ?? "O valor original não estava consistente com as regras de negócio."}</p>
            </div>
            <div className="rounded-xl border border-line bg-neutral-50 p-3">
              <div className="text-xs font-semibold uppercase text-muted">O que foi feito</div>
              <p className="mt-1">{ACAO_TXT[sel.acao] ?? sel.acao}</p>
              <p className="tnum mt-1">
                De <b className="text-muted">{sel.valor_original}</b> → <b>{sel.valor_novo}</b>
              </p>
              <p className="mt-1 text-xs text-muted">Regra: {sel.regra} · Critério: {sel.criterio}</p>
            </div>
          </div>
        </Dialog>
      )}
    </div>
  );
}
