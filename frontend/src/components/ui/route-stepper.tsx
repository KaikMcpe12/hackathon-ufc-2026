import type { ParadaDescarga } from "../../api/types";
import { titulo } from "../../lib/format";

export function RouteStepper({ paradas }: { paradas: ParadaDescarga[] }) {
  return (
    <ol className="space-y-1">
      {paradas.map((s) => (
        <li key={s.cidade} className="flex items-center gap-3 py-1.5">
          <span
            className={`grid h-7 w-7 place-items-center rounded-full text-xs font-bold ${
              s.qtd_pedidos ? "bg-brand text-ink" : "bg-neutral-200 text-neutral-500"
            }`}
          >
            {s.ordem}
          </span>
          <span className="font-medium">{titulo(s.cidade)}</span>
          <span className={`ml-auto text-xs ${s.qtd_pedidos ? "text-ink" : "text-muted"}`}>
            {s.qtd_pedidos ? `${s.qtd_pedidos} pedido(s)` : "Nenhum"}
          </span>
        </li>
      ))}
    </ol>
  );
}
