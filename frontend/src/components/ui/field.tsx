import { cloneElement, isValidElement, useId } from "react";
import type { ReactElement, ReactNode } from "react";

export function Field({
  label,
  htmlFor,
  hint,
  children,
}: {
  label: string;
  htmlFor?: string;
  hint?: string;
  children: ReactNode;
}) {
  // Associa label ↔ controle: usa `htmlFor` explícito ou gera um id e injeta no filho.
  const auto = useId();
  const id = htmlFor ?? auto;
  const child =
    !htmlFor && isValidElement(children)
      ? cloneElement(children as ReactElement<{ id?: string }>, {
          id: (children.props as { id?: string }).id ?? id,
        })
      : children;

  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-xs font-bold text-ink">
        {label}
      </label>
      {child}
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
}
