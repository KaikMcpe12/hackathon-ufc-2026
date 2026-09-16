import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Sparkles, Truck as TruckIcon } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api, type ApiError } from "../api/client";
import type { Eixo, Insight, PedidoSelecionado, PlanoDeCarga, Veiculo } from "../api/types";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, SectionCard } from "../components/ui/card";
import { Combobox } from "../components/ui/combobox";
import { Field } from "../components/ui/field";
import { PageHero } from "../components/ui/hero";
import { MetricCard } from "../components/ui/metric";
import { DataTable } from "../components/ui/data-table";
import { OrganizacaoCargaView } from "../components/ui/organizacao";
import { ProdutosDialog } from "../components/ui/produtos";
import { RouteStepper } from "../components/ui/route-stepper";
import { Truck } from "../components/ui/truck";
import { moeda, peso, titulo, volume } from "../lib/format";
import { savePlano } from "../lib/planoStore";

export default function Planejamento() {
  const nav = useNavigate();
  const eixos = useQuery({ queryKey: ["eixos"], queryFn: () => api.get<{ eixos: Eixo[] }>("/eixos") });
  const veiculos = useQuery({
    queryKey: ["veiculos"],
    queryFn: () => api.get<{ veiculos: Veiculo[] }>("/veiculos"),
  });

  const [eixo, setEixo] = useState("4");
  const [veiculo, setVeiculo] = useState("ACELLO 815");
  const [semana, setSemana] = useState("");
  const [incluir, setIncluir] = useState(true);
  const [plano, setPlano] = useState<PlanoDeCarga | null>(null);
  const [sel, setSel] = useState<PedidoSelecionado | null>(null);

  const otimizar = useMutation({
    mutationFn: () =>
      api.post<PlanoDeCarga>("/otimizar", {
        eixo: Number(eixo),
        veiculo,
        semana: semana ? Number(semana) : null,
        incluir_estimadas: incluir,
      }),
    onSuccess: (p) => {
      setPlano(p);
      savePlano(p);
      toast.success(`Carga otimizada · ${p.totais.quantidade_pedidos} pedidos`);
    },
    onError: (e) => toast.error((e as unknown as ApiError).detail),
  });

  const insight = useMutation({
    mutationFn: (p: PlanoDeCarga) => api.post<Insight>("/insight", { plano: p }),
  });

  const veicOpts =
    veiculos.data?.veiculos.map((v) => ({
      value: v.nome,
      label: v.nome,
      disabled: !v.selecionavel,
      hint: v.selecionavel ? `${v.capacidade_peso} kg · ${v.capacidade_volume} m³` : "fora do escopo",
    })) ?? [];
  const eixoOpts =
    eixos.data?.eixos.map((e) => ({ value: String(e.id), label: `Eixo ${e.id}`, hint: e.nome })) ?? [];
  const t = plano?.totais;

  return (
    <div className="space-y-4">
      <PageHero
        title="Planejamento"
        highlight="inteligente de cargas"
        subtitle="Mais eficiência para sua operação. Aproveite melhor cada viagem."
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(320px,0.9fr)]">
        {/* Coluna principal */}
        <div className="space-y-4">
          <SectionCard
            icon={<TruckIcon className="h-5 w-5" />}
            title="Configurar carga"
            subtitle="Selecione os parâmetros para montar e otimizar sua carga."
          >
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <Field label="Eixo de entrega">
                <Combobox options={eixoOpts} value={eixo} onChange={setEixo} ariaLabel="Eixo de entrega" />
              </Field>
              <Field label="Veículo">
                <Combobox options={veicOpts} value={veiculo} onChange={setVeiculo} ariaLabel="Veículo" />
              </Field>
              <Field label="Semana" hint="Vazio = todas as semanas do eixo (recomendado).">
                <Combobox
                  options={[
                    { value: "", label: "Todas as semanas" },
                    ...[1, 2, 3, 4].map((s) => ({ value: String(s), label: `Semana ${s}` })),
                  ]}
                  value={semana}
                  onChange={setSemana}
                  ariaLabel="Semana"
                />
              </Field>
              <label className="flex items-end gap-2 pb-2 text-sm text-neutral-600">
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-brand-500"
                  checked={incluir}
                  onChange={(e) => setIncluir(e.target.checked)}
                />
                Incluir cubagem estimada (🟡)
              </label>
            </div>
            <Button
              className="mt-4"
              onClick={() => otimizar.mutate()}
              disabled={otimizar.isPending}
            >
              <Sparkles className="h-4 w-4" />
              {otimizar.isPending ? "Otimizando…" : "Otimizar carga"}
            </Button>
          </SectionCard>

          {t && (
            <div aria-live="polite" className="space-y-4">
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <MetricCard label="Peso utilizado" value={t.peso_utilizado} format={peso} sub={`de ${peso(t.peso_capacidade)}`} ocupacao={t.ocupacao_peso} />
                <MetricCard label="Volume utilizado" value={t.volume_utilizado} format={volume} sub={`de ${volume(t.volume_capacidade)}`} ocupacao={t.ocupacao_volume} />
                <MetricCard label="Valor da carga" value={t.valor_total} format={moeda} sub="receita total" />
                <MetricCard label="Pedidos" value={t.quantidade_pedidos} format={(n) => String(Math.round(n))} sub={`de ${plano!.pedidos_selecionados.length + plano!.pedidos_rejeitados.length} elegíveis`} />
              </div>

              <SectionCard icon={<TruckIcon className="h-5 w-5" />} title="Pedidos selecionados" subtitle="Na ordem de descarga efetiva.">
                <DataTable
                  caption="Pedidos selecionados na carga"
                  getKey={(r) => r.pedido}
                  rows={plano!.pedidos_selecionados}
                  onRowClick={(r) => setSel(r)}
                  columns={[
                    { key: "ordem", header: "#", render: (r) => r.ordem },
                    { key: "pedido", header: "Pedido", render: (r) => r.pedido },
                    { key: "cidade", header: "Cidade", render: (r) => titulo(r.cidade) },
                    { key: "itens", header: "Itens", align: "right", render: (r) => r.qtd_itens ?? r.itens?.length ?? 0 },
                    { key: "valor", header: "Valor", align: "right", render: (r) => moeda(r.valor) },
                    { key: "peso", header: "Peso", align: "right", render: (r) => peso(r.peso_kg) },
                    { key: "vol", header: "Volume", align: "right", render: (r) => volume(r.volume_m3) },
                  ]}
                  footer={["Total", moeda(t.valor_total), peso(t.peso_utilizado), volume(t.volume_utilizado)]}
                />
              </SectionCard>
            </div>
          )}
        </div>

        {/* Painel lateral */}
        <motion.aside layout className="space-y-4">
          {plano && t ? (
            <>
              <SectionCard title="Resumo da carga" action={<Badge variant="green">✓ Carga válida</Badge>}>
                <div className="grid grid-cols-2 gap-2">
                  <div className="rounded-xl border border-line bg-neutral-50 p-3">
                    <div className="text-xs text-muted">Fator limitante</div>
                    <div className="mt-1 font-bold">{plano.gargalo}</div>
                  </div>
                  <div className="rounded-xl border border-line bg-neutral-50 p-3">
                    <div className="text-xs text-muted">Violações</div>
                    <div className={`mt-1 font-bold ${plano.violacoes ? "text-danger" : "text-ok"}`}>{plano.violacoes}</div>
                  </div>
                </div>
                <Truck />
                <div className="text-center">
                  <strong>{plano.veiculo.nome}</strong>
                  <div className="text-xs text-muted">{plano.veiculo.capacidade_peso} kg • {plano.veiculo.capacidade_volume} m³</div>
                </div>
                <div className="mt-4">
                  <div className="mb-1 text-sm font-semibold">Rota de descarga</div>
                  <RouteStepper paradas={plano.sequencia_descarga} />
                  <div className="mt-3 rounded-lg border border-amber-200 bg-brand-100/60 p-2.5 text-xs text-amber-900">
                    <b>LIFO:</b> {plano.orientacao_carregamento.descricao}
                  </div>
                </div>
              </SectionCard>

              <OrganizacaoCargaView org={plano.organizacao_carga} />

              <SectionCard
                icon={<Sparkles className="h-5 w-5" />}
                title="Insight de IA"
                subtitle="Leitura operacional da carga."
                action={
                  <button className="text-xs font-semibold text-brand-500 hover:underline" onClick={() => insight.mutate(plano)} disabled={insight.isPending}>
                    {insight.isPending ? "Gerando…" : "Gerar"}
                  </button>
                }
              >
                {insight.isError && <p className="text-sm text-muted">Insight de IA não disponível no momento.</p>}
                {insight.data && <p className="text-sm text-neutral-700">{insight.data.resumo}</p>}
                {!insight.data && !insight.isError && <p className="text-sm text-muted">Clique em “Gerar” para uma leitura da carga.</p>}
              </SectionCard>

              <Button variant="dark" className="w-full" onClick={() => nav("/romaneio")}>
                Gerar plano de carga →
              </Button>
            </>
          ) : (
            <Card className="p-5">
              <p className="text-sm text-muted">O resultado da otimização aparece aqui: fator limitante, rota de descarga e insight de IA.</p>
            </Card>
          )}
        </motion.aside>
      </div>

      {sel && (
        <ProdutosDialog
          open={!!sel}
          onOpenChange={(o) => !o && setSel(null)}
          pedido={sel.pedido}
          cidade={sel.cidade}
          itens={sel.itens ?? []}
        />
      )}
    </div>
  );
}
