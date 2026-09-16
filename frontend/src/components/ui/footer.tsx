import { AtSign, MapPin, Phone } from "lucide-react";

const SEGMENTOS = [
  "Porcelanatos", "Iluminação", "Tintas & Texturas",
  "Elétrica", "Hidráulica", "Ferramentas", "Decoração",
];

export function Footer() {
  return (
    <footer className="mt-8 border-t border-line bg-white">
      <div className="mx-auto grid max-w-content grid-cols-1 gap-8 px-6 py-10 sm:grid-cols-3">
        {/* Sobre */}
        <div>
          <div className="mb-3 flex items-center gap-3">
            <img src="/nobre-lar-logo.png" alt="Nobre Lar Homecenter" className="h-10 w-10 rounded-lg object-contain" />
            <div>
              <div className="font-bold leading-tight">Nobre Lar Homecenter</div>
              <div className="text-xs text-muted">Tudo para sua obra em um só lugar</div>
            </div>
          </div>
          <p className="text-sm text-neutral-600">
            Home center com <b>38 anos</b> de mercado e mais de <b>40 mil itens</b>, referência em materiais
            de construção no Sertão Central e Inhamuns (Crateús-CE).
          </p>
        </div>

        {/* Segmentos / representação */}
        <div>
          <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">Segmentos</div>
          <div className="flex flex-wrap gap-1.5">
            {SEGMENTOS.map((s) => (
              <span key={s} className="rounded-full border border-line bg-neutral-50 px-2.5 py-1 text-xs text-neutral-700">
                {s}
              </span>
            ))}
          </div>
        </div>

        {/* Contato */}
        <div>
          <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">Contato</div>
          <ul className="space-y-2 text-sm text-neutral-600">
            <li className="flex items-start gap-2">
              <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-brand-500" />
              Av. Dr. Edilberto Frota, 2000 — Planalto, Crateús-CE
            </li>
            <li className="flex items-center gap-2">
              <Phone className="h-4 w-4 shrink-0 text-brand-500" />
              <a className="hover:underline" href="https://wa.me/558899520982">(88) 99952-0982 · WhatsApp</a>
            </li>
            <li className="flex items-center gap-2">
              <AtSign className="h-4 w-4 shrink-0 text-brand-500" />
              <a className="hover:underline" href="https://instagram.com/nobrelar_">@nobrelar_</a>
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t border-line py-3 text-center text-xs text-muted">
        NobreLOG Optimizer · ferramenta interna de otimização de carga · Nobre Lar Homecenter
      </div>
    </footer>
  );
}
