import { useQuery } from "@tanstack/react-query";
import { Filter, Search } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client";
import type { MotivoExclusao, Pedido } from "../api/types";
import { StatusBadge } from "../components/ui/badge";
import { SectionCard } from "../components/ui/card";
import { Combobox } from "../components/ui/combobox";
import { DataTable } from "../components/ui/data-table";
import { Field } from "../components/ui/field";
import { PageHero } from "../components/ui/hero";
import { ProdutosDialog } from "../components/ui/produtos";
import { Skeleton } from "../components/ui/skeleton";
import { peso, titulo, volume } from "../lib/format";

export default function Triagem() {
  const [eixo, setEixo] = useState("");
  const [qualidade, setQualidade] = useState("");
  const [q, setQ] = useState("");
  const [sel, setSel] = useState<Pedido | null>(null);

  const params = new URLSearchParams();
  if (eixo) params.set("eixo", eixo);
  if (qualidade) params.set("qualidade", qualidade);
  if (q) params.set("q", q);

  const pedidos = useQuery({
    queryKey: ["pedidos", eixo, qualidade, q],
    queryFn: () => api.get<{ total: number; pedidos: Pedido[] }>("/pedidos?" + params.toString()),
  });
  const motivos = useQuery({
    queryKey: ["motivos"],
    queryFn: () => api.get<{ motivos: MotivoExclusao[] }>("/qualidade/motivos-exclusao"),
  });

  return (
    <div className="space-y-4">
      <PageHero title="Pedidos" highlight="elegíveis e triagem" subtitle={`${pedidos.data?.total ?? 0} pedidos após filtros de elegibilidade.`} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(300px,0.9fr)]">
        <div className="space-y-4">
          <SectionCard icon={<Filter className="h-5 w-5" />} title="Filtros" subtitle="Refine a lista de pedidos.">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <Field label="Eixo">
                <Combobox
                  options={[{ value: "", label: "Todos" }, ...[1, 2, 3, 4, 5].map((e) => ({ value: String(e), label: `Eixo ${e}` }))]}
                  value={eixo}
                  onChange={setEixo}
                  ariaLabel="Filtrar por eixo"
                />
              </Field>
              <Field label="Qualidade da cubagem">
                <Combobox
                  options={[
                    { value: "", label: "Todas" },
                    { value: "COMPLETA", label: "🟢 Completa" },
                    { value: "ESTIMADA", label: "🟡 Estimada" },
                    { value: "AUSENTE", label: "🔴 Ausente" },
                  ]}
                  value={qualidade}
                  onChange={setQualidade}
                  ariaLabel="Filtrar por qualidade"
                />
              </Field>
              <Field label="Busca" htmlFor="busca">
                <div className="flex h-11 items-center gap-2 rounded-lg border border-neutral-300 bg-white px-3">
                  <Search className="h-4 w-4 text-muted" />
                  <input id="busca" className="w-full bg-transparent text-sm outline-none" placeholder="nº do pedido" value={q} onChange={(e) => setQ(e.target.value)} />
                </div>
              </Field>
            </div>
          </SectionCard>

          <SectionCard title="Lista de pedidos" subtitle="Clique numa linha para ver os produtos do pedido.">
            {pedidos.isLoading ? (
              <Skeleton className="h-48" />
            ) : (
              <DataTable
                caption="Lista de pedidos elegíveis"
                getKey={(p) => p.pedido}
                rows={pedidos.data?.pedidos ?? []}
                onRowClick={(p) => setSel(p)}
                columns={[
                  { key: "pedido", header: "Pedido", render: (p) => p.pedido },
                  { key: "cidade", header: "Cidade", render: (p) => titulo(p.cidade) },
                  { key: "itens", header: "Itens", align: "right", render: (p) => p.itens?.length ?? 0 },
                  { key: "peso", header: "Peso", align: "right", render: (p) => peso(p.peso_kg) },
                  { key: "vol", header: "Volume", align: "right", render: (p) => volume(p.volume_m3) },
                  { key: "selo", header: "Cubagem", render: (p) => <StatusBadge>{p.qualidade_cubagem}</StatusBadge> },
                ]}
              />
            )}
          </SectionCard>
        </div>

        <aside>
          <SectionCard title="Motivos de exclusão" subtitle="Por que pedidos saíram da base.">
            {motivos.isLoading && <Skeleton className="h-40" />}
            <ul className="space-y-3 text-sm">
              {motivos.data?.motivos.map((m) => (
                <li key={m.codigo}>
                  <div className="flex justify-between">
                    <span>{m.motivo}</span>
                    <span className="tnum text-muted">{m.total} · {m.percentual}%</span>
                  </div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-neutral-200">
                    <div className="h-full rounded-full bg-ink" style={{ width: `${m.percentual}%` }} />
                  </div>
                </li>
              ))}
            </ul>
          </SectionCard>
        </aside>
      </div>

      {sel && (
        <ProdutosDialog
          open={!!sel}
          onOpenChange={(o) => !o && setSel(null)}
          pedido={sel.pedido}
          cidade={sel.cidade}
          itens={sel.itens ?? []}
          editavel={sel.qualidade_cubagem === "AUSENTE"}
        />
      )}
    </div>
  );
}
