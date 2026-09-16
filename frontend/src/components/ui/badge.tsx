import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../../lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold",
  {
    variants: {
      variant: {
        green: "bg-emerald-100 text-emerald-700",
        red: "bg-red-100 text-red-700",
        warn: "bg-brand-100 text-amber-800",
        blue: "bg-blue-100 text-blue-700",
        gray: "bg-neutral-200 text-neutral-700",
        purple: "bg-violet-100 text-violet-700",
      },
    },
    defaultVariants: { variant: "gray" },
  }
);

export function Badge({
  children,
  variant,
  className,
}: { children: React.ReactNode; className?: string } & VariantProps<typeof badgeVariants>) {
  return <span className={cn(badgeVariants({ variant }), className)}>{children}</span>;
}

// Mapa status/selo → variante (fonte única de verdade).
const MAPA: Record<string, VariantProps<typeof badgeVariants>["variant"]> = {
  COMPLETA: "green", ESTIMADA: "warn", AUSENTE: "red",
  "Carga válida": "green", Elegível: "green",
  Cancelado: "red", "Violação": "red",
  Faturado: "blue", Separacao: "blue",
  Retirada: "gray", "Cubagem incompleta": "warn",
};

export function StatusBadge({ children }: { children: string }) {
  const selo = { COMPLETA: "🟢 Completa", ESTIMADA: "🟡 Estimada", AUSENTE: "🔴 Ausente" }[children];
  return <Badge variant={MAPA[children] ?? "gray"}>{selo ?? children}</Badge>;
}
