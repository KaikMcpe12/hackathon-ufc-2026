import { lazy, Suspense } from "react";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { Skeleton } from "./components/ui/skeleton";

const Planejamento = lazy(() => import("./pages/Planejamento"));
const Romaneio = lazy(() => import("./pages/Romaneio"));
const Simulacao = lazy(() => import("./pages/Simulacao"));
const Qualidade = lazy(() => import("./pages/Qualidade"));
const Triagem = lazy(() => import("./pages/Triagem"));
const Importar = lazy(() => import("./pages/Importar"));

const NAV = [
  ["/", "Planejamento"],
  ["/triagem", "Pedidos elegíveis"],
  ["/qualidade", "Dados & cubagem"],
  ["/simulacao", "Simulação"],
  ["/romaneio", "Plano de carga"],
  ["/importar", "Importar"],
];

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 flex h-[76px] items-center justify-between border-b border-line bg-white px-5 sm:px-8">
        <div className="flex items-center gap-4">
          <div className="text-[27px] font-black leading-none tracking-[-4px]">
            N<span className="text-brand">L</span>
          </div>
          <div>
            <div className="text-lg font-bold leading-tight">
              Nobre<span className="text-brand">LOG</span>
            </div>
            <div className="text-xs text-muted">Inteligência Logística</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <div className="text-sm font-semibold leading-tight">Coordenador</div>
            <div className="text-xs text-muted">Nobre Lar Home Center</div>
          </div>
          <div className="grid h-9 w-9 place-items-center rounded-full bg-ink text-white" aria-hidden>
            ◉
          </div>
        </div>
      </header>

      <nav aria-label="Navegação principal" className="flex gap-2 overflow-x-auto px-4 pt-3 sm:px-6">
        {NAV.map(([to, label]) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `whitespace-nowrap rounded-full border px-3.5 py-2 text-xs font-medium transition-colors ${
                isActive
                  ? "border-ink bg-ink text-white"
                  : "border-line bg-white text-neutral-600 hover:bg-neutral-100"
              }`
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>

      <main className="mx-auto max-w-content px-4 py-5 sm:px-6">
        <Suspense fallback={<Skeleton className="h-64 w-full" />}>
          <Routes>
            <Route path="/" element={<Planejamento />} />
            <Route path="/romaneio" element={<Romaneio />} />
            <Route path="/simulacao" element={<Simulacao />} />
            <Route path="/qualidade" element={<Qualidade />} />
            <Route path="/triagem" element={<Triagem />} />
            <Route path="/importar" element={<Importar />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </Suspense>
      </main>
    </div>
  );
}
