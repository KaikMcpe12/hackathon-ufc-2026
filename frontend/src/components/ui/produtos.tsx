import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { api, type ApiError } from "../../api/client";
import type { ItemPedido } from "../../api/types";
import { peso, titulo, volume } from "../../lib/format";
import { Badge } from "./badge";
import { Button } from "./button";
import { Dialog } from "./dialog";

// Modal com os PRODUTOS de um pedido (resolve a lacuna pedido↔produto).
// Com `editavel`, permite informar a cubagem de itens 🔴 (UC07).
export function ProdutosDialog({
  open,
  onOpenChange,
  pedido,
  cidade,
  itens,
  editavel = false,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  pedido: string;
  cidade?: string;
  itens: ItemPedido[];
  editavel?: boolean;
  onSaved?: () => void;
}) {
  const qc = useQueryClient();
  const faltantes = itens.filter((it) => it.peso_total_kg == null || it.volume_total_m3 == null);
  const [vals, setVals] = useState<Record<string, { peso: string; volume: string }>>({});

  const salvar = useMutation({
    mutationFn: () =>
      api.post(`/pedidos/${pedido}/revisar`, {
        itens: faltantes.map((it) => ({
          codigo: it.codigo,
          peso_kg: Number(vals[it.codigo]?.peso ?? 0),
          volume_m3: Number(vals[it.codigo]?.volume ?? 0),
        })),
      }),
    onSuccess: () => {
      toast.success(`Cubagem do pedido ${pedido} atualizada`);
      qc.invalidateQueries({ queryKey: ["pedidos"] });
      onSaved?.();
      onOpenChange(false);
    },
    onError: (e) => toast.error((e as unknown as ApiError).detail || "Falha ao salvar"),
  });

  const podeSalvar = faltantes.every(
    (it) => Number(vals[it.codigo]?.peso) > 0 && Number(vals[it.codigo]?.volume) > 0
  );

  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
      title={`Produtos do pedido ${pedido}`}
      subtitle={cidade ? `${titulo(cidade)} · ${itens.length} item(ns)` : `${itens.length} item(ns)`}
    >
      {itens.length === 0 ? (
        <p className="text-sm text-muted">Sem itens cubados para este pedido.</p>
      ) : (
        <div className="overflow-auto rounded-xl border border-line">
          <table className="w-full min-w-[560px] text-sm">
            <thead className="bg-neutral-100">
              <tr className="text-left text-xs uppercase text-muted">
                <th className="px-3 py-2">Cód.</th>
                <th className="px-3 py-2">Produto</th>
                <th className="px-3 py-2 text-right">Qtd</th>
                <th className="px-3 py-2 text-right">Caixas</th>
                <th className="px-3 py-2 text-right">Peso</th>
                <th className="px-3 py-2 text-right">Volume</th>
              </tr>
            </thead>
            <tbody className="tnum">
              {itens.map((it, i) => (
                <tr key={`${it.codigo}-${i}`} className="border-t border-line">
                  <td className="px-3 py-2">{it.codigo}</td>
                  <td className="px-3 py-2">
                    <span className="block max-w-[240px] truncate" title={it.descricao}>{it.descricao}</span>
                    {it.dado_estimado && <Badge variant="warn">estimado</Badge>}
                  </td>
                  <td className="px-3 py-2 text-right">{it.quantidade} {it.unidade_venda}</td>
                  <td className="px-3 py-2 text-right">{it.caixas ?? "—"}</td>
                  <td className="px-3 py-2 text-right">{peso(it.peso_total_kg)}</td>
                  <td className="px-3 py-2 text-right">{volume(it.volume_total_m3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {editavel && faltantes.length > 0 && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-brand-100/40 p-3">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-amber-900">
            <AlertTriangle className="h-4 w-4" />
            Informe a cubagem dos itens sem dados (o pedido volta a ser elegível como 🟡)
          </div>
          <div className="space-y-2">
            {faltantes.map((it) => (
              <div key={it.codigo} className="grid grid-cols-[1fr_auto_auto] items-center gap-2 text-sm">
                <span className="truncate" title={it.descricao}>{it.codigo} · {it.descricao}</span>
                <input
                  type="number" step="0.001" min="0" placeholder="peso kg"
                  aria-label={`Peso total do item ${it.codigo} em kg`}
                  className="h-9 w-24 rounded-lg border border-neutral-300 px-2"
                  value={vals[it.codigo]?.peso ?? ""}
                  onChange={(e) => setVals((v) => ({ ...v, [it.codigo]: { peso: e.target.value, volume: v[it.codigo]?.volume ?? "" } }))}
                />
                <input
                  type="number" step="0.00001" min="0" placeholder="vol m³"
                  aria-label={`Volume total do item ${it.codigo} em m³`}
                  className="h-9 w-24 rounded-lg border border-neutral-300 px-2"
                  value={vals[it.codigo]?.volume ?? ""}
                  onChange={(e) => setVals((v) => ({ ...v, [it.codigo]: { peso: v[it.codigo]?.peso ?? "", volume: e.target.value } }))}
                />
              </div>
            ))}
          </div>
          <Button
            className="mt-3"
            size="sm"
            onClick={() => salvar.mutate()}
            disabled={!podeSalvar || salvar.isPending}
          >
            {salvar.isPending ? "Salvando…" : "Salvar cubagem"}
          </Button>
        </div>
      )}
    </Dialog>
  );
}
