import { useMutation } from "@tanstack/react-query";
import { FileDown, Printer } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { api, type ApiError } from "../api/client";
import type { PedidoSelecionado } from "../api/types";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, SectionCard } from "../components/ui/card";
import { DataTable } from "../components/ui/data-table";
import { PageHero } from "../components/ui/hero";
import { MetricCard } from "../components/ui/metric";
import { OrganizacaoCargaView } from "../components/ui/organizacao";
import { ProdutosDialog } from "../components/ui/produtos";
import { RouteStepper } from "../components/ui/route-stepper";
import { moeda, peso, titulo, volume } from "../lib/format";
import { loadPlano } from "../lib/planoStore";

function Meta({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex-1 border-r border-line px-4 py-3 last:border-r-0">
      <div className="text-[10px] uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-0.5 font-semibold">{children}</div>
    </div>
  );
}

export default function Romaneio() {
  const plano = loadPlano();
  const [sel, setSel] = useState<PedidoSelecionado | null>(null);
  const exportar = useMutation({
    mutationFn: async () => {
      const blob = await api.postBlob("/romaneio/generate", {
        plano,
        coordenador: "Coordenador",
        data_carga: plano?.data_carga,
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "romaneio.pdf";
      a.click();
      URL.revokeObjectURL(url);
    },
    onSuccess: () => toast.success("PDF exportado"),
    onError: (e) => toast.error((e as unknown as ApiError).detail || "Falha ao gerar PDF"),
  });

  if (!plano)
    return (
      <div className="space-y-4">
        <PageHero title="Plano de carga /" highlight="Romaneio" subtitle="Documento operacional para expedição e conferência." />
        <Card className="p-6">
          <p className="text-muted">
            Nenhum plano ativo. Volte ao{" "}
            <Link className="font-semibold text-brand-500 underline" to="/">Planejamento</Link> e otimize uma carga.
          </p>
        </Card>
      </div>
    );

  const t = plano.totais;
  return (
    <div className="space-y-4">
      <PageHero
        title="Plano de carga /"
        highlight="Romaneio"
        subtitle="Documento operacional para expedição e conferência."
        action={
          <div className="flex gap-2">
            <Button variant="light" onClick={() => window.print()}><Printer className="h-4 w-4" /> Imprimir</Button>
            <Button onClick={() => exportar.mutate()} disabled={exportar.isPending}>
              <FileDown className="h-4 w-4" /> {exportar.isPending ? "Gerando…" : "Exportar PDF"}
            </Button>
          </div>
        }
      />

      <Card className="flex flex-wrap">
        <Meta label="Veículo">{plano.veiculo.nome}</Meta>
        <Meta label="Eixo">{plano.eixo.id}</Meta>
        <Meta label="Data">{plano.data_carga}</Meta>
        <Meta label="Coordenador">Coordenador</Meta>
        <Meta label="Status"><Badge variant="green">✓ Carga válida</Badge></Meta>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(320px,0.9fr)]">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MetricCard label="Peso" value={t.peso_utilizado} format={peso} ocupacao={t.ocupacao_peso} />
            <MetricCard label="Volume" value={t.volume_utilizado} format={volume} ocupacao={t.ocupacao_volume} />
            <MetricCard label="Valor" value={t.valor_total} format={moeda} sub="receita total" />
            <MetricCard label="Pedidos" value={t.quantidade_pedidos} format={(n) => String(Math.round(n))} sub={`gargalo ${plano.gargalo}`} />
          </div>

          <SectionCard title="Pedidos da carga" subtitle="Na ordem de descarga efetiva.">
            <DataTable
              caption="Pedidos da carga"
              getKey={(r) => r.pedido}
              rows={plano.pedidos_selecionados}
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
            <div className="mt-6 grid grid-cols-1 gap-6 text-center text-xs text-muted sm:grid-cols-3">
              {["Conferente", "Motorista", "Expedição"].map((r) => (
                <div key={r} className="border-t border-neutral-400 pt-5">{r} — nome e assinatura</div>
              ))}
            </div>
          </SectionCard>
        </div>

        <aside className="space-y-4">
          <SectionCard title="Sequência de descarga" subtitle="Ordem de atendimento.">
            <RouteStepper paradas={plano.sequencia_descarga} />
          </SectionCard>
          <SectionCard title="Orientação de carregamento" subtitle="Organização física sugerida.">
            <div className="rounded-xl border border-line bg-neutral-50 p-3">
              <strong>Carregue na ordem inversa da entrega.</strong>
              <p className="mt-1.5 text-sm text-muted">{plano.orientacao_carregamento.descricao}</p>
            </div>
          </SectionCard>
          <OrganizacaoCargaView org={plano.organizacao_carga} />
        </aside>
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
