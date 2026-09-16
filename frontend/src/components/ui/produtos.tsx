import type { ItemPedido } from "../../api/types";
import { peso, titulo, volume } from "../../lib/format";
import { Badge } from "./badge";
import { Dialog } from "./dialog";

// Modal com os PRODUTOS de um pedido (resolve a lacuna pedido↔produto).
export function ProdutosDialog({
  open,
  onOpenChange,
  pedido,
  cidade,
  itens,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  pedido: string;
  cidade?: string;
  itens: ItemPedido[];
}) {
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
                  <td className="px-3 py-2 text-right">
                    {it.quantidade} {it.unidade_venda}
                  </td>
                  <td className="px-3 py-2 text-right">{it.caixas ?? "—"}</td>
                  <td className="px-3 py-2 text-right">{peso(it.peso_total_kg)}</td>
                  <td className="px-3 py-2 text-right">{volume(it.volume_total_m3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Dialog>
  );
}
