import * as Popover from "@radix-ui/react-popover";
import { Command } from "cmdk";
import { Check, ChevronDown, Search } from "lucide-react";
import { useState } from "react";
import { cn } from "../../lib/utils";

export interface Option {
  value: string;
  label: string;
  disabled?: boolean;
  hint?: string;
}

export function Combobox({
  options,
  value,
  onChange,
  placeholder = "Selecione",
  searchPlaceholder = "Buscar…",
  ariaLabel,
  id,
}: {
  options: Option[];
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  ariaLabel?: string;
  id?: string;
}) {
  const [open, setOpen] = useState(false);
  const sel = options.find((o) => o.value === value);
  return (
    <Popover.Root open={open} onOpenChange={setOpen}>
      <Popover.Trigger asChild>
        <button
          type="button"
          id={id}
          aria-label={ariaLabel}
          className="flex h-11 w-full items-center justify-between rounded-lg border border-neutral-300 bg-white px-3 text-left text-sm transition-colors hover:border-neutral-400"
        >
          <span className={cn("truncate", !sel && "text-muted")}>{sel ? sel.label : placeholder}</span>
          <ChevronDown className="h-4 w-4 shrink-0 text-muted" />
        </button>
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Content
          align="start"
          sideOffset={6}
          className="z-50 w-[var(--radix-popover-trigger-width)] overflow-hidden rounded-xl border border-line bg-white shadow-card data-[state=open]:animate-fade-up"
        >
          <Command loop>
            <div className="flex items-center gap-2 border-b border-line px-3">
              <Search className="h-4 w-4 text-muted" />
              <Command.Input
                placeholder={searchPlaceholder}
                className="h-10 w-full bg-transparent text-sm outline-none placeholder:text-muted"
              />
            </div>
            <Command.List className="max-h-64 overflow-auto p-1">
              <Command.Empty className="px-3 py-6 text-center text-sm text-muted">
                Nada encontrado.
              </Command.Empty>
              {options.map((o) => (
                <Command.Item
                  key={o.value}
                  value={o.label}
                  disabled={o.disabled}
                  onSelect={() => {
                    if (!o.disabled) {
                      onChange(o.value);
                      setOpen(false);
                    }
                  }}
                  className="flex cursor-pointer items-center justify-between gap-2 rounded-lg px-3 py-2 text-sm aria-selected:bg-neutral-100 data-[disabled='true']:cursor-not-allowed data-[disabled='true']:opacity-40"
                >
                  <span className="min-w-0">
                    <span className="block truncate">{o.label}</span>
                    {o.hint && <span className="block truncate text-xs text-muted">{o.hint}</span>}
                  </span>
                  {o.value === value && <Check className="h-4 w-4 shrink-0 text-brand-500" />}
                </Command.Item>
              ))}
            </Command.List>
          </Command>
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}
