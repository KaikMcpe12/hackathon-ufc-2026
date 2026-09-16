import * as D from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import type { ReactNode } from "react";

export function Dialog({
  open,
  onOpenChange,
  title,
  subtitle,
  children,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <D.Root open={open} onOpenChange={onOpenChange}>
      <D.Portal>
        <D.Overlay className="fixed inset-0 z-40 bg-black/40 data-[state=open]:animate-fade-up" />
        <D.Content className="fixed left-1/2 top-1/2 z-50 max-h-[85vh] w-[92vw] max-w-2xl -translate-x-1/2 -translate-y-1/2 overflow-auto rounded-2xl border border-line bg-white p-5 shadow-card data-[state=open]:animate-fade-up focus:outline-none">
          <div className="mb-3 flex items-start justify-between gap-4">
            <div>
              <D.Title className="text-lg font-semibold">{title}</D.Title>
              {subtitle && <D.Description className="text-sm text-muted">{subtitle}</D.Description>}
            </div>
            <D.Close className="grid h-8 w-8 place-items-center rounded-lg text-muted hover:bg-neutral-100" aria-label="Fechar">
              <X className="h-4 w-4" />
            </D.Close>
          </div>
          {children}
        </D.Content>
      </D.Portal>
    </D.Root>
  );
}
