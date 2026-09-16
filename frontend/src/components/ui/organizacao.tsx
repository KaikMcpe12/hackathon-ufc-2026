import { AlertTriangle, Boxes, PackageOpen } from "lucide-react";
import type { OrganizacaoCarga } from "../../api/types";
import { peso, titulo, volume } from "../../lib/format";
import { Badge } from "./badge";
import { SectionCard } from "./card";

const dens = (v: number | null) =>
  v == null ? "—" : new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(v) + " kg/m³";

export function OrganizacaoCargaView({ org }: { org: OrganizacaoCarga }) {
  return (
    <SectionCard
      icon={<Boxes className="h-5 w-5" />}
      title="Organização da carga"
      subtitle="Zonas do fundo à porta (LIFO pela rota) + densidade."
    >
      {org.abaixo_minimo && org.alerta_minimo && (
        <div className="mb-3 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-2.5 text-xs text-red-700" role="alert">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{org.alerta_minimo}</span>
        </div>
      )}

      <div className="mb-3 rounded-xl border border-line bg-neutral-50 p-3">
        <div className="flex items-center justify-between">
          <span className="text-xs uppercase text-muted">Perfil da carga</span>
          <Badge variant={org.perfil.startsWith("DENSA") ? "warn" : "blue"}>{org.perfil}</Badge>
        </div>
        <div className="tnum mt-1.5 text-sm">
          Densidade da carga <b>{dens(org.densidade_carga)}</b>{" "}
          <span className="text-muted">(ideal do veículo {dens(org.densidade_veiculo)})</span>
        </div>
        <p className="mt-1 flex items-start gap-1.5 text-xs text-neutral-600">
          <PackageOpen className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-500" />
          {org.sugestao}
        </p>
      </div>

      <ol className="space-y-2">
        {org.zonas.map((z) => (
          <li key={z.ordem} className="rounded-xl border border-line p-3">
            <div className="flex items-center justify-between">
              <span className="font-semibold">{titulo(z.cidade)}</span>
              <Badge variant="gray">{z.posicao}</Badge>
            </div>
            <div className="tnum mt-0.5 text-xs text-muted">
              {z.qtd_pedidos} pedido(s) · {peso(z.peso_kg)} · {volume(z.volume_m3)} · {dens(z.densidade)}
            </div>
            <ul className="mt-2 space-y-1">
              {z.pedidos.map((p) => (
                <li key={p.pedido} className="flex items-center justify-between gap-2 text-xs">
                  <span className="min-w-0">
                    <b>{p.pedido}</b>
                    {p.itens_base[0] && <span className="text-muted"> · {p.itens_base[0]}</span>}
                  </span>
                  <span className="tnum shrink-0 text-muted">{dens(p.densidade)}</span>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ol>
    </SectionCard>
  );
}
