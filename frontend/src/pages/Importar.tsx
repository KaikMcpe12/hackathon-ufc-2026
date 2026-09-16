import { useMutation } from "@tanstack/react-query";
import { CheckCircle2, UploadCloud } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { api, type ApiError } from "../api/client";
import type { QualidadeResumo } from "../api/types";
import { Button } from "../components/ui/button";
import { Card, SectionCard } from "../components/ui/card";
import { PageHero } from "../components/ui/hero";
import { MetricCard } from "../components/ui/metric";

const SLOTS: [string, string][] = [
  ["semana_1", "Pedidos — Semana 1"],
  ["semana_2", "Pedidos — Semana 2"],
  ["semana_3", "Pedidos — Semana 3"],
  ["semana_4", "Pedidos — Semana 4"],
  ["ranking", "Ranking Top 85"],
  ["rotas", "Rotas e Coletas"],
];

export default function Importar() {
  const [files, setFiles] = useState<Record<string, File | undefined>>({});
  const enviar = useMutation({
    mutationFn: () => {
      const fd = new FormData();
      for (const [slot, f] of Object.entries(files)) if (f) fd.append(slot, f);
      return api.postForm("/etl/ingest", fd) as Promise<{
        semanas_atualizadas: number[];
        resumo_qualidade: QualidadeResumo;
      }>;
    },
    onSuccess: () => toast.success("Dados reprocessados em memória"),
    onError: (e) => toast.error((e as unknown as ApiError).detail || "Falha na ingestão"),
  });

  const algum = Object.values(files).some((f) => f);

  return (
    <div className="space-y-4">
      <PageHero title="Importar" highlight="dados" subtitle="Envie novos CSVs para reprocessar em memória. Só os arquivos enviados são substituídos." />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <SectionCard icon={<UploadCloud className="h-5 w-5" />} title="Arquivos" subtitle="Reinício do servidor volta ao seed versionado.">
          <div className="space-y-2">
            {SLOTS.map(([slot, label]) => {
              const f = files[slot];
              return (
                <label
                  key={slot}
                  className="flex cursor-pointer items-center justify-between gap-3 rounded-xl border border-dashed border-neutral-300 px-4 py-3 text-sm transition-colors hover:border-brand hover:bg-brand-100/30"
                >
                  <span className="flex items-center gap-2">
                    {f ? <CheckCircle2 className="h-4 w-4 text-ok" /> : <UploadCloud className="h-4 w-4 text-muted" />}
                    <span className={f ? "font-medium" : "text-neutral-600"}>{label}</span>
                  </span>
                  <span className="max-w-[45%] truncate text-xs text-muted">{f ? f.name : "Escolher CSV"}</span>
                  <input type="file" accept=".csv" className="sr-only" onChange={(e) => setFiles((s) => ({ ...s, [slot]: e.target.files?.[0] }))} />
                </label>
              );
            })}
          </div>
          <Button className="mt-4" onClick={() => enviar.mutate()} disabled={enviar.isPending || !algum}>
            {enviar.isPending ? "Processando…" : "Processar"}
          </Button>
        </SectionCard>

        <div className="space-y-4">
          {enviar.data ? (
            <>
              <div className="grid grid-cols-2 gap-3">
                <MetricCard label="Registros" value={enviar.data.resumo_qualidade.registros_processados} format={(n) => String(Math.round(n))} />
                <MetricCard label="Cubagem completa 🟢" value={enviar.data.resumo_qualidade.pedidos_completa} format={(n) => String(Math.round(n))} sub={`${enviar.data.resumo_qualidade.pedidos_estimada} estimadas`} />
              </div>
              <Card className="p-4 text-sm text-muted">
                Semanas atualizadas: <b className="text-ink">{enviar.data.semanas_atualizadas.join(", ") || "—"}</b>
              </Card>
            </>
          ) : (
            <Card className="grid min-h-[200px] place-items-center p-6 text-center text-sm text-muted">
              O relatório de qualidade da ingestão aparece aqui após processar.
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
