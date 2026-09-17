import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { PackagePlus, Upload } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { api, type ApiError } from "../api/client";
import { Button } from "../components/ui/button";
import { Card, SectionCard } from "../components/ui/card";
import { Field } from "../components/ui/field";
import { PageHero } from "../components/ui/hero";

interface Relatorio {
  inseridos: number;
  atualizados: number;
  rejeitados: number;
  motivos: string[];
}
type Status = { ativo: boolean; produtos?: number; pedidos?: number };

const inputCls = "h-10 w-full rounded-lg border border-neutral-300 px-3 text-sm";

function RelatorioView({ r }: { r: Relatorio }) {
  return (
    <div className="mt-3 rounded-lg border border-line bg-neutral-50 p-2.5 text-sm">
      <b className="text-ok">{r.inseridos} inseridos</b> · <b className="text-info">{r.atualizados} atualizados</b> ·{" "}
      <b className={r.rejeitados ? "text-danger" : "text-muted"}>{r.rejeitados} rejeitados</b>
      {r.motivos.length > 0 && <div className="mt-1 text-xs text-muted">{r.motivos.join(" · ")}</div>}
    </div>
  );
}

export default function Cadastro() {
  const qc = useQueryClient();
  const status = useQuery({ queryKey: ["cadastro-status"], queryFn: () => api.get<Status>("/cadastro/status") });
  const refresh = () => qc.invalidateQueries({ queryKey: ["cadastro-status"] });

  if (status.data && !status.data.ativo)
    return (
      <div className="space-y-4">
        <PageHero title="Cadastro de" highlight="produtos e pedidos" subtitle="Registro individual (formulário) ou em lote (CSV)." />
        <Card className="p-6 text-sm text-muted">
          O cadastro exige persistência em banco. Suba o backend com <code className="rounded bg-neutral-100 px-1">STATE_BACKEND=sqlite</code>.
        </Card>
      </div>
    );

  return (
    <div className="space-y-4">
      <PageHero
        title="Cadastro de"
        highlight="produtos e pedidos"
        subtitle="Registro individual (formulário) ou em lote (CSV). Reenvio atualiza pelo código/pedido."
        action={
          <div className="text-right text-sm text-neutral-300">
            {status.data?.produtos ?? 0} produtos · {status.data?.pedidos ?? 0} pedidos
          </div>
        }
      />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ProdutoCard onDone={refresh} />
        <PedidoCard onDone={refresh} />
      </div>
    </div>
  );
}

function ProdutoCard({ onDone }: { onDone: () => void }) {
  const [f, setF] = useState({ codigo: "", produto: "", unidade_venda: "UN", peso_kg: "", volume_m3: "" });
  const [rel, setRel] = useState<Relatorio | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const set = (k: string, v: string) => setF((s) => ({ ...s, [k]: v }));

  const salvar = useMutation({
    mutationFn: () => api.post<Relatorio>("/cadastro/produto", f),
    onSuccess: (r) => { setRel(r); onDone(); toast.success("Produto cadastrado"); },
    onError: (e) => toast.error((e as unknown as ApiError).detail),
  });
  const enviarCsv = useMutation({
    mutationFn: () => { const fd = new FormData(); fd.append("arquivo", file!); return api.postForm("/cadastro/produtos", fd) as Promise<Relatorio>; },
    onSuccess: (r) => { setRel(r); onDone(); toast.success("Produtos importados"); },
    onError: (e) => toast.error((e as unknown as ApiError).detail),
  });

  return (
    <SectionCard icon={<PackagePlus className="h-5 w-5" />} title="Produtos" subtitle="Catálogo (Ranking). Chave: código.">
      <div className="grid grid-cols-2 gap-2">
        <Field label="Código"><input className={inputCls} value={f.codigo} onChange={(e) => set("codigo", e.target.value)} /></Field>
        <Field label="Unidade"><input className={inputCls} value={f.unidade_venda} onChange={(e) => set("unidade_venda", e.target.value)} /></Field>
        <div className="col-span-2"><Field label="Descrição"><input className={inputCls} value={f.produto} onChange={(e) => set("produto", e.target.value)} /></Field></div>
        <Field label="Peso (kg)"><input className={inputCls} placeholder="15,0" value={f.peso_kg} onChange={(e) => set("peso_kg", e.target.value)} /></Field>
        <Field label="Volume (m³)"><input className={inputCls} placeholder="0,036" value={f.volume_m3} onChange={(e) => set("volume_m3", e.target.value)} /></Field>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <Button size="sm" onClick={() => salvar.mutate()} disabled={!f.codigo || salvar.isPending}>Salvar produto</Button>
        <span className="text-xs text-muted">ou lote:</span>
        <input type="file" accept=".csv" className="text-xs" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <Button size="sm" variant="light" onClick={() => enviarCsv.mutate()} disabled={!file || enviarCsv.isPending}><Upload className="h-4 w-4" /> CSV</Button>
      </div>
      {rel && <RelatorioView r={rel} />}
    </SectionCard>
  );
}

function PedidoCard({ onDone }: { onDone: () => void }) {
  const [f, setF] = useState({ pedido: "", cidade: "", valor_pedido: "", situacao: "Faturado", situacao_csv_entrega: "NORMAL", itens_resumo: "", semana: 4 });
  const [rel, setRel] = useState<Relatorio | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const set = (k: string, v: string | number) => setF((s) => ({ ...s, [k]: v }));

  const salvar = useMutation({
    mutationFn: () => api.post<Relatorio>("/cadastro/pedido", f),
    onSuccess: (r) => { setRel(r); onDone(); toast.success("Pedido cadastrado"); },
    onError: (e) => toast.error((e as unknown as ApiError).detail),
  });
  const enviarCsv = useMutation({
    mutationFn: () => { const fd = new FormData(); fd.append("arquivo", file!); return api.postForm(`/cadastro/pedidos?semana=${f.semana}`, fd) as Promise<Relatorio>; },
    onSuccess: (r) => { setRel(r); onDone(); toast.success("Pedidos importados"); },
    onError: (e) => toast.error((e as unknown as ApiError).detail),
  });

  return (
    <SectionCard icon={<PackagePlus className="h-5 w-5" />} title="Pedidos" subtitle="Chave: nº do pedido. Itens no formato do resumo.">
      <div className="grid grid-cols-2 gap-2">
        <Field label="Pedido"><input className={inputCls} placeholder="L12609999" value={f.pedido} onChange={(e) => set("pedido", e.target.value)} /></Field>
        <Field label="Cidade"><input className={inputCls} value={f.cidade} onChange={(e) => set("cidade", e.target.value)} /></Field>
        <Field label="Valor"><input className={inputCls} placeholder="R$ 1.000,00" value={f.valor_pedido} onChange={(e) => set("valor_pedido", e.target.value)} /></Field>
        <Field label="Semana"><input type="number" min={1} max={4} className={inputCls} value={f.semana} onChange={(e) => set("semana", Number(e.target.value))} /></Field>
        <div className="col-span-2"><Field label="Itens (código - desc (qtd UN) | …)"><input className={inputCls} placeholder="14900 - ARGAMASSA (7,00 UN)" value={f.itens_resumo} onChange={(e) => set("itens_resumo", e.target.value)} /></Field></div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <Button size="sm" onClick={() => salvar.mutate()} disabled={!f.pedido || salvar.isPending}>Salvar pedido</Button>
        <span className="text-xs text-muted">ou lote:</span>
        <input type="file" accept=".csv" className="text-xs" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <Button size="sm" variant="light" onClick={() => enviarCsv.mutate()} disabled={!file || enviarCsv.isPending}><Upload className="h-4 w-4" /> CSV</Button>
      </div>
      {rel && <RelatorioView r={rel} />}
    </SectionCard>
  );
}
